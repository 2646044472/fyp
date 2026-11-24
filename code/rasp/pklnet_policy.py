"""Label-independent PKLNet branch diagnostics and historical policy checks.

These are engineering consistency guards, not a calibrated probability that
the crop is anatomically correct. Two branches can still agree on a wrong ROI.
"""
from __future__ import annotations

import cv2
import numpy as np

MIN_AXIS_COSINE = 0.80
MIN_SPAN_AGREEMENT = 0.65
MIN_QUAD_IOU = 0.50
MIN_KEYPOINT_SPAN_RATIO = 0.10


def align_endpoints_and_fuse(heatmap, fc):
    """Fuse the same physical endpoints, independent of their array ordering.

    PalmKit's crop is invariant to swapping the first two points (the winding
    compensates). Index-wise averaging is not invariant and can collapse the
    span. Choose the permutation by spatial distance only, never by identity.
    The third point is left unchanged: it selects the palm-facing side.
    """
    hm = np.asarray(heatmap, dtype=np.float32).reshape(-1)
    direct = np.asarray(fc, dtype=np.float32).reshape(-1)
    if hm.size != 6 or direct.size != 6 or not np.isfinite(np.r_[hm,direct]).all():
        raise ValueError("Expected two finite three-point predictions")
    swapped = direct[[2,3,0,1,4,5]]
    direct_cost = float(np.square(hm[:4]-direct[:4]).sum())
    swap_cost = float(np.square(hm[:4]-swapped[:4]).sum())
    use_swap = swap_cost < direct_cost
    aligned = swapped if use_swap else direct
    return (hm+aligned)*np.float32(.5), {
        "pklnet_endpoint_swap": use_swap,
        "pklnet_direct_endpoint_cost": direct_cost,
        "pklnet_aligned_endpoint_cost": min(direct_cost,swap_cost),
    }


def branch_consensus(heatmap, fc, image_size, geometry):
    """Check both branches in original-image coordinates; never choose by ID."""
    result = {"pklnet_consensus_valid": False, "pklnet_consensus_reason": None,
              "pklnet_consensus_limits": {"min_axis_cosine": MIN_AXIS_COSINE,
                                          "min_span_agreement": MIN_SPAN_AGREEMENT,
                                          "min_quad_iou": MIN_QUAD_IOU}}
    branches = []
    for name, value in (("heatmap", heatmap), ("fc", fc)):
        kp = np.asarray(value, dtype=np.float32).reshape(-1)
        if kp.size != 6 or not np.isfinite(kp).all():
            result["pklnet_consensus_reason"] = "pklnet_invalid_branch_keypoints"
            return result
        axis = kp[2:4] - kp[:2]
        span = float(np.linalg.norm(axis))
        result[f"pklnet_{name}_keypoints"] = kp.tolist()
        result[f"pklnet_{name}_span_ratio"] = span / min(image_size)
        if span / min(image_size) < MIN_KEYPOINT_SPAN_RATIO:
            result["pklnet_consensus_reason"] = "pklnet_branch_span_too_small"
            return result
        quad = np.asarray(geometry.getROIckp(kp[:2], kp[2:4], geometry.isAntiClock(kp)), dtype=np.float32)
        if quad.shape != (4, 2) or not np.isfinite(quad).all():
            result["pklnet_consensus_reason"] = "pklnet_invalid_branch_quad"
            return result
        result[f"pklnet_{name}_quad"] = quad.tolist()
        if not ((quad >= 0).all() and (quad[:, 0] < image_size[0]).all() and (quad[:, 1] < image_size[1]).all()):
            result["pklnet_consensus_reason"] = "pklnet_branch_out_of_bounds"
            return result
        branches.append((axis, span, quad))
    (a, sa, qa), (b, sb, qb) = branches
    cosine = float(np.clip(np.dot(a, b) / (sa * sb), -1, 1))
    ratio = min(sa, sb) / max(sa, sb)
    intersection = max(0., float(cv2.intersectConvexConvex(qa, qb)[0]))
    union = abs(cv2.contourArea(qa)) + abs(cv2.contourArea(qb)) - intersection
    iou = float(np.clip(intersection / max(union, 1e-9), 0, 1))
    result.update(pklnet_branch_axis_cosine=cosine, pklnet_branch_span_agreement=ratio, pklnet_branch_quad_iou=iou)
    reason = ("pklnet_branch_direction_conflict" if cosine < MIN_AXIS_COSINE else
              "pklnet_branch_scale_conflict" if ratio < MIN_SPAN_AGREEMENT else
              "pklnet_branch_location_conflict" if iou < MIN_QUAD_IOU else None)
    result.update(pklnet_consensus_reason=reason, pklnet_consensus_valid=reason is None)
    return result


def require_matchable_quality(quality):
    """Historical offline quality gate; the app now records these metrics only."""
    contrast = float(quality.get("contrast", float('nan')))
    sharpness = float(quality.get("sharpness", float('nan')))
    if not np.isfinite([contrast, sharpness]).all():
        raise ValueError("ROI quality is missing or invalid; capture a new palm image.")
    if contrast < 12.0:
        raise ValueError(f"Low contrast ({contrast:.1f}); improve palm lighting and capture again.")
    if sharpness < 2.0:
        raise ValueError(f"Low sharpness ({sharpness:.1f}); keep the palm in focus and capture again.")
