"""Enrollment-only best recent exact-frame selection. Standard-library only."""
import math
from math import isfinite
import threading
import time


def ranking_status(status):
    out = dict(status)
    for key in ("status", "reason", "consecutive_frames", "required_frames"):
        out["demo_quality_" + key] = out.get("quality_" + key)
    # The browser/CSI precheck may start scanning, but only the camera loop's
    # exact fresh quadrilateral and usable pixels can become a candidate.
    if (out.get("enrollment_geometry_valid") is True
            and out.get("camera_ready") is True and out.get("roi_status_fresh") is True
            and finite_roi_quality(out.get("quality", {})) is not None):
        out.update(demo_quality_status="READY", demo_quality_reason=None,
                   demo_quality_consecutive_frames=1, demo_quality_required_frames=1)
    out["demo_quality"] = out.get("quality", {})
    out["demo_quality_config"] = {}
    return out


def finite_roi_quality(quality):
    try:
        score = tuple(float(quality[k]) for k in ("sharpness", "contrast"))
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    return score if all(isfinite(v) and v > 0 for v in score) else None


def select_frame(feed, is_ready, failure_class, *, clock=time.monotonic,
                 first_timeout=2.0, sample_window=0.60, hard_deadline=math.inf):
    with feed.frame_condition:
        started = clock()
        first = feed.latest
        after = max(getattr(feed, "station_enroll_last", -1),
                    -1 if first is None else first.frame_id)
        best = None
        deadline = min(started + first_timeout,hard_deadline)
        while feed.running:
            p = feed.latest_processed
            now = clock()
            if now >= deadline:
                break
            if p is not None and p.captured.frame_id > after:
                c = p.captured
                after = c.frame_id
                age = now - c.captured_monotonic
                stat = dict(p.roi_status)
                stat.update(feed._camera_frame_state())
                stat["roi_status_fresh"] = (feed.processing_thread.is_alive()
                                            and 0 <= age <= 1.25)
                score = finite_roi_quality(stat.get("quality", {}))
                quad = getattr(p, "enrollment_quad", p.roi_quad)
                if (c.captured_monotonic >= started and score is not None
                        and p.roi is not None and quad is not None
                        and not is_ready(ranking_status(stat))):
                    key = (*score, c.frame_id)
                    if best is None:
                        deadline = min(now + sample_window,hard_deadline)
                    if best is None or key > best[0]:
                        best = key, p, quad
            if now >= deadline:
                break
            feed.frame_condition.wait(timeout=max(0.0, deadline - clock()))
        # Removal/invalid geometry in subsequent frames does not make a frame
        # taken inside this bounded window stale, but device loss does.
        if best is None or not feed.running or not feed._camera_frame_state().get("camera_ready"):
            raise failure_class("ROI_NOT_READY", "No new usable palm region. Place your whole palm in the frame.")
        _, p, quad = best
        c = p.captured
        feed.station_enroll_last = after
        image = c.image.copy()
        return image.copy(), image, {
            "capture_backend": feed.camera_backend,
            "capture_kind": "station_enroll_best_fresh_video_roi",
            "capture_frame_id": c.frame_id,
            "station_captured_s": c.captured_monotonic,
            "capture_resolution": list(image.size),
            "color_order": "RGB",
            "capture_profile": feed.capture_profile,
            "processed_roi": p.roi.copy(),
            "processed_roi_quad": quad.copy(),
            "processed_roi_quality": dict(p.roi_status.get("quality", {})),
            "processed_roi_mode": p.roi_status.get("roi_mode"),
            "station_original_jpeg": getattr(c, "original_jpeg", None),
        }


def install(app):
    # The former live-probe gate and storage flow stay installed; only
    # enrollment captures on this request's thread get the ranking path.
    import demo_flow as flow
    from enrollment_window_adapter import initialize, run_step, session_status
    local = threading.local()
    strict_ready = app._capture_readiness_gate_failure
    strict_quality = flow.enrollment_quality_issue

    def ready(status):
        if getattr(local, "enrollment", False):
            return strict_ready(ranking_status(status) if isinstance(status, dict) else status)
        return strict_ready(status)

    def quality(value):
        if getattr(local, "enrollment", False):
            return None if finite_roi_quality(value) is not None else "Palm image quality could not be checked. Remove your hand and try again."
        return strict_quality(value)

    app._capture_readiness_gate_failure = ready
    flow.enrollment_quality_issue = app.enrollment_quality_issue = quality
    base_camera, base_app = app.CameraFeed, app.App

    def capture_best(camera):
        recorded = select_frame(camera, strict_ready, app.CaptureProcessingFailure,
                                hard_deadline=getattr(local,"capture_deadline",math.inf))
        local.review_frame = (recorded[2]["capture_frame_id"], recorded[1],
                              recorded[2]["station_captured_s"], recorded[2]["station_original_jpeg"])
        return recorded

    class Camera(base_camera):
        def capture_highres(self):
            if getattr(local, "enrollment", False):
                return capture_best(self)
            return super().capture_highres()

        def capture_ready_processed_frame(self):
            if getattr(local, "enrollment", False):
                return capture_best(self)
            return super().capture_ready_processed_frame()

    class App(base_app):
        def capture_demo_feature(self, *args, **kwargs):
            previous = getattr(local, "enrollment", False)
            local.enrollment = bool(kwargs.get("enrollment", False))
            try:
                return super().capture_demo_feature(*args, **kwargs)
            finally:
                local.enrollment = previous

    # The app checks quality in its own call and then DemoFlow checks it again
    # after that call unwinds. Scope its second check around the enrollment step.
    original_step = flow.DemoFlow.enrollment_step
    def enrollment_step(self, token, *args, **kwargs):
        previous = getattr(local, "enrollment", False)
        local.enrollment = True
        local.review_frame = None
        try:
            return run_step(self, original_step, local, token, *args, **kwargs)
        finally:
            local.enrollment = previous
            local.review_frame = None
            local.capture_deadline = math.inf
    flow.DemoFlow.enrollment_step = enrollment_step
    if hasattr(flow.DemoFlow, "enrollment_start"):
        original_start = flow.DemoFlow.enrollment_start
        def enrollment_start(self, *args, **kwargs):
            result=original_start(self,*args,**kwargs)
            with self.lock:
                ses=self.enrollment_session
                if ses is not None and ses["token"] == result["token"]:
                    if hasattr(self, "station_capture_seconds"):
                        ses["station_capture_seconds"] = self.station_capture_seconds
                    ses["station_continuous"] = getattr(self, "station_continuous", False)
                    ses["station_preview_seconds"] = getattr(self, "station_preview_seconds", 0)
                    ses["station_target_count"] = getattr(self, "station_target_count", 5)
                    result["required"] = ses["station_target_count"]
                    initialize(ses) # Idempotent retries do not reset the deadline.
            return result
        flow.DemoFlow.enrollment_start=enrollment_start
    if hasattr(flow.DemoFlow, "enrollment_status"):
        original_status = flow.DemoFlow.enrollment_status
        def enrollment_status(self, token):
            result = original_status(self, token)
            with self.lock:
                ses = self.enrollment_session
                if ses is not None and ses["token"] == token:
                    result=session_status(ses,result)
            return result
        flow.DemoFlow.enrollment_status = enrollment_status
    app.CameraFeed, app.App = Camera, App
