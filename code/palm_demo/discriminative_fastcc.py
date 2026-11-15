"""Enrollment-only, gallery-adaptive reliability weighting for binary FastCC."""
from __future__ import annotations

import threading
import hashlib

import numpy as np

def gallery_discriminability_weights(groups, *, floor: float = 0.25, epsilon: float = 1e-6):
    """Weight code positions stable within a hand and variable across hands.

    ``groups`` is the prepared enrollment gallery. No query features or labels
    outside that gallery are used. The returned weights are normalized to mean 1.
    """
    if len(groups) < 2:
        raise ValueError("At least two enrolled hands are required")
    if not 0 < floor <= 1 or not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("Invalid reliability-weight parameters")
    per_hand = []
    for samples in groups.values():
        # The retained matcher sample starts with the 32x32 pose FastCC code.
        codes = [np.asarray(sample[0]) for sample in samples]
        if len(codes) < 2 or any(code.shape != (32, 32) for code in codes):
            raise ValueError("Every enrolled hand needs at least two 32x32 FastCC codes")
        per_hand.append(np.stack([code.astype(np.float32, copy=False) for code in codes]))
    # Enrollment counts may differ (including a held-out frame in a diagnostic
    # split); estimate each hand's moments independently so identities remain
    # equally weighted rather than weighting hands by frame count.
    hand_means = np.stack([codes.mean(axis=0) for codes in per_hand])
    within = np.stack([codes.var(axis=0) for codes in per_hand]).mean(axis=0)
    between = np.var(hand_means, axis=0)
    reliability = between / (between + within + epsilon)
    weights = floor + reliability
    weights /= weights.mean()
    if not np.isfinite(weights).all() or (weights <= 0).any():
        raise ValueError("Invalid gallery-derived bit weights")
    return weights.astype(np.float32)


class WeightedShiftedHammingKernel:
    """Precompute shifted index/weight windows and score each pair in one batch."""

    def __init__(self, weights, *, shift: int = 4):
        weights = np.asarray(weights)
        if weights.shape != (32, 32):
            raise ValueError("Expected a 32x32 weight map")
        if type(shift) is not int or not 0 <= shift <= 8:
            raise ValueError("Shift must be an integer from 0 through 8")
        if not np.isfinite(weights).all() or (weights <= 0).any():
            raise ValueError("Weights must be finite and positive")
        offsets = range(-shift, shift + 1)
        left_indices, right_indices, pair_weights = [], [], []
        flat_weights = weights.astype(np.float32, copy=False).reshape(-1)
        for dy in offsets:
            for dx in offsets:
                ay0, ay1 = (abs(dy) - dy) // 2, 32 - (abs(dy) + dy) // 2
                ax0, ax1 = (abs(dx) - dx) // 2, 32 - (abs(dx) + dx) // 2
                by0, by1 = (abs(dy) + dy) // 2, 32 - (abs(dy) - dy) // 2
                bx0, bx1 = (abs(dx) + dx) // 2, 32 - (abs(dx) - dx) // 2
                height, width = ay1 - ay0, ax1 - ax0
                rows, cols = np.mgrid[:32, :32]
                valid = (rows < height) & (cols < width)
                left = (rows + ay0) * 32 + cols + ax0
                right = (rows + by0) * 32 + cols + bx0
                left[~valid] = right[~valid] = 0
                current = 0.5 * (flat_weights[left] + flat_weights[right])
                current[~valid] = 0.0
                left_indices.append(left.astype(np.int32, copy=False).reshape(-1))
                right_indices.append(right.astype(np.int32, copy=False).reshape(-1))
                pair_weights.append(current.reshape(-1))
        self.left_indices = np.stack(left_indices)
        self.right_indices = np.stack(right_indices)
        self.pair_weights = np.stack(pair_weights)
        self.denominators = self.pair_weights.sum(axis=1)

    def __call__(self, left, right):
        left, right = np.asarray(left), np.asarray(right)
        if left.shape != right.shape or left.shape != (32, 32):
            raise ValueError("Expected equal 32x32 FastCC codes")
        a = np.take(left.reshape(-1), self.left_indices)
        b = np.take(right.reshape(-1), self.right_indices)
        mismatches = np.logical_xor(a, b)
        numerators = (self.pair_weights * mismatches).sum(axis=1)
        distances = numerators / self.denominators
        return float(np.clip(distances.min(), 0.0, 1.0))


def weighted_shifted_hamming(left, right, weights, *, shift: int = 4) -> float:
    return WeightedShiftedHammingKernel(weights, shift=shift)(left, right)


class GalleryWeightedPairMatcher:
    """Callable wrapper preserving the underlying extractor and matcher API."""

    def __init__(self, ordinary_match, weights, *, shift: int = 4):
        self.ordinary_match = ordinary_match
        self.weights = np.asarray(weights, dtype=np.float32).copy()
        self.kernel = WeightedShiftedHammingKernel(self.weights, shift=shift)
        self.shift = shift
        self.weighted_calls = 0
        self.fallback_calls = 0
        self._counter_lock = threading.Lock()

    def __call__(self, left, right):
        left, right = np.asarray(left), np.asarray(right)
        if left.shape != (32, 32) or right.shape != (32, 32):
            with self._counter_lock:
                self.fallback_calls += 1
            return self.ordinary_match(left, right)
        with self._counter_lock:
            self.weighted_calls += 1
        return self.kernel(left, right)


class GalleryDiscriminativeFastCCMatcher:
    """Opt-in v34 retained pipeline with enrollment-derived bit reliability."""

    name = "FastCCGalleryDiscriminative-v34-experimental"

    def __init__(self, base, matcher_base, *, shift: int = 4):
        self.base = base
        self.matcher_base = matcher_base
        if type(shift) is not int or not 0 <= shift <= 8:
            raise ValueError("Shift must be an integer from 0 through 8")
        self.shift = shift
        self._ordinary_match = base.match
        self._gallery_key = None
        self._weight_lock = threading.RLock()
        self._weights = None
        self._weighted_matcher = None
        self._accelerated_matcher = getattr(matcher_base, "base", None)
        self.last_score_path_trace = None

    def prepare_gallery(self, groups):
        key = tuple((identity, tuple(id(sample) for sample in samples))
                    for identity, samples in sorted(groups.items()))
        with self._weight_lock:
            if key != self._gallery_key:
                self.base.match = self._ordinary_match
                if len(groups) < 2 or any(len(samples) < 2 for samples in groups.values()):
                    # App startup and partial galleries are valid states. Keep
                    # the normal matcher until there are enough enrolled hands
                    # and frames to estimate stable between/within variation.
                    self._weights = None
                    self._weighted_matcher = None
                    self._gallery_key = key
                    return self.matcher_base.prepare_gallery(groups)
                self._weights = gallery_discriminability_weights(groups)
                self._weighted_matcher = GalleryWeightedPairMatcher(
                    self._ordinary_match, self._weights, shift=self.shift
                )
                self.base.match = self._weighted_matcher
                self._gallery_key = key
        return self.matcher_base.prepare_gallery(groups)

    def score_gallery(self, probe, groups):
        if self._weighted_matcher is None:
            dispatch_before = getattr(self._accelerated_matcher, "instance_override_dispatches", 0)
            scores = self.matcher_base.score_gallery(probe, groups)
            self.last_score_path_trace = {
                "metric": "ordinary-fallback-insufficient-gallery",
                "score_direction": "lower_is_better",
                "weight_sha256": None,
                "weighted_pair_calls": 0,
                "ordinary_fallback_calls": 0,
                "accelerated_instance_override_dispatches": (
                    getattr(self._accelerated_matcher, "instance_override_dispatches", 0) - dispatch_before
                ),
            }
            return scores
        weighted_before = getattr(self._weighted_matcher, "weighted_calls", 0)
        fallback_before = getattr(self._weighted_matcher, "fallback_calls", 0)
        dispatch_before = getattr(self._accelerated_matcher, "instance_override_dispatches", 0)
        scores = self.matcher_base.score_gallery(probe, groups)
        self.last_score_path_trace = {
            "metric": "gallery-discriminative-weighted-shifted-hamming",
            "score_direction": "lower_is_better",
            "weight_sha256": hashlib.sha256(self._weights.tobytes()).hexdigest(),
            "weighted_pair_calls": getattr(self._weighted_matcher, "weighted_calls", 0) - weighted_before,
            "ordinary_fallback_calls": getattr(self._weighted_matcher, "fallback_calls", 0) - fallback_before,
            "accelerated_instance_override_dispatches": (
                getattr(self._accelerated_matcher, "instance_override_dispatches", 0) - dispatch_before
            ),
        }
        return scores

    def __getattr__(self, name):
        return getattr(self.matcher_base, name)

    def close(self):
        with self._weight_lock:
            self.base.match = self._ordinary_match
            self._gallery_key = None
            self._weights = None
            self._weighted_matcher = None
        return self.matcher_base.close()
