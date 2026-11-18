from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

cv2 = pytest.importorskip("cv2")

from live_roi import LiveROIOverlay


def seed():
    pixels = np.random.default_rng(5).integers(0, 256, (240, 320), dtype=np.uint8)
    image = Image.fromarray(pixels).convert("RGB")
    quad = np.array(((90, 70), (210, 70), (210, 170), (90, 170)), dtype=np.float32)
    return SimpleNamespace(
        captured=SimpleNamespace(image=image, frame_id=1, captured_monotonic=10.0),
        roi_quad=quad,
        roi_status={"roi_status": "tracking", "frame_id": 1},
    )


def test_overlay_follows_current_frame_between_detector_results():
    processed = seed()
    overlay = LiveROIOverlay()
    for frame_id, dx in enumerate((5, 10, 15), start=2):
        moved = cv2.warpAffine(
            np.array(processed.captured.image),
            np.float32(((1, 0, dx), (0, 1, -4))), (320, 240),
        )
        quad, status = overlay.update(Image.fromarray(moved), frame_id, 10.0 + frame_id / 10, processed)
        assert quad is not None
        np.testing.assert_allclose(quad, processed.roi_quad + (dx, -4), atol=1.0)
        assert status["overlay_frame_id"] == frame_id
        assert status["overlay_seed_frame_id"] == 1
        assert status["overlay_source"] == "optical_flow"
    np.testing.assert_array_equal(processed.roi_quad[0], (90, 70))


def test_overlay_expires_even_with_a_frozen_detector():
    processed = seed()
    overlay = LiveROIOverlay()
    overlay.update(processed.captured.image, 1, 10.0, processed)
    quad, status = overlay.update(processed.captured.image, 60, 12.0, processed)
    assert quad is None
    assert status["roi_reason"] == "preview_expired"


def test_overlay_drops_quad_when_texture_disappears():
    processed = seed()
    overlay = LiveROIOverlay()
    overlay.update(processed.captured.image, 1, 10.0, processed)
    quad, status = overlay.update(Image.new("RGB", (320, 240)), 2, 10.1, processed)
    assert quad is None
    assert status["roi_reason"] == "preview_motion_lost"


def test_overlay_clears_on_detector_rejection():
    processed = seed()
    overlay = LiveROIOverlay()
    overlay.update(processed.captured.image, 1, 10.0, processed)
    processed.roi_quad = None
    processed.roi_status = {"roi_status": "no_hand", "roi_reason": "below_threshold"}
    quad, status = overlay.update(processed.captured.image, 2, 10.1, processed)
    assert quad is None
    assert status["roi_status"] == "no_hand"
