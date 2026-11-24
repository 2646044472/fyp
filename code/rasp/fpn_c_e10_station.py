#!/usr/bin/env python3
"""Opt-in loopback FPN+C V3 capture. No authorization routes or legacy templates."""
import argparse
import base64
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from urllib.parse import urlsplit

from fpn_c_e10_shadow import PIPELINE, ShadowFailure, load_pipeline, parse_manifest

GEOMETRY = "fpn-native-gray128-v1"
MAX_FRAME_AGE = 1.2
SCORE_AGE_LIMIT = 1.25
# Explicitly separate from old 8088, which may still own the camera.
PORT = 8080
CAPTURE_SOURCE = "fpn-c-e10-v3-video-native"


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


def require_template(np, features, metadata, required):
    if any(metadata.get(key) != value for key, value in required.items()):
        raise ValueError("FPN+C 模板版本不符；请用独立目录重新登记。")
    if (features.shape != (5, 512) or features.dtype != np.float32 or not np.isfinite(features).all()
            or np.any(np.linalg.norm(features.astype(np.float64), axis=1) <= 0)):
        raise ValueError("FPN+C 模板损坏或不完整。")


def score_gallery(np, probe, store, required):
    vector = np.asarray(probe, dtype=np.float64)
    length = np.linalg.norm(vector)
    if vector.shape != (512,) or not np.isfinite(vector).all() or not math.isfinite(length) or length <= 0:
        raise ValueError("查询特征无效。")
    vector /= length
    scores = []
    for name in store.list_template_ids():
        if not store.exists(name):
            raise ValueError("影子模板不完整。")
        features, metadata = store.load(name)
        require_template(np, features, metadata, required)
        template = features.astype(np.float64)
        template /= np.linalg.norm(template, axis=1, keepdims=True)
        a = (template @ vector).max()
        if not np.isfinite(a) or abs(float(a)) > 1 + 1e-12:
            raise ValueError("分数无效。")
        scores.append(float(np.clip(a, -1., 1.)))
    scores.sort(reverse=True)
    return {"mode": "scores_only", "gallery_size": len(scores), "top_cosines": scores[:2],
            "tied_top": bool(len(scores) > 1 and scores[0] == scores[1])}


def make_camera(base, frame_class, backend, localizer, np, cv):
    class Camera(base):
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


def station_stack(base, backend, localizer, c_model, root, identity, np, cv):
    """Reuse V3 session window and review, no DemoFlow payment/storage bootstrap."""
    import demo_flow
    import enrollment_best_frame
    from templates import TemplateStore

    required = {"algorithm": PIPELINE, "roi_geometry": GEOMETRY, "matcher_runtime_identity": identity}

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
                raise ValueError("影子模板不一致。")
        def balance_for(self, _name):
            return 0
        def list_users(self):
            result = []
            for name in self.store.list_template_ids():
                if self.store.exists(name):
                    result.append({"user_id": name, "display_name": self.display_name_for(name), "balance_cents": 0})
            return result

    class ShadowFlow(demo_flow.DemoFlow):
        def __init__(self, feed, candidate):
            self.algorithm = SimpleNamespace(name=PIPELINE)
            self.gallery = SimpleNamespace(required_metadata=required)
            self.runtime_identity = identity
            self.roi_geometry = GEOMETRY
            self.capture_profile = "fpn-shadow-" + feed.capture_profile
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
            raise ValueError("没有可用的通行判定。")

    class ShadowApp:
        def __init__(self, feed):
            self.camera = feed
            self.score_lock = threading.Lock()
            self.encode_lock = threading.Lock()
            self.last_probe_frame = -1
            self.demo = ShadowFlow(feed, lambda: self.capture_demo_feature(enrollment=True, include_candidate=True))
        def status(self):
            status = dict(self.camera.status(), backend=PIPELINE, mode="scores_only", acceptance_available=False)
            original_size = getattr(self.camera, "uvc_native_size", None) or getattr(self.camera, "capture_size", None)
            if original_size is not None:
                status["original_capture_size"] = list(original_size)
            return status
        def encode(self, crop):
            with self.encode_lock:
                feature = np.asarray(backend.encode_c(c_model, crop[None], device="cpu"))
            if feature.shape != (1, 512) or feature.dtype != np.float32 or not np.isfinite(feature).all():
                raise ValueError("FPN+C 未生成有效特征。")
            return feature[0].copy()
        def capture_demo_feature(self, *, enrollment, include_candidate):
            if not enrollment or not include_candidate:
                raise demo_flow.CaptureProcessingFailure("ROI_NOT_READY")
            _preview, full, snapshot = self.camera.capture_ready_processed_frame()
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
        def check_score(self):
            if not self.score_lock.acquire(blocking=False):
                raise ValueError("上一轮分数尚未完成。")
            try:
                with self.demo.lock:
                    if self.demo.enrollment_session is not None:
                        raise ValueError("先确认或取消本次登记。")
                # Read a current processed exposure once, no second localization.
                with self.camera.lock:
                    frame = self.camera.latest_processed
                    now = time.monotonic()
                    if (frame is None or frame.captured.frame_id <= self.last_probe_frame
                            or not 0 <= now - frame.captured.captured_monotonic <= SCORE_AGE_LIMIT
                            or frame.roi_status.get("roi_mode") != PIPELINE or frame.enrollment_quad is None
                            or not self.camera._camera_frame_state()["camera_ready"]):
                        raise ValueError("没有新的有效 FPN 掌区；请调整手掌后再试。")
                    self.last_probe_frame = frame.captured.frame_id
                    roi = frame.roi.copy()
                feature = self.encode(roi)
                with self.demo.lock:
                    if self.demo.enrollment_session is not None:
                        raise ValueError("先确认或取消本次登记。")
                    return score_gallery(np, feature, self.demo.store, required)
            finally:
                self.score_lock.release()

    base.CameraFeed = make_camera(base.CameraFeed, base.ProcessedFrame, backend, localizer, np, cv)
    base.App = ShadowApp
    enrollment_best_frame.install(base)
    return base.CameraFeed, base.App


SCORE_PAGE = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>FPN + C E10 分数</title>
<style>body{font:17px system-ui;max-width:850px;margin:auto;padding:24px;color:#20394b}
img{width:min(100%,640px);display:block}button{padding:10px;margin:12px 0;font:inherit}</style></head>
<body><h1>FPN + C E10 分数预览</h1><p>仅测分，不显示身份，不判定通过，无放行。</p>
<img id="live" alt="当前镜头帧"><button id="score">计算当前帧分数</button>
<p id="result" role="status"></p><p><a href="/enroll">返回 60 秒登记</a></p>
<script>
const img=document.querySelector('#live'), btn=document.querySelector('#score'), out=document.querySelector('#result');
let url;
async function preview(){try{if(!document.hidden){const r=await fetch('/frame.jpg',{cache:'no-store'});if(r.ok){
 const next=URL.createObjectURL(await r.blob());img.src=next;if(url)URL.revokeObjectURL(url);url=next;}}}
catch(_){}finally{setTimeout(preview,240)}}preview();
btn.onclick=async()=>{btn.disabled=true;out.textContent='读取当前有效掌区…';try{
 const r=await fetch('/api/fpn/score',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
 const data=await r.json();if(!r.ok)throw new Error(data.message);
 out.textContent=data.gallery_size===0?'还没有已确认的 FPN+C 模板。':
 '库内 '+data.gallery_size+' 掌；最高余弦 '+data.top_cosines.map(x=>x.toFixed(4)).join(' / ')+
 (data.tied_top?'（最高分并列）':'')+'；仅作分数记录，不判定身份。';
}catch(e){out.textContent=e.message||'分数未返回。'}finally{btn.disabled=false}};
</script></body></html>"""


def build_handler(application, enrollment_html):
    from capture_station import send
    from enrollment_best_frame import ranking_status
    from enrollment_review import mutate
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

        def do_GET(self):
            if not self.local_request():
                return self.respond({"message": "仅限本站。"}, 403)
            route = urlsplit(self.path).path
            if route in ("/", "/enroll"):
                return send(self, enrollment_html)
            if route == "/gate":
                return send(self, SCORE_PAGE)
            if route in ("/api/status", "/api/station/enroll-status"):
                status = application.status()
                return self.respond(ranking_status(status) if route.endswith("enroll-status") else status)
            if route == "/station-health":
                status = application.status()
                return self.respond({"backend": PIPELINE, "mode": "scores_only",
                                    "ready": bool(status.get("camera_ready") and status.get("processing_thread_alive")),
                                    "acceptance_available": False})
            if route == "/api/demo/users":
                with application.demo.lock:
                    return self.respond({"users": application.demo.users()})
            if route == "/frame.jpg":
                try:
                    data = application.camera.jpeg_frame()
                except (OSError, RuntimeError, ValueError):
                    return self.respond({"message": "等待本机摄像头。"}, 503)
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            return self.respond({"message": "影子服务不提供此路由。"}, 404)

        def do_POST(self):
            if not self.local_request():
                return self.respond({"message": "仅限本站。"}, 403)
            route = urlsplit(self.path).path
            allow = {
                "/api/demo/enroll/start", "/api/demo/enroll/status", "/api/demo/enroll/step",
                "/api/demo/enroll/commit", "/api/demo/enroll/cancel", "/api/station/enroll-review",
                "/api/station/enroll-remove", "/api/station/enroll-refill", "/api/station/enroll-stop",
                "/api/fpn/score",
            }
            if route not in allow:
                return self.respond({"message": "影子服务没有通行、支付或旧模板写入。"}, 404)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 4096 or self.headers.get_content_type() != "application/json":
                    raise ValueError("请求格式不正确。")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("请求格式不正确。")
                if route == "/api/fpn/score":
                    if data:
                        raise ValueError("只可使用当前镜头帧。")
                    return self.respond(application.check_score())
                flow = application.demo
                token = data.get("token")
                if not isinstance(token, str) or len(token) != 32:
                    raise ValueError("本次登记已失效。")
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
                        raise ValueError("请选择本次登记的一张照片。")
                    result = mutate(flow, token, frame, stop=route.endswith("-stop"))
                return self.respond(result)
            except (ValueError, TypeError, CaptureProcessingFailure):
                return self.respond({"message": "当前请求不可用：检查登记状态、帧是否有效、或目录是否匹配。"}, 400)
            except (OSError, RuntimeError):
                return self.respond({"message": "本机相机或影子模板不可用。"}, 503)

    return Handler


def render_enrollment():
    import capture_station
    from demo_page import HTML
    page = capture_station.render(HTML, "/enroll")
    page = page.replace("<body>", '<body><p role="note"><strong>FPN + C E10</strong> · 独立影子登记，仅显示分数，无通行判断。</p>', 1)
    page = page.replace("前往放掌验证 →", "前往分数预览 →").replace("可以返回通行体验。", "可以返回分数预览。")
    return page.replace('<a href="/collect">③ 数据管理</a>', "")


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
    args = parser.parse_args(argv)
    if args.uvc_native_size and (not args.uvc_device or args.uvc_native_size[0] < 640 or args.uvc_native_size[1] < 480):
        parser.error("--uvc-native-size requires a UVC device and dimensions at least 640×480")
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
                Camera, App = station_stack(base, backend, fpn, c, args.runtime, identity, np, cv2)
                # Internal 'fixed' prevents creating any legacy tracker; the override
                # supplies the one native FPN worker and explicit frame provenance.
                feed = Camera(
                    0, 640, 480, roi_mode="fixed", hand_model=base.DEFAULT_HAND_MODEL,
                    hand_pose_model=base.DEFAULT_HAND_POSE_MODEL, refine_pose=False,
                    inference_ms=0., input_size=(256, 320), recovery_pass=False,
                    camera_tuning_file=args.csi_tuning, capture_only=False,
                    camera_backend="uvc" if args.uvc_device else "picamera2", uvc_device=args.uvc_device,
                    uvc_native_size=tuple(args.uvc_native_size) if args.uvc_native_size else None,
                )
                try:
                    server.RequestHandlerClass = build_handler(App(feed), render_enrollment())
                    print(f"FPN+C score-only: http://127.0.0.1:{PORT}/enroll", flush=True)
                    server.serve_forever()
                finally:
                    feed.close()
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
