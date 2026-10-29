import numpy as np
import pytest
from types import SimpleNamespace
from quality_evidence_matcher import weighted_distances,quality_bank,QualityEvidenceMatcher


@pytest.mark.parametrize('initial,weighted,replace', [
    ([.2,.45],[.1,.5],False),
    ([.34,.39],[.30,.35],False),
    ([.34,.39],[.20,.45],True),
])
def test_rescue_keeps_metrics_separate(monkeypatch,initial,weighted,replace):
    import quality_evidence_matcher as module
    monkeypatch.setattr(module.PooledEnrollmentMatcher,'_enrollment_link_stage',lambda *args:None)
    matcher=QualityEvidenceMatcher.__new__(QualityEvidenceMatcher)
    matcher.base=SimpleNamespace(_difference=None)
    bank=(np.ones((1,32,32)),np.ones((1,32,32)))
    groups={u:[(None,None,None,None,bank)] for u in ('a','b')}
    pairs={('a',0):initial[0],('b',0):initial[1]}
    probe=SimpleNamespace(native=None,source=None)
    calls=[]
    monkeypatch.setattr(module,'quality_bank',lambda *args:bank)
    def distances(*args):
        calls.append(True)
        return np.asarray(weighted)
    monkeypatch.setattr(module,'weighted_distances',distances)
    matcher._enrollment_link_stage(probe,groups,pairs)
    assert list(pairs.values()) == (weighted if replace else initial)
    assert bool(calls) == (initial[0]>.32)
    assert getattr(probe,'link_stage_route',None) == ('quality_evidence_confident' if replace else None)


def test_weighted_matrix_matches_direct_overlap_definition():
    rng=np.random.default_rng(24)
    qs=rng.choice([-1.,1.],(2,32,32));gs=rng.choice([-1.,1.],(3,32,32))
    qw=rng.random(qs.shape);gw=rng.random(gs.shape)
    qw[:,:2]=0;gw[:,:2]=0
    expected=np.ones(3)
    for i in range(3):
        for pose in range(2):
            for dy in range(-4,5):
                for dx in range(-4,5):
                    a=(slice(max(-dy,0),32-max(dy,0)),slice(max(-dx,0),32-max(dx,0)))
                    b=(slice(max(dy,0),32-max(-dy,0)),slice(max(dx,0),32-max(-dx,0)))
                    w=qw[pose][a]*gw[i][b]
                    value=np.sum(w*(qs[pose][a]!=gs[i][b]))/w.sum()
                    expected[i]=min(expected[i],value)
    np.testing.assert_allclose(weighted_distances((qs,qw),(gs,gw)),expected,atol=1e-14,rtol=0)


def test_weighted_distance_has_no_support_fallback_and_identical_code_zero():
    ones=np.ones((1,32,32));zero=np.zeros_like(ones)
    np.testing.assert_array_equal(weighted_distances((ones,zero),(ones,ones)),[1.])
    np.testing.assert_array_equal(weighted_distances((ones,ones),(ones,ones)),[0.])


def test_quality_bank_rejects_out_of_frame_and_masks_kernel_border():
    native=np.random.default_rng(1).integers(0,256,(640,640),dtype=np.uint8)
    kernel=np.ones((17,17));kernel[8,8]=-288
    source=np.asarray([[1.,0,-128],[0,1.,-128],[0,0,1.]])
    bank=quality_bank(native,source,kernel,[(0,1)])
    assert bank is not None
    weights=bank[1]
    assert not weights[:,:2].any() and not weights[:,-2:].any()
    assert not weights[:,:,:2].any() and not weights[:,:,-2:].any()
    assert quality_bank(native,np.asarray([[1.,0,1000],[0,1.,1000],[0,0,1.]]),kernel,[(0,1)]) is None
    assert QualityEvidenceMatcher.requires_exhaustive_fallback
