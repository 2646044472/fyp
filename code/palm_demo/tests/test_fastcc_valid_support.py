import importlib
from pathlib import Path
import cv2,numpy as np,pytest


@pytest.fixture
def support(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('fastcc_valid_support')


def test_all_valid_crop_excludes_only_filter_boundary(support):
    mask,info=support.propagate_support((128,128),[(np.eye(3),(128,128))])
    np.testing.assert_array_equal(mask,support.constant_rf_mask())
    assert info['valid_pixels']==128*128 and info['valid_features']==784


def test_real_warp_padding_and_filter_footprint_are_propagated(support):
    matrix=np.asarray([[1.,0,16],[0,1,0],[0,0,1]])
    mask,info=support.propagate_support((128,128),[(matrix,(128,128))])
    assert info['invalid_pixels']==16*128
    assert not mask[:,:6].any() and mask[2:30,6:30].all()
    # Black intensity is irrelevant: geometric source support is a separate plane.
    full,_=support.propagate_support((128,128),[(np.eye(3),(128,128))],np.ones((128,128)))
    assert full.sum()==784


def test_multistep_rotation_support_matches_actual_raster_chain(support):
    first=np.vstack([cv2.getRotationMatrix2D((64,64),23,1),[0,0,1]])
    second=np.asarray([[1.,.15,0],[.05,1,0],[.001,0,1]])
    mask,info=support.propagate_support((128,128),[(first,(128,128)),(second,(128,128))])
    raw=cv2.warpPerspective(np.ones((128,128),np.float32),first,(128,128))
    raw=cv2.warpPerspective(raw,second,(128,128));valid=(raw>=1-4*np.finfo(np.float32).eps).astype(np.uint8)
    expected=cv2.erode(valid,np.ones((17,17),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)[::4,::4]
    np.testing.assert_array_equal(mask,expected)
    assert 0<info['valid_features']<784


def test_invalid_agreement_can_artificially_reduce_ordinary_distance(support):
    left=np.zeros((32,32),bool);right=np.zeros_like(left);valid=support.constant_rf_mask();right[valid]=True
    grid=support.compare_codes(left,right,valid,valid)
    assert grid['supported_score']==1
    assert grid['original_score']<1 and grid['original_winners'][0]['invalid_agreements']>0


def test_vectorized_supported_distance_matches_all_shift_oracle(support):
    rng=np.random.default_rng(76);kernel=support.ReceptiveFieldFastCC();valid=support.constant_rf_mask()
    for _ in range(12):
        left=rng.integers(0,2,(32,32),dtype=np.uint8);right=rng.integers(0,2,(32,32),dtype=np.uint8)
        assert kernel.match(left,right)==support.compare_codes(left,right,valid,valid)['supported_score']
