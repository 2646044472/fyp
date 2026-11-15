"""Keep complete wide-capacity features when one global index will not fit.

This opt-in matcher retains the 64 MiB enrollment representation and the
existing staged/exhaustive scorer. When the descriptor payload exceeds the
single-FLANN limit, it skips building that index and lets uncertain queries
use the existing complete original-image fallback; it never trims descriptors.
"""

import numpy as np

from indexed_demo_matcher import INDEX_DESCRIPTOR_LIMIT_BYTES
from wide_capacity_matcher import WideCapacityLazyMatcher


class WideCapacityFallbackMatcher(WideCapacityLazyMatcher):
    name = "FastCCWideFallback-v35-experimental"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gallery_index_status = None

    @staticmethod
    def _gallery_key(groups):
        return tuple((user, id(samples)) for user, samples in sorted(groups.items()))

    @staticmethod
    def _descriptor_bytes(groups):
        return sum(int(view[3].nbytes)
                   for samples in groups.values()
                   for sample in samples
                   for view in sample[1]
                   if len(view[3]) >= 4)

    def _disable_oversized_index(self, groups, descriptor_bytes):
        # Preserve the group snapshots and cache key even though this gallery
        # has no index, so later queries do not retry the same failed build.
        with self._index_lock:
            self._index = None
            self._labels = np.empty(0, np.int32)
            self._mapping = []
            self._positions = {}
            self._references = dict(groups)
            self._index_key = self._gallery_key(groups)
            self.gallery_index_status = {
                "backend": "complete_exhaustive_fallback",
                "reason": "descriptor_payload_exceeds_single_flann_limit",
                "descriptor_bytes": int(descriptor_bytes),
                "limit_bytes": INDEX_DESCRIPTOR_LIMIT_BYTES,
                "descriptors_dropped": 0,
            }
        self._prepare_enrollment_links(groups)

    def prepare_gallery(self, groups):
        key = self._gallery_key(groups)
        with self._index_lock:
            if key == self._index_key:
                self._prepare_enrollment_links(groups)
                return

        descriptor_bytes = self._descriptor_bytes(groups)
        if descriptor_bytes > INDEX_DESCRIPTOR_LIMIT_BYTES:
            self._disable_oversized_index(groups, descriptor_bytes)
            return

        result = super().prepare_gallery(groups)
        self.gallery_index_status = {
            "backend": "single_flann" if self._index is not None else "no_index_small_gallery",
            "reason": None,
            "descriptor_bytes": descriptor_bytes,
            "limit_bytes": INDEX_DESCRIPTOR_LIMIT_BYTES,
            "descriptors_dropped": 0,
        }
        return result
