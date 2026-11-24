"""Small, supervised palm-to-simulated-payment flow for the Pi demo."""

from __future__ import annotations

import threading
import time
import uuid
import json
import zipfile
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

from gallery import Gallery
from acceptance_policy import load_acceptance_policy
from enrollment_photo_selection import PhotoCandidate, is_near_duplicate, select_enrollment_photos
from payment import PaymentService
from templates import TemplateStore, safe_user_id
from runtime_diagnostics import safe_event, stage
from roi_quality import DEMO_CAPTURE_MIN_CONTRAST, DEMO_CAPTURE_MIN_SHARPNESS


ENROLLMENT_TIMEOUT_SECONDS = 600
ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS = 8

CAPTURE_FAILURE_MESSAGES = {
    "NO_HAND": "No palm detected. Place your hand in the center of the preview.",
    "ROI_UNSTABLE": "Palm detection is not stable yet. Open your hand, hold still and wait until ready.",
    "ROI_GEOMETRY_INVALID": "Palm detected, but its geometry is invalid. Keep the whole hand in view and adjust the distance.",
    "CAMERA_BUSY": "Camera busy capturing. Try again shortly.",
    "CAMERA_UNAVAILABLE": "Camera frame temporarily unavailable. Check the connection and retry.",
    "CAPTURE_TIMEOUT": "No fresh camera frame arrived in time. Check that the preview is updating, then continue.",
    "ROI_NOT_READY": "Palm status is not stable yet. Wait for the preview to show ready before capturing.",
}


def enrollment_quality_issue(quality: dict[str, Any]) -> str | None:
    contrast, sharpness = float(quality.get("contrast", 0)), float(quality.get("sharpness", 0))
    if not np.isfinite([contrast, sharpness]).all():
        return "Invalid palm quality data. Reposition your hand and retry."
    if sharpness < DEMO_CAPTURE_MIN_SHARPNESS:
        return (f"Image is blurry: sharpness {sharpness:.2f} / {DEMO_CAPTURE_MIN_SHARPNESS:.2f}, "
                f"contrast {contrast:.2f} / {DEMO_CAPTURE_MIN_CONTRAST:.2f}; "
                "hold still and wait for a clear frame. The system will retry automatically.")
    if contrast < DEMO_CAPTURE_MIN_CONTRAST:
        return (f"Insufficient palm contrast: sharpness {sharpness:.2f} / {DEMO_CAPTURE_MIN_SHARPNESS:.2f}, "
                f"contrast {contrast:.2f} / {DEMO_CAPTURE_MIN_CONTRAST:.2f}; "
                "adjust the lighting or hand position. The system will retry automatically.")
    return None


def classify_camera_capture_error(error: BaseException) -> str:
    message = str(error).casefold()
    waiting_for_frame = "waiting for a fresh" in message
    return "CAPTURE_TIMEOUT" if waiting_for_frame or "timed out" in message or "timeout" in message else "CAMERA_UNAVAILABLE"


def classify_roi_capture_error(error: BaseException) -> str:
    reason = str(error).strip().casefold()
    if reason in {"no_hand", "no_candidate", "tracking_lost", "tracking_stale", "hand_not_detected"}:
        return "NO_HAND"
    geometry_terms = ("span is too small", "outside the frame", "degenerate", "stable axis", "quad", "geometry")
    if any(term in reason for term in geometry_terms):
        return "ROI_GEOMETRY_INVALID"
    return "ROI_UNSTABLE"


class CaptureProcessingFailure(RuntimeError):
    """A frame could not produce a usable ROI or feature."""

    def __init__(self, reason: str, detail: str | None = None) -> None:
        message = detail or CAPTURE_FAILURE_MESSAGES.get(reason, reason)
        super().__init__(message)
        self.reason = reason
        self.detail = message


class DemoFlow:
    def __init__(self, runtime: Path, algorithm: Any, capture_feature: Callable[[], tuple[np.ndarray, str, str]], *, roi_geometry: str | None = None, capture_enrollment_feature: Callable[[], tuple[np.ndarray,str,str]] | None = None, capture_profile: str = "noir-ir", capture_source: str = "3280x2464-full-still") -> None:
        self.algorithm = algorithm
        self.capture_feature = capture_feature
        self.capture_enrollment_feature = capture_enrollment_feature or capture_feature
        self.roi_geometry = roi_geometry
        self.capture_profile = capture_profile
        self.capture_source = capture_source
        self.runtime_identity = getattr(algorithm, "runtime_identity", None)
        if getattr(algorithm, "requires_isolated_demo_runtime", False):
            if not (runtime / ".ppnet-demo-runtime").is_file():
                raise ValueError("PPNet requires a fresh isolated demo runtime")
            if (runtime / "demo_acceptance_policy.json").exists():
                raise ValueError("PPNet does not support demo acceptance policies")
        acceptance_policy = load_acceptance_policy(runtime / "demo_acceptance_policy.json")
        store_factory = getattr(algorithm, 'template_store_factory', TemplateStore)
        self.store = store_factory(runtime / "demo_templates",
                                   compression_level=getattr(algorithm, 'template_compression_level', None))
        self.payments = PaymentService(runtime / "demo_payment.sqlite3")
        # Ranking-only remains the default. Opt-in rejection is explicit and
        # keeps independent profiles for ordinary, angular and weighted scores.
        required = {"algorithm": algorithm.name}
        if roi_geometry is not None:
            required["roi_geometry"] = roi_geometry
        if self.runtime_identity is not None:
            required["matcher_runtime_identity"] = self.runtime_identity
        if getattr(algorithm, 'template_codec', None):
            required.update(template_codec=algorithm.template_codec,
                            template_storage_schema=algorithm.template_storage_schema)
        candidate_threshold = getattr(algorithm, "default_threshold", 1.0) if getattr(
            algorithm, "requires_isolated_demo_runtime", False) else 1.0
        candidate_margin = getattr(algorithm, "default_min_margin", 0.0) if getattr(
            algorithm, "requires_isolated_demo_runtime", False) else 0.0
        self.gallery = Gallery(
            self.store,
            algorithm,
            threshold=candidate_threshold,
            min_margin=candidate_margin,
            required_metadata=required,
            acceptance_policy=acceptance_policy,
            strict_integrity=True,
        )
        self._integrity_cache: dict[str, tuple[tuple, dict[str, Any]]] = {}
        self.lock = threading.Lock()
        self.enrollment_capture_lock = threading.Lock()
        self.pending: dict[str, tuple[str, int, float]] = {}
        self.enrollment_candidate: Callable[[], tuple] | None = None
        self.enrollment_session: dict[str, Any] | None = None
        self.enrollment_request_states: dict[str, str] = {}
        self.enrollment_archive_root: Path | None = None

    def enroll(self, user_id: str, display_name: str) -> dict[str, Any]:
        user_id = safe_user_id(user_id)
        display_name = display_name.strip()
        if not display_name or len(display_name) > 60:
            raise ValueError("Enter a name with 1–60 characters.")
        with self.lock:
            has_template = self.store.exists(user_id)
            if not has_template and user_id in self.store.list_template_ids():
                raise ValueError("Template files for this ID are incomplete. Check the existing record first.")
            has_account = self.payments.user_exists(user_id)
            refreshing = False
            if has_template or has_account:
                if not (has_template and has_account):
                    raise ValueError("The template or account for this ID is incomplete. Check the existing record first.")
                _, metadata = self.store.load(user_id)
                refreshing = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
                if not refreshing:
                    raise ValueError("This ID is already enrolled. Choose another ID.")
                display_name = self.payments.display_name_for(user_id)
            features = []
            sources = []
            for _ in range(5):
                feature, _, source = self.capture_enrollment_feature()
                features.append(feature)
                sources.append(source)
            # Persist only after all five captures pass geometry and quality.
            # On failure the old template and account remain usable for rollback.
            batch = getattr(self.store, 'batch_features', np.stack)(features)
            metadata = {
                "user": user_id, "display_name": display_name, "algorithm": self.algorithm.name,
                "capture_profile": self.capture_profile, "samples": 5,
                "source": self.capture_source,
                "roi_geometry": self.roi_geometry,
                "roi_sources": sources,
            }
            if self.runtime_identity is not None:
                metadata["matcher_runtime_identity"] = self.runtime_identity
            self.store.save(user_id, batch, metadata)
            if not refreshing:
                try:
                    self.payments.create_account(user_id, display_name, 10000)
                except Exception as error:
                    raise RuntimeError("Account status is unconfirmed. The template was retained; check existing records.") from error
            self.pending.clear()
            response = {"user_id": user_id, "display_name": display_name,
                        "balance_cents": self.payments.balance_for(user_id), "reenrolled": refreshing}
            if hasattr(self.algorithm, 'prepare_gallery'):
                try:
                    integrity_reason = self._gallery_integrity_reason()
                    if integrity_reason is not None:
                        raise ValueError(integrity_reason)
                    self.gallery.warm_up(capture_profile=self.capture_profile)
                    response['recognition_ready'] = True
                except (ValueError, RuntimeError, OSError) as error:
                    # Enrollment is already committed. Do not falsely report
                    # it as rolled back when optional index preparation fails.
                    response.update(recognition_ready=False, preparation_error=str(error))
            return response

    @stage
    def enrollment_start(self, user_id: str, display_name: str, hand: str,
                         request_token: str | None = None) -> dict[str, Any]:
        user_id = safe_user_id(user_id)
        display_name = display_name.strip()
        request_display_name = display_name
        if not display_name or len(display_name) > 60 or hand not in ("left", "right"):
            raise ValueError("Enter a name and choose left or right hand.")
        if request_token is not None and (len(request_token) != 32 or
                any(char not in "0123456789abcdef" for char in request_token)):
            raise ValueError("Invalid enrollment request ID. Start again.")
        for suffix in ("left", "right"):
            if user_id.lower().endswith("_" + suffix) and hand != suffix:
                raise ValueError("The hand suffix in the ID does not match the selected hand.")
        with self.lock:
            if self.enrollment_session is not None and time.monotonic() - self.enrollment_session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                self._finish_enrollment(self.enrollment_session, "EXPIRED")
            if self.enrollment_session is not None:
                active = self.enrollment_session
                if (request_token == active["token"] and
                        user_id == active["user_id"] and
                        display_name == active["request_display_name"] and
                        hand == active["hand"]):
                    idle = max(0.0, time.monotonic() - active["last_activity"])
                    return {"token": active["token"], "diagnostic_id": active["diagnostic_id"],
                            "selection_mode": active["selection_mode"], "kept": len(active["features"]), "required": 5,
                            "max_quality_failures": None,
                            "candidate_pool_required": active["candidate_pool_required"],
                            "timeout_seconds": ENROLLMENT_TIMEOUT_SECONDS,
                            "timeout_ms_remaining": max(0, int((ENROLLMENT_TIMEOUT_SECONDS - idle) * 1000)),
                            "timeout_seconds_remaining": max(0, math.ceil(ENROLLMENT_TIMEOUT_SECONDS - idle)),
                            "hand_check": "user_confirmation_required"}
                raise ValueError("An enrollment is already in progress. Cancel it first.")
            if request_token is not None and request_token in self.enrollment_request_states:
                raise ValueError("This enrollment request has ended. Start again.")
            has_template, has_account = self.store.exists(user_id), self.payments.user_exists(user_id)
            if not has_template and user_id in self.store.list_template_ids():
                raise ValueError("Template files for this ID are incomplete. Check the existing record first.")
            if has_template != has_account:
                raise ValueError("The template or account for this ID is incomplete. Check the existing record first.")
            refreshing = False
            archive_only = False
            if has_template:
                _, metadata = self.store.load(user_id)
                if metadata.get("hand_declared_by_user") not in (None, hand):
                    raise ValueError("The hand in the original ID differs from the selected hand.")
                refreshing = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
                archive_only = not refreshing and getattr(self, "allow_repeat_capture", False)
                if not refreshing and not archive_only:
                    raise ValueError("This ID is already enrolled. Choose another ID.")
                display_name = self.payments.display_name_for(user_id)
            started = time.monotonic()
            session = {"token": request_token or uuid.uuid4().hex, "diagnostic_id": uuid.uuid4().hex, "user_id": user_id,
                       "request_display_name": request_display_name, "display_name": display_name,
                       "refreshing": refreshing, "archive_only": archive_only, "hand": hand, "features": [], "sources": [],
                       "rois": [], "qualities": [], "attempts": 0, "quality_failures": 0,
                       "feature_failures": 0, "quality_failure_streak": 0,
                       "duplicate_frames": 0, "photo_candidates": [], "candidate_pool_required": 8,
                       "five_candidates_since": None,
                       "last_capture_frame_id": None,
                       "selected_roi_images": [], "selected_frame_ids": [], "selection_mode": None,
                       "started": started, "last_activity": started, "capture_in_flight": False}
            self.enrollment_session = session
            self.enrollment_request_states[session["token"]] = "ACTIVE"
            return {"token": session["token"], "diagnostic_id": session["diagnostic_id"],
                    "selection_mode": None, "kept": 0, "required": 5, "max_quality_failures": None,
                    "candidate_pool_required": session["candidate_pool_required"],
                    "timeout_seconds": ENROLLMENT_TIMEOUT_SECONDS,
                    "timeout_ms_remaining": ENROLLMENT_TIMEOUT_SECONDS * 1000,
                    "timeout_seconds_remaining": ENROLLMENT_TIMEOUT_SECONDS,
                    "hand_check": "user_confirmation_required"}

    def _active_enrollment(self, token: str) -> dict[str, Any]:
        session = self.enrollment_session
        if session is None or token != session["token"]:
            raise ValueError("Enrollment session expired. Start again.")
        return session

    def _finish_enrollment(self, session: dict[str, Any], status: str) -> None:
        self.enrollment_request_states[session["token"]] = status
        if self.enrollment_session is session:
            self.enrollment_session = None
            safe_event("enrollment_terminal", diagnostic_id=session["diagnostic_id"], status=status,
                       selection_mode=session["selection_mode"], attempts=session["attempts"],
                       candidate_pool_count=len(session["photo_candidates"]),
                       quality_failures=session["quality_failures"], feature_failures=session["feature_failures"],
                       duplicate_frames=session["duplicate_frames"])

    def enrollment_status(self, token: str) -> dict[str, Any]:
        with self.lock:
            session = self.enrollment_session
            if session is None or token != session["token"]:
                status = self.enrollment_request_states.get(token)
                if status in {"CANCELLED", "COMPLETED", "EXPIRED"}:
                    return {"status": status}
                if status is None and isinstance(token, str) and len(token) == 32 and all(
                        char in "0123456789abcdef" for char in token):
                    # Sessions are process-local. A browser can outlive the
                    # server and retain a token whose candidates were never
                    # committed; expose that terminal state to the UI.
                    return {"status": "LOST"}
                raise ValueError("Enrollment session expired. Start again.")
            elapsed = time.monotonic() - session["started"]
            idle = time.monotonic() - session["last_activity"]
            if idle >= ENROLLMENT_TIMEOUT_SECONDS:
                self._finish_enrollment(session, "EXPIRED")
                return {"status": "EXPIRED"}
            kept = len(session["features"])
            if kept == 5:
                status = "READY"
            else:
                status = "PAUSED"
            return {
                "status": status,
                "user_id": session["user_id"],
                "display_name": session["display_name"],
                "hand": session["hand"],
                "kept": kept,
                "required": 5,
                "attempts": session["attempts"],
                "quality_failures": session["quality_failures"],
                "duplicate_frames": session["duplicate_frames"],
                "feature_failures": session["feature_failures"],
                "candidate_pool_count": len(session["photo_candidates"]),
                "candidate_pool_required": session["candidate_pool_required"],
                "fallback_after_ms": (max(0, math.ceil((ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS - (time.monotonic() - session["five_candidates_since"])) * 1000)) if kept < 5 and len(session["photo_candidates"]) >= 5 and session["five_candidates_since"] is not None else None),
                "elapsed_ms": max(0.0, elapsed * 1000),
                "max_quality_failures": None,
                "timeout_ms_remaining": max(0, int((ENROLLMENT_TIMEOUT_SECONDS - idle) * 1000)),
                "timeout_seconds_remaining": max(0, math.ceil(ENROLLMENT_TIMEOUT_SECONDS - idle)),
                "selected_roi_images": list(session["selected_roi_images"]),
                "candidate_roi_image": (max(session["photo_candidates"], key=lambda candidate: candidate.frame_id).payload["encoded_roi"] if kept < 5 and session["photo_candidates"] else None),
                "selection_mode": session["selection_mode"],
            }

    @stage
    def enrollment_step(self, token: str, *, selection_only: bool = False) -> dict[str, Any]:
        step_started = time.monotonic()
        with self.lock:
            session = self._active_enrollment(token)
            kept = len(session["features"])
            station_managed = bool(session.get("station_step_in_flight"))
            def progress(status: str, reason: str | None = None, **extra: Any) -> dict[str, Any]:
                elapsed = max(0.0, time.monotonic() - session["started"])
                idle = max(0.0, time.monotonic() - session["last_activity"])
                result = {"status": status, "diagnostic_id": session["diagnostic_id"],
                          "selection_mode": session["selection_mode"], "kept": len(session["features"]), "required": 5,
                          "attempts": session["attempts"], "quality_failures": session["quality_failures"],
                          "feature_failures": session["feature_failures"],
                          "duplicate_frames": session["duplicate_frames"],
                          "candidate_pool_count": len(session["photo_candidates"]),
                          "candidate_pool_required": session["candidate_pool_required"],
                          "elapsed_ms": elapsed * 1000,
                          "step_elapsed_ms": max(0.0, (time.monotonic() - step_started) * 1000),
                          "timeout_ms_remaining": max(0, int((ENROLLMENT_TIMEOUT_SECONDS - idle) * 1000)),
                          "timeout_seconds_remaining": max(0, math.ceil(ENROLLMENT_TIMEOUT_SECONDS - idle))}
                if reason is not None:
                    result["reason"] = reason
                result.update(extra)
                return result
            def finish_selection(candidate_pool, fallback_ready):
                baseline = candidate_pool[:5]
                sharpness_floor = min(item.sharpness for item in baseline)
                contrast_floor = min(item.contrast for item in baseline)
                quality_eligible = [item for item in candidate_pool
                                    if item.sharpness >= sharpness_floor and item.contrast >= contrast_floor]
                selected = select_enrollment_photos(quality_eligible,
                    capacity=session["candidate_pool_required"], select_count=5)
                if len(selected) != 5:
                    raise RuntimeError("Fewer than five enrollment candidates; selection cannot finish.")
                chosen = [candidate.payload for candidate in selected]
                session["features"] = [item["feature"] for item in chosen]
                session["sources"] = [item["source"] for item in chosen]
                session["rois"] = [item["roi"].copy() for item in chosen]
                session["qualities"] = [item["quality"] for item in chosen]
                session["selected_roi_images"] = [item["encoded_roi"] for item in chosen]
                session["selected_frame_ids"] = [candidate.frame_id for candidate in selected]
                session["selection_mode"] = "five_candidate_wait" if fallback_ready else "full_candidate_pool"
                reason = ("Automatically selected five from the available qualified candidates. Saving." if fallback_ready else
                          "Automatically selected five candidate frames. Saving.")
                return progress("READY", reason,
                                selection_mode=session["selection_mode"],
                                selected_roi_images=list(session["selected_roi_images"]),
                                selected_frame_ids=list(session["selected_frame_ids"]),
                                selector_quality_floor={"sharpness": sharpness_floor,
                                                         "contrast": contrast_floor})

            if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                return progress("STOPPED", "Enrollment session idle for 600 seconds. No collected candidates were saved. Cancel and start again.")
            if session["capture_in_flight"]:
                return progress("WAIT", "Capture in progress. Please wait.", retry_after_ms=1000)
            if not station_managed and kept == 5:
                session["last_activity"] = time.monotonic()
                return progress("READY")
            five_since = session["five_candidates_since"]
            if (not station_managed and len(session["photo_candidates"]) >= 5 and five_since is not None and
                    time.monotonic() - five_since >= ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS):
                session["last_activity"] = time.monotonic()
                return finish_selection(session["photo_candidates"], True)
            if selection_only:
                session["last_activity"] = time.monotonic()
                return progress("WAIT", "Waiting for selection from the qualified candidates.", retry_after_ms=250)
            if self.enrollment_candidate is None:
                raise RuntimeError("Enrollment candidate collector unavailable.")
            if not self.enrollment_capture_lock.acquire(blocking=False):
                return progress("WAIT", "Previous frame still processing. Capture device busy; please wait.", retry_after_ms=1000)
            session["last_activity"] = time.monotonic()
            session["attempts"] += 1
            session["capture_in_flight"] = True
            callback = self.enrollment_candidate
            captured = None
            failure = None
            self.lock.release()
            try:
                captured = callback()
            except BaseException as error:
                failure = error
            finally:
                self.lock.acquire()
                session["capture_in_flight"] = False
                self.enrollment_capture_lock.release()
            if self.enrollment_session is not session:
                return {"status": "STOPPED", "reason": "Enrollment session ended; this capture was discarded."}
            if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                return progress("STOPPED", "Enrollment request exceeded 600 seconds. This photo was neither added nor saved. Cancel and start again.")
            try:
                feature_factory = None
                if failure is not None:
                    raise failure
                capture_frame_id = session["attempts"]
                if len(captured) == 5:
                    feature, encoded_roi, source, quality, roi = captured
                    # Compatibility path for existing mock/custom capture callbacks.
                    height, width = np.asarray(roi).shape[:2]
                    roi_quad = np.asarray([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
                    frame_size = (width, height)
                elif len(captured) == 6:
                    feature, encoded_roi, source, quality, roi, candidate_metadata = captured
                    roi_quad = np.asarray(candidate_metadata["roi_quad"], dtype=np.float32)
                    frame_size = tuple(candidate_metadata["frame_size"])
                    capture_frame_id = candidate_metadata.get("capture_frame_id")
                    if capture_frame_id is not None:
                        capture_frame_id = int(capture_frame_id)
                        previous_frame_id = session["last_capture_frame_id"]
                        if previous_frame_id is not None and capture_frame_id <= previous_frame_id:
                            session["duplicate_frames"] += 1
                            return progress("WAIT", "The camera is still returning the previous frame. Waiting for a fresh frame before continuing.",
                                            capture_failure="DUPLICATE_FRAME",
                                            capture_frame_id=capture_frame_id,
                                            retry_after_ms=250)
                        session["last_capture_frame_id"] = capture_frame_id
                    else:
                        capture_frame_id = session["attempts"]
                    if candidate_metadata.get("feature_deferred"):
                        if not callable(feature):
                            raise RuntimeError("Enrollment candidate feature extractor unavailable.")
                        feature_factory, feature = feature, None
                else:
                    raise RuntimeError("Invalid response format from the enrollment candidate collector.")
            except CaptureProcessingFailure as error:
                if error.reason == "NO_HAND":
                    return progress("NO_HAND",
                                    "No palm detected. Auto-capture paused. Return your hand to the frame; capture resumes automatically after consecutive ready frames. You may also cancel enrollment.",
                                    capture_failure=error.reason, resume_required=True,
                                    fallback_after_ms=(max(0, math.ceil((ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS - (time.monotonic() - session["five_candidates_since"])) * 1000)) if len(session["photo_candidates"]) >= 5 and session["five_candidates_since"] is not None else None))
                if error.reason in {"ROI_UNSTABLE", "LOW_QUALITY"}:
                    session["quality_failures"] += 1
                session["quality_failure_streak"] += 1
                return progress("WAIT", error.detail or "Palm region unavailable. Reposition your hand and retry.",
                                capture_failure=error.reason, retry_after_ms=2000 if session["quality_failure_streak"] >= 15 else 500,
                                fallback_after_ms=(max(0, math.ceil((ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS - (time.monotonic() - session["five_candidates_since"])) * 1000)) if error.reason in {"CAMERA_UNAVAILABLE", "ROI_NOT_READY"} and len(session["photo_candidates"]) >= 5 and session["five_candidates_since"] is not None else None))
            except (ValueError, RuntimeError):
                session["quality_failures"] += 1
                session["quality_failure_streak"] += 1
                return progress("WAIT", "Palm region unavailable. Reposition your hand and retry.",
                                capture_failure="CAPTURE_ERROR", retry_after_ms=2000 if session["quality_failure_streak"] >= 15 else 500)
            if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                return progress("STOPPED", "Enrollment request exceeded 600 seconds. This photo was neither added nor saved. Cancel and start again.")
            contrast, sharpness = float(quality.get("contrast", 0)), float(quality.get("sharpness", 0))
            issue = enrollment_quality_issue(quality)
            if issue is not None:
                session["quality_failures"] += 1
                session["quality_failure_streak"] += 1
                return progress("WAIT", issue, retry_after_ms=2000 if session["quality_failure_streak"] >= 15 else 500)
            session["quality_failure_streak"] = 0
            roi = np.asarray(roi, dtype=np.uint8)
            candidate_pool = session["photo_candidates"]
            small_y = np.linspace(0, roi.shape[0] - 1, 16).astype(int)
            small_x = np.linspace(0, roi.shape[1] - 1, 16).astype(int)
            texture = roi[np.ix_(small_y, small_x)].astype(np.float32).reshape(-1)
            texture -= float(texture.mean())
            if float(np.linalg.norm(texture)) <= 1e-12:
                texture = roi[np.ix_(small_y, small_x)].astype(np.float32).reshape(-1)
            payload = {"feature": feature, "encoded_roi": encoded_roi, "source": source,
                       "quality": {"contrast": contrast, "sharpness": sharpness}, "roi": roi.copy()}
            photo = PhotoCandidate(capture_frame_id, sharpness, contrast, roi_quad, texture, frame_size, payload)

            def materialize_feature():
                nonlocal feature_factory
                if feature_factory is None:
                    return None
                session["capture_in_flight"] = True
                feature_error = None
                resolved_feature = None
                self.lock.release()
                try:
                    resolved_feature = feature_factory()
                except Exception as error:
                    feature_error = error
                finally:
                    self.lock.acquire()
                    session["capture_in_flight"] = False
                if self.enrollment_session is not session:
                    return {"status": "STOPPED", "reason": "Enrollment session ended; this capture was discarded."}
                if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                    return progress("STOPPED", "Enrollment request exceeded 600 seconds. This photo was neither added nor saved. Cancel and start again.")
                if feature_error is not None or resolved_feature is None:
                    session["feature_failures"] += 1
                    reason = (feature_error.reason if isinstance(feature_error, CaptureProcessingFailure)
                              else "FEATURE_ERROR")
                    detail = (feature_error.detail if isinstance(feature_error, CaptureProcessingFailure)
                              else "Palm feature extraction failed. Hold your hand steady and retry.")
                    return progress("WAIT", detail, capture_failure=reason, retry_after_ms=500)
                payload["feature"] = resolved_feature
                feature_factory = None
                return None

            fallback_ready = False
            for index, old in enumerate(candidate_pool):
                old_roi = old.payload["roi"]
                if old_roi.shape != roi.shape:
                    continue
                same_pixels = np.mean(np.abs(old_roi.astype(np.int16) - roi.astype(np.int16))) < 2.5
                if not same_pixels and not is_near_duplicate(photo, old):
                    continue
                session["duplicate_frames"] += 1
                improved = sharpness > old.sharpness * 1.1
                if improved:
                    deferred_result = materialize_feature()
                    if deferred_result is not None:
                        return deferred_result
                    candidate_pool[index] = photo
                five_since = session["five_candidates_since"]
                fallback_ready = (not station_managed and len(candidate_pool) >= 5 and five_since is not None and
                                  time.monotonic() - five_since >= ENROLLMENT_FIVE_CANDIDATE_WAIT_SECONDS)
                if fallback_ready:
                    break
                if improved:
                    return progress("COLLECTING", "Replaced a duplicate with a sharper frame. Continue capturing different angles.",
                                    candidate_roi_image=encoded_roi, retry_after_ms=300)
                return progress("WAIT", "Duplicate candidate frame. Move or rotate the same hand slightly, then hold it steady.",
                                retry_after_ms=700)
            else:
                deferred_result = materialize_feature()
                if deferred_result is not None:
                    return deferred_result
                candidate_pool.append(photo)
                if not station_managed and len(candidate_pool) == 5:
                    session["five_candidates_since"] = time.monotonic()
            if station_managed or (not fallback_ready and len(candidate_pool) < session["candidate_pool_required"]):
                return progress("COLLECTING", "Collecting clear candidate frames with different poses.",
                                candidate_roi_image=encoded_roi, retry_after_ms=500)
            return finish_selection(candidate_pool, fallback_ready)

    @stage
    def enrollment_commit(self, token: str, confirm_hand: str) -> dict[str, Any]:
        with self.lock:
            session = self._active_enrollment(token)
            if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                self._finish_enrollment(session, "EXPIRED")
                raise ValueError("Enrollment session timed out; candidates were not saved. Cancel and start again.")
            if session["capture_in_flight"] or session.get("station_step_in_flight"):
                raise ValueError("Capture in progress. Wait before confirming.")
            target = session.get("station_target_count", 5)
            if len(session["features"]) != target or confirm_hand != session["hand"]:
                raise ValueError(f"Confirm that all {target} photos show the same selected hand.")
            user_id, display_name, refreshing = session["user_id"], session["display_name"], session["refreshing"]
            archive_only = session.get("archive_only", False)
            expected_existing = refreshing or archive_only
            if not self.store.exists(user_id) and user_id in self.store.list_template_ids():
                raise ValueError("Template files for this ID are incomplete. Check the existing record first.")
            if self.store.exists(user_id) != expected_existing or self.payments.user_exists(user_id) != expected_existing:
                raise ValueError("Account status changed during enrollment. Start again.")
            template_count = getattr(self, "station_template_count", target)
            batch = getattr(self.store, 'batch_features', np.stack)(session["features"][:template_count])
            metadata = {
                "user": user_id, "display_name": display_name, "algorithm": self.algorithm.name,
                "capture_profile": self.capture_profile, "samples": template_count, "source": self.capture_source,
                "roi_geometry": self.roi_geometry, "roi_sources": session["sources"][:template_count],
                "hand_declared_by_user": session["hand"],
                "enrollment_selection": {
                    "mode": session["selection_mode"],
                    "candidate_count": len(session["photo_candidates"]),
                    "attempts": session["attempts"],
                    "quality_failures": session["quality_failures"],
                    "duplicate_frames": session["duplicate_frames"],
                    "selected_frame_ids": list(session["selected_frame_ids"]),
                },
            }
            if self.runtime_identity is not None:
                metadata["matcher_runtime_identity"] = self.runtime_identity
            archive_id = None
            if self.enrollment_archive_root is None:
                self.store.save(user_id, batch, metadata)
            else:
                from enrollment_archive import save_enrollment
                archive_id = save_enrollment(self.enrollment_archive_root, self.store, user_id, batch, metadata, session,
                                             update_template=not archive_only,
                                             include_native_roi=getattr(self, "archive_native_roi", False))
            if not expected_existing:
                try:
                    self.payments.create_account(user_id, display_name, 10000)
                except Exception as error:
                    raise RuntimeError("Account status is unconfirmed. The template was retained; check existing records.") from error
            self.pending.clear()
            self._finish_enrollment(session, "COMPLETED")
            response = {"user_id": user_id, "display_name": display_name,
                        "diagnostic_id": session["diagnostic_id"], "selection_mode": session["selection_mode"],
                        "balance_cents": self.payments.balance_for(user_id), "reenrolled": refreshing}
            if archive_id is not None:
                response["enrollment_archive_id"] = archive_id
                if archive_only:
                    response["archive_only"] = True
            if hasattr(self.algorithm, 'prepare_gallery'):
                try:
                    integrity_reason = self._gallery_integrity_reason()
                    if integrity_reason is not None:
                        raise ValueError(integrity_reason)
                    self.gallery.warm_up(capture_profile=self.capture_profile)
                    response['recognition_ready'] = True
                except (ValueError, RuntimeError, OSError) as error:
                    response.update(recognition_ready=False, preparation_error=str(error))
            response["enrollment_elapsed_ms"] = max(0.0, (time.monotonic() - session["started"]) * 1000)
            return response

    def enrollment_cancel(self, token: str) -> dict[str, str]:
        with self.lock:
            session = self.enrollment_session
            if session is None or token != session["token"]:
                status = self.enrollment_request_states.get(token)
                if status in {"CANCELLED", "EXPIRED", "COMPLETED"}:
                    return {"status": status}
                if status is None and isinstance(token, str) and len(token) == 32 and all(
                        char in "0123456789abcdef" for char in token):
                    self.enrollment_request_states[token] = "CANCELLED"
                    return {"status": "CANCELLED"}
                raise ValueError("Enrollment session expired. Start again.")
            if time.monotonic() - session["last_activity"] >= ENROLLMENT_TIMEOUT_SECONDS:
                self._finish_enrollment(session, "EXPIRED")
                return {"status": "EXPIRED"}
            self._finish_enrollment(session, "CANCELLED")
            return {"status": "CANCELLED"}

    @stage
    def identify(self) -> dict[str, Any]:
        with self.lock:
            self.pending.clear()
            started=time.perf_counter()
            integrity_reason = self._gallery_integrity_reason()
            if integrity_reason is not None:
                elapsed = (time.perf_counter() - started) * 1000
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": integrity_reason, "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": 0.0, "gallery": elapsed, "total": elapsed}}
            capture_started = time.perf_counter()
            if not self.enrollment_capture_lock.acquire(blocking=False):
                elapsed = (time.perf_counter() - started) * 1000
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": "CAMERA_BUSY", "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": 0.0, "gallery": elapsed, "total": elapsed}}
            capture_failure = None
            self.lock.release()
            try:
                try:
                    feature, roi_image, source = self.capture_feature()
                except CaptureProcessingFailure as error:
                    capture_failure = error
            finally:
                self.lock.acquire()
                self.enrollment_capture_lock.release()
            captured = time.perf_counter()
            if capture_failure is not None:
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": capture_failure.reason, "detail": capture_failure.detail,
                        "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": (captured-capture_started)*1000,
                                      "gallery": (capture_started-started)*1000,
                                      "total": (captured-started)*1000}}
            # Enrollment can change while the capture callback is outside the
            # session lock. Do not score against an invalidated gallery.
            integrity_reason = self._gallery_integrity_reason()
            if integrity_reason is not None:
                finished = time.perf_counter()
                return {"status": "RETRY", "score": None, "second_score": None,
                        "reason": integrity_reason, "roi_image": None, "roi_source": None,
                        "timing_ms": {"capture_and_extract": (captured-capture_started)*1000,
                                      "gallery": ((finished-captured)+(capture_started-started))*1000,
                                      "total": (finished-started)*1000}}
            result = self.gallery.identify(feature, self.capture_profile)
            matched=time.perf_counter()
            response = {"status": result.status, "score": result.score,
                        "second_score": result.second_score, "reason": result.reason,
                        "roi_image": roi_image, "roi_source": source,
                        "timing_ms": {"capture_and_extract": (captured-capture_started)*1000,
                                      "gallery": ((matched-captured)+(capture_started-started))*1000,
                                      "total": (matched-started)*1000}}
            if hasattr(feature, 'route'):
                response['recognition_route'] = feature.route
            if result.status != "MATCH" or result.user_id is None:
                return response
            token = uuid.uuid4().hex
            self.pending[token] = (result.user_id, 2000, time.monotonic() + 120)
            response.update({"token": token, "user_id": result.user_id,
                             "display_name": self.payments.display_name_for(result.user_id),
                             "amount_cents": 2000})
            return response

    def _gallery_integrity_reason(self) -> str | None:
        """Never identify against a silently reduced device enrollment gallery.

        File signatures invalidate validation when an enrollment changes. Heavy
        prepared-template validation shares Gallery's existing cache; unchanged
        enrollments need only file stats and the account list on later queries.
        Complete templates for other capture profiles remain ordinary exclusions.
        """
        account_ids = {user["user_id"] for user in self.payments.list_users()}
        template_ids = set(self.store.list_template_ids())
        for stale in set(self._integrity_cache) - template_ids:
            del self._integrity_cache[stale]
        if account_ids - template_ids:
            return "GALLERY_INCOMPLETE_TEMPLATES"
        prepared_mode = all(hasattr(self.algorithm, name) for name in
                            ("prepare_probe", "prepare_enrollment", "prepared_bytes", "score_prepared"))
        for user_id in sorted(template_ids):
            try:
                signature = self.gallery._signature(user_id)
            except FileNotFoundError:
                return "GALLERY_INCOMPLETE_TEMPLATES"
            except (OSError, ValueError):
                return "GALLERY_INVALID_TEMPLATES"
            cached = self._integrity_cache.get(user_id)
            if cached is not None and cached[0] == signature:
                metadata = cached[1]
            else:
                try:
                    read_metadata = getattr(self.store, 'read_metadata', None)
                    metadata = (read_metadata(user_id) if read_metadata is not None else
                                json.loads(self.store.paths(user_id)[1].read_text(encoding="utf-8")))
                    if not isinstance(metadata, dict):
                        return "GALLERY_INVALID_TEMPLATES"
                    if not isinstance(metadata.get("capture_profile"), str) or not metadata["capture_profile"]:
                        return "GALLERY_INVALID_TEMPLATES"
                    if metadata.get("capture_profile") == self.capture_profile:
                        if any(metadata.get(key) != value for key, value in self.gallery.required_metadata.items()):
                            return "GALLERY_INCOMPATIBLE_TEMPLATES"
                        if prepared_mode:
                            prepared, _ = self.gallery._load_prepared(user_id)
                            if prepared is None or len(prepared) != 5:
                                return "GALLERY_INVALID_TEMPLATES"
                        else:
                            features, _ = self.store.load(user_id)
                            if (len(features) != 5 or any(np.asarray(frame).size == 0 or
                                    not np.isfinite(frame).all() for frame in features)):
                                return "GALLERY_INVALID_TEMPLATES"
                    if signature != self.gallery._signature(user_id):
                        return "GALLERY_CHANGED_DURING_QUERY"
                except (OSError, ValueError, KeyError, EOFError, zipfile.BadZipFile, TypeError, AttributeError, RuntimeError):
                    return "GALLERY_INVALID_TEMPLATES"
                self._integrity_cache[user_id] = (signature, metadata)
            if metadata.get("capture_profile") != self.capture_profile:
                continue
            if user_id not in account_ids:
                return "GALLERY_ACCOUNT_MISMATCH"
        return None

    def _payment_receipt(self, token: str, user_id: str | None = None) -> dict[str, Any] | None:
        transaction = self.payments.transaction_for_request(token)
        if transaction is None:
            return None
        matched_user = transaction["user_id"]
        if user_id is not None and user_id != matched_user:
            raise ValueError("The confirmed identity differs from the recognition result. No additional charge.")
        return {
            "status": transaction["status"],
            "user_id": matched_user,
            "display_name": self.payments.display_name_for(matched_user),
            "amount_cents": transaction["amount_cents"],
            "balance_cents": transaction["balance_after_cents"],
            "transaction_id": transaction["transaction_id"],
        }

    def cancel(self, token: str) -> dict[str, Any]:
        with self.lock:
            receipt = self._payment_receipt(token)
            self.pending.pop(token, None)
            if receipt is not None:
                # A lost confirmation response must not turn a committed
                # transaction into a misleading "cancelled, not charged".
                return {**receipt, "status": "PAID", "payment_status": receipt["status"]}
        return {"status": "CANCELLED"}

    def confirm(self, token: str, user_id: str) -> dict[str, Any]:
        with self.lock:
            receipt = self._payment_receipt(token, user_id)
            if receipt is not None:
                self.pending.pop(token, None)
                return receipt
            pending = self.pending.get(token)
            if pending is None or pending[2] < time.monotonic():
                self.pending.pop(token, None)
                raise ValueError("Recognition result expired. Capture again.")
            matched_user, amount, _ = pending
            if user_id != matched_user:
                raise ValueError("The confirmed identity differs from the recognition result. No charge.")
            payment = self.payments.pay(matched_user, amount, token)
            if payment.transaction_id is None:
                raise ValueError("Simulated payment incomplete. Check the account and retry this confirmation.")
            receipt = self._payment_receipt(token, matched_user)
            if receipt is None:
                raise RuntimeError("Could not read the simulated payment result. Retry this confirmation.")
            self.pending.pop(token, None)
            return receipt

    def users(self) -> list[dict[str, Any]]:
        users = self.payments.list_users()
        for user in users:
            try:
                paths = self.store.paths(user["user_id"])
                # Listing names needs no biometric arrays. Packed five-frame
                # enrollments can be tens of MiB each; validation belongs to
                # the existing identification integrity check, not this UI read.
                if not paths or not paths[0].is_file():
                    raise FileNotFoundError(paths[0] if paths else user["user_id"])
                read_metadata = getattr(self.store, "read_metadata", None)
                if callable(read_metadata):
                    metadata = read_metadata(user["user_id"])
                elif len(paths) == 2 and paths[1].is_file():
                    metadata = json.loads(paths[1].read_text(encoding="utf-8"))
                else:
                    raise FileNotFoundError(user["user_id"])
                if not isinstance(metadata, dict):
                    raise ValueError("Invalid enrollment metadata")
                user["needs_reenrollment"] = any(metadata.get(k) != v for k, v in self.gallery.required_metadata.items())
            except (OSError, KeyError, ValueError, EOFError, zipfile.BadZipFile):
                user["needs_reenrollment"] = True
        return users
