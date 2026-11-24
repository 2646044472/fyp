"""Resource-aware candidate-first variant with one stable prepared gallery."""

from __future__ import annotations

import threading
import time

from wide_candidate_matcher import WideCandidateFirstMatcher


class WideCandidateFirstV38(WideCandidateFirstMatcher):
    """Keep the gallery cache warm and time every costly candidate stage."""

    name = "FastCCWideCandidateFirst-v38-experimental"
    candidate_pair_limit = 8
    wide_candidate_pair_limit = 16
    # v36's 256 MiB LRU evicts prepared enrollment groups that the sharded
    # index and linked stage retain anyway. Recreating them changes object IDs
    # and rebuilds the complete gallery index on later queries.
    prepared_cache_limit_bytes = 512 * 1024 * 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._candidate_profile = threading.local()

    @staticmethod
    def _record_timing(probe, name, started):
        trace = getattr(probe, "candidate_first_trace", None)
        if trace is not None:
            trace.setdefault("timings_ms", {})[name] = (time.perf_counter() - started) * 1000

    def score_gallery(self, probe, groups):
        self._candidate_profile.probe = probe
        started = time.perf_counter()
        try:
            return super().score_gallery(probe, groups)
        finally:
            self._record_timing(probe, "matcher_score_gallery_total", started)
            self._candidate_profile.probe = None

    def prepare_gallery(self, groups):
        probe = getattr(self._candidate_profile, "probe", None)
        started = time.perf_counter()
        key = self._gallery_key(groups)
        with self._index_lock:
            reused = key == self._index_key
        result = super().prepare_gallery(groups)
        trace = getattr(probe, "candidate_first_trace", None)
        if trace is not None:
            trace["gallery_index_key_reused"] = reused
            self._record_timing(probe, "gallery_prepare_during_query", started)
        return result

    def _auxiliary_scores(self, probe, groups):
        started = time.perf_counter()
        try:
            return super()._auxiliary_scores(probe, groups)
        finally:
            self._record_timing(probe, "auxiliary_gallery_score", started)

    def _stage_views(self, probe, wide):
        stage = "wide" if wide else "normal"
        self._candidate_profile.stage = stage
        started = time.perf_counter()
        try:
            return super()._stage_views(probe, wide)
        finally:
            self._record_timing(probe, f"{stage}_query_feature_views", started)

    def _rank_candidate_pairs(self, views):
        probe = getattr(self._candidate_profile, "probe", None)
        stage = getattr(self._candidate_profile, "stage", "candidate")
        started = time.perf_counter()
        try:
            return super()._rank_candidate_pairs(views)
        finally:
            self._record_timing(probe, f"{stage}_sharded_index_search", started)

    def _refine_candidates(self, probe, groups, pairs, views, proposals, selected):
        stage = getattr(self._candidate_profile, "stage", "candidate")
        started = time.perf_counter()
        try:
            return super()._refine_candidates(probe, groups, pairs, views, proposals, selected)
        finally:
            self._record_timing(probe, f"{stage}_fastcc_candidate_refinement", started)
