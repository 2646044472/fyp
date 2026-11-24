import importlib,threading
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import numpy as np,pytest
from staged_index_matcher import StagedIndexMatcher


@pytest.fixture
def pilot(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('retained_evidence_pilot')


def test_per_frame_merge_preserves_both_disjoint_good_views(pilot):
    before={('u',0):.2,('u',1):.9,('u',2):.8};after={('u',0):.9,('u',1):.2,('u',2):.8}
    value=pilot.merge_frame_evidence(before,after)
    assert np.mean(sorted(value.values())[:2])==.2
    assert before[('u',1)]==.9 and after[('u',0)]==.9


def test_changed_frame_set_or_invalid_distance_aborts(pilot):
    with pytest.raises(ValueError,match='Frame set'):pilot.merge_frame_evidence({('u',0):.2},{('u',1):.2})
    with pytest.raises(ValueError,match='distance'):pilot.merge_frame_evidence({('u',0):float('nan')},{('u',0):.2})


def test_actual_terminal_patch_fixes_discarded_evidence_without_new_threshold(pilot):
    installed=pilot.install_retained_evidence_pilot()
    class Fake:
        confident=staticmethod(StagedIndexMatcher.confident)
        _aggregate=staticmethod(lambda v:float(np.mean(sorted(v)[:2])))
        prepare_gallery=lambda self,g:None
        _legacy_probe=lambda self,p:(None,None)
        _legacy_pair=lambda self,p,a,b,t:t[0]
        _unpack=lambda self,value:value
        _match_unpacked=lambda self,query,target:target
    fake=Fake();fake.base=SimpleNamespace(match=lambda probe,value:value);fake._index=None;fake._index_lock=threading.RLock()
    groups={'true':[(.3084353298611111,None,None,.3876953125)]*5,'wrong':[(.3836000504032258,None,None,.3836000504032258)]*5}
    def probe():return SimpleNamespace(bank=np.zeros((1,1,1)),exhaustive=lambda:'full')
    try:
        with ThreadPoolExecutor(max_workers=2)as pool:
            fake._workers=pool;fake._retain_fastcc_evidence_pilot=False
            baseline=StagedIndexMatcher.score_gallery(fake,probe(),groups)
            fake._retain_fastcc_evidence_pilot=True
            result=StagedIndexMatcher.score_gallery(fake,probe(),groups)
        assert min(baseline,key=baseline.get)=='wrong'
        assert min(result,key=result.get)=='true'
        assert result['wrong']==baseline['wrong']
        assert not fake.confident(result)  # the existing .08 margin is unchanged
    finally:StagedIndexMatcher.score_gallery=installed['original']
