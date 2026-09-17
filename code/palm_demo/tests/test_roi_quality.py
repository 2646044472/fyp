import json
import shutil
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

import numpy as np
from PIL import Image

from roi_quality import (
    DEBUG_DATASET_SCHEMA_VERSION,
    ROIQualityGate,
    DebugDatasetWriter,
)


def palm_quad(left=20.0, top=20.0, width=40.0, height=50.0):
    return np.array(
        [[left, top], [left + width, top], [left + width, top + height], [left, top + height]],
        dtype=np.float32,
    )


def good_update(gate, frame_id, *, status="tracking", quad=None, contrast=20.0, sharpness=5.0, age_ms=50.0):
    return gate.update(
        frame_id=frame_id,
        captured_monotonic_ms=1_000.0,
        now_monotonic_ms=1_000.0 + age_ms,
        image_size=(100, 100),
        roi_quad=palm_quad() if quad is None else quad,
        tracker_status=status,
        quality={"contrast": contrast, "sharpness": sharpness},
    )


def test_gate_requires_five_fresh_stable_frames_before_ready():
    gate = ROIQualityGate(required_frames=5, min_contrast=12.0, min_sharpness=2.0)

    states = [good_update(gate, frame_id).state for frame_id in range(1, 6)]

    assert states == ["TRACKING", "TRACKING", "TRACKING", "TRACKING", "READY"]


def test_stale_tracking_resets_gate_and_cannot_reuse_previous_roi():
    gate = ROIQualityGate(required_frames=2, min_contrast=12.0, min_sharpness=2.0)
    good_update(gate, 1)
    assert good_update(gate, 2).state == "READY"

    lost = good_update(gate, 3, status="tracking_lost", quad=None)
    recovering = good_update(gate, 4)

    assert lost.state == "NO_HAND"
    assert lost.roi_quad is None
    assert recovering.state == "TRACKING"


def test_bad_geometry_or_blur_is_low_quality_and_resets_stability():
    gate = ROIQualityGate(required_frames=2, min_contrast=12.0, min_sharpness=2.0)
    good_update(gate, 1)

    low_quality = good_update(gate, 2, sharpness=1.0)
    outside = good_update(gate, 3, quad=palm_quad(left=80.0, top=20.0))

    assert low_quality.state == "LOW_QUALITY"
    assert low_quality.reason == "sharpness_below_minimum"
    assert outside.state == "LOW_QUALITY"
    assert outside.reason == "roi_out_of_bounds"


def test_debug_dataset_writer_preserves_exact_raw_and_matcher_roi():
    root = Path(__file__).parent / ".tmp-debug-capture"
    shutil.rmtree(root, ignore_errors=True)
    try:
        writer = DebugDatasetWriter(
            root / "session-1",
            camera_settings={"camera": 0, "width": 480, "height": 360, "format": "RGB888"},
            roi_algorithm_version="palm-detector-mcp-v2",
        )
        raw = Image.fromarray(np.arange(4 * 6, dtype=np.uint8).reshape(4, 6), mode="L").convert("RGB")
        roi = (np.arange(128 * 128, dtype=np.uint16).reshape(128, 128) % 256).astype(np.uint8)

        sample_dir = writer.save(
            sample_index=1,
            raw_image=raw,
            roi_128=roi,
            metadata={
                "captured_at": "2026-09-17T00:00:00+00:00",
                "frame_id": 42,
                "roi_quad": palm_quad().tolist(),
                "tracking_status": "READY",
                "quality": {"contrast": 20.0, "sharpness": 5.0},
            },
        )

        assert (sample_dir / "raw.png").exists()
        assert (sample_dir / "roi_128.png").exists()
        metadata = json.loads((sample_dir / "metadata.json").read_text(encoding="utf-8"))
        saved_roi = np.asarray(Image.open(sample_dir / "roi_128.png"))

        assert saved_roi.shape == (128, 128)
        assert np.array_equal(saved_roi, roi)
        assert metadata["schema_version"] == DEBUG_DATASET_SCHEMA_VERSION
        assert metadata["sample_index"] == 1
        assert metadata["frame_id"] == 42
        assert metadata["tracking_status"] == "READY"
        assert metadata["camera_settings"]["format"] == "RGB888"
        assert metadata["roi_algorithm_version"] == "palm-detector-mcp-v2"
        assert set(metadata["artifacts"]) == {"raw.png", "roi_128.png"}
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_feature_rejects_a_stale_quad_even_when_one_is_supplied():
    import debug_ui

    class Algorithm:
        def extract(self, roi):
            return np.zeros((8,), dtype=bool)

    app = debug_ui.App.__new__(debug_ui.App)
    app.camera = SimpleNamespace(roi_mode="dynamic")
    app.algorithm = Algorithm()
    image = Image.fromarray(np.tile(np.linspace(0, 255, 100, dtype=np.uint8), (100, 1)), mode="L").convert("RGB")

    with pytest.raises(RuntimeError, match="ROI quality is not READY"):
        app.feature(
            image,
            palm_quad(),
            {"roi_status": "tracking_lost", "quality_status": "NO_HAND"},
        )


def test_debug_dataset_requires_a_no_hand_rearm_between_samples():
    import debug_ui

    app = debug_ui.App.__new__(debug_ui.App)
    app.camera = SimpleNamespace(status=lambda: {"quality_status": "READY"})
    app.debug_writer = SimpleNamespace(root=Path("session-1"))
    app.debug_sample_index = 2
    app.debug_requires_removal = True

    assert app.status()["debug_capture"]["requires_removal"] is True

    app.camera = SimpleNamespace(status=lambda: {"quality_status": "NO_HAND"})
    assert app.status()["debug_capture"]["requires_removal"] is False


def test_debug_capture_api_rejects_capture_before_no_hand_rearm():
    import debug_ui

    class Camera:
        def snapshot(self, **kwargs):
            raise AssertionError("capture must be blocked before reading a frame")

    app = debug_ui.App.__new__(debug_ui.App)
    app.camera = Camera()
    app.debug_requires_removal = True
    app.debug_last_frame_id = None

    with pytest.raises(RuntimeError, match="Remove the palm"):
        app.capture_debug_sample()


def test_snapshot_returns_the_exact_roi_with_the_matching_frame():
    import debug_ui

    captured = debug_ui.CapturedFrame(
        frame_id=7,
        image=Image.new("RGB", (20, 20), color="black"),
        captured_monotonic=1.0,
    )
    roi = np.full((128, 128), 9, dtype=np.uint8)
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.roi_mode = "dynamic"
    feed.latest_processed = debug_ui.ProcessedFrame(
        captured=captured,
        roi_quad=palm_quad(2, 2, 10, 10),
        roi=roi,
        roi_status={"quality_status": "READY"},
    )
    feed.frame_condition = threading.Condition(threading.Lock())

    image, returned_roi, quad, status, frame_id = feed.snapshot()

    assert image is not captured.image
    assert np.array_equal(returned_roi, roi)
    assert np.array_equal(quad, palm_quad(2, 2, 10, 10))
    assert status["quality_status"] == "READY"
    assert frame_id == 7
