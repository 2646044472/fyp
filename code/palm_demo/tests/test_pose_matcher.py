from types import SimpleNamespace

import numpy as np
from PIL import Image
import pytest

from biometric import score_probe
from pose_matcher import FastCCPoseMatcher, POSES
from palm_app.biometric import load_algorithm
from pathlib import Path


def bank(value):
    result=np.full((len(POSES),32,32),-1,np.int8)
    result[0]=value
    return result


def fake_matcher():
    return FastCCPoseMatcher(SimpleNamespace(match=lambda a,b:float(np.mean(a!=b))))


def test_optional_invalid_poses_do_not_become_all_true_features():
    matcher=fake_matcher()
    assert matcher.match(bank(0),bank(1))==1


def test_query_pose_search_uses_only_original_gallery_pose():
    matcher=fake_matcher();probe=bank(0);candidate=bank(1)
    candidate[1]=0
    assert matcher.match(probe,candidate)==1
    probe[2]=1
    assert matcher.match(probe,candidate)==0


def test_versioned_nearest_enrollment_hook_is_used():
    matcher=fake_matcher();templates=np.stack([bank(0)]+[bank(1)]*4)
    assert score_probe(matcher,bank(0),templates)==0


def test_malformed_or_old_templates_are_rejected():
    matcher=fake_matcher()
    with pytest.raises(ValueError,match='shape'):matcher.match(np.zeros((32,32)),bank(0))
    broken=bank(0);broken[1,0,0]=0
    with pytest.raises(ValueError,match='Partially'):matcher.match(broken,bank(0))


def test_original_pixels_and_optional_boundary_flags():
    matcher=load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python','FastCCPoseNearest-v1')
    image=Image.fromarray(np.random.default_rng(52).integers(0,255,(200,200,3),dtype=np.uint8))
    roi=np.random.default_rng(53).integers(0,255,(128,128),dtype=np.uint8)
    quad=np.array([[0,0],[128,0],[128,128],[0,128]],np.float32)
    result=matcher.extract_with_context(image,quad,roi)
    np.testing.assert_array_equal(result[0],matcher.base.extract(roi))
    assert result.shape==(9,32,32) and result.dtype==np.int8
    assert any((p==-1).all() for p in result[1:])
    matcher._validate(result)
