"""Isolated exact-index capacity candidate; decisions may differ from FLANN."""
import numpy as np
from bounded_exact_index import BoundedExactIndex
from wide_capacity_matcher import WideCapacityLazyMatcher

class BoundedWideMatcher(WideCapacityLazyMatcher):
    name = 'FastCCBoundedExactWide-experimental'
    # Descriptor payload only; not a process memory cap.
    descriptor_budget_bytes = 768 * 1024 * 1024

    def prepare_gallery(self, groups):
        key = tuple((user, id(samples)) for user, samples in sorted(groups.items()))
        with self._index_lock:
            if key == self._index_key:
                self._prepare_enrollment_links(groups)
                return
            descriptors, mapping, positions = [], [], {}
            for user, samples in sorted(groups.items()):
                for sample, prepared in enumerate(samples):
                    positions[(user, sample)] = []
                    for view_index, view in enumerate(prepared[1]):
                        d = view[3]
                        if len(d) < 4:
                            continue
                        positions[(user, sample)].append(len(mapping))
                        mapping.append((user, sample, view_index))
                        descriptors.append(d)
            total = sum(len(d) for d in descriptors)
            index = BoundedExactIndex(descriptors, max_descriptor_bytes=self.descriptor_budget_bytes) if total >= 16 else None
            labels = np.concatenate([np.full(len(d), group, np.int32) for group, d in enumerate(descriptors)]) if descriptors else np.empty(0, np.int32)
            self._index, self._labels = index, labels
            self._mapping, self._positions = mapping, positions
            self._references, self._index_key = dict(groups), key
            self._prepare_enrollment_links(groups)
