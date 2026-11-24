import importlib.util

import cv2
import numpy as np
from PIL import Image
import pytest

from pklnet_roi import PKLNET_ROOT, PKLNetROI, PKLNetUnavailable, ROI_GEOMETRY_VERSION


def prediction(points, valid=True, reason=None):
    points = np.asarray(points, np.float32)
    quad = np.array([[100, 200], [300, 200], [300, 400], [100, 400]], np.float32)
    return np.zeros((128, 128), np.uint8), quad, dict(
        roi_geometry_valid=valid, roi_geometry_reason=reason,
        pklnet_keypoints=points.reshape(-1).tolist(), roi_quad_full=quad.tolist(),
        pklnet_heatmap_keypoints=points.reshape(-1).tolist(),
        pklnet_heatmap_quad=quad.tolist(), roi_geometry=ROI_GEOMETRY_VERSION)


def test_retry_preserves_orientation_and_crops_original_pixels(monkeypatch):
    extractor = PKLNetROI(policy="aspect")
    spec = importlib.util.spec_from_file_location('aspect_test_geometry', PKLNET_ROOT/'roiExtractor.py')
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    extractor._roi_extractor = geometry
    image = Image.fromarray(np.random.default_rng(21).integers(0, 256, (1080, 1920, 3), dtype=np.uint8))
    first = prediction([[200, 200], [201, 200], [200, 250]], False, 'pklnet_keypoint_span_too_small')
    second = prediction([[100, 200], [300, 200], [200, 350]])
    sizes = []
    results = iter([first, second])
    def infer(view, **kwargs):
        sizes.append(view.size)
        return next(results)
    monkeypatch.setattr(extractor, '_extract_once', infer)
    raw, quad, details = extractor.extract(image)
    assert sizes == [(1920, 1080), (1440, 1080)]
    assert details['pklnet_retry_box'] == [240, 0, 1680, 1080]
    np.testing.assert_array_equal(quad, second[1] + [240, 0])
    np.testing.assert_array_equal(np.asarray(details['pklnet_keypoints']).reshape(3, 2), [[340,200],[540,200],[440,350]])
    np.testing.assert_array_equal(details['pklnet_heatmap_quad'], quad)
    expected = geometry.getROIimg(cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR), quad)
    np.testing.assert_array_equal(raw, expected)
    assert details['roi_geometry_valid']
    assert details['pklnet_full_frame_reason'] == 'pklnet_keypoint_span_too_small'
    assert details['pklnet_keypoint_span_ratio'] == pytest.approx(200/1080)


def test_valid_first_pass_is_not_changed_or_repeated(monkeypatch):
    extractor = PKLNetROI(policy="aspect")
    result = prediction([[100,200],[300,200],[200,350]])
    calls = []
    monkeypatch.setattr(extractor, '_extract_once', lambda view, **kwargs: calls.append(view.size) or result)
    actual = extractor.extract(Image.new('RGB', (1920,1080)))
    assert len(calls) == 1
    assert actual[0] is result[0] and actual[1] is result[1]
    assert not actual[2]['pklnet_aspect_retry']


def test_invalid_retry_does_not_turn_failure_into_acceptance(monkeypatch):
    extractor = PKLNetROI(policy="aspect")
    bad = prediction([[100,200],[101,200],[100,250]], False, 'pklnet_keypoint_span_too_small')
    monkeypatch.setattr(extractor, '_extract_once', lambda *args, **kwargs: (bad[0], bad[1].copy(), dict(bad[2])))
    _, _, details = extractor.extract(Image.new('RGB', (1920,1080)))
    assert not details['roi_geometry_valid']
    assert details['pklnet_retry_reason'] == 'pklnet_keypoint_span_too_small'


def test_degenerate_retry_preserves_original_failure(monkeypatch):
    extractor = PKLNetROI(policy="aspect")
    calls = []
    def infer(*args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise PKLNetUnavailable('degenerate keypoints')
        return prediction([[100,200],[101,200],[100,250]], False, 'pklnet_keypoint_span_too_small')
    monkeypatch.setattr(extractor, '_extract_once', infer)
    _, _, details = extractor.extract(Image.new('RGB', (1920,1080)))
    assert not details['roi_geometry_valid']
    assert details['pklnet_retry_error'] == 'degenerate keypoints'


@pytest.mark.parametrize('size,box', [((1920,1080),(240,0,1680,1080)), ((1080,1920),(0,240,1080,1680)),
                                     ((3280,2464),(0,0,3280,2464)), ((300,400),(0,0,300,400))])
def test_crop_keeps_short_axis_and_rotation_class(size, box):
    assert PKLNetROI._aspect_retry_box(size) == box
    assert min(box[2]-box[0], box[3]-box[1]) == min(size)
    assert (box[2]-box[0] > box[3]-box[1]) == (size[0] > size[1])


def test_historical_heatmap_keeps_v3_policy_and_single_pass(monkeypatch):
    extractor = PKLNetROI(policy='heatmap')
    assert extractor.roi_geometry == 'pklnet-heatmap-v3'
    result = prediction([[100,200],[101,200],[100,250]], False, 'pklnet_keypoint_span_too_small')
    monkeypatch.setattr(extractor, '_extract_once', lambda *args, **kwargs: result)
    assert extractor.extract(Image.new('RGB', (1920,1080))) is result
