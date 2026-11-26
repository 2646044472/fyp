#!/usr/bin/env python3
"""Loopback FPN+C capture and demonstration verification."""
import argparse
import base64
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from urllib.parse import urlsplit

from fpn_c_e10_shadow import PIPELINE, ShadowFailure, load_pipeline, parse_manifest
from station_camera_power import CameraPower

GEOMETRY = "fpn-native-gray128-v1"
MAX_FRAME_AGE = 1.2
SCORE_AGE_LIMIT = 1.25
DEMO_MATCH_THRESHOLD = 0.80
CAPTURE_COUNT = 10
TEMPLATE_COUNT = 5
# Explicitly separate from old 8088, which may still own the camera.
PORT = 8080
CAPTURE_SOURCE = "fpn-c-e10-v3-video-native"
START_ERRORS = {
    "Enter a name and choose left or right hand.": "Enter a display name and choose the left or right hand.",
    "user must contain a letter or number": "Enter a valid ID.",
    "Invalid enrollment request ID. Start again.": "Invalid enrollment session. Start again.",
    "The hand suffix in the ID does not match the selected hand.": "The hand suffix in the ID does not match the selected hand.",
    "An enrollment is already in progress. Cancel it first.": "A capture session is already in progress. Save or cancel it first.",
    "This enrollment request has ended. Start again.": "This capture session has ended. Start again.",
    "This ID is already enrolled. Choose another ID.": "This ID is already enrolled. Use a different ID for a new session.",
    "The hand in the original ID differs from the selected hand.": "The other hand is already enrolled under this ID.",
}


class VerificationUnavailable(ValueError):
    """A recoverable verification request with a message for the station UI."""


def identify_namespace(config):
    signature = ":".join((PIPELINE, GEOMETRY, config["fpn"][1], config["c"][1]))
    return hashlib.sha256(signature.encode("ascii")).hexdigest()


def open_workspace(path, identity):
    """Use an empty exclusive directory or one marked for these exact assets."""
    if path.is_symlink():
        raise ShadowFailure("runtime_path_must_not_be_symlink")
    if not path.is_dir():
        path.mkdir(mode=0o700, parents=False, exist_ok=False)
    if path.stat().st_mode & 0o077:
        raise ShadowFailure("runtime_must_be_private_0700")
    marker = path / ".fpn-c-e10-runtime.json"
    lock = path / ".fpn-c-e10-lock"
    if not marker.exists() and not marker.is_symlink() and set(path.iterdir()) - {lock}:
        raise ShadowFailure("runtime_not_empty_or_legacy")
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    handle = os.fdopen(fd, "r+", encoding="ascii")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        expected = {"geometry": GEOMETRY, "identity": identity, "schema": 1}
        if marker.exists() or marker.is_symlink():
            if marker.is_symlink() or json.loads(marker.read_text("ascii")) != expected:
                raise ShadowFailure("runtime_identity_mismatch")
        elif set(path.iterdir()) != {lock}:
            raise ShadowFailure("runtime_not_empty_or_legacy")
        else:
            with marker.open("x", encoding="ascii") as file:
                json.dump(expected, file)
        gallery = path / "templates"
        if gallery.is_symlink() or any(f.is_symlink() for f in gallery.glob("*")):
            raise ShadowFailure("runtime_templates_must_not_be_symlinks")
        return handle
    except BaseException:
        handle.close()
        # Do not remove the lock file; another process may own the inode.
        raise


def classify_frame(np, cv, backend, model, rgb, *, processed_age):
    """Evaluate exactly the captured RGB; a low confidence is not 'no hand'."""
    roi, reason, corners = backend.crop_gray(model, rgb, device="cpu")
    if processed_age() > MAX_FRAME_AGE:
        return None, None, {"contrast": 0., "sharpness": 0.}, "fpn_frame_stale"
    if roi is None:
        return None, None, {"contrast": 0., "sharpness": 0.}, reason
    if (roi.dtype != np.uint8 or roi.shape != (128, 128)
            or corners.shape != (4, 2) or not np.isfinite(corners).all()):
        return None, None, {"contrast": 0., "sharpness": 0.}, "fpn_output_mismatch"
    x = roi.astype(np.float32)
    gx = cv.Sobel(x, cv.CV_32F, 1, 0, ksize=3)
    gy = cv.Sobel(x, cv.CV_32F, 0, 1, ksize=3)
    quality = {"contrast": float(np.std(x)), "sharpness": float(np.var(np.hypot(gx, gy)))}
    if not all(math.isfinite(v) and v > 0 for v in quality.values()):
        return None, None, quality, "fpn_crop_unusable"
    return roi, corners, quality, "valid"


def capture_reference(np, cv, roi, corners, size):
    """Descriptive measurements from the same exposure as the visible ROI."""
    return {
        "roi_area_pct": round(100 * cv.contourArea(corners.astype(np.float32)) / math.prod(size), 1),
        "median_gray": round(float(np.median(roi)), 1),
        "dark_pct": round(100 * float(np.mean(roi <= 5)), 1),
        "bright_pct": round(100 * float(np.mean(roi >= 250)), 1),
    }


def read_uvc_controls(camera):
    settings = {}
    if camera is None:
        return settings
    try:
        result = subprocess.run(["v4l2-ctl", "--device", str(camera.device), "--list-ctrls"],
                                capture_output=True, text=True, timeout=1.5, check=True)
    except (OSError, subprocess.SubprocessError):
        return settings
    controls = {"auto_exposure", "focus_automatic_continuous", "brightness", "contrast", "sharpness"}
    for line in result.stdout.splitlines():
        match = re.match(r"\s*(\w+)\s+0x\w+.*?\bvalue=(-?\d+)", line)
        if match and match[1] in controls:
            settings[match[1]] = int(match[2])
    return settings


def require_template(np, features, metadata, required):
    if any(metadata.get(key) != value for key, value in required.items()):
        raise ValueError("FPN+C template version mismatch. Re-enroll in a separate directory.")
    if (features.shape != (TEMPLATE_COUNT, 512) or features.dtype != np.float32 or not np.isfinite(features).all()
            or np.any(np.linalg.norm(features.astype(np.float64), axis=1) <= 0)):
        raise ValueError("The FPN+C template is corrupt or incomplete.")


def score_gallery(np, probe, store, required, *, threshold=None):
    vector = np.asarray(probe, dtype=np.float64)
    length = np.linalg.norm(vector)
    if vector.shape != (512,) or not np.isfinite(vector).all() or not math.isfinite(length) or length <= 0:
        raise ValueError("Invalid query embedding.")
    vector /= length
    scores = []
    for name in store.list_template_ids():
        if not store.exists(name):
            raise ValueError("The station template is incomplete.")
        features, metadata = store.load(name)
        require_template(np, features, metadata, required)
        template = features.astype(np.float64)
        template /= np.linalg.norm(template, axis=1, keepdims=True)
        similarities = template @ vector
        sample_index = int(np.argmax(similarities))
        a = similarities[sample_index]
        if not np.isfinite(a) or abs(float(a)) > 1 + 1e-12:
            raise ValueError("Invalid match scores.")
        scores.append((float(np.clip(a, -1., 1.)), name, metadata, sample_index + 1))
    scores.sort(key=lambda item: item[0], reverse=True)
    top = [item[0] for item in scores[:2]]
    tied = len(top) == 2 and abs(top[0] - top[1]) <= 1e-12
    result = {"mode": "scores_only", "gallery_size": len(scores), "top_cosines": top, "tied_top": tied}
    if threshold is None:
        return result
    result.update(mode="demo_verification", threshold=threshold, decision="EMPTY", best_match=None)
    if tied:
        result["decision"] = "TIED"
    elif scores:
        score, name, meta, index = scores[0]
        result["decision"] = "MATCH" if score >= threshold else "BELOW_THRESHOLD"
        result["best_match"] = {
            "user_id": name, "display_name": meta.get("display_name", name), "hand": meta.get("hand_declared_by_user"),
            "archive_id": meta.get("enrollment_archive_id"), "sample_index": index,
        }
    return result


def make_camera(base, frame_class, backend, localizer, np, cv):
    class Camera(base):
        def jpeg_frame(self):
            with self._jpeg_lock:
                with self.lock:
                    if not self._camera_frame_state()["camera_ready"] or self.latest is None:
                        raise RuntimeError("camera unavailable")
                    frame = self.latest_processed
                    annotated = (frame is not None and frame.enrollment_quad is not None
                                 and 0 <= time.monotonic() - frame.captured.captured_monotonic <= MAX_FRAME_AGE)
                    source = frame.captured if annotated else self.latest
                    key = (source.frame_id, annotated)
                    if getattr(self, "_station_preview_key", None) == key:
                        return self._station_preview
                data = self._encode_preview(source.image, frame.enrollment_quad if annotated else None,
                                            frame.roi_status if annotated else {"roi_mode": "capture"})
                self._station_preview_key, self._station_preview = key, data
                return data

        def _processing_loop(self):
            while self.running:
                with self.frame_condition:
                    self.frame_condition.wait_for(lambda: not self.running or self.pending_frame is not None)
                    if not self.running:
                        return
                    captured, self.pending_frame = self.pending_frame, None
                try:
                    roi, corners, quality, reason = classify_frame(
                        np, cv, backend, localizer, np.asarray(captured.image, dtype=np.uint8),
                        processed_age=lambda: time.monotonic() - captured.captured_monotonic,
                    )
                except Exception:
                    roi, corners, quality, reason = None, None, {"contrast": 0., "sharpness": 0.}, "fpn_processing_error"
                valid = roi is not None
                state = "READY" if valid else "TRACKING"
                status = {
                    "roi_mode": PIPELINE, "roi_geometry": GEOMETRY, "roi_status": "tracking" if valid else reason,
                    "roi_reason": None if valid else reason, "frame_id": captured.frame_id,
                    "quality_status": state, "quality_reason": None if valid else reason,
                    "quality_consecutive_frames": int(valid), "quality_required_frames": 1,
                    "demo_quality_status": state, "demo_quality_reason": None if valid else reason,
                    "demo_quality_consecutive_frames": int(valid), "demo_quality_required_frames": 1,
                    "enrollment_geometry_valid": valid, "quality": quality,
                    "preview_label": "FPN ROI",
                    "capture_reference": capture_reference(np, cv, roi, corners, captured.image.size) if valid else None,
                    "captured_monotonic_ms": captured.captured_monotonic * 1000.,
                    "processed_monotonic_ms": time.monotonic() * 1000.,
                }
                with self.frame_condition:
                    # Replace stale success even on failure; never recycle it.
                    self.latest_processed = frame_class(
                        captured, corners if valid else None,
                        roi if valid else np.zeros((128, 128), np.uint8), status, corners if valid else None)
                    self.latest_roi_status = status
                    self.frame_condition.notify_all()
    return Camera


def station_stack(base, backend, localizer, c_model, root, identity, np, cv, *, match_threshold=DEMO_MATCH_THRESHOLD):
    """Reuse V3 session window and review, no DemoFlow payment/storage bootstrap."""
    import demo_flow
    import enrollment_best_frame
    from enrollment_window_adapter import arm_preview, sync_selection
    from templates import TemplateStore

    required = {"algorithm": PIPELINE, "roi_geometry": GEOMETRY, "matcher_runtime_identity": identity}

    def active_enrollment(flow):
        session = flow.enrollment_session
        return bool(session and time.monotonic() - session["last_activity"] < demo_flow.ENROLLMENT_TIMEOUT_SECONDS)

    class Roster:
        """Compatibility facade for the enrollment lifecycle; no payment system."""
        def __init__(self, store):
            self.store = store
        def user_exists(self, user_id):
            return self.store.exists(user_id)
        def display_name_for(self, user_id):
            return self.store.read_metadata(user_id)["display_name"]
        def create_account(self, user_id, display_name, _amount):
            if display_name != self.display_name_for(user_id):
                raise ValueError("The station templates are inconsistent.")
        def balance_for(self, _name):
            return 0
        def list_users(self):
            result = []
            for name in self.store.list_template_ids():
                if self.store.exists(name):
                    result.append({"user_id": name, "display_name": self.display_name_for(name), "balance_cents": 0})
            return result

    class ShadowFlow(demo_flow.DemoFlow):
        station_capture_seconds = 60
        station_continuous = True
        station_target_count = CAPTURE_COUNT
        station_template_count = TEMPLATE_COUNT
        allow_repeat_capture = True
        archive_native_roi = True

        def __init__(self, capture_profile, candidate):
            self.algorithm = SimpleNamespace(name=PIPELINE)
            self.gallery = SimpleNamespace(required_metadata=required)
            self.runtime_identity = identity
            self.roi_geometry = GEOMETRY
            self.capture_profile = "fpn-shadow-" + capture_profile
            self.capture_source = CAPTURE_SOURCE
            self.store = TemplateStore(root / "templates", compression_level=1)
            self.payments = Roster(self.store)
            self.lock = threading.Lock()
            self.enrollment_capture_lock = threading.Lock()
            self.enrollment_candidate = candidate
            self.pending = {}
            self.enrollment_session = None
            self.enrollment_request_states = {}
            self.enrollment_archive_root = root / "enrollment_pairs"
        def enrollment_start(self, user_id, display_name, hand, request_token=None):
            # Do not use base refresh semantics to overwrite wrong-version records.
            user_id = demo_flow.safe_user_id(user_id)
            if self.store.exists(user_id):
                require_template(np, *self.store.load(user_id), required)
            return super().enrollment_start(user_id, display_name, hand, request_token)
        def identify(self):
            raise ValueError("No verification decision is available.")

    class ShadowApp:
        def __init__(self, feed=None, *, create_feed=None, native_size=None):
            self.power = CameraPower(create_feed, on_idle=self.pause_camera)
            self.power.feed = feed
            self.managed_camera = create_feed is not None
            self.native_size = native_size
            self.camera_controls = read_uvc_controls(getattr(feed, "uvc_camera", None))
            self.score_lock = threading.Lock()
            self.encode_lock = threading.Lock()
            self.last_probe_frame = -1
            profile = feed.capture_profile if feed is not None else "camera-off"
            self.demo = ShadowFlow(profile, lambda: self.capture_demo_feature(enrollment=True, include_candidate=True))
            self.demo.station_preview_seconds = 5 if self.managed_camera else 0

        @property
        def camera(self):
            return self.power.feed

        def use_camera(self, owner):
            previous = self.camera
            feed = self.power.use(owner)
            if feed is not previous:
                self.camera_controls = read_uvc_controls(getattr(feed, "uvc_camera", None))
                with self.demo.lock:
                    self.demo.capture_profile = "fpn-shadow-" + feed.capture_profile

        def reconcile_capture(self, token):
            if not self.managed_camera:
                return
            owner = ("capture", token)
            with self.power.lock:
                with self.demo.lock:
                    s = self.demo.enrollment_session
                    collecting = (active_enrollment(self.demo) and s["token"] == token
                                  and s.get("station_state") == "collecting")
                if collecting:
                    self.use_camera(owner)
                    if s.get("station_preview_until") is None:
                        camera = self.camera
                        with camera.lock:
                            camera_ready = camera._camera_frame_state()["camera_ready"]
                        if camera_ready:
                            with self.demo.lock:
                                if self.demo.enrollment_session is s and s.get("station_state") == "collecting":
                                    arm_preview(s, time.monotonic())
                else:
                    self.power.close(owner)

        def pause_camera(self, owner):
            if owner[0] == "capture":
                with self.demo.lock:
                    s = self.demo.enrollment_session
                    if active_enrollment(self.demo) and s["token"] == owner[1] and s.get("station_state") == "collecting":
                        sync_selection(s, stop=True)

        def verify_camera(self, token, action):
            owner = ("verify", token)
            with self.power.lock:
                if action == "stop":
                    self.power.close(owner)
                    return {"camera_open": False}
                with self.demo.lock:
                    if active_enrollment(self.demo):
                        raise VerificationUnavailable("Capture is in progress. Save or cancel the current session first.")
                if action == "keepalive" and self.power.owner != owner:
                    return {"camera_open": False}
                if self.power.owner not in (None, owner):
                    raise VerificationUnavailable("The camera is in use in another tab.")
                if self.managed_camera:
                    self.use_camera(owner)
                return {"camera_open": self.camera is not None}

        def status(self):
            with self.power.lock:
                camera = self.camera
                mode = self.power.owner[0] if self.power.owner else None
                controls = self.camera_controls
            status = camera.status() if camera is not None else {
                "camera_ready": False, "processing_thread_alive": False, "roi_status_fresh": False,
            }
            status.update(backend=PIPELINE, mode="scores_only", acceptance_available=False,
                          camera_open=camera is not None, camera_mode=mode)
            status.update(match_threshold=match_threshold, capture_target_count=CAPTURE_COUNT)
            with self.demo.lock:
                status["enrollment_active"] = active_enrollment(self.demo)
            uvc = getattr(camera, "uvc_camera", None)
            if uvc is not None:
                status.update(capture_format=uvc.fourcc, analysis_size=list(uvc.analysis_size))
            if controls:
                status["camera_controls_at_start"] = controls
            original_size = self.native_size or getattr(camera, "uvc_native_size", None) or getattr(camera, "capture_size", None)
            if original_size is not None:
                status["original_capture_size"] = list(original_size)
            return status
        def encode(self, crop):
            with self.encode_lock:
                feature = np.asarray(backend.encode_c(c_model, crop[None], device="cpu"))
            if feature.shape != (1, 512) or feature.dtype != np.float32 or not np.isfinite(feature).all():
                raise ValueError("FPN+C did not produce a usable embedding.")
            return feature[0].copy()
        def capture_demo_feature(self, *, enrollment, include_candidate):
            camera = self.camera
            if not enrollment or not include_candidate or camera is None:
                raise demo_flow.CaptureProcessingFailure("ROI_NOT_READY")
            _preview, full, snapshot = camera.capture_ready_processed_frame()
            if snapshot.get("processed_roi_mode") != PIPELINE:
                raise demo_flow.CaptureProcessingFailure("ROI_NOT_READY")
            crop, quad = snapshot["processed_roi"], snapshot["processed_roi_quad"]
            if crop.shape != (128, 128) or quad.shape != (4, 2):
                raise demo_flow.CaptureProcessingFailure("ROI_NOT_READY")
            out = io.BytesIO()
            from PIL import Image
            Image.fromarray(crop).save(out, "PNG")
            tags = {"roi_quad": quad, "frame_size": full.size, "capture_frame_id": snapshot["capture_frame_id"],
                    "capture_kind": CAPTURE_SOURCE, "localization_reused": True, "feature_deferred": True}
            return (lambda: self.encode(crop), base64.b64encode(out.getvalue()).decode("ascii"),
                    PIPELINE, snapshot["processed_roi_quality"], crop, tags)
        def check_score(self, *, verify=False, token=None, threshold=None):
            if not self.score_lock.acquire(blocking=False):
                raise VerificationUnavailable("The previous check is still running. Please wait.")
            try:
                with self.demo.lock:
                    if active_enrollment(self.demo):
                        raise VerificationUnavailable("Capture is in progress. Save or cancel the current session first.")
                # Read a current processed exposure once, no second localization.
                with self.power.lock:
                    camera = self.camera
                    if (camera is None or (self.managed_camera and verify and self.power.owner != ("verify", token))):
                        raise VerificationUnavailable("Select Start verification to open the camera.")
                with camera.lock:
                    frame = camera.latest_processed
                    now = time.monotonic()
                    if (frame is None or frame.captured.frame_id <= self.last_probe_frame
                            or not 0 <= now - frame.captured.captured_monotonic <= SCORE_AGE_LIMIT
                            or frame.roi_status.get("roi_mode") != PIPELINE or frame.enrollment_quad is None
                            or not camera._camera_frame_state()["camera_ready"]):
                        raise VerificationUnavailable("No new usable palm region yet. Face your palm toward the camera and hold still.")
                    self.last_probe_frame = frame.captured.frame_id
                    roi = frame.roi.copy()
                feature = self.encode(roi)
                with self.demo.lock:
                    if active_enrollment(self.demo):
                        raise VerificationUnavailable("Capture is in progress. Save or cancel the current session first.")
                    return score_gallery(np, feature, self.demo.store, required,
                                         threshold=(match_threshold if threshold is None else threshold) if verify else None)
            finally:
                self.score_lock.release()

    base.CameraFeed = make_camera(base.CameraFeed, base.ProcessedFrame, backend, localizer, np, cv)
    base.App = ShadowApp
    enrollment_best_frame.install(base)
    return base.CameraFeed, base.App


def build_handler(application, enrollment_html):
    from capture_station import send
    from enrollment_best_frame import ranking_status
    from enrollment_review import mutate, selected_photo
    from enrollment_archive import native_roi_png, rectified_roi_png
    from station_library import ArchiveEditError, list_archives, archive_image, delete_archive, edit_archive
    from enrollment_window_adapter import start_refill
    from demo_flow import CaptureProcessingFailure

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, value, status=200):
            return send(self, json.dumps(value, ensure_ascii=False, allow_nan=False), status,
                        "application/json; charset=utf-8")

        def local_request(self):
            port = self.server.server_port
            h = self.headers.get("Host")
            return h in {f"127.0.0.1:{port}", f"localhost:{port}"} and (
                self.headers.get("Origin") in {None, "http://" + h}
            )

        def image(self, data, mime):
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            if not self.local_request():
                return self.respond({"message": "This request is only available from this station."}, 403)
            route = urlsplit(self.path).path
            if route in ("/", "/enroll"):
                return send(self, enrollment_html)
            if route in ("/gate", "/collect", "/library"):
                return send(self, render_enrollment("/gate" if route == "/gate" else "/collect"))
            if route in ("/api/status", "/api/station/enroll-status"):
                status = application.status()
                return self.respond(ranking_status(status) if route.endswith("enroll-status") else status)
            if route == "/station-health":
                status = application.status()
                return self.respond({"backend": PIPELINE, "mode": "scores_only",
                                    "ready": not status["camera_open"] or bool(status.get("camera_ready") and status.get("processing_thread_alive")),
                                    "camera_open": status["camera_open"],
                                    "camera_ready": status["camera_ready"],
                                    "acceptance_available": False})
            if route == "/api/demo/users":
                with application.demo.lock:
                    return self.respond({"users": application.demo.users()})
            if route == "/frame.jpg":
                try:
                    camera = application.camera
                    if camera is None:
                        return self.respond({"message": "Camera on standby."}, 503)
                    data = camera.jpeg_frame()
                except (OSError, RuntimeError, ValueError):
                    return self.respond({"message": "Waiting for the local camera."}, 503)
                return self.image(data, "image/jpeg")
            return self.respond({"message": "This route is not available on this station."}, 404)

        def do_POST(self):
            if not self.local_request():
                return self.respond({"message": "This request is only available from this station."}, 403)
            route = urlsplit(self.path).path
            allow = {
                "/api/demo/enroll/start", "/api/demo/enroll/status", "/api/demo/enroll/step",
                "/api/demo/enroll/commit", "/api/demo/enroll/cancel", "/api/station/enroll-review",
                "/api/station/enroll-remove", "/api/station/enroll-refill", "/api/station/enroll-stop",
                "/api/station/enroll-select",
                "/api/fpn/score", "/api/fpn/verify", "/api/fpn/camera", "/api/station/camera-sleep", "/api/station/enroll-image",
                "/api/library/list", "/api/library/image", "/api/library/delete", "/api/library/edit",
            }
            if route not in allow:
                return self.respond({"message": "This station does not support access actions, payments, or writes to legacy templates."}, 404)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError("Invalid request format.")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("Invalid request format.")
                if route == "/api/fpn/score":
                    if data:
                        raise ValueError("Only the current camera frame can be used.")
                    return self.respond(application.check_score())
                if route == "/api/fpn/verify":
                    threshold = data.get("threshold")
                    if "threshold" in data and (type(threshold) not in (int, float) or not 0 <= threshold <= 1):
                        return self.respond({"message": "Enter a threshold between 0 and 1."}, 400)
                    return self.respond(application.check_score(verify=True, token=data.get("token"), threshold=threshold))
                flow = application.demo
                if route.startswith("/api/library/"):
                    root = flow.enrollment_archive_root
                    with flow.lock:
                        if route.endswith("/list"):
                            result = {"archives": list_archives(root)}
                        elif route.endswith("/delete"):
                            result = delete_archive(root, data)
                        elif route.endswith("/edit"):
                            result = edit_archive(root, data)
                        else:
                            image = archive_image(root, data)
                    if route.endswith("/image"):
                        return self.image(*image)
                    return self.respond(result)
                token = data.get("token")
                if not isinstance(token, str) or len(token) != 32:
                    raise ValueError("This enrollment session is no longer valid.")
                if route == "/api/fpn/camera":
                    action = data.get("action")
                    if action not in ("start", "stop", "keepalive"):
                        raise ValueError("Invalid camera command.")
                    return self.respond(application.verify_camera(token, action))
                if route == "/api/station/camera-sleep":
                    owner = ("capture", token)
                    with application.power.lock:
                        if application.power.owner == owner:
                            application.pause_camera(owner)
                            application.power.close(owner)
                    return self.respond({"camera_open": False})
                if route.endswith("-image"):
                    candidate = selected_photo(flow, token, data.get("frame"))
                    kind = data.get("kind")
                    if kind == "original":
                        return self.image(candidate.payload["station_original_jpeg"], "image/jpeg")
                    if kind == "detail":
                        return self.image(native_roi_png(candidate)[0], "image/png")
                    if kind == "detail-preview" and candidate.payload.get("station_review_rgb"):
                        jpeg = base64.b64decode(candidate.payload["station_review_rgb"])
                        return self.image(rectified_roi_png(candidate, jpeg)[0], "image/png")
                    raise ValueError("Unknown image type.")
                if route.endswith("/start"):
                    result = flow.enrollment_start(str(data.get("user_id", "")),
                                                   str(data.get("display_name", "")), str(data.get("hand", "")), token)
                elif route.endswith("/status"):
                    result = flow.enrollment_status(token)
                elif route.endswith("/step"):
                    result = flow.enrollment_step(token, selection_only=data.get("selection_only") is True)
                elif route.endswith("/commit"):
                    result = flow.enrollment_commit(token, str(data.get("confirm_hand", "")))
                    result.pop("balance_cents", None)
                elif route.endswith("/cancel"):
                    result = flow.enrollment_cancel(token)
                elif route.endswith("-refill"):
                    result = start_refill(flow, token)
                else:
                    frame = data.get("frame") if route.endswith("-remove") else None
                    if route.endswith("-remove") and type(frame) is not int:
                        raise ValueError("Select a photo from this enrollment session.")
                    result = mutate(flow, token, frame, stop=route.endswith("-stop"),
                                    select=route.endswith("-select"), geometry=True)
                application.reconcile_capture(token)
                return self.respond(result)
            except ArchiveEditError as error:
                return self.respond({"message": str(error)}, 400)
            except FileNotFoundError:
                if route.startswith("/api/library/"):
                    return self.respond({"message": "This photo has been removed from the library. Refresh to continue."}, 404)
                return self.respond({"message": "A required file is temporarily unavailable."}, 503)
            except VerificationUnavailable as error:
                return self.respond({"message": str(error)}, 400 if route == "/api/fpn/score" else 409)
            except (ValueError, TypeError, CaptureProcessingFailure) as error:
                message = START_ERRORS.get(str(error)) if route.endswith("/start") else None
                if route.endswith("/commit"):
                    message = "Could not save. Make sure all 10 photos are selected and the hand is correct."
                elif route.endswith("-select"):
                    message = "Capture for at least 60 seconds, collect 10 candidates, and wait for the current frame to finish processing before selecting."
                elif route == "/api/fpn/verify":
                    message = "Could not match the enrolled templates. Refresh and try again."
                return self.respond({"message": message or "This operation is temporarily unavailable. Refresh and try again."}, 400)
            except (OSError, RuntimeError):
                return self.respond({"message": "The local camera or station templates are unavailable."}, 503)

    return Handler


def render_enrollment(active="/enroll"):
    from capture_station import nav
    page = Path(__file__).with_name("fpn_station.html").read_text("utf-8")
    navigation = nav(active).replace("③ Data management", "③ Photo library")
    return page.replace("<!--station-nav-->", navigation).replace("__ACTIVE_PAGE__", active)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True, help="Private empty directory, not the old station runtime")
    camera = parser.add_mutually_exclusive_group()
    camera.add_argument("--uvc-device", type=Path)
    camera.add_argument("--csi-tuning", type=Path)
    parser.add_argument("--uvc-native-size", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"),
                        help="Keep native MJPEG originals while processing at 640×480.")
    parser.add_argument("--cpu-threads", type=int, choices=(1, 2, 3, 4), default=2)
    parser.add_argument("--match-threshold", type=float, default=DEMO_MATCH_THRESHOLD,
                        help="Demo cosine threshold. Default 0.80 is an uncalibrated starting point.")
    args = parser.parse_args(argv)
    if args.uvc_native_size and (not args.uvc_device or args.uvc_native_size[0] < 640 or args.uvc_native_size[1] < 480):
        parser.error("--uvc-native-size requires a UVC device and dimensions at least 640×480")
    if not 0 <= args.match_threshold <= 1:
        parser.error("--match-threshold must be between 0 and 1")
    try:
        import cv2
        import numpy as np
        import torch
        import frozen_fpn_c_e10 as backend
        from palm_app import debug_ui as base
        torch.set_num_threads(args.cpu_threads)
        cv2.setNumThreads(1)
        config = parse_manifest(args.manifest)
        fpn, c = load_pipeline(config, backend)
        identity = identify_namespace(config)
        with open_workspace(args.runtime, identity):
            # Bind first; no camera race if an existing process owns this port.
            server = ThreadingHTTPServer(("127.0.0.1", PORT), BaseHTTPRequestHandler)
            try:
                Camera, App = station_stack(base, backend, fpn, c, args.runtime, identity, np, cv2,
                                            match_threshold=args.match_threshold)
                # Internal 'fixed' prevents creating any legacy tracker; the override
                # supplies the one native FPN worker and explicit frame provenance.
                native_size = tuple(args.uvc_native_size) if args.uvc_native_size else None
                def create_feed(last_frame):
                    return Camera(
                        0, 640, 480, roi_mode="fixed", hand_model=base.DEFAULT_HAND_MODEL,
                        hand_pose_model=base.DEFAULT_HAND_POSE_MODEL, refine_pose=False,
                        inference_ms=0., input_size=(256, 320), recovery_pass=False,
                        camera_tuning_file=args.csi_tuning, capture_only=False,
                        camera_backend="uvc" if args.uvc_device else "picamera2", uvc_device=args.uvc_device,
                        uvc_native_size=native_size, initial_frame_id=last_frame,
                    )
                application = App(create_feed=create_feed, native_size=native_size)
                try:
                    server.RequestHandlerClass = build_handler(application, render_enrollment())
                    print(f"FPN+C capture and verification: http://127.0.0.1:{PORT}/enroll", flush=True)
                    server.serve_forever()
                finally:
                    application.power.close()
            finally:
                server.server_close()
    except KeyboardInterrupt:
        return 0
    except ShadowFailure as error:
        print("FPN+C station unavailable: " + str(error), file=sys.stderr)
        return 2
    except Exception:
        print("FPN+C station unavailable: check native dependencies, camera, port and private runtime", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
