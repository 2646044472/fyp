"""Continuous capture buffers ten candidates and commits only five selected frames."""

import numpy as np
import pytest
import time

from demo_flow import (CaptureProcessingFailure, DemoFlow, classify_camera_capture_error,
                       classify_roi_capture_error)


class Algorithm:
    name = "burst-test"
    def prepare_gallery(self, _groups):
        pass


def candidate(index, *, sharpness=8, contrast=25, roi=None, feature_value=None):
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
            {"contrast": contrast, "sharpness": sharpness}, roi,
            {"roi_quad": quad, "frame_size": (100, 100)})


def make_flow(tmp_path):
    algorithm = Algorithm()
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(4), "", "mock"))
    warmed = []
    flow.gallery.warm_up = lambda *, capture_profile: warmed.append(capture_profile)
    return flow, warmed


def test_selection_metadata_survives_reopen_and_legacy_template_update(tmp_path):
    flow, _ = make_flow(tmp_path)
    flow.store.save("legacy_left", np.zeros((5, 4)), {
        "user": "legacy_left", "display_name": "Legacy", "algorithm": "old-algorithm",
        "capture_profile": flow.capture_profile, "hand_declared_by_user": "left",
    })
    flow.payments.create_account("legacy_left", "Legacy", 10000)
    reopened, _ = make_flow(tmp_path)
    old_features, old_metadata = reopened.store.load("legacy_left")
    assert old_features.shape == (5, 4) and "enrollment_selection" not in old_metadata

    for user in ("fresh_left", "legacy_left"):
        reopened.enrollment_candidate = iter(candidate(i) for i in range(1, 9)).__next__
        token = reopened.enrollment_start(user, user, "left")["token"]
        states = [reopened.enrollment_step(token) for _ in range(8)]
        assert states[-1]["status"] == "READY"
        reopened.enrollment_commit(token, "left")
        restarted, _ = make_flow(tmp_path)
        features, metadata = restarted.store.load(user)
        assert features.shape == (5, 4)
        assert metadata["enrollment_selection"] == {
            "mode": "full_candidate_pool", "candidate_count": 8, "attempts": 8,
            "quality_failures": 0, "duplicate_frames": 0,
            "selected_frame_ids": states[-1]["selected_frame_ids"],
        }
        assert restarted.payments.user_exists(user)


def test_enrollment_start_replays_lost_response_with_same_client_token(tmp_path):
    flow, _ = make_flow(tmp_path)
    request_token = "a" * 32
    first = flow.enrollment_start("p1_left", "P1", "left", request_token)
    assert first["timeout_seconds_remaining"] == 600 and first["timeout_ms_remaining"] == 600000
    session = flow.enrollment_session
    started = session["started"]

    replay = flow.enrollment_start("p1_left", "P1", "left", request_token)

    assert replay["token"] == first["token"] == request_token
    assert replay["timeout_ms_remaining"] <= 600_000
    assert flow.enrollment_session is session
    assert flow.enrollment_session["started"] == started
    with pytest.raises(ValueError, match="An enrollment is already in progress"):
        flow.enrollment_start("p1_left", "P1", "left", "b" * 32)
    with pytest.raises(ValueError, match="An enrollment is already in progress"):
        flow.enrollment_start("p1_left", "Other", "left", request_token)
    with pytest.raises(ValueError, match="Invalid enrollment request ID"):
        flow.enrollment_start("p2_left", "P2", "left", "not-a-token")


def test_cancelled_client_request_cannot_be_resurrected_by_late_replay(tmp_path):
    flow, _ = make_flow(tmp_path)
    request_token = "c" * 32
    flow.enrollment_start("p1_left", "P1", "left", request_token)

    assert flow.enrollment_cancel(request_token) == {"status": "CANCELLED"}
    assert flow.enrollment_status(request_token) == {"status": "CANCELLED"}
    assert flow.enrollment_cancel(request_token) == {"status": "CANCELLED"}
    with pytest.raises(ValueError, match="enrollment request has ended"):
        flow.enrollment_start("p1_left", "P1", "left", request_token)
    assert flow.enrollment_session is None


def test_cancel_arriving_before_start_prevents_late_session_creation(tmp_path):
    flow, _ = make_flow(tmp_path)
    request_token = "e" * 32

    assert flow.enrollment_cancel(request_token) == {"status": "CANCELLED"}
    with pytest.raises(ValueError, match="enrollment request has ended"):
        flow.enrollment_start("p1_left", "P1", "left", request_token)
    assert flow.enrollment_session is None


def test_cancelling_unknown_token_does_not_cancel_other_active_session(tmp_path):
    flow, _ = make_flow(tmp_path)
    active_token = "f" * 32
    unknown_token = "0" * 32
    flow.enrollment_start("p1_left", "P1", "left", active_token)

    assert flow.enrollment_cancel(unknown_token) == {"status": "CANCELLED"}
    assert flow.enrollment_session["token"] == active_token
    with pytest.raises(ValueError, match="An enrollment is already in progress"):
        flow.enrollment_start("p2_left", "P2", "left", unknown_token)
    assert flow.enrollment_session["token"] == active_token
    assert flow.enrollment_cancel(active_token) == {"status": "CANCELLED"}
    with pytest.raises(ValueError, match="enrollment request has ended"):
        flow.enrollment_start("p2_left", "P2", "left", unknown_token)
    assert flow.enrollment_session is None


def test_expired_client_request_cannot_be_resurrected_by_late_replay(tmp_path, monkeypatch):
    flow, _ = make_flow(tmp_path)
    request_token = "d" * 32
    flow.enrollment_start("p1_left", "P1", "left", request_token)
    started = flow.enrollment_session["started"]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: started + 601.0)

    with pytest.raises(ValueError, match="enrollment request has ended"):
        flow.enrollment_start("p1_left", "P1", "left", request_token)
    assert flow.enrollment_session is None
    assert flow.enrollment_status(request_token) == {"status": "EXPIRED"}



def test_in_progress_status_restores_latest_candidate_preview(tmp_path):
    flow, _ = make_flow(tmp_path)
    flow.enrollment_candidate = iter([candidate(1), candidate(2)]).__next__
    token = flow.enrollment_start("preview_left", "Preview", "left")["token"]
    first = flow.enrollment_step(token)
    second = flow.enrollment_step(token)
    assert first["candidate_roi_image"] == "roi-1"
    assert second["candidate_roi_image"] == "roi-2"
    assert flow.enrollment_status(token)["candidate_roi_image"] == "roi-2"


def test_improved_duplicate_replaces_candidate_preview(tmp_path):
    flow, _ = make_flow(tmp_path)
    first = candidate(1, sharpness=8)
    flow.enrollment_candidate = iter([first, candidate(2, sharpness=10, roi=first[4].copy())]).__next__
    token = flow.enrollment_start("preview_left", "Preview", "left")["token"]
    flow.enrollment_step(token)
    result = flow.enrollment_step(token)
    assert result["candidate_pool_count"] == 1
    assert result["duplicate_frames"] == 1
    assert result["candidate_roi_image"] == "roi-2"
    assert flow.enrollment_status(token)["candidate_roi_image"] == "roi-2"


def test_deferred_feature_skips_duplicate_but_keeps_clearer_replacement(tmp_path):
    flow, _ = make_flow(tmp_path)
    extracted = []

    def lazy_candidate(index, *, sharpness=8, roi=None):
        row = candidate(index, sharpness=sharpness, roi=roi)
        feature = row[0]

        def extract():
            extracted.append(index)
            return feature

        metadata = {**row[5], "feature_deferred": True}
        return (extract, row[1], row[2], row[3], row[4], metadata)

    first = lazy_candidate(1)
    duplicate = lazy_candidate(2, roi=first[4].copy())
    clearer_duplicate = lazy_candidate(3, sharpness=10, roi=first[4].copy())
    frames = iter([first, duplicate, clearer_duplicate,
                   lazy_candidate(4), lazy_candidate(5), lazy_candidate(6), lazy_candidate(7)])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]

    assert flow.enrollment_step(token)["status"] == "COLLECTING"
    repeated = flow.enrollment_step(token)
    assert repeated["status"] == "WAIT" and repeated["duplicate_frames"] == 1
    assert extracted == [1]
    replaced = flow.enrollment_step(token)
    assert replaced["status"] == "COLLECTING" and replaced["duplicate_frames"] == 2
    assert extracted == [1, 3]
    for _ in range(4):
        flow.enrollment_step(token)

    pool = flow.enrollment_session["photo_candidates"]
    assert len(pool) == 5
    assert pool[0].payload["source"] == "mock-still"
    assert pool[0].sharpness == 10
    assert pool[0].payload["feature"].tolist() == [3.0] * 4
    assert extracted == [1, 3, 4, 5, 6, 7]
    assert flow.enrollment_session["attempts"] == 7
    assert flow.enrollment_session["feature_failures"] == 0
    assert not flow.store.exists("p1_left")


def test_deferred_feature_failure_is_counted_and_does_not_enter_pool(tmp_path):
    flow, _ = make_flow(tmp_path)
    bad = list(candidate(1))
    bad[0] = lambda: None
    bad[5] = {**bad[5], "feature_deferred": True}
    good = list(candidate(2))
    good_feature = good[0]
    good[0] = lambda: good_feature
    good[5] = {**good[5], "feature_deferred": True}
    frames = iter([tuple(bad), tuple(good)])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]

    failed = flow.enrollment_step(token)
    assert failed["status"] == "WAIT" and failed["capture_failure"] == "FEATURE_ERROR"
    assert failed["feature_failures"] == 1 and failed["candidate_pool_count"] == 0
    assert flow.enrollment_session["capture_in_flight"] is False
    recovered = flow.enrollment_step(token)
    assert recovered["status"] == "COLLECTING" and recovered["candidate_pool_count"] == 1
    assert recovered["feature_failures"] == 1
    assert not flow.store.exists("p1_left")

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
    assert states[1]["candidate_roi_image"] == "roi-1"
    assert states[2]["status"] == "WAIT"
    assert "candidate_roi_image" not in states[2]
    assert states[2]["candidate_pool_count"] == states[1]["candidate_pool_count"]
    assert states[-1]["status"] == "READY"
    assert states[-1]["candidate_pool_count"] == states[-1]["candidate_pool_required"] == 8
    assert states[-1]["kept"] == 5 and states[-1]["attempts"] == 10
    assert states[-1]["quality_failures"] == 1 and states[-1]["duplicate_frames"] == 1
    assert states[-1]["elapsed_ms"] >= 0
    assert states[-1]["step_elapsed_ms"] >= 0
    assert 0 <= states[-1]["timeout_seconds_remaining"] <= 600
    assert len(states[-1]["selected_roi_images"]) == 5
    assert len(flow.enrollment_session["features"]) == len(flow.enrollment_session["rois"]) == 5
    assert not flow.store.exists("p1_left")
    assert flow.enrollment_status(token)["elapsed_ms"] >= states[-1]["elapsed_ms"]
    with pytest.raises(ValueError, match="same selected hand"):
        flow.enrollment_commit(token, "right")
    result = flow.enrollment_commit(token, "left")
    assert result["user_id"] == "p1_left"
    assert result["enrollment_elapsed_ms"] >= states[-1]["elapsed_ms"]
    assert flow.enrollment_status(token) == {"status": "COMPLETED"}
    with pytest.raises(ValueError, match="enrollment request has ended"):
        flow.enrollment_start("p1_left", "P1", "left", token)
    features, metadata = flow.store.load("p1_left")
    assert len(features) == 5 and metadata["hand_declared_by_user"] == "left"
    assert metadata["enrollment_selection"] == {
        "mode": "full_candidate_pool", "candidate_count": 8, "attempts": 10,
        "quality_failures": 1, "duplicate_frames": 1,
        "selected_frame_ids": states[-1]["selected_frame_ids"],
    }


def test_cancel_after_restart_cannot_prove_uncertain_commit_was_not_saved(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 9))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(8):
        state = flow.enrollment_step(token)
    assert state["status"] == "READY"
    flow.enrollment_commit(token, "left")
    restarted, _ = make_flow(tmp_path)
    assert restarted.enrollment_status(token) == {"status": "LOST"}
    assert restarted.enrollment_cancel(token) == {"status": "CANCELLED"}
    assert restarted.store.exists("p1_left")


def test_global_brightness_shift_does_not_fill_enrollment_candidate_pool(tmp_path):
    flow, _ = make_flow(tmp_path)
    first = candidate(1)
    brightness_shifted = list(first)
    brightness_shifted[4] = np.clip(first[4].astype(np.float32) * 0.8 + 30, 0, 255).astype(np.uint8)
    assert np.mean(np.abs(first[4].astype(np.int16) - brightness_shifted[4].astype(np.int16))) >= 2.5
    frames = iter([first, tuple(brightness_shifted)])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]

    first_state = flow.enrollment_step(token)
    second_state = flow.enrollment_step(token)

    assert first_state["candidate_pool_count"] == 1
    assert second_state["status"] == "WAIT"
    assert second_state["candidate_pool_count"] == 1
    assert second_state["duplicate_frames"] == 1


def test_candidate_runtime_identity_is_saved_with_selected_templates(tmp_path):
    identity = {
        "matcher": "candidate-test", "source_sha256": "source", "checkpoint_sha256": "checkpoint",
        "onnx_sha256": "model", "feature_contract": "feature-v1", "score_contract": "score-v1",
        "threshold": 1.0, "min_margin": 0.1,
    }
    algorithm = Algorithm()
    algorithm.runtime_identity = identity
    flow = DemoFlow(tmp_path, algorithm, lambda: (np.zeros(4), "", "mock"))
    flow.gallery.warm_up = lambda *, capture_profile: None
    frames = iter(candidate(index) for index in range(8))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(8):
        state = flow.enrollment_step(token)
    assert state["status"] == "READY"
    flow.enrollment_commit(token, "left")
    _, metadata = flow.store.load("p1_left")
    assert metadata["matcher_runtime_identity"] == identity


@pytest.mark.parametrize(("failure", "message"), [
    ("ROI_UNSTABLE", "Palm detection is not stable yet"),
    ("ROI_NOT_READY", "Palm status is not stable yet"),
    ("ROI_GEOMETRY_INVALID", "geometry is invalid"),
    ("CAMERA_UNAVAILABLE", "Camera frame temporarily unavailable"),
    ("CAPTURE_TIMEOUT", "No fresh camera frame arrived in time"),
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
    assert "paused" in state["reason"] and "resumes automatically" in state["reason"] and "cancel" in state["reason"]
    assert state["quality_failures"] == 0 and state["candidate_pool_count"] == 0
    assert state["capture_failure"] == "NO_HAND" and "retry_after_ms" not in state


def test_cancel_before_selection_discards_candidate_pool(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(index) for index in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    with pytest.raises(ValueError, match="hand"):
        flow.enrollment_start("p1_left", "P1", "right")
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(4):
        flow.enrollment_step(token)
    with pytest.raises(ValueError, match="same selected hand"):
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
    assert 0 <= partial["timeout_seconds_remaining"] <= 600
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
    with pytest.raises(ValueError, match="expired"):
        flow.enrollment_status("wrong-token")
    assert flow.enrollment_session is not None
    flow.enrollment_session["last_activity"] -= 601
    assert flow.enrollment_status(token) == {"status": "EXPIRED"}
    assert flow.enrollment_session is None


def test_enrollment_status_reports_lost_process_local_session(tmp_path):
    old_process, _ = make_flow(tmp_path / "old")
    token = old_process.enrollment_start("p1_left", "P1", "left")["token"]

    restarted_process, _ = make_flow(tmp_path / "restarted")

    assert restarted_process.enrollment_status(token) == {"status": "LOST"}
    with pytest.raises(ValueError, match="expired"):
        restarted_process.enrollment_status("not-a-token")


def test_timeout_countdown_rounds_up_until_the_session_expires(tmp_path):
    flow, _ = make_flow(tmp_path)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    flow.enrollment_session["last_activity"] -= 599.2
    state = flow.enrollment_status(token)
    assert state["status"] == "PAUSED"
    assert state["timeout_seconds_remaining"] == 1
    assert 0 < state["timeout_ms_remaining"] <= 800


def test_capture_finishing_after_timeout_is_not_added_to_candidate_pool(tmp_path):
    flow, _ = make_flow(tmp_path)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]

    def capture_past_deadline():
        flow.enrollment_session["last_activity"] = time.monotonic() - 601
        return candidate(1)

    flow.enrollment_candidate = capture_past_deadline
    state = flow.enrollment_step(token)
    assert state["status"] == "STOPPED"
    assert "This photo was neither added nor saved" in state["reason"]
    assert state["candidate_pool_count"] == 0
    assert flow.enrollment_session["features"] == []


def test_commit_after_enrollment_timeout_does_not_save_templates(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(index) for index in range(1, 9))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(8):
        assert flow.enrollment_step(token)["status"] in {"COLLECTING", "READY"}
    flow.enrollment_session["last_activity"] = time.monotonic() - 601
    with pytest.raises(ValueError, match="timed out"):
        flow.enrollment_commit(token, "left")
    assert not flow.store.exists("p1_left")
    assert flow.enrollment_cancel(token)["status"] == "EXPIRED"


def test_selector_never_lowers_first_five_minimum_quality(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = [candidate(index, sharpness=8, feature_value=index) for index in range(1, 6)]
    # A later frame is sharper overall by contrast but falls below the initial
    # five's sharpness floor, so the production selector must exclude it.
    frames.extend(candidate(index, sharpness=3, contrast=48, feature_value=index)
                  for index in range(6, 9))
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
    assert all(item["sharpness"] >= 2 and item["contrast"] >= 12
               for item in flow.enrollment_session["qualities"])


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
    assert "duplicate" in repeated[-1]["reason"].lower()
    assert not flow.store.exists("p1_left")
    finish = [flow.enrollment_step(token) for _ in range(7)]
    assert finish[-1]["status"] == "READY" and finish[-1]["kept"] == 5
    assert finish[-1]["attempts"] == 25
    assert not flow.store.exists("p1_left")
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"
    assert not flow.store.exists("p1_left")


def test_blurry_frames_back_off_and_resume_automatically(tmp_path):
    flow, _ = make_flow(tmp_path)
    frames = iter([candidate(1, sharpness=0)] * 20 + [candidate(i) for i in range(1, 9)])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    bad = [flow.enrollment_step(token) for _ in range(20)]
    assert all(row["status"] == "WAIT" for row in bad)
    assert bad[13]["retry_after_ms"] == 500 and bad[14]["retry_after_ms"] == 2000
    assert bad[-1]["quality_failures"] == 20
    assert flow.enrollment_status(token)["status"] == "PAUSED"
    good = [flow.enrollment_step(token) for _ in range(8)]
    assert good[-1]["status"] == "READY" and good[-1]["kept"] == 5
    assert flow.enrollment_session["quality_failure_streak"] == 0
    assert flow.enrollment_commit(token, "left")["user_id"] == "p1_left"


def test_repeated_geometry_failure_backs_off_without_stopping(tmp_path):
    flow, _ = make_flow(tmp_path)
    def fail():
        raise CaptureProcessingFailure("ROI_GEOMETRY_INVALID")
    flow.enrollment_candidate = fail
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    results = [flow.enrollment_step(token) for _ in range(16)]
    assert all(row["status"] == "WAIT" for row in results)
    assert results[13]["retry_after_ms"] == 500
    assert results[14]["retry_after_ms"] == results[15]["retry_after_ms"] == 2000
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"


def test_active_steps_extend_idle_deadline_without_resetting_elapsed(tmp_path, monkeypatch):
    clock = [10000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    flow.enrollment_candidate = lambda: candidate(1, sharpness=0)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    clock[0] += 590
    first = flow.enrollment_step(token)
    assert first["status"] == "WAIT" and first["timeout_seconds_remaining"] == 600
    clock[0] += 20
    state = flow.enrollment_status(token)
    assert state["status"] == "PAUSED" and state["elapsed_ms"] == 610000
    assert state["timeout_seconds_remaining"] == 580
    clock[0] += 581
    assert flow.enrollment_status(token) == {"status": "EXPIRED"}
    assert not flow.store.exists("p1_left")


def test_status_or_start_replay_does_not_refresh_idle_deadline(tmp_path, monkeypatch):
    clock = [20000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    token = "a" * 32
    flow.enrollment_start("p1_left", "P1", "left", token)
    clock[0] += 590
    assert flow.enrollment_status(token)["timeout_seconds_remaining"] == 10
    replay = flow.enrollment_start("p1_left", "P1", "left", token)
    assert replay["timeout_seconds_remaining"] == 10
    clock[0] += 11
    stopped = flow.enrollment_step(token)
    assert stopped["status"] == "STOPPED" and stopped["attempts"] == 0
    assert flow.enrollment_status(token) == {"status": "EXPIRED"}
    assert not flow.store.exists("p1_left")


def test_five_distinct_good_candidates_finish_after_duplicate_wait(tmp_path, monkeypatch):
    clock = [10000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    candidates = [candidate(i) for i in range(1, 6)]
    frames = iter(candidates + [candidates[0], candidates[0]])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    states = [flow.enrollment_step(token) for _ in range(5)]
    assert states[-1]["candidate_pool_count"] == 5 and states[-1]["status"] == "COLLECTING"
    clock[0] += 7.9
    assert flow.enrollment_step(token)["status"] == "WAIT"
    clock[0] += 0.1
    result = flow.enrollment_step(token)
    assert result["status"] == "READY" and result["kept"] == 5
    assert result["selection_mode"] == "five_candidate_wait"
    assert result["candidate_pool_count"] == 5 and result["duplicate_frames"] == 1
    assert flow.enrollment_status(token)["selection_mode"] == "five_candidate_wait"
    assert [feature.tolist() for feature in flow.enrollment_session["features"]] == [[float(i)] * 4 for i in range(1, 6)]
    assert flow.enrollment_commit(token, "left")["user_id"] == "p1_left"
    _, metadata = flow.store.load("p1_left")
    assert metadata["enrollment_selection"] == {
        "mode": "five_candidate_wait", "candidate_count": 5, "attempts": 6,
        "quality_failures": 0, "duplicate_frames": 1,
        "selected_frame_ids": result["selected_frame_ids"],
    }


def test_duplicate_wait_never_substitutes_for_missing_distinct_candidates(tmp_path, monkeypatch):
    clock = [20000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    candidates = [candidate(i) for i in range(1, 5)]
    frames = iter(candidates + [candidates[0]])
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(4):
        flow.enrollment_step(token)
    clock[0] += 30
    state = flow.enrollment_step(token)
    assert state["status"] == "WAIT" and state["candidate_pool_count"] == 4 and state["kept"] == 0
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"


@pytest.mark.parametrize("failure", ["LOW_QUALITY", "ROI_UNSTABLE", "ROI_NOT_READY", "NO_HAND", "CAMERA_UNAVAILABLE"])
def test_five_candidate_fallback_uses_only_previously_qualified_frames(tmp_path, monkeypatch, failure):
    clock = [30000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    candidates = [candidate(i) for i in range(1, 6)]
    frames = iter(candidates)
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(5):
        flow.enrollment_step(token)
    def failed_capture():
        raise CaptureProcessingFailure(failure)
    flow.enrollment_candidate = failed_capture
    clock[0] += 7.9
    first = flow.enrollment_step(token)
    assert first["status"] in ("WAIT", "NO_HAND")
    if failure in {"CAMERA_UNAVAILABLE", "ROI_NOT_READY"}:
        assert 0 <= first["fallback_after_ms"] <= 101
    clock[0] += 0.1
    state = flow.enrollment_step(token)
    assert state["status"] == "READY" and state["kept"] == 5
    assert state["candidate_pool_count"] == 5 and state["selection_mode"] == "five_candidate_wait"
    assert [f.tolist() for f in flow.enrollment_session["features"]] == [[float(i)] * 4 for i in range(1, 6)]
    assert not flow.store.exists("p1_left")
    with pytest.raises(ValueError, match="same selected hand"):
        flow.enrollment_commit(token, "right")
    assert flow.enrollment_cancel(token)["status"] == "CANCELLED"


def test_selection_only_never_captures_before_five_candidate_deadline(tmp_path, monkeypatch):
    clock = [40000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(5): flow.enrollment_step(token)
    def forbidden(): raise AssertionError("selection-only must not capture")
    flow.enrollment_candidate = forbidden
    assert flow.enrollment_step(token, selection_only=True)["status"] == "WAIT"
    clock[0] += 8
    assert flow.enrollment_step(token, selection_only=True)["status"] == "READY"


def test_selection_only_through_http_does_not_capture(tmp_path, monkeypatch):
    import json
    import threading
    from http.server import ThreadingHTTPServer
    from types import SimpleNamespace
    from urllib.request import Request, urlopen
    from palm_app.debug_ui import make_handler

    clock = [50000.0]
    monkeypatch.setattr("demo_flow.time.monotonic", lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start("p1_left", "P1", "left")["token"]
    for _ in range(5): flow.enrollment_step(token)
    def forbidden(): raise AssertionError("selection-only must not capture")
    flow.enrollment_candidate = forbidden
    class QuietHandler(make_handler(SimpleNamespace(capture_only=False, demo=flow))):
        def log_message(self, *_args): pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def post(selection_only=True):
            req = Request(f"http://127.0.0.1:{server.server_port}/api/demo/enroll/step",
                          data=json.dumps({"token": token, "selection_only": selection_only}).encode(),
                          headers={"Content-Type": "application/json"})
            with urlopen(req, timeout=2) as response: return json.loads(response.read())
        def unavailable(): raise CaptureProcessingFailure("CAMERA_UNAVAILABLE")
        flow.enrollment_candidate = unavailable
        failed = post(False)
        assert failed["capture_failure"] == "CAMERA_UNAVAILABLE" and failed["fallback_after_ms"] == 8000
        flow.enrollment_candidate = forbidden
        assert post()["status"] == "WAIT"
        clock[0] += 8
        result = post()
        assert result["status"] == "READY" and result["kept"] == 5
        assert not flow.store.exists("p1_left")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_restored_status_exposes_fallback_deadline_without_capture(tmp_path, monkeypatch):
    clock = [40000.0]
    monkeypatch.setattr('demo_flow.time.monotonic', lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start('restore_left', 'Restore', 'left')['token']
    for _ in range(4):
        flow.enrollment_step(token)
    assert flow.enrollment_status(token)['fallback_after_ms'] is None
    flow.enrollment_step(token)
    clock[0] += 3
    state = flow.enrollment_status(token)
    assert state['status'] == 'PAUSED' and state['fallback_after_ms'] == 5000
    def forbidden():
        raise AssertionError('selection-only must not capture')
    flow.enrollment_candidate = forbidden
    assert flow.enrollment_step(token, selection_only=True)['status'] == 'WAIT'
    clock[0] += 5
    assert flow.enrollment_step(token, selection_only=True)['status'] == 'READY'
    assert not flow.store.exists('restore_left')
    assert flow.enrollment_cancel(token)['status'] == 'CANCELLED'


def test_restored_fallback_respects_expired_session(tmp_path, monkeypatch):
    clock = [50000.0]
    monkeypatch.setattr('demo_flow.time.monotonic', lambda: clock[0])
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 6))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start('expired_left', 'Expired', 'left')['token']
    for _ in range(5):
        flow.enrollment_step(token)
    clock[0] += 601
    assert flow.enrollment_status(token) == {'status': 'EXPIRED'}
    assert not flow.store.exists('expired_left')
    with pytest.raises(ValueError):
        flow.enrollment_step(token, selection_only=True)


def test_delayed_original_and_manual_commit_write_only_once(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    flow, _ = make_flow(tmp_path)
    frames = iter(candidate(i) for i in range(1, 9))
    flow.enrollment_candidate = lambda: next(frames)
    token = flow.enrollment_start('race_left', 'Race', 'left')['token']
    for _ in range(8):
        result = flow.enrollment_step(token)
    assert result['status'] == 'READY'
    barrier = Barrier(2)
    saved = []
    original_save = flow.store.save
    def save(*args, **kwargs):
        saved.append(args[0])
        return original_save(*args, **kwargs)
    monkeypatch.setattr(flow.store, 'save', save)
    def submit():
        barrier.wait()
        try:
            return flow.enrollment_commit(token, 'left')['user_id']
        except ValueError:
            return 'already_finished'
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: submit(), range(2)))
    assert sorted(results) == ['already_finished', 'race_left']
    assert saved == ['race_left']
    assert flow.enrollment_status(token) == {'status': 'COMPLETED'}


def test_reused_camera_frame_id_is_not_added_as_an_enrollment_candidate(tmp_path):
    flow, _ = make_flow(tmp_path)

    def with_frame_id(index, frame_id):
        value = list(candidate(index))
        value[5] = {**value[5], "capture_frame_id": frame_id}
        return tuple(value)

    flow.enrollment_candidate = iter([
        with_frame_id(1, 100),
        with_frame_id(2, 100),
        with_frame_id(3, 101),
    ]).__next__
    token = flow.enrollment_start("fresh_video_left", "Fresh Video", "left")["token"]

    first = flow.enrollment_step(token)
    repeated = flow.enrollment_step(token)
    next_frame = flow.enrollment_step(token)

    assert first["candidate_pool_count"] == 1
    assert repeated["status"] == "WAIT"
    assert repeated["capture_failure"] == "DUPLICATE_FRAME"
    assert repeated["candidate_pool_count"] == 1
    assert repeated["duplicate_frames"] == 1
    assert next_frame["candidate_pool_count"] == 2
    assert [item.frame_id for item in flow.enrollment_session["photo_candidates"]] == [100, 101]
