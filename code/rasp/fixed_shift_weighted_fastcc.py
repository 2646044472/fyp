"""Isolated experimental FastCC: choose a shift before applying weights.

Weights are the gallery-derived spatial map; corresponding positions in the
selected pair of windows receive the mean of their two spatial weights.
"""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FixedShiftScore:
    score: float
    ordinary_score: float
    shift: tuple[int, int]


def _windows(array, dy, dx):
    rows, cols = array.shape
    return (array[(abs(dy)-dy)//2:rows-(abs(dy)+dy)//2,
                  (abs(dx)-dx)//2:cols-(abs(dx)+dx)//2],
            array[(abs(dy)+dy)//2:rows-(abs(dy)-dy)//2,
                  (abs(dx)+dx)//2:cols-(abs(dx)-dx)//2])


def fixed_shift_weighted_hamming(left, right, weights, *, shift=4):
    """Return weighted distance at the first ordinary minimum shift (dy, dx)."""
    left, right, weights = np.asarray(left), np.asarray(right), np.asarray(weights)
    if left.shape != (32, 32) or right.shape != left.shape or weights.shape != left.shape:
        raise ValueError("Expected 32x32 codes and weight map")
    if type(shift) is not int or not 0 <= shift <= 8:
        raise ValueError("Shift must be an integer from 0 through 8")
    if not np.isfinite(weights).all() or (weights <= 0).any():
        raise ValueError("Weights must be finite and positive")
    best = float('inf')
    for dy in range(-shift, shift + 1):
        for dx in range(-shift, shift + 1):
            a, _ = _windows(left, dy, dx)
            _, b = _windows(right, dy, dx)
            ordinary = float(np.mean(np.logical_xor(a, b)))
            if ordinary < best:
                best, chosen = ordinary, (dy, dx)
    dy, dx = chosen
    a, _ = _windows(left, dy, dx)
    _, b = _windows(right, dy, dx)
    wa, wb = _windows(weights.astype(np.float64, copy=False), dy, dx)
    pair_weights = (wa + wb) * 0.5
    score = np.sum(pair_weights * np.logical_xor(a, b)) / np.sum(pair_weights)
    return FixedShiftScore(float(score), best, chosen)
