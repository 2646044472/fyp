"""Opt-in AKAZE development candidate; no production default changes.

The existing numeric envelope stores 61 binary bytes losslessly as float32,
zero-padded to 128 columns. A distinct outer magic prevents SIFT template reuse.
"""
import cv2
import numpy as np
from demo_matcher import FastCCDemoMatcher
from fastcc_accelerated import AcceleratedFastCC
from registered_matcher import MAX_POINTS
from registration_accelerated import estimate_pairs


def akaze_features(pixels):
    keys, descriptors = cv2.AKAZE_create().detectAndCompute(pixels, None)
    if descriptors is None:
        return np.empty((0, 2), np.float32), np.empty((0, 128), np.float32)
    if len(keys) > MAX_POINTS:
        indices = sorted(range(len(keys)), key=lambda i: -keys[i].response)[:MAX_POINTS]
        keys, descriptors = [keys[i] for i in indices], descriptors[indices]
    if descriptors.shape[1] != 61:
        raise ValueError('Expected default AKAZE 61-byte descriptors')
    packed = np.zeros((len(keys), 128), np.float32)
    packed[:, :61] = descriptors
    return np.asarray([k.pt for k in keys], np.float32), packed


def binary_bytes(value):
    value = np.asarray(value)
    if (value.ndim != 2 or value.shape[1] != 128 or value.dtype != np.float32
        or not np.isfinite(value).all() or (value < 0).any() or (value > 255).any()
        or (value != np.floor(value)).any() or value[:, 61:].any()):
        raise ValueError('Invalid packed AKAZE descriptor')
    return np.ascontiguousarray(value[:, :61], dtype=np.uint8)


def akaze_registration(left, right):
    pa, da = left
    pb, db = right
    if min(len(da), len(db)) < 4:
        return None
    a, b = binary_bytes(da), binary_bytes(db)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    forward, reverse = matcher.knnMatch(a, b, k=2), matcher.knnMatch(b, a, k=1)
    pairs = [(m.queryIdx, m.trainIdx) for m, n in forward
             if m.distance < .85*n.distance and reverse[m.trainIdx][0].trainIdx == m.queryIdx]
    return estimate_pairs(pa, pb, pairs)


class BinaryDemoMatcher(FastCCDemoMatcher):
    name = 'FastCCAKAZE-v11-experimental'
    magic = 2801051
    local_features = staticmethod(akaze_features)
    registration = staticmethod(akaze_registration)

    def __init__(self, base):
        super().__init__(AcceleratedFastCC(base))
        self.legacy.local_features = akaze_features
        self.legacy.registration = akaze_registration
