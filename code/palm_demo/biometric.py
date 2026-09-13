from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np


def load_fastcc(baseline_path: str | Path) -> Any:
    baseline_path = Path(baseline_path)
    if not baseline_path.is_dir():
        raise RuntimeError(
            f"Baseline not found at {baseline_path}. Run ./install_pi.sh first, "
            "or pass --baseline-path to a checked-out baseline."
        )
    if str(baseline_path) not in sys.path:
        sys.path.insert(0, str(baseline_path))
    from palmprint.algorithms.fastcc import FastCCAlgorithm

    return FastCCAlgorithm()


def extract_feature(algorithm: Any, roi: np.ndarray) -> np.ndarray:
    return np.asarray(algorithm.extract(roi))


def score_probe(algorithm: Any, probe: np.ndarray, enrolled_features: list[np.ndarray] | np.ndarray) -> float:
    scores = [float(algorithm.match(probe, candidate)) for candidate in enrolled_features]
    if not scores:
        raise ValueError("at least one enrolled feature is required")
    return float(np.median(scores))
