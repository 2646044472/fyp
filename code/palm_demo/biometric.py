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
            f"Baseline not found at {baseline_path}. Run ./install_pi.sh first, "
            "or pass --baseline-path to a checked-out baseline."
        )
    if str(baseline_path) not in sys.path:
        sys.path.insert(0, str(baseline_path))
    from palmprint.algorithms.registry import get_algorithm

    if name == "FastCCCompNetEvidence-v25-experimental":
        from compnet_evidence_matcher import CompNetEvidenceMatcher
        return CompNetEvidenceMatcher(get_algorithm("FastCC"))
    if name == "FastCCQualityEvidence-v24-experimental":
        from quality_evidence_matcher import QualityEvidenceMatcher
        return QualityEvidenceMatcher(get_algorithm("FastCC"))
    if name == "FastCCPooledEnrollment-v20-experimental":
        from pooled_enrollment_matcher import PooledEnrollmentMatcher
        return PooledEnrollmentMatcher(get_algorithm("FastCC"))
    if name == "FastCCAffineEnrollment-v13-experimental":
        from affine_enrollment_matcher import AffineEnrollmentMatcher
        return AffineEnrollmentMatcher(get_algorithm("FastCC"))
    if name == "FastCCLinkedEnrollment-v12-experimental":
        from linked_enrollment_matcher import LinkedEnrollmentMatcher
        return LinkedEnrollmentMatcher(get_algorithm("FastCC"))
    if name == "FastCCAKAZE-v11-experimental":
        from binary_demo_matcher import BinaryDemoMatcher
        return BinaryDemoMatcher(get_algorithm("FastCC"))
    if name == "FastCCStagedIndex-v10-experimental":
        from staged_index_matcher import StagedIndexMatcher
        return StagedIndexMatcher(get_algorithm("FastCC"))
    if name == "FastCCGuardedIndex-v9-experimental":
        from guarded_index_matcher import GuardedIndexMatcher
        return GuardedIndexMatcher(get_algorithm("FastCC"))
    if name == "FastCCProposedIndex-v8-experimental":
        from proposed_index_matcher import ProposedIndexMatcher
        return ProposedIndexMatcher(get_algorithm("FastCC"))
    if name == "FastCCIndexed-v7-experimental":
        from indexed_demo_matcher import IndexedDemoMatcher
        return IndexedDemoMatcher(get_algorithm("FastCC"))
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
