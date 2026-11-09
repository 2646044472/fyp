"""Continuous capture buffers ten candidates and commits only five selected frames."""

import numpy as np
import pytest

from demo_flow import (CaptureProcessingFailure, DemoFlow, classify_camera_capture_error,
                       classify_roi_capture_error)


class Algorithm:
    name = "burst-test"
    def prepare_gallery(self, _groups):
        pass


def candidate(index, *, sharpness=8, roi=None, feature_value=None):
    if roi is None:
        y, x = np.indices((32, 32))
        roi = ((x * (index + 1) + y * (index + 3) + (x * y) % (index + 5)) % 256).astype(np.uint8)
    feature_value = index if feature_value is None else feature_value
    angle = index * 0.035
    center = np.array([48.0 + index * 1.1, 50.0 - index * 0.7])
    u = np.array([np.cos(angle), np.sin(angle)]) * (18 + index % 3)
    v = np.array([-np.sin(angle), np.cos(angle)]) * (15 + index % 4)
    quad = np.stack([center-u-v, center+u-v, center+u+v, center-u+v]).astype(np.float32)
    return (np.full((4,), feature_value, dtype=np.float32), f"roi-{index}", "mock-still",
            {"contrast": 25, "sharpness": sharpness}, roi,
            {"roi_quad": quad, "frame_size": (100, 100)})


def make_flow(tmp_path):
    algorithm = Algorithm()
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(4), "", "mock"))
    warmed = []
    flow.gallery.warm_up = lambda *, capture_profile: warmed.append(capture_profile)
    return flow, warmed


def test_quality_duplicate_diversity_selection_and_confirmed_commit(tmp_path):
    flow, _ = make_flow(tmp_path)
    first = candidate(1)
    frames = iter([candidate(0, sharpness=0), first, candidate(2, roi=first[4].copy()),
                   *[candidate(i) for i in range(2, 9)]])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    states = [flow.enrollment_step(token) for _ in range(10)]
    assert states[0]["status"] == "WAIT"
    assert states[1]["status"] == "COLLECTING"
    assert states[2]["status"] == "WAIT"
    assert states[-1]["status"] == "READY"
    assert states[-1]["candidate_pool_count"] == states[-1]["candidate_pool_required"] == 8
    assert states[-1]["kept"] == 5 and states[-1]["attempts"] == 10
    assert states[-1]["quality_failures"] == 1 and states[-1]["duplicate_frames"] == 1
    assert len(states[-1]["selected_roi_images"]) == 5
    assert len(flow.enrollment_session["features"]) == len(flow.enrollment_session["rois"]) == 5
    assert not flow.store.exists("p1_left")
    with pytest.raises(ValueError, match="同一只手"):
        flow.enrollment_commit(token, "right")
    result = flow.enrollment_commit(token, "left")
    assert result["user_id"] == "p1_left"
    features, metadata = flow.store.load("p1_left")
    assert len(features) == 5 and metadata["hand_declared_by_user"] == "left"


@pytest.mark.parametrize(("failure", "message"), [
    ("ROI_UNSTABLE", "掌区检测尚未稳定"),
    ("ROI_GEOMETRY_INVALID", "几何范围无效"),
    ("CAMERA_UNAVAILABLE", "暂时无法读取相机画面"),
    ("CAPTURE_TIMEOUT", "没有及时提供新画面"),
])
def test_capture_failure_shows_actionable_reason_without_buffering(tmp_path, failure, message):
    flow, _ = make_flow(tmp_path)
    def fail_capture():
        raise CaptureProcessingFailure(failure)
    flow.enrollment_candidate = fail_capture
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    state = flow.enrollment_step(token)
    assert state["status"] == "WAIT"
    assert state["capture_failure"] == failure
    assert message in state["reason"]
    assert state["candidate_pool_count"] == 0
    assert state["quality_failures"] == (1 if failure == "ROI_UNSTABLE" else 0)


@pytest.mark.parametrize(("detail", "expected"), [
    ("no_hand", "NO_HAND"),
    ("palm span is too small (12px)", "ROI_GEOMETRY_INVALID"),
    ("dynamic palm ROI is outside the frame", "ROI_GEOMETRY_INVALID"),
    ("wrist and MCP landmarks do not define a stable axis", "ROI_GEOMETRY_INVALID"),
    ("detector candidate unstable", "ROI_UNSTABLE"),
])
def test_roi_capture_errors_map_to_distinct_actionable_states(detail, expected):
    assert classify_roi_capture_error(ValueError(detail)) == expected


@pytest.mark.parametrize(("detail", "expected"), [
    ("Timed out waiting for a fresh UVC frame", "CAPTURE_TIMEOUT"),
    ("Waiting for a fresh UVC frame", "CAPTURE_TIMEOUT"),
    ("Cannot open camera device", "CAMERA_UNAVAILABLE"),
])
def test_camera_capture_timeout_is_distinct_from_unavailable(detail, expected):
    assert classify_camera_capture_error(RuntimeError(detail)) == expected


def test_no_hand_pauses_enrollment_without_using_quality_failure_budget(tmp_path):
    flow, _ = make_flow(tmp_path)
    def no_hand():
        raise CaptureProcessingFailure("NO_HAND")
    flow.enrollment_candidate = no_hand
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    state = flow.enrollment_step(token)
    assert state["status"] == "NO_HAND" and state["resume_required"] is True
    assert "已暂停" in state["reason"] and "继续采集" in state["reason"] and "取消" in state["reason"]
    assert state["quality_failures"] == 0 and state["candidate_pool_count"] == 0
    assert state["capture_failure"] == "NO_HAND" and "retry_after_ms" not in state


def test_cancel_before_selection_discards_candidate_pool(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(index) for index in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    with pytest.raises(ValueError, match="手别"):
        flow.enrollment_start("p1_left", "P1", "right")
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(4):
        flow.enrollment_step(token)
    with pytest.raises(ValueError, match="同一只手"):
        flow.enrollment_commit(token, "left")
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"
    assert not flow.store.exists("p1_left")


def test_sharper_duplicate_replaces_buffered_frame(tmp_path):
    flow, _ = make_flow(tmp_path)
    first = candidate(1, sharpness=4)
    sharper = candidate(2, sharpness=8, roi=first[4].copy(), feature_value=99)
    frames = iter([first, sharper, *[candidate(i) for i in range(3, 10)]])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    flow.enrollment_step(token)
    flow.enrollment_step(token)
    assert len(flow.enrollment_session["photo_candidates"]) == 1
    assert flow.enrollment_session["photo_candidates"][0].payload["feature"][0] == 99
    assert flow.enrollment_session["photo_candidates"][0].frame_id == 2
    for _ in range(7):
        state = flow.enrollment_step(token)
    assert state["status"] == "READY" and state["duplicate_frames"] == 1


def test_enrollment_status_restores_partial_and_ready_sessions(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(index) for index in range(1, 9))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    flow.enrollment_step(token)
    partial = flow.enrollment_status(token)
    assert partial["status"] == "PAUSED"
    assert (partial["user_id"], partial["display_name"], partial["hand"]) == ("p1_left", "P1", "left")
    assert partial["candidate_pool_count"] == 1 and partial["kept"] == 0
    for _ in range(7):
        state = flow.enrollment_step(token)
    assert state["status"] == "READY"
    ready = flow.enrollment_status(token)
    assert ready["status"] == "READY" and ready["kept"] == 5
    assert ready["selected_roi_images"] == [f"roi-{index}" for index in flow.enrollment_session["selected_frame_ids"]]
    assert len(ready["selected_roi_images"]) == 5


def test_enrollment_status_expires_only_matching_session(tmp_path):
    flow, _ = make_flow(tmp_path)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    with pytest.raises(ValueError, match="已失效"):
        flow.enrollment_status("wrong-token")
    assert flow.enrollment_session is not None
    flow.enrollment_session["started"] -= 121
    assert flow.enrollment_status(token) == {"status": "EXPIRED"}
    assert flow.enrollment_session is None


def test_selector_never_lowers_first_five_minimum_quality(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = [candidate(index, sharpness=8, feature_value=index) for index in range(1, 6)]
    frames.extend(candidate(index, sharpness=3, feature_value=index) for index in range(6, 9))
    iterator = iter(frames)
    flow.enrollment_candidate = lambda: next(iterator)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    state = None
    for _ in range(8):
        state = flow.enrollment_step(token)
    assert state["status"] == "READY"
    assert state["selector_quality_floor"] == {"sharpness": 8, "contrast": 25}
    assert state["selected_frame_ids"] == [1, 2, 3, 4, 5]
    assert all(item["sharpness"] >= 8 for item in flow.enrollment_session["qualities"])


def test_uvc_profile_is_saved_and_used_when_warming_gallery(tmp_path):
    algorithm = Algorithm()
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(4), "", "mock"),
                    capture_profile="uvc-test-YUYV-640x360",
                    capture_source="uvc-stream-frame-YUYV-640x360")
    warmed_profiles = []
    flow.gallery.warm_up = lambda *, capture_profile: warmed_profiles.append(capture_profile)
    candidates = iter(candidate(index) for index in range(1, 9))
    flow.enrollment_candidate = lambda: next(candidates)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(8):
        flow.enrollment_step(token)
    flow.enrollment_commit(token, "left")
    _, metadata = flow.store.load("p1_left")
    assert metadata["capture_profile"] == "uvc-test-YUYV-640x360"
    assert metadata["source"] == "uvc-stream-frame-YUYV-640x360"
    assert warmed_profiles == ["uvc-test-YUYV-640x360"]


def test_repeated_clear_frame_does_not_exhaust_quality_budget(tmp_path):
    flow, _ = make_flow(tmp_path)
    first = candidate(1)
    frames = iter([first] * 18 + [candidate(i) for i in range(2, 9)])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    flow.enrollment_step(token)
    repeated = [flow.enrollment_step(token) for _ in range(17)]
    assert all(item["status"] == "WAIT" for item in repeated)
    assert repeated[-1]["attempts"] == 18
    assert repeated[-1]["duplicate_frames"] == 17
    assert repeated[-1]["quality_failures"] == 0
    assert "重复" in repeated[-1]["reason"]
    assert not flow.store.exists("p1_left")
    finish = [flow.enrollment_step(token) for _ in range(7)]
    assert finish[-1]["status"] == "READY" and finish[-1]["kept"] == 5
    assert finish[-1]["attempts"] == 25
    assert not flow.store.exists("p1_left")
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"
    assert not flow.store.exists("p1_left")


def test_blurry_frames_still_have_finite_retry_budget(tmp_path):
    flow, _ = make_flow(tmp_path)
    flow.enrollment_candidate = lambda: candidate(1, sharpness=0)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    assert all(flow.enrollment_step(token)["status"] == "WAIT" for _ in range(15))
    stopped = flow.enrollment_step(token)
    assert stopped["status"] == "STOPPED"
    assert stopped["attempts"] == stopped["quality_failures"] == 15
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"
