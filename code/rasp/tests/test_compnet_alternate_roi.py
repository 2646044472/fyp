from types import SimpleNamespace
import numpy as np
import pytest
from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher


def fixture():
    matcher=CompNetAlternateROIMatcher.__new__(CompNetAlternateROIMatcher)
    matcher.geometry=SimpleNamespace(isAntiClock=lambda p:False)
    a=np.zeros(512,np.float32);a[0]=1;b=np.zeros(512,np.float32);b[1]=1
    uncertain=(a+b)/np.sqrt(2)
    calls=[]
    def embedding(native,source):
        calls.append(source.copy())
        return uncertain if np.array_equal(source,np.eye(3)) else a
    matcher._embedding=embedding
    sample=lambda v:(None,None,None,None,None,v)
    groups={'a':[sample(a),sample(a)],'b':[sample(b),sample(b)]}
    quad=lambda x:[[x,100],[x+384,100],[x+384,484],[x,484]]
    probe=SimpleNamespace(native=np.zeros((900,900),np.uint8),source=np.eye(3),
        localization_candidates=[dict(valid=True,quad=quad(100))])
    return matcher,groups,probe,calls,a,b


def test_available_alternate_roi_can_supply_separate_global_evidence():
    matcher,groups,probe,calls,a,b=fixture()
    scores=matcher._auxiliary_scores(probe,groups)
    assert matcher.confident(scores) and min(scores,key=scores.get)=='a'
    assert probe.auxiliary_route=='compnet_alternate_roi_confident'
    assert len(calls)==2


def test_confident_original_skips_alternate_and_missing_diagnostics():
    matcher,groups,probe,calls,a,b=fixture();matcher._embedding=lambda *args:a
    del probe.localization_candidates
    assert matcher._auxiliary_scores(probe,groups)['a']==0
    assert not hasattr(probe,'auxiliary_route')


def test_identical_primary_and_disjoint_roi_do_not_add_inference():
    matcher,groups,probe,calls,a,b=fixture()
    probe.localization_candidates=[dict(valid=True,quad=[[0,0],[384,0],[384,384],[0,384]]),
        dict(valid=True,quad=[[500,500],[884,500],[884,884],[500,884]])]
    scores=matcher._auxiliary_scores(probe,groups)
    assert not matcher.confident(scores) and len(calls)==1


def test_conflicting_alternates_keep_original_uncertain_evidence():
    matcher,groups,probe,calls,a,b=fixture()
    original=matcher._embedding
    matcher._embedding=lambda native,s:b if np.isclose(s[0,2],-150) else original(native,s)
    probe.localization_candidates.append(dict(valid=True,quad=[[150,100],[534,100],[534,484],[150,484]]))
    scores=matcher._auxiliary_scores(probe,groups)
    assert not matcher.confident(scores) and not hasattr(probe,'auxiliary_route')


def test_uncertain_original_requires_base_diagnostics_and_valid_geometry():
    matcher,groups,probe,calls,a,b=fixture()
    probe.localization_candidates=[]
    with pytest.raises(ValueError,match='base localization'):matcher._auxiliary_scores(probe,groups)
    probe.localization_candidates=[dict(valid=True,quad=[[0,0]])]
    with pytest.raises(ValueError,match='Invalid alternate'):matcher._auxiliary_scores(probe,groups)


def test_single_identity_does_not_run_the_encoder():
    matcher,groups,probe,calls,a,b=fixture()
    assert matcher._auxiliary_scores(probe,{'a':groups['a']}) is None
    assert calls==[]
