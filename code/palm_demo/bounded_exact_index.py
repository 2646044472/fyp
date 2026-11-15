"""Bounded exact nearest neighbours for oversized galleries.

This is not FLANN: exact neighbours can differ from approximate FLANN results.
Only an explicitly named experimental matcher may use this index. All original
descriptor rows and their global indices are retained, without quantisation.
"""
import cv2
import numpy as np


class BoundedExactIndex:
    def __init__(self, arrays, *, shard_rows=8192, query_rows=32, checkpoint=None, max_descriptor_bytes=None):
        if type(shard_rows) is not int or shard_rows < 1 or type(query_rows) is not int or query_rows < 1:
            raise ValueError('Invalid index batch dimensions')
        # OpenCV BFMatcher requires each training matrix to have < 2**18 rows.
        if shard_rows >= (1 << 18):
            raise ValueError('Index shard exceeds OpenCV row limit')
        self.arrays = tuple(np.asarray(a) for a in arrays)
        if any(a.dtype != np.float32 or a.ndim != 2 or a.shape[1] != 128 for a in self.arrays):
            raise ValueError('Expected float32 descriptors with 128 columns')
        self.total = sum(len(a) for a in self.arrays)
        # This is a logical payload limit, not a process RSS bound.
        self.descriptor_bytes = sum(a.nbytes for a in self.arrays)
        if max_descriptor_bytes is not None:
            if type(max_descriptor_bytes) is not int or max_descriptor_bytes < 0:
                raise ValueError('Invalid descriptor byte budget')
            if self.descriptor_bytes > max_descriptor_bytes:
                raise ValueError('Descriptor byte budget exceeded')
        self.shard_rows, self.query_rows = shard_rows, query_rows
        self.checkpoint = checkpoint or (lambda: None)

    def knnMatch(self, query, k):
        query = np.asarray(query)
        if query.dtype != np.float32 or query.ndim != 2 or query.shape[1] != 128:
            raise ValueError('Invalid query descriptors')
        if type(k) is not int or k < 1 or self.total < k:
            raise ValueError('Insufficient descriptors or invalid k')
        output = []
        for start in range(0, len(query), self.query_rows):
            part = np.ascontiguousarray(query[start:start+self.query_rows])
            best = [[] for _ in part]
            offset = 0
            matcher = cv2.BFMatcher(cv2.NORM_L2)
            for array in self.arrays:
                for first in range(0, len(array), self.shard_rows):
                    self.checkpoint()
                    shard = np.ascontiguousarray(array[first:first+self.shard_rows])
                    for i, matches in enumerate(matcher.knnMatch(part, shard, k=min(k, len(shard)))):
                        best[i].extend((m.distance, offset + first + m.trainIdx) for m in matches)
                        best[i] = sorted(best[i])[:k]
                    self.checkpoint()
                offset += len(array)
            output.extend([[cv2.DMatch(start+i, index, float(distance)) for distance, index in row]
                           for i, row in enumerate(best)])
        return output
