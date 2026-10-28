from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np


def load_fastcc(baseline_path: str | Path) -> Any:
    return load_algorithm(baseline_path, "FastCC")


def load_algorithm(baseline_path: str | Path, name: str) -> Any:
    baseline_path = Path(baseline_path)
    if not baseline_path.is_dir():
        raise RuntimeError(
            f"Baseline not found at {baseline_path}. Run ./deploy/install_pi.sh first, "
            "or pass --baseline-path to a checked-out baseline."
        )
    if str(baseline_path) not in sys.path:
        sys.path.insert(0, str(baseline_path))
    from palmprint.algorithms.registry import get_algorithm

    if name == "FastCCDemo-v6":
        from demo_matcher import FastCCDemoMatcher
        return FastCCDemoMatcher(get_algorithm("FastCC"))
    if name == "FastCCAnchoredUnion-v5":
        from anchored_matcher import FastCCAnchoredUnionMatcher
        return FastCCAnchoredUnionMatcher(get_algorithm("FastCC"))
    if name == "FastCCWindowUnion-v4":
        from union_matcher import FastCCWindowUnionMatcher
        return FastCCWindowUnionMatcher(get_algorithm("FastCC"))
    if name == "FastCCMultiROI-v3":
        from multiroi_matcher import FastCCMultiROIMatcher
        return FastCCMultiROIMatcher(get_algorithm("FastCC"))
    if name == "FastCCRegisteredBest2-v2":
        from registered_matcher import FastCCDualRegisteredMatcher
        return FastCCDualRegisteredMatcher(get_algorithm("FastCC"))
    if name == "FastCCRegisteredBest2-v1":
        from registered_matcher import FastCCRegisteredMatcher
        return FastCCRegisteredMatcher(get_algorithm("FastCC"))
    if name == "FastCCPoseNearest-v1":
        from pose_matcher import FastCCPoseMatcher
        return FastCCPoseMatcher(get_algorithm("FastCC"))
    return get_algorithm(name)


def extract_feature(algorithm: Any, roi: np.ndarray) -> np.ndarray:
    return np.asarray(algorithm.extract(roi))


def score_probe(algorithm: Any, probe: np.ndarray, enrolled_features: list[np.ndarray] | np.ndarray) -> float:
    if hasattr(algorithm, "score_enrollment"):
        return float(algorithm.score_enrollment(probe, enrolled_features))
    scores = [float(algorithm.match(probe, candidate)) for candidate in enrolled_features]
    if not scores:
        raise ValueError("at least one enrolled feature is required")
    return float(np.median(scores))
