"""Experimental FastCC metric with evidence across multiple palm regions.

This implementation lives in the application repository so the candidate is
not lost with the ignored, locally supplied ``vendor/`` dependency.
"""
from __future__ import annotations

import numpy as np

from palmprint.algorithms.fastcc import FastCCAlgorithm
from palmprint.core.matching import minimum_shifted_hamming


def quadrant_consensus_hamming(left: np.ndarray, right: np.ndarray, *, drop_worst: int = 1) -> float:
    """Average the best ``4-drop_worst`` quadrant scores after local shifts."""
    left, right = np.asarray(left), np.asarray(right)
    if left.shape != right.shape:
        raise ValueError(f"Feature shapes differ: {left.shape} != {right.shape}")
    if left.ndim != 2 or left.shape != (32, 32):
        raise ValueError("BlockConsensus FastCC expects 32x32 feature codes")
    if type(drop_worst) is not int or not 0 <= drop_worst < 4:
        raise ValueError("drop_worst must be an integer from 0 through 3")
    scores = []
    for row in (0, 16):
        for col in (0, 16):
            a = left[row:row + 16, col:col + 16]
            b = right[row:row + 16, col:col + 16]
            scores.append(minimum_shifted_hamming(a, b, shift=1))
    scores.sort()
    return float(np.mean(scores[:4 - drop_worst]))


class FastCCBlockConsensusAlgorithm(FastCCAlgorithm):
    """Opt-in FastCC extractor with a spatially distributed match score."""

    name = "FastCCBlockConsensus"

    def match(self, feature_a: np.ndarray, feature_b: np.ndarray) -> float:
        return quadrant_consensus_hamming(feature_a, feature_b, drop_worst=1)
