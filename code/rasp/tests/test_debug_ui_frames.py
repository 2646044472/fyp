from __future__ import annotations

import json
import io
import threading
import time
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

import debug_ui


def make_feed() -> debug_ui.CameraFeed:
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed.frame_condition = threading.Condition(feed.lock)
    feed.roi_mode = "dynamic"
    feed.latest_roi_status = {"roi_status": "tracking"}
    feed.latest = debug_ui.CapturedFrame(9, Image.new("RGB", (8, 8), "red"), 2.0)
    processed_image = Image.new("RGB", (8, 8), "blue")
    feed.latest_processed = debug_ui.ProcessedFrame(
        debug_ui.CapturedFrame(7, processed_image, 1.0),
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        {"roi_status": "tracking", "frame_id": 7},
    )
    return feed


def test_dynamic_snapshot_uses_the_detector_source_frame():
    feed = make_feed()

    image, _, quad, status, frame_id = feed.snapshot()

    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert frame_id == 7
    assert status["frame_id"] == 7
    assert quad is not None


def test_dynamic_snapshot_can_require_a_new_processed_frame():
    feed = make_feed()

    image, _, _, _, frame_id = feed.snapshot(after_frame_id=6)

    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert frame_id == 7


def test_processed_debug_frame_uses_detector_source_image():
    feed = make_feed()

    image, _, _, frame_id, status = feed.processed_debug_frame()

    image = image.convert("RGB")
    red, green, blue = image.getpixel((0, 0))
    assert blue > red + 100
    assert blue > green + 100
    assert frame_id == 7
    assert status["frame_id"] == 7


def make_ready_uvc_feed(*, quality_status="READY", captured_age_ms=20):
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed.frame_condition = threading.Condition(feed.lock)
    feed.camera_backend = "uvc"
    feed.capture_profile = "uvc-test"
    feed.jpeg = b"preview-jpeg"
    feed.latest_roi_status = {"error": None}
    now = time.monotonic()
    feed.latest = debug_ui.CapturedFrame(12, Image.new("RGB", (8, 8), "red"), now)
    frame = debug_ui.CapturedFrame(
        11, Image.new("RGB", (8, 8), "blue"), now - captured_age_ms / 1000.0
    )
    feed.latest_processed = debug_ui.ProcessedFrame(
        frame,
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        {
            "frame_id": 11,
            "captured_monotonic_ms": frame.captured_monotonic * 1000.0,
            "roi_status": "tracking",
            "quality_status": quality_status,
            "quality_consecutive_frames": 5 if quality_status == "READY" else 0,
            "quality_required_frames": 5,
            "demo_quality_status": quality_status,
            "demo_quality_consecutive_frames": 5 if quality_status == "READY" else 0,
            "demo_quality_required_frames": 5,
        },
    )
    feed.quality_gate = SimpleNamespace(max_age_ms=500)
    feed.processing_thread = SimpleNamespace(is_alive=lambda: True)
    return feed


def test_ready_uvc_capture_returns_exact_frame_whose_roi_gate_is_ready():
    feed = make_ready_uvc_feed()

    preview, full, metadata = feed.capture_ready_processed_frame()

    assert preview.getpixel((0, 0)) == (0, 0, 255)
    assert full.getpixel((0, 0)) == (0, 0, 255)
    assert metadata["capture_frame_id"] == feed.latest_processed.captured.frame_id == 11
    assert metadata["capture_kind"] == "same_fresh_ready_processed_frame"


def test_ready_uvc_capture_rechecks_no_hand_on_the_exact_processed_frame():
    feed = make_ready_uvc_feed(quality_status="NO_HAND")

    with pytest.raises(debug_ui.CaptureProcessingFailure) as caught:
        feed.capture_ready_processed_frame()

    assert caught.value.reason == "NO_HAND"


def test_ready_uvc_capture_rejects_stale_processed_frame():
    feed = make_ready_uvc_feed(captured_age_ms=2000)

    with pytest.raises(debug_ui.CaptureProcessingFailure) as caught:
        feed.capture_ready_processed_frame()

    assert caught.value.reason == "CAPTURE_TIMEOUT"


def test_capture_loop_honors_eight_fps_cap_and_stops_with_fake_camera(monkeypatch):
    class FakeClock:
        now = 0.0
        sleeps: list[float] = []

        def monotonic(self):
            return self.now

        def sleep(self, seconds):
            self.sleeps.append(seconds)
            self.now += seconds

    clock = FakeClock()
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.running = True
    feed.camera_backend = "picamera2"
    feed.camera_io_lock = threading.Lock()
    feed.lock = threading.Lock()
    feed.frame_condition = threading.Condition(feed.lock)
    feed.capture_only = True
    feed._capture_interval_s = 1.0 / debug_ui.CAPTURE_FPS_CAP
    feed._preview_interval_s = 1.0 / debug_ui.PREVIEW_FPS_CAP
    feed._next_frame_id = 0
    feed.latest = None
    feed.latest_processed = None
    feed.latest_roi_status = {}
    feed.latest_preview_status = {}
    feed._preview_source = None
    feed.preview_overlay = None
    feed.jpeg = None
    feed._last_preview_time = 0.0
    jpeg_encodes = []
    feed._encode_preview = lambda image, quad, status: jpeg_encodes.append(True) or b"jpeg"

    class FakeCamera:
        capture_times: list[float] = []

        def capture_array(self, name):
            assert name == "main"
            self.capture_times.append(clock.now)
            if len(self.capture_times) == 4:
                feed.running = False
            return np.zeros((2, 2, 3), dtype=np.uint8)

    camera = FakeCamera()
    feed.camera = camera
    monkeypatch.setattr(debug_ui.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(debug_ui.time, "sleep", clock.sleep)

    feed._capture_loop()

    assert debug_ui.CAPTURE_FPS_CAP == 8.0
    assert camera.capture_times == pytest.approx([0.0, 0.125, 0.25, 0.375])
    assert clock.sleeps == pytest.approx([0.125, 0.125, 0.125])
    assert feed._next_frame_id == 4
    assert feed._preview_source[0].frame_id == 4
    assert jpeg_encodes == []
    assert feed.running is False


def test_preview_jpeg_is_encoded_on_demand_and_reused_until_due(monkeypatch):
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed._jpeg_lock = threading.Lock()
    feed.capture_only = True
    feed.latest_roi_status = {}
    feed.latest_preview_status = {}
    feed.preview_overlay = None
    feed.jpeg = None
    feed._jpeg_frame_id = -1
    feed._last_preview_time = 0.0
    feed._preview_interval_s = 1.0 / debug_ui.PREVIEW_FPS_CAP
    now = time.monotonic()
    first = debug_ui.CapturedFrame(1, Image.new("RGB", (8, 8), "red"), now)
    feed.latest = first
    feed._preview_source = (first, None, {"roi_mode": "capture"})
    encoded = []
    feed._encode_preview = lambda image, quad, status: encoded.append(image) or b"jpeg-1"

    assert feed._camera_frame_state()["camera_ready"]
    assert feed.jpeg is None
    assert feed.jpeg_frame() == b"jpeg-1"
    assert len(encoded) == 1
    assert feed.jpeg_frame() == b"jpeg-1"
    assert len(encoded) == 1

    second = debug_ui.CapturedFrame(2, Image.new("RGB", (8, 8), "blue"), now + 0.1)
    feed.latest = second
    feed._preview_source = (second, None, {"roi_mode": "capture"})
    assert feed.jpeg_frame() == b"jpeg-1"
    assert len(encoded) == 1

    third = debug_ui.CapturedFrame(3, Image.new("RGB", (8, 8), "green"), now + 0.25)
    feed.latest = third
    feed._preview_source = (third, None, {"roi_mode": "capture"})
    feed._encode_preview = lambda image, quad, status: encoded.append(image) or b"jpeg-3"
    assert feed.jpeg_frame() == b"jpeg-3"
    assert len(encoded) == 2


def test_display_preview_preserves_capture_frame_size():
    source = Image.new("RGB", (640, 480), "red")
    jpeg = debug_ui.CameraFeed._encode_preview(source, None, {"roi_mode": "capture"})
    preview = Image.open(io.BytesIO(jpeg))
    assert preview.size == (640, 480)
    assert source.size == (640, 480)


def test_collection_session_manager_lists_and_deletes_one_session(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    session_id = "20261006T123456789012Z-a1b2c3d4"
    sample_id = "20261006T123457789012Z-e5f6a7b8"
    session_root = runtime / "highres_sessions" / session_id
    sample_root = runtime / "highres_capture" / sample_id
    session_root.mkdir(parents=True)
    sample_root.mkdir(parents=True)
    (sample_root / "full.jpg").write_bytes(b"full")
    (sample_root / "roi_128.png").write_bytes(b"roi")
    (sample_root / "metadata.json").write_text(json.dumps({"session_id": session_id}), encoding="utf-8")
    (session_root / "manifest.json").write_text(json.dumps({
        "session_id": session_id,
        "subject": "p01",
        "hand": "right",
        "background": "existing",
        "distance_cm": 30,
        "notes": "",
        "sample_ids": [sample_id],
        "phase": "await_hand",
    }), encoding="utf-8")

    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", runtime)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock()
    app.collection_lock = threading.Lock()
    app.collection_batch = {"session_id": session_id}

    sessions = app.list_highres_sessions()
    assert sessions[0]["session_id"] == session_id
    assert sessions[0]["sample_count"] == 1

    result = app.delete_highres_session(session_id)
    assert result == {"status": "DELETED", "session_id": session_id, "deleted_samples": 1, "recoverable": True}
    assert list((runtime / "collection_trash").rglob("full.jpg"))[0].read_bytes() == b"full"
    assert not session_root.exists()
    assert not sample_root.exists()
    assert app.collection_batch is None
    assert app.list_highres_sessions() == []


def test_collection_session_manager_rejects_invalid_session_id(tmp_path, monkeypatch):
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", tmp_path / "runtime")
    app = debug_ui.App.__new__(debug_ui.App)
    with pytest.raises(ValueError, match="Invalid session ID"):
        app.delete_highres_session("../runtime")


def test_delete_damaged_photos_keeps_others_and_allows_retake(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    session_id = "20261029T123456000000Z-a1b2c3d4"
    ids = [f"20261029T12345600000{i}Z-{i:08x}" for i in range(1, 6)]
    root = runtime / "highres_sessions" / session_id
    root.mkdir(parents=True)
    batch = dict(session_id=session_id, subject="p01", hand="left", background="existing",
                 distance_cm=None, notes="", started_at_pi_utc="", client_time_utc="",
                 sample_ids=ids[:], phase="await_hand")
    (root / "manifest.json").write_text(json.dumps(batch), encoding="utf-8")
    for i, sample in enumerate(ids, 1):
        folder = runtime / "highres_capture" / sample
        folder.mkdir(parents=True)
        (folder / "full.jpg").write_bytes(b"original" if i <= 3 else b"")
        (folder / "metadata.json").write_text(json.dumps(dict(session_id=session_id, sample_id=sample, sample_index=i)) if i <= 3 else "", encoding="utf-8")
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", runtime)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock()
    app.collection_lock = threading.Lock()
    app.collection_batch = batch
    app.capture_only = True
    app.camera = SimpleNamespace(camera_backend="uvc", roi_mode="capture", capture_highres=lambda: (Image.new("RGB", (8, 8)), Image.new("RGB", (16, 16)), {}), capture_settings=lambda: {})
    assert app.latest_highres()["sample_id"] in ids[:3]
    assert app.delete_highres_sample(session_id, ids[3])["captured"] == 4
    assert (runtime / "highres_capture" / ids[4] / "metadata.json").read_bytes() == b""
    assert app.delete_highres_sample(session_id, ids[4])["captured"] == 3
    for sample in ids[:3]:
        assert (runtime / "highres_capture" / sample / "full.jpg").read_bytes() == b"original"
    assert len(list((runtime / "collection_trash").rglob("full.jpg"))) == 2
    result = app.capture_highres_batch()
    assert result["sample_index"] == 4
    assert app.highres_batch_status()["captured"] == 4


def test_cannot_delete_photo_owned_by_another_session(tmp_path, monkeypatch):
    session_id = "20261029T123456000000Z-a1b2c3d4"
    other = "20261029T123456000001Z-a1b2c3d4"
    sample = "20261029T123456000002Z-a1b2c3d4"
    root = tmp_path / "highres_sessions" / session_id
    photo = tmp_path / "highres_capture" / sample
    root.mkdir(parents=True); photo.mkdir(parents=True)
    (root / "manifest.json").write_text(json.dumps({"sample_ids": [sample]}))
    (photo / "metadata.json").write_text(json.dumps({"session_id": other}))
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", tmp_path)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock();app.collection_lock = threading.Lock()
    with pytest.raises(ValueError, match="does not belong"):
        app.delete_highres_sample(session_id, sample)
    assert photo.is_dir()


def test_preview_encode_cadence_is_capped_separately_from_capture():
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.jpeg = b"existing-preview"
    feed._last_preview_time = 10.0
    feed._preview_interval_s = 1.0 / debug_ui.PREVIEW_FPS_CAP

    assert debug_ui.CAPTURE_FPS_CAP == 8.0
    assert debug_ui.PREVIEW_FPS_CAP == 5.0
    assert not feed._preview_due(10.199)
    assert feed._preview_due(10.201)

    feed.jpeg = None
    assert feed._preview_due(10.001)


def test_processing_loop_skips_stale_status_update_when_detector_rate_limiter_rejects_frame(monkeypatch):
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.running = True
    feed.lock = threading.Lock()
    feed.frame_condition = threading.Condition(feed.lock)
    feed.pending_frame = debug_ui.CapturedFrame(
        8, Image.new("RGB", (32, 24), "white"), 0.8
    )
    feed.roi_mode = "dynamic"
    feed._last_processing_time = 0.0
    feed._processing_interval_s = 0.8
    feed.latest_roi_status = {"roi_status": "tracking", "quality_status": "READY"}
    feed.latest_preview_status = {}
    roi = np.ones((128, 128), dtype=np.uint8)
    old_frame = debug_ui.CapturedFrame(7, Image.new("RGB", (32, 24), "blue"), 0.0)
    old_status = {
        "roi_status": "tracking", "captured_monotonic_ms": 0.0,
        "quality_status": "READY", "quality_consecutive_frames": 5, "quality_required_frames": 5,
        "demo_quality_status": "READY", "demo_quality_consecutive_frames": 5,
        "demo_quality_required_frames": 5,
    }
    feed.latest_processed = debug_ui.ProcessedFrame(old_frame, None, roi, old_status)
    feed.latest = feed.pending_frame
    feed.capture_only = False
    feed.processing_thread = SimpleNamespace(is_alive=lambda: True)
    feed.quality_gate = SimpleNamespace(max_age_ms=500.0)

    class RateLimitedTracker:
        status_calls = 0

        def submit(self, _image, _timestamp_ms):
            feed.running = False
            return False

        def roi_status(self, *_args, **_kwargs):
            self.status_calls += 1
            raise AssertionError("a skipped inference must not replace the last accepted ROI state")

    tracker = RateLimitedTracker()
    feed.tracker = tracker
    monkeypatch.setattr(debug_ui.time, "monotonic", lambda: 0.8)

    feed._processing_loop()

    assert tracker.status_calls == 0
    assert feed.latest_processed.captured.frame_id == 7
    assert feed.latest_roi_status == {"roi_status": "tracking", "quality_status": "READY"}
    status = feed.status()
    assert status["quality_status"] == "READY" and status["roi_status_fresh"] is False
    with pytest.raises(debug_ui.CaptureProcessingFailure) as caught:
        feed.capture_ready_processed_frame()
    assert caught.value.reason == "CAPTURE_TIMEOUT"


def test_roi_jpeg_is_encoded_on_demand_once_per_processed_frame():
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed._roi_jpeg_lock = threading.Lock()
    feed.roi_jpeg = None
    feed._roi_jpeg_frame_id = -1
    roi = np.arange(128 * 128, dtype=np.uint8).reshape(128, 128)
    captured = debug_ui.CapturedFrame(21, Image.new("RGB", (64, 48)), 1.0)
    feed.latest_processed = debug_ui.ProcessedFrame(captured, None, roi, {})
    encoded_rois = []
    feed._encode_roi_jpeg = lambda current: encoded_rois.append(current.copy()) or b"jpeg-21"

    assert feed.roi_frame() == b"jpeg-21"
    assert feed.roi_frame() == b"jpeg-21"
    assert len(encoded_rois) == 1
    assert np.array_equal(encoded_rois[0], roi)

    next_roi = np.flipud(roi).copy()
    next_frame = debug_ui.CapturedFrame(22, Image.new("RGB", (64, 48)), 2.0)
    feed.latest_processed = debug_ui.ProcessedFrame(next_frame, None, next_roi, {})
    assert feed.roi_frame() == b"jpeg-21"
    assert len(encoded_rois) == 2
    assert np.array_equal(encoded_rois[1], next_roi)


def test_roi_jpeg_encode_race_does_not_cache_an_old_frame_over_a_new_one():
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed._roi_jpeg_lock = threading.Lock()
    feed.roi_jpeg = None
    feed._roi_jpeg_frame_id = -1
    first_roi = np.zeros((128, 128), dtype=np.uint8)
    second_roi = np.ones((128, 128), dtype=np.uint8)
    first_frame = debug_ui.CapturedFrame(31, Image.new("RGB", (32, 24)), 1.0)
    second_frame = debug_ui.CapturedFrame(32, Image.new("RGB", (32, 24)), 2.0)
    first = debug_ui.ProcessedFrame(first_frame, None, first_roi, {})
    second = debug_ui.ProcessedFrame(second_frame, None, second_roi, {})
    feed.latest_processed = first
    calls = []

    def encode(roi):
        calls.append(roi.copy())
        if len(calls) == 1:
            with feed.lock:
                feed.latest_processed = second
            return b"jpeg-31"
        return b"jpeg-32"

    feed._encode_roi_jpeg = encode

    assert feed.roi_frame() == b"jpeg-31"
    assert feed.roi_jpeg is None and feed._roi_jpeg_frame_id == -1
    assert feed.roi_frame() == b"jpeg-32"
    assert feed.roi_jpeg == b"jpeg-32" and feed._roi_jpeg_frame_id == 32
    assert len(calls) == 2
    assert np.array_equal(calls[0], first_roi)
    assert np.array_equal(calls[1], second_roi)
