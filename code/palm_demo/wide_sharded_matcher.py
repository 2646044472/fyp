"""Lossless bounded-size FLANN shards for wide enrollment galleries.

For galleries whose complete descriptor payload exceeds OpenCV's single-index
limit, build multiple smaller indexes and merge their local top-k results into
one global top-k list. All descriptor rows and original sample/group mappings
are retained. Multi-index search is approximate and requires a paired replay.
"""

from __future__ import annotations

import cv2
import numpy as np

from indexed_demo_matcher import INDEX_DESCRIPTOR_LIMIT_BYTES
from wide_capacity_matcher import WideCapacityLazyMatcher


DEFAULT_SHARD_BYTES = 192 * 1024 * 1024


class _ShardedFlannIndex:
    """Facade matching the small `knnMatch` surface used by staged scoring."""

    def __init__(self, shards):
        self.shards = tuple(shards)

    def knnMatch(self, query, k):
        query = np.asarray(query)
        if query.dtype != np.float32 or query.ndim != 2 or query.shape[1] != 128:
            raise ValueError("Expected float32 query descriptors with 128 columns")
        if type(k) is not int or k < 1:
            raise ValueError("Invalid nearest-neighbor count")
        candidates = [[] for _ in query]
        for shard in self.shards:
            local_k = min(k, shard["rows"])
            if local_k < 1:
                continue
            index = shard["index"]
            offsets = shard["image_offsets"]
            global_offset = shard["global_offset"]
            for query_index, matches in enumerate(index.knnMatch(query, k=local_k)):
                for match in matches:
                    if match.imgIdx < 0 or match.imgIdx >= len(offsets):
                        raise RuntimeError("FLANN returned an unknown train image")
                    train_index = global_offset + offsets[match.imgIdx] + match.trainIdx
                    candidates[query_index].append((float(match.distance), int(train_index)))
        merged = []
        for query_index, row in enumerate(candidates):
            nearest = sorted(row, key=lambda item: (item[0], item[1]))[:k]
            merged.append([cv2.DMatch(query_index, train_index, 0, distance)
                           for distance, train_index in nearest])
        return merged


class WideCapacityShardedMatcher(WideCapacityLazyMatcher):
    """64 MiB templates with complete descriptors indexed in bounded shards."""

    name = "FastCCWideSharded-v36-experimental"
    shard_bytes = DEFAULT_SHARD_BYTES
    shard_trees = 4
    search_checks = 64

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if type(self.shard_bytes) is not int or self.shard_bytes < 128 * 4 * 16:
            raise ValueError("Shard capacity must hold at least 16 descriptors")
        if type(self.shard_trees) is not int or self.shard_trees < 1:
            raise ValueError("FLANN shard tree count must be positive")
        if type(self.search_checks) is not int or self.search_checks < 1:
            raise ValueError("FLANN search checks must be positive")
        self.gallery_index_status = None

    @staticmethod
    def _gallery_key(groups):
        return tuple((user, id(samples)) for user, samples in sorted(groups.items()))

    def _make_shards(self, descriptors):
        max_rows = self.shard_bytes // (128 * np.dtype(np.float32).itemsize)
        segments, segment_rows = [], 0
        shards, global_offset = [], 0

        def train(pending, rows, offset):
            if rows < 16:
                return None
            cv2.setRNGSeed(20261028)
            index = cv2.FlannBasedMatcher(
                dict(algorithm=1, trees=self.shard_trees), dict(checks=self.search_checks))
            index.add(pending)
            index.train()
            offsets = []
            local_offset = 0
            for array in pending:
                offsets.append(local_offset)
                local_offset += len(array)
            return {"index": index, "arrays": tuple(pending),
                    "image_offsets": tuple(offsets), "global_offset": offset,
                    "rows": rows}

        for array in descriptors:
            if array.dtype != np.float32 or array.ndim != 2 or array.shape[1] != 128:
                raise ValueError("Expected float32 gallery descriptors with 128 columns")
            start = 0
            while start < len(array):
                take = min(max_rows - segment_rows, len(array) - start)
                piece = array[start:start + take]
                if take:
                    segments.append(piece)
                    segment_rows += take
                    start += take
                if segment_rows == max_rows:
                    shard = train(segments, segment_rows, global_offset)
                    if shard is not None:
                        shards.append(shard)
                    global_offset += segment_rows
                    segments, segment_rows = [], 0
        if segment_rows:
            shard = train(segments, segment_rows, global_offset)
            if shard is not None:
                shards.append(shard)
        return shards

    def prepare_gallery(self, groups):
        key = self._gallery_key(groups)
        with self._index_lock:
            if key == self._index_key:
                self._prepare_enrollment_links(groups)
                return

        descriptors, mapping, positions = [], [], {}
        for user, samples in sorted(groups.items()):
            for sample_index, sample in enumerate(samples):
                key_pair = (user, sample_index)
                positions[key_pair] = []
                for view_index, view in enumerate(sample[1]):
                    descriptor = view[3]
                    if len(descriptor) < 4:
                        continue
                    group_index = len(mapping)
                    mapping.append((user, sample_index, view_index))
                    positions[key_pair].append(group_index)
                    descriptors.append(descriptor)

        descriptor_bytes = sum(int(array.nbytes) for array in descriptors)
        if descriptor_bytes <= INDEX_DESCRIPTOR_LIMIT_BYTES:
            super().prepare_gallery(groups)
            self.gallery_index_status = {
                "backend": "single_flann",
                "reason": None,
                "descriptor_bytes": descriptor_bytes,
                "limit_bytes": INDEX_DESCRIPTOR_LIMIT_BYTES,
                "shard_bytes": self.shard_bytes,
                "descriptors_dropped": 0,
            }
            return

        shards = self._make_shards(descriptors)
        labels = np.empty(sum(len(array) for array in descriptors), np.int32)
        # Mapping entries are view-level groups; each descriptor row inherits
        # its originating view's group label in the same global row order.
        cursor = 0
        for group_index, (user, sample_index, view_index) in enumerate(mapping):
            descriptor = groups[user][sample_index][1][view_index][3]
            labels[cursor:cursor + len(descriptor)] = group_index
            cursor += len(descriptor)
        if cursor != len(labels):
            raise RuntimeError("Sharded gallery label count does not cover all descriptors")

        with self._index_lock:
            self._index = _ShardedFlannIndex(shards) if shards else None
            self._labels = labels
            self._mapping = mapping
            self._positions = positions
            self._references = dict(groups)
            self._index_key = self._gallery_key(groups)
            self.gallery_index_status = {
                "backend": "lossless_flann_shards" if shards else "no_index_small_gallery",
                "reason": "descriptor_payload_exceeds_single_flann_limit",
                "descriptor_bytes": descriptor_bytes,
                "limit_bytes": INDEX_DESCRIPTOR_LIMIT_BYTES,
                "shard_bytes": self.shard_bytes,
                "shard_count": len(shards),
                "shard_rows": [int(shard["rows"]) for shard in shards],
                "descriptors_dropped": 0,
            }
        self._prepare_enrollment_links(groups)
