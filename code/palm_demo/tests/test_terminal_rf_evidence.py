import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('terminal_rf_evidence')
    base=SimpleNamespace(match=lambda a,b:float(np.mean(np.asarray(a,bool)!=np.asarray(b,bool))))
    original={'a':.1,'b':.2}
    groups={user:[(np.full((32,32),value,bool),[],None,SimpleNamespace(code=np.full((32,32),value,bool))) for _ in range(5)]
        for user,value in [('a',1),('b',0)]}
    algorithm=SimpleNamespace(base=base,legacy=SimpleNamespace(base=base),_pose=SimpleNamespace(base=base),
        _retain_fastcc_evidence_pilot=True,_aggregate=lambda values:float(np.mean(sorted(values)[:2])))
    algorithm._match_unpacked=lambda probe,target,details=None:base.match(probe.code,target.code.copy())
    algorithm._legacy_pair=lambda probe,p,s,target:base.match(probe.code,target[0].copy())
    def original_score(probe,gallery):
        for user,samples in gallery.items():
            for sample in samples:
                base.match(probe.code,sample[0])
                algorithm._match_unpacked(probe,sample[3])
                algorithm._legacy_pair(probe,None,None,sample)
        if getattr(probe,'unknown',False):base.match(probe.code,np.zeros((32,32),bool))
        probe.route=probe.original_route
        if probe.route==module.ORIGINAL_TERMINAL:probe.exhaustive()
        return original
    algorithm.score_gallery=original_score
    probe=SimpleNamespace(code=np.zeros((32,32),bool),original_route='pose_confident',exhaustive=lambda:None)
    module.install(algorithm)
    return module,algorithm,groups,probe,original


def test_confident_scores_and_route_are_verbatim_with_zero_rf_or_extra_search(fixture):
    module,algorithm,groups,probe,original=fixture
    assert algorithm.score_gallery(probe,groups) is original
    assert probe.route=='pose_confident'
    trace=algorithm._terminal_rf_trace
    assert not trace['rf_applied'] and trace['rf_unique_comparisons']==0 and trace['exhaustive_callback_calls']==0
    assert trace['unknown_calls']==0 and trace['ordinary_calls']==30


def test_terminal_vector_is_independent_and_all_frame_scopes_are_retained(fixture):
    module,algorithm,groups,probe,original=fixture;probe.original_route=module.ORIGINAL_TERMINAL
    result=algorithm.score_gallery(probe,groups)
    assert result=={'a':1.,'b':0.} and result['a']>original['a']
    trace=algorithm._terminal_rf_trace
    assert trace['rf_applied'] and trace['unknown_calls']==0 and trace['captured_pairs']==10
    assert trace['rf_unique_comparisons']==2 and trace['exhaustive_callback_calls']==1
    assert probe.route==module.TERMINAL_ROUTE


def test_unknown_comparison_aborts_terminal_and_does_not_leak_to_next_request(fixture):
    module,algorithm,groups,probe,original=fixture
    callback=probe.exhaustive;probe.original_route=module.ORIGINAL_TERMINAL;probe.unknown=True
    with pytest.raises(ValueError,match='Incomplete per-frame'):algorithm.score_gallery(probe,groups)
    assert probe.exhaustive is callback
    probe.unknown=False;probe.original_route='legacy_confident'
    assert algorithm.score_gallery(probe,groups) is original
    assert algorithm._terminal_rf_trace['unknown_calls']==0


def test_mixed_distance_installation_is_rejected_and_outside_calls_keep_old_metric(fixture):
    module,algorithm,groups,probe,original=fixture
    with pytest.raises(ValueError,match='already installed'):module.install(algorithm)
    assert algorithm.base.match(np.zeros((32,32)),np.ones((32,32)))==1.
