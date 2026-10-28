from types import SimpleNamespace

import numpy as np
from PIL import Image

from pklnet_roi import PKLNetROI, ROI_GEOMETRY_VERSION
from pklnet_tracker import PKLNetStatus
from palm_app.debug_ui import App
from gallery import Gallery
from demo_flow import DemoFlow
from templates import TemplateStore
from pklnet_tracker import PKLNetTracker
import pytest


def test_landscape_keypoints_map_back_to_original_height_not_width():
    # A 640x480 landscape image becomes 480x640 after clockwise rotation.
    keypoints = np.array([0, 0, 100, 200, 299, 399], dtype=np.float32)
    actual = PKLNetROI._unrotate_keypoints(keypoints, (480, 640), (640, 480), (1.6, 1.6))
    np.testing.assert_allclose(actual, [0, 479, 320, 319, 638.4, 0.6], atol=0.001)


def test_padding_maps_each_axis_using_its_actual_resize_scale():
    image = Image.new("RGB", (3280, 2464), (1, 2, 3))
    tensor, original, rotated, scales = PKLNetROI._prepare(image)
    assert tensor.shape == (1, 3, 400, 300)
    assert scales == (2464 / 300, 3280 / 399)
    # Upstream normalization consumes BGR byte order.
    np.testing.assert_allclose(tensor[0, :, 0, 0], (np.array([3, 2, 1]) / 255 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225], atol=1e-6)
    kp = PKLNetROI._unrotate_keypoints(np.array([0, 399, 299, 0], dtype=np.float32), original, rotated, scales)
    np.testing.assert_allclose(kp, [3280, 2463, 0, 2463 - 299 * 2464 / 300], atol=0.001)


def test_tracker_reports_pklnet_geometry_instead_of_old_dynamic_geometry():
    result = PKLNetStatus(None, "no_hand").as_dict()
    assert result["roi_mode"] == "pklnet"
    assert result["roi_geometry"] == ROI_GEOMETRY_VERSION


def test_matcher_uses_exact_processed_pklnet_pixels():
    exact = np.arange(128 * 128, dtype=np.uint8).reshape(128, 128)
    app = App.__new__(App)
    app.camera = SimpleNamespace(roi_mode="pklnet")
    seen = []
    app.algorithm = SimpleNamespace(extract=lambda roi: seen.append(roi.copy()) or np.array([True]))
    status = {"quality_status": "READY", "quality": {"contrast": 20.0, "sharpness": 10.0}}
    app.feature(Image.new("RGB", (480, 360), "black"), np.ones((4, 2)), status, processed_roi=exact)
    np.testing.assert_array_equal(seen[0], exact)


def test_demo_gallery_excludes_templates_from_old_roi(tmp_path):
    store = TemplateStore(tmp_path)
    store.save("old", np.array([[0]]), {"capture_profile": "noir-ir", "algorithm": "FastCC"})
    store.save("new", np.array([[1]]), {"capture_profile": "noir-ir", "algorithm": "FastCC", "roi_geometry": ROI_GEOMETRY_VERSION})
    algorithm = SimpleNamespace(match=lambda probe, candidate: float(candidate[0]))
    gallery = Gallery(store, algorithm, threshold=2.0, required_metadata={"algorithm": "FastCC", "roi_geometry": ROI_GEOMETRY_VERSION})
    assert gallery.identify(np.array([0]), "noir-ir").user_id == "new"


def test_demo_gallery_excludes_previous_matcher_templates(tmp_path):
    algorithm = SimpleNamespace(name="DoN", match=lambda probe, candidate: float(candidate[0]))
    flow = DemoFlow(tmp_path, algorithm, lambda: None, roi_geometry=ROI_GEOMETRY_VERSION)
    flow.store.save("fastcc", np.array([[0]]), {"capture_profile": "noir-ir", "algorithm": "FastCC", "roi_geometry": ROI_GEOMETRY_VERSION})
    flow.store.save("oc", np.array([[0.25]]), {"capture_profile": "noir-ir", "algorithm": "OC", "roi_geometry": ROI_GEOMETRY_VERSION})
    flow.store.save("don", np.array([[1]]), {"capture_profile": "noir-ir", "algorithm": "DoN", "roi_geometry": ROI_GEOMETRY_VERSION})
    # The old matcher would win by distance if its incompatible template were used.
    assert flow.gallery.identify(np.array([0]), "noir-ir").user_id == "don"


def test_collapsed_prediction_clears_previous_roi_without_fallback():
    tracker = PKLNetTracker.__new__(PKLNetTracker)
    quad = np.array([[20, 20], [80, 20], [80, 80], [20, 80]], dtype=np.float32)
    presence = SimpleNamespace(status="tracking", quad=quad, hand_score=0.99, as_dict=lambda: {})
    tracker.detector = SimpleNamespace(submit=lambda *args: None, roi_status=lambda *args, **kwargs: presence)
    raw = np.arange(128 * 128, dtype=np.uint8).reshape(128, 128)
    predictions = iter([(raw, quad, {"roi_geometry_valid": True}), (raw, quad, {"roi_geometry_valid": False, "roi_geometry_reason": "pklnet_keypoint_span_too_small"})])
    tracker.extractor = SimpleNamespace(extract=lambda image: next(predictions))
    image = Image.new("RGB", (100, 100))
    tracker.submit(image, 1)
    assert tracker.processing_roi()[0].shape == (128, 128)
    tracker.submit(image, 2)
    status = tracker.roi_status(image.size, frame_timestamp_ms=2)
    assert status.quad is None
    assert status.status == "pklnet_error"
    assert status.reason == "pklnet_keypoint_span_too_small"
    with pytest.raises(RuntimeError, match="No PKLNet ROI"):
        tracker.processing_roi()
