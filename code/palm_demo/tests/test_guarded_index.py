from types import SimpleNamespace
import pytest
from guarded_index_matcher import GuardedIndexMatcher
from proposed_index_matcher import ProposedIndexMatcher
from demo_matcher import FastCCDemoMatcher


def test_uncertain_route_requires_original_fallback_and_preserves_full_scores(monkeypatch):
    algorithm=object.__new__(GuardedIndexMatcher)
    monkeypatch.setattr(ProposedIndexMatcher,'score_gallery',lambda *_: {'a':.38,'b':.39})
    with pytest.raises(ValueError,match='complete original-image'):
        algorithm.score_gallery(SimpleNamespace(),{})
    calls=[]
    probe=SimpleNamespace(exhaustive=lambda: calls.append('extracted') or 'full')
    monkeypatch.setattr(GuardedIndexMatcher,'_unpack',lambda self,f: ('decoded',f))
    def score(self,full,samples):
        assert full==('decoded','full')
        return samples[0]
    monkeypatch.setattr(FastCCDemoMatcher,'score_prepared',score)
    groups={'a':[(None,None,None,.4)],'b':[(None,None,None,.2)]}
    assert algorithm.score_gallery(probe,groups)=={'a':.4,'b':.2}
    assert calls==['extracted'] and probe.route=='exhaustive_fallback'


def test_confident_route_does_not_extract_exhaustive_query(monkeypatch):
    algorithm=object.__new__(GuardedIndexMatcher)
    monkeypatch.setattr(ProposedIndexMatcher,'score_gallery',lambda *_: {'a':.2,'b':.4})
    def unexpected():raise AssertionError('unneeded exhaustive extraction')
    assert algorithm.score_gallery(SimpleNamespace(exhaustive=unexpected),{})=={'a':.2,'b':.4}
