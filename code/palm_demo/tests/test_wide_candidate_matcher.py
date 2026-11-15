import threading
from concurrent.futures import ThreadPoolExecutor
import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from staged_index_matcher import StagedIndexMatcher
from wide_candidate_matcher import WideCandidateFirstMatcher
from wide_candidate_matcher_v38 import WideCandidateFirstV38
from wide_candidate_matcher_v39 import WideCandidateFirstV39
from wide_candidate_matcher_v40 import WideCandidateFirstV40
from wide_candidate_matcher_v41 import WideCandidateFirstV41
from wide_candidate_matcher_v43 import WideCandidateFirstV43
from wide_candidate_matcher_v44 import WideCandidateFirstV44


class TinyIndex:
    def knnMatch(self, descriptors, k):
        # Two query descriptors vote for group 0; the third votes for group 1.
        rows = [[SimpleNamespace(distance=0.05, trainIdx=0),
                 SimpleNamespace(distance=0.06, trainIdx=1)] for _ in range(len(descriptors))]
        return rows


def test_index_votes_are_aggregated_by_enrollment_frame():
    matcher = object.__new__(WideCandidateFirstMatcher)
    matcher._index_lock = threading.RLock()
    matcher._index = TinyIndex()
    matcher._labels = np.asarray([0, 1], dtype=np.int32)
    matcher._mapping = [("hand-a", 2, 0), ("hand-b", 0, 1)]
    views = [(np.eye(3), np.zeros((3, 2)), np.zeros((3, 128), np.float32))]

    ranked, proposals, votes = matcher._rank_candidate_pairs(views)

    assert ranked == [("hand-a", 2), ("hand-b", 0)]
    assert votes[("hand-a", 2)] > votes[("hand-b", 0)]
    assert proposals[0][0] == {0, 1, 2}
    assert proposals[0][1] == {0, 1, 2}


def test_candidate_refinement_can_return_without_full_gallery_legacy_scoring():
    with ThreadPoolExecutor(max_workers=1) as workers:
        matcher = object.__new__(WideCandidateFirstMatcher)
        matcher._workers = workers
        matcher._index_lock = threading.RLock()
        matcher._index = object()
        matcher.base = SimpleNamespace(match=lambda probe, target: float(target),
                                       extract=lambda pixels: pixels)
        matcher._aggregate = lambda values: float(min(values))
        matcher._stage_views = lambda probe, wide: [(None, None, None)]
        matcher._auxiliary_scores = lambda probe, groups: None
        matcher.prepare_gallery = lambda groups: None
        matcher._rank_candidate_pairs = lambda views: (
            [("true", 0)], [{}], {("true", 0): 1.0})

        def refine(probe, groups, pairs, views, proposals, selected):
            pairs[("true", 0)] = 0.15
            return len(selected)

        matcher._refine_candidates = refine
        probe = SimpleNamespace(bank=np.asarray([[[1]]]), native=None, source=None)
        groups = {"true": [(0.4,)], "other": [(0.45,)]}

        scores = matcher.score_gallery(probe, groups)

    assert scores == {"true": 0.15, "other": 0.45}
    assert probe.route == "candidate_first_normal_index_confident"
    assert probe.candidate_first_trace["normal_candidate_pairs_refined"] == 1
    assert probe.candidate_first_trace["full_gallery_fallback"] is False
    assert probe.candidate_first_trace["terminal_route"] == probe.route


def test_candidate_uncertainty_keeps_the_complete_gallery_as_fallback(monkeypatch):
    from lazy_cached_matcher import LazyCachedRetainedMatcher

    fallback_calls = []
    monkeypatch.setattr(LazyCachedRetainedMatcher, "score_gallery",
                        lambda self, probe, groups: fallback_calls.append((probe, groups)) or {"fallback": 0.2})
    with ThreadPoolExecutor(max_workers=1) as workers:
        matcher = object.__new__(WideCandidateFirstMatcher)
        matcher._workers = workers
        matcher._index_lock = threading.RLock()
        matcher._index = object()
        matcher.base = SimpleNamespace(match=lambda probe, target: float(target))
        matcher._aggregate = lambda values: float(min(values))
        matcher._stage_views = lambda probe, wide: [(None, None, None)]
        matcher._auxiliary_scores = lambda probe, groups: None
        matcher.prepare_gallery = lambda groups: None
        matcher._rank_candidate_pairs = lambda views: ([], [{}], {})
        matcher._refine_candidates = lambda *args: 0
        matcher.confident = lambda scores: False
        probe = SimpleNamespace(bank=np.asarray([[[1]]]), native=None, source=None)
        groups = {"a": [(0.4,)], "b": [(0.45,)]}

        scores = matcher.score_gallery(probe, groups)

    assert scores == {"fallback": 0.2}
    assert fallback_calls == [(probe, groups)]
    assert probe.candidate_first_trace["full_gallery_fallback"] is True


def test_v38_bounds_candidate_work_and_keeps_all_prepared_hands_cached():
    assert WideCandidateFirstV38.candidate_pair_limit == 8
    assert WideCandidateFirstV38.wide_candidate_pair_limit == 16
    assert WideCandidateFirstV38.prepared_cache_limit_bytes == 512 * 1024 * 1024
    assert issubclass(WideCandidateFirstV38, WideCandidateFirstMatcher)


def test_v39_skips_duplicate_wide_stage_and_bounds_query_reuse_memory():
    assert WideCandidateFirstV39.candidate_pair_limit == 8
    assert WideCandidateFirstV39.wide_candidate_pair_limit == 0
    assert WideCandidateFirstV39.exact_reuse_limit_bytes == 64 * 1024 * 1024
    assert WideCandidateFirstV39.prepared_cache_limit_bytes == 512 * 1024 * 1024


def test_v40_disables_query_local_memo_storage():
    assert WideCandidateFirstV40.exact_reuse_limit_bytes == 0
    assert WideCandidateFirstV40.candidate_pair_limit == 8
    assert WideCandidateFirstV40.prepared_cache_limit_bytes == 512 * 1024 * 1024


def test_v41_uses_two_tree_shards_with_unchanged_search_checks(monkeypatch):
    assert WideCandidateFirstV41.shard_trees == 2
    assert WideCandidateFirstV41.search_checks == 64
    calls = []

    class Index:
        def add(self, arrays):
            self.arrays = arrays

        def train(self):
            return None

    def create(index_params, search_params):
        calls.append((index_params, search_params))
        return Index()

    monkeypatch.setattr("wide_sharded_matcher.cv2.FlannBasedMatcher", create)
    matcher = object.__new__(WideCandidateFirstV41)
    matcher.shard_bytes = 16 * 128 * 4
    matcher.shard_trees = WideCandidateFirstV41.shard_trees
    matcher.search_checks = WideCandidateFirstV41.search_checks
    matcher._make_shards([np.zeros((16, 128), dtype=np.float32)])
    assert calls == [({"algorithm": 1, "trees": 2}, {"checks": 64})]


def test_v43_expands_only_the_normal_candidate_shortlist():
    assert issubclass(WideCandidateFirstV43, WideCandidateFirstV41)
    assert WideCandidateFirstV43.candidate_pair_limit == 16
    assert WideCandidateFirstV43.wide_candidate_pair_limit == WideCandidateFirstV41.wide_candidate_pair_limit == 0
    assert WideCandidateFirstV43.shard_trees == WideCandidateFirstV41.shard_trees == 2
    assert WideCandidateFirstV43.search_checks == WideCandidateFirstV41.search_checks == 64


def test_v44_candidate_early_stop_uses_loaded_fastcc_policy_only_for_accepts():
    from acceptance_policy import AcceptancePolicy

    matcher = object.__new__(WideCandidateFirstV44)
    matcher.candidate_early_policy = AcceptancePolicy({
        "version": 1,
        "name": "test-fixed-policy",
        "profiles": {"fastcc": {"max_distance": 0.32, "min_margin": 0.02}},
    })
    route = "candidate_first_normal_index_confident"
    assert WideCandidateFirstV44.candidate_pair_limit == 16
    assert matcher._policy_candidate_decision({"a": 0.20, "b": 0.25}, route)["would_accept"]
    assert matcher._policy_candidate_decision({"a": 0.33, "b": 0.40}, route)["status"] == "UNKNOWN"
    assert matcher._policy_candidate_decision({"a": 0.20, "b": 0.21}, route)["status"] == "RETRY"


def test_v38_is_reachable_from_both_algorithm_factories(monkeypatch):
    baseline = Path(__file__).resolve().parents[1] / "vendor" / "palmprint-recognition-python"
    monkeypatch.setattr(WideCandidateFirstV38, "__init__",
                        lambda self, base: setattr(self, "test_base", base))
    for module_name in ("biometric", "palm_app.biometric"):
        factory = importlib.import_module(module_name)
        for name, expected_type in (
                ("FastCCWideCandidateFirst-v38-experimental", WideCandidateFirstV38),
                ("FastCCWideCandidateFirst-v39-experimental", WideCandidateFirstV39),
                ("FastCCWideCandidateFirst-v40-experimental", WideCandidateFirstV40),
                ("FastCCWideCandidateFirst-v41-experimental", WideCandidateFirstV41),
                ("FastCCWideCandidateFirst-v43-experimental", WideCandidateFirstV43),
                ("FastCCWideCandidateFirst-v44-experimental", WideCandidateFirstV44)):
            matcher = factory.load_algorithm(baseline, name)
            assert type(matcher) is expected_type
            assert matcher.name == name
            assert hasattr(matcher, "test_base")
