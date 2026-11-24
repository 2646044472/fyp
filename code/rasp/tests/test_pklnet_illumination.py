import importlib.util

import cv2
import numpy as np
import pytest
from PIL import Image

from pklnet_roi import PKLNET_ROOT, PKLNetROI, PKLNetUnavailable


def test_enhancement_only_changes_inference_not_roi_pixels(monkeypatch):
    ext = PKLNetROI()
    assert ext.roi_geometry == 'pklnet-illumination-consistent-v5'
    spec = importlib.util.spec_from_file_location('illumination_geometry', PKLNET_ROOT/'roiExtractor.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    ext._roi_extractor = engine
    rgb = np.random.default_rng(4).integers(0, 80, (300, 400, 3), dtype=np.uint8)
    quad = np.array([[40, 40], [190, 40], [190, 190], [40, 190]], np.float32)
    seen = []
    def infer(image, **kwargs):
        seen.append(np.asarray(image))
        return np.full((64, 64), 255, np.uint8), quad, {'roi_geometry_valid': True}
    monkeypatch.setattr(ext, '_extract_aspect', infer)
    raw, actual_quad, d = ext.extract(Image.fromarray(rgb), side=64)
    np.testing.assert_array_equal(seen[0], rgb)
    np.testing.assert_array_equal(seen[1], np.rint((rgb.astype(np.float32)/255)**.6*255).astype(np.uint8))
    np.testing.assert_array_equal(raw, engine.getROIimg(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), quad, side=64))
    np.testing.assert_array_equal(actual_quad, quad)
    assert d['pklnet_roi_pixels'] == 'original'


@pytest.mark.parametrize('raises', [False, True])
def test_failed_adjusted_view_retries_original_without_accepting_failure(monkeypatch, raises):
    ext = PKLNetROI()
    image = Image.new('RGB', (400, 300), (20, 40, 60))
    original = np.asarray(image)
    seen = []
    def infer(view, **kwargs):
        seen.append(np.asarray(view))
        if len(seen)==2 and raises:
            raise PKLNetUnavailable('degenerate')
        return np.zeros((128, 128), np.uint8), np.zeros((4, 2)), {
            'roi_geometry_valid': False, 'roi_geometry_reason': 'roi_out_of_bounds'}
    monkeypatch.setattr(ext, '_extract_aspect', infer)
    _, _, d = ext.extract(image)
    assert len(seen)==2 and not np.array_equal(seen[1], original)
    np.testing.assert_array_equal(seen[0], original)
    assert not d['roi_geometry_valid']
    assert d['pklnet_illumination_view']=='original_fallback'


def test_inconsistent_but_valid_adjusted_quad_keeps_original(monkeypatch):
    ext=PKLNetROI()
    original=(np.zeros((128,128)),np.array([[0,0],[80,0],[80,80],[0,80]],np.float32),{'roi_geometry_valid':True})
    adjusted=(np.ones((128,128)),original[1]+150,{'roi_geometry_valid':True})
    results=iter([original,adjusted])
    monkeypatch.setattr(ext,'_extract_aspect',lambda *a,**k:next(results))
    raw,quad,d=ext.extract(Image.new('RGB',(400,300)))
    assert raw is original[0] and quad is original[1]
    assert d['pklnet_illumination_failure']=='illumination_localization_disagreement'
    assert d['pklnet_illumination_iou']==0
    assert [x['view'] for x in d['pklnet_roi_candidates']]==['original','gamma']
    np.testing.assert_array_equal(d['pklnet_roi_candidates'][1]['quad'],adjusted[1])


def test_explicit_v4_keeps_original_input_and_version(monkeypatch):
    ext = PKLNetROI(policy='aspect')
    assert ext.roi_geometry == 'pklnet-heatmap-aspect-v4'
    image = Image.new('RGB', (400, 300), (20, 40, 60))
    seen = []
    result = (np.zeros((128,128)), np.zeros((4,2)), {'roi_geometry_valid':True,'roi_geometry_reason':None})
    monkeypatch.setattr(ext, '_extract_once', lambda view, **kwargs: seen.append(view) or result)
    assert ext.extract(image)[0] is result[0]
    assert seen == [image]
