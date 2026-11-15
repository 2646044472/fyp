from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np


def load_fastcc(baseline_path: str | Path) -> Any:
    return load_algorithm(baseline_path, "FastCC")


def load_algorithm(baseline_path: str | Path, name: str, *, ppnet_model_root=None) -> Any:
    if name == "PPNet-Tongji-600-Nearest-experimental":
        if ppnet_model_root is None:
            raise ValueError("PPNet requires an explicit ONNX model directory")
        from ppnet_demo_matcher import PPNetDemoMatcher
        return PPNetDemoMatcher(ppnet_model_root)
    baseline_path = Path(baseline_path)
    if not baseline_path.is_dir():
        raise RuntimeError(
            f"Baseline not found at {baseline_path}. Run ./install_pi.sh first, "
            "or pass --baseline-path to a checked-out baseline."
        )
    if str(baseline_path) not in sys.path:
        sys.path.insert(0, str(baseline_path))
    from palmprint.algorithms.registry import get_algorithm

    if name == "DoNMinTemplate-v1":
        from don_min_aggregation import DoNMinimumTemplateMatcher
        return DoNMinimumTemplateMatcher(get_algorithm("DoN"))
    if name == "FastCCBoundedExactWide-experimental":
        from bounded_wide_matcher import BoundedWideMatcher
        return BoundedWideMatcher(get_algorithm("FastCC"))
    if name == "FastCCRetainedLossless-experimental":
        from lossless_retained_matcher import LosslessRetainedMatcher
        return LosslessRetainedMatcher(get_algorithm("FastCC"))
    if name == "FastCCSharedLazy-v30-experimental":
        from shared_snapshot_matcher import SharedSnapshotLazyMatcher
        return SharedSnapshotLazyMatcher(get_algorithm("FastCC"))
    if name == "FastCCWideLazy-v29-experimental":
        from wide_capacity_matcher import WideCapacityLazyMatcher
        return WideCapacityLazyMatcher(get_algorithm("FastCC"))
    if name == "FastCCWideFallback-v35-experimental":
        from wide_fallback_matcher import WideCapacityFallbackMatcher
        return WideCapacityFallbackMatcher(get_algorithm("FastCC"))
    if name == "FastCCWideSharded-v36-experimental":
        from wide_sharded_matcher import WideCapacityShardedMatcher
        return WideCapacityShardedMatcher(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v37-experimental":
        from wide_candidate_matcher import WideCandidateFirstMatcher
        return WideCandidateFirstMatcher(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v38-experimental":
        from wide_candidate_matcher_v38 import WideCandidateFirstV38
        return WideCandidateFirstV38(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v39-experimental":
        from wide_candidate_matcher_v39 import WideCandidateFirstV39
        return WideCandidateFirstV39(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v40-experimental":
        from wide_candidate_matcher_v40 import WideCandidateFirstV40
        return WideCandidateFirstV40(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v41-experimental":
        from wide_candidate_matcher_v41 import WideCandidateFirstV41
        return WideCandidateFirstV41(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v43-experimental":
        from wide_candidate_matcher_v43 import WideCandidateFirstV43
        return WideCandidateFirstV43(get_algorithm("FastCC"))
    if name == "FastCCWideCandidateFirst-v44-experimental":
        from wide_candidate_matcher_v44 import WideCandidateFirstV44
        return WideCandidateFirstV44(get_algorithm("FastCC"))
    if name == "FastCCLazyRetained-v28-experimental":
        from lazy_cached_matcher import LazyCachedRetainedMatcher
        return LazyCachedRetainedMatcher(get_algorithm("FastCC"))
    if name == "FastCCBlockConsensus-v31-experimental":
        from lazy_cached_matcher import BlockConsensusLazyRetainedMatcher
        from block_consensus_fastcc import FastCCBlockConsensusAlgorithm
        return BlockConsensusLazyRetainedMatcher(FastCCBlockConsensusAlgorithm())
    if name == "FastCCTop3Consensus-v32-experimental":
        from lazy_cached_matcher import Top3ConsensusLazyRetainedMatcher
        return Top3ConsensusLazyRetainedMatcher(get_algorithm("FastCC"))
    if name == "FastCCGalleryDiscriminative-v34-experimental":
        from discriminative_fastcc import GalleryDiscriminativeFastCCMatcher
        from fastcc_accelerated import AcceleratedFastCC
        from lazy_cached_matcher import LazyCachedRetainedMatcher
        base = get_algorithm("FastCC")
        matcher_base = LazyCachedRetainedMatcher(base)
        if not isinstance(matcher_base.base, AcceleratedFastCC):
            matcher_base.close()
            raise RuntimeError("v34 requires the indexed pipeline's AcceleratedFastCC scorer")
        matcher_base.base.track_dispatch = True
        return GalleryDiscriminativeFastCCMatcher(base, matcher_base)
    if name == "FastCCRetainedEvidence-v27-experimental":
        from retained_evidence_matcher import RetainedCompNetAlternateROIMatcher
        return RetainedCompNetAlternateROIMatcher(get_algorithm("FastCC"))
    if name == "FastCCCompNetAlternateROI-v26-experimental":
        from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher
        return CompNetAlternateROIMatcher(get_algorithm("FastCC"))
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
