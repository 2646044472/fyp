"""Experimental sequential FLANN shards; not wired into a demo matcher.

Each query builds and frees one bounded index at a time. Sharded approximate
search can return different neighbours from a single FLANN index, so this is
an algorithm experiment, not a byte-identical v28 replacement.
"""
import gc

import cv2
import numpy as np


class StreamingFlannPilot:
    def __init__(self, descriptors, *, shard_bytes=8 * 1024 * 1024, checkpoint=None, allow_approximate=False):
        if type(shard_bytes) is not int or shard_bytes < 128 * 4:
            raise ValueError('Invalid shard capacity')
        self.arrays = tuple(np.asarray(a) for a in descriptors)
        if any(a.dtype != np.float32 or a.ndim != 2 or a.shape[1] != 128 for a in self.arrays):
            raise ValueError('Expected float32 descriptors with 128 columns')
        self.rows = sum(len(a) for a in self.arrays)
        self.shard_rows = shard_bytes // (128 * 4)
        if type(allow_approximate) is not bool:
            raise ValueError('Expected an explicit boolean approximation opt-in')
        if self.rows > self.shard_rows and not allow_approximate:
            raise ValueError('Multiple FLANN shards may change neighbours; experimental opt-in required')
        self.checkpoint = checkpoint or (lambda: None)

    def _shards(self):
        pending = []
        count = offset = 0
        for array in self.arrays:
            pos = 0
            while pos < len(array):
                take = min(self.shard_rows - count, len(array) - pos)
                pending.append(array[pos:pos + take]); count += take; pos += take
                if count == self.shard_rows:
                    yield offset, np.concatenate(pending)
                    offset += count; count = 0; pending = []
        if count:
            yield offset, np.concatenate(pending)

    def knnMatch(self, query, k):
        query = np.asarray(query)
        if query.dtype != np.float32 or query.ndim != 2 or query.shape[1] != 128:
            raise ValueError('Invalid query descriptors')
        if type(k) is not int or k < 1 or self.rows < k:
            raise ValueError('Insufficient descriptors or invalid k')
        best = [[] for _ in query]
        for offset, packed in self._shards():
            self.checkpoint()
            cv2.setRNGSeed(20261028)
            index = cv2.FlannBasedMatcher(dict(algorithm=1, trees=4), dict(checks=64))
            index.add([packed]); index.train()
            self.checkpoint()
            for i, matches in enumerate(index.knnMatch(query, k=min(k, len(packed)))):
                best[i].extend((m.distance, offset + m.trainIdx) for m in matches)
                best[i] = sorted(best[i])[:k]
            del index, packed
            gc.collect()
            self.checkpoint()
        return [[cv2.DMatch(i, index, float(distance)) for distance, index in matches]
                for i, matches in enumerate(best)]
