"""Experimental v28 retained matcher with variable lossless feature storage."""
import threading

import numpy as np

from lazy_cached_matcher import LazyCachedRetainedMatcher, Top3ConsensusLazyRetainedMatcher
from union_lossless_codec import CODEC, decode, pack
from lossless_template_store import LosslessTemplateStore, SCHEMA


class ExactFastCCPairCache:
    """Bounded query-local memo for the pure binary FastCC distance kernel."""

    def __init__(self, distance, *, max_entries=20000):
        if not callable(distance) or type(max_entries) is not int or max_entries < 0:
            raise ValueError('Invalid FastCC pair-cache configuration')
        self.distance = distance
        self.max_entries = max_entries
        self.entries = {}
        self.calls = self.hits = self.misses = self.bypassed = 0

    @staticmethod
    def _key(left, right):
        left, right = np.asarray(left), np.asarray(right)
        if left.dtype != np.bool_ or right.dtype != np.bool_ or left.shape != (32, 32) or right.shape != (32, 32):
            return None
        left_bytes = np.packbits(left, bitorder='little').tobytes()
        right_bytes = np.packbits(right, bitorder='little').tobytes()
        if right_bytes < left_bytes:
            left_bytes, right_bytes = right_bytes, left_bytes
        return left.shape, left_bytes, right_bytes

    def __call__(self, left, right):
        self.calls += 1
        key = self._key(left, right)
        if key is None:
            self.bypassed += 1
            return self.distance(left, right)
        cached = self.entries.get(key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        value = self.distance(left, right)
        if len(self.entries) < self.max_entries:
            self.entries[key] = value
        else:
            self.bypassed += 1
        return value

    def stats(self):
        return {'calls': self.calls, 'hits': self.hits, 'misses': self.misses,
                'entries': len(self.entries), 'bypassed': self.bypassed,
                'max_entries': self.max_entries}


class LosslessRetainedMatcher(LazyCachedRetainedMatcher):
    name = 'FastCCRetainedLossless-experimental'
    template_codec = CODEC
    template_storage_schema = SCHEMA
    template_store_factory = LosslessTemplateStore

    def _pack(self, legacy, png, queries, gallery):
        return pack(legacy, png, queries, gallery)

    def _unpack(self, feature, *, decode_native=True):
        return decode(feature, decode_native=decode_native).parts

    def score_gallery(self, probe, groups):
        # All comparison reuse expires with this one query. The matcher lock
        # already serializes gallery calls, including its lazy fallback scope.
        with self._lazy_query_lock:
            original = self.base.match
            cache = ExactFastCCPairCache(original)
            self.base.match = cache
            try:
                return super().score_gallery(probe, groups)
            finally:
                self.base.match = original
                self.last_exact_pair_cache_stats = cache.stats()


class Top3ConsensusLosslessRetainedMatcher(LosslessRetainedMatcher):
    """The v32 score aggregation over the existing lossless template format."""

    name = "FastCCTop3Consensus-v32-experimental"
    _aggregate = staticmethod(Top3ConsensusLazyRetainedMatcher._aggregate)
