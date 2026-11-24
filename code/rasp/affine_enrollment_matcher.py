"""Experimental bounded affine rescue after unchanged v12 early stages.

Tilted palms need not be related by uniform scale and rotation. Estimate a
query-to-template affine map from the legacy stage's mutual RootSIFT pairs.
This avoids repeating descriptor searches. Six inliers, spatial coverage and bounded
anisotropy guard this extra model; ranking thresholds and fallback stay intact.
"""
import cv2
import numpy as np
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from registered_matcher import _RANSAC_LOCK, SIDE
from registration_accelerated import estimate_pairs
from pose_matcher import FastCCPoseMatcher
from pklnet_roi import normalize_roi_pixels


def bounded_affine(matrix):
    t = np.asarray(matrix)
    if t.shape != (3, 3) or not np.isfinite(t).all():
        return False
    if not np.allclose(t[2], [0, 0, 1], atol=1e-8) or np.linalg.det(t[:2, :2]) <= 0:
        return False
    singular = np.linalg.svd(t[:2, :2], compute_uv=False)
    return bool(singular.min() >= .5 and singular.max() <= 2
                and singular.max()/singular.min() <= 1.5
                and abs(np.rad2deg(np.arctan2(t[1, 0], t[0, 0]))) <= 40)


def affine_registration(left, right, pair_finder=None):
    pa, da = left
    pb, db = right
    if min(len(da), len(db)) < 6:
        return None
    if pair_finder is None:
        matcher = cv2.BFMatcher()
        forward = matcher.knnMatch(da, db, k=2)
        reverse = matcher.knnMatch(db, da, k=1)
        pairs = [(m.queryIdx, m.trainIdx) for m, n in forward
                 if m.distance < .85*n.distance and reverse[m.trainIdx][0].trainIdx == m.queryIdx]
    else:
        pairs = pair_finder(da, db)
    if len(pairs) < 6:
        return None
    p = np.asarray([pa[i] for i, j in pairs], np.float32)
    q = np.asarray([pb[j] for i, j in pairs], np.float32)
    with _RANSAC_LOCK:
        cv2.setRNGSeed(20261028)
        transform, mask = cv2.estimateAffine2D(p, q, method=cv2.RANSAC,
            ransacReprojThreshold=3., maxIters=2000, confidence=.99, refineIters=10)
    if transform is None or mask is None:
        return None
    keep = mask.ravel().astype(bool)
    if keep.sum() < 6:
        return None
    coverage = min(cv2.contourArea(cv2.convexHull(v[keep])) for v in (p, q))/(SIDE*SIDE)
    transform = np.vstack([transform, [0., 0., 1.]])
    if coverage < .02 or not bounded_affine(transform):
        return None
    inverse = np.linalg.inv(transform)
    return transform if bounded_affine(inverse) else None


class AffineEnrollmentMatcher(LinkedEnrollmentMatcher):
    name = 'FastCCAffineEnrollment-v13-experimental'
    magic = 2801053

    def _correspondences(self, left, right):
        da, db = left[1], right[1]
        if min(len(da), len(db)) < 4:
            return []
        native = getattr(self.registration, 'pairs', None)
        if native is not None:
            return native(da, db)
        matcher = cv2.BFMatcher()
        forward = matcher.knnMatch(da, db, k=2)
        reverse = matcher.knnMatch(db, da, k=1)
        return [(m.queryIdx, m.trainIdx) for m, n in forward
                if m.distance < .85*n.distance and reverse[m.trainIdx][0].trainIdx == m.queryIdx]

    def score_gallery(self, probe, groups):
        probe.affine_pairs = {}
        try:
            return super().score_gallery(probe, groups)
        finally:
            # Correspondences are strictly query-local, never reused on a new image.
            probe.affine_pairs.clear()

    def _legacy_pair(self, probe, primary, secondary, target):
        tp, ts = target[2]
        score = FastCCPoseMatcher.match(self.legacy, primary[0], tp[0])
        found, correspondences = [], []
        for left, right in (((primary[4], primary[5]), (tp[4], tp[5])), (secondary, ts)):
            pairs = self._correspondences(left, right)
            correspondences.append(pairs)
            transform = estimate_pairs(left[0], right[0], pairs)
            if transform is not None:
                found.append(transform)
                score = min(score, self.legacy._aligned_score(primary[1], primary[2], primary[3], tp[0], transform, score))
        probe.enrollment_direct[id(target)] = found
        probe.affine_pairs[id(target)] = correspondences
        return score

    def _enrollment_link_stage(self, probe, groups, pairs):
        super()._enrollment_link_stage(probe, groups, pairs)
        probe.link_stage_route = 'enrollment_link_confident'
        def aggregate():
            return {u:self._aggregate([pairs[u, j] for j in range(len(ss))]) for u, ss in groups.items()}
        if self.confident(aggregate()):
            return
        primary, secondary = self._legacy_probe(probe)
        corners = np.asarray([[0, 0, 1], [128, 0, 1], [128, 128, 1], [0, 128, 1]])
        def group_job(item):
            user, samples = item
            updated = {j:pairs[user, j] for j in range(len(samples))}
            for j, target in enumerate(samples):
                tp, ts = target[2]
                for channel, (query, enrollment) in enumerate((((primary[4], primary[5]), (tp[4], tp[5])), (secondary, ts))):
                    correspondences = probe.affine_pairs[id(target)][channel]
                    transform = affine_registration(query, enrollment, lambda a, b: correspondences)
                    if transform is None:
                        continue
                    warp = np.diag([1/3, 1/3, 1]) @ transform @ probe.source
                    mapped = corners @ np.linalg.inv(warp).T
                    mapped = mapped[:, :2]/mapped[:, 2:]
                    if (not np.isfinite(mapped).all() or (mapped < 1).any()
                        or (mapped[:, 0] >= probe.native.shape[1]-1).any()
                        or (mapped[:, 1] >= probe.native.shape[0]-1).any()
                        or not self._accept_alignment((None, None, probe.source), mapped)):
                        continue
                    pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native, warp, (128, 128)))
                    updated[j] = min(updated[j], self.base.match(self.base.extract(pixels), target[0]))
            return user, updated
        for user, updated in self._workers.map(group_job, groups.items()):
            pairs.update({(user, j):score for j, score in updated.items()})
        probe.link_stage_route = 'affine_confident'
