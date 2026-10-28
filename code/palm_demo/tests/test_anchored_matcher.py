from pathlib import Path
import cv2
import numpy as np
import pytest
from PIL import Image
from anchored_matcher import overlaps_anchor
from palm_app.biometric import load_algorithm


def algorithms():
    root=Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python'
    return [load_algorithm(root,name) for name in ['FastCCWindowUnion-v4','FastCCAnchoredUnion-v5']]


def test_background_and_boundary_touch_are_not_shared_palm_region():
    q=np.array([[20,20],[100,20],[100,100],[20,100]],np.float32)
    assert overlaps_anchor(q+10,q)
    assert not overlaps_anchor(q+200,q)
    assert not overlaps_anchor(q+[80,0],q)
    assert not overlaps_anchor(q*np.nan,q)


def test_direct_capture_and_numeric_migration_have_identical_features():
    v4,v5=algorithms();rng=np.random.default_rng(102)
    rgb=rng.integers(0,256,(400,600,3),dtype=np.uint8);full=Image.fromarray(rgb)
    q=np.array([[80,80],[200,80],[200,200],[80,200]],np.float32)
    roi=cv2.resize(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),(128,128))
    candidates=[dict(quad=q,valid=True),dict(quad=q+[300,0],valid=True,kind='window')]
    old=v4.extract_with_hypotheses(full,q,roi,candidates)
    direct=v5.extract_with_hypotheses(full,q,roi,candidates)
    migrated=v5.upgrade_v4_template(old)
    np.testing.assert_array_equal(direct,migrated)
    assert len(v5._unpack(direct)[-1])==10
    assert v5.candidate_decisions(q,candidates)[1]['reason']=='disjoint_from_anchor'
    with pytest.raises(ValueError,match='header'):v5.match(old,direct)
    assert v5.match(direct,direct)==0
    trace=v5.match_with_diagnostics(direct,direct)
    assert trace['score']==v5.match(direct,direct)
    assert trace['winner']['branch']=='legacy_v2'
    assert v5.score_enrollment(direct,[direct,migrated])==0


def test_aligned_region_guard_blocks_departure_from_anchor():
    _,v5=algorithms();q=np.array([[0,0],[384,0],[384,384],[0,384]],np.float32)
    primary=(None,None,np.eye(3))
    assert v5._accept_alignment(primary,q)
    assert not v5._accept_alignment(primary,q+500)
