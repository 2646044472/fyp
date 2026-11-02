"""Optional single-device matcher with local registration and pose fallback.

Templates are fixed-size numeric byte arrays, never pickled Python objects.
They contain biometric pixels/descriptors and must be treated like other templates.
"""
from __future__ import annotations

import threading

import cv2
import numpy as np
from PIL import Image

from pklnet_roi import normalize_roi_pixels
from pose_matcher import FastCCPoseMatcher

NAME = 'FastCCRegisteredBest2-v1'
SIDE = 384
CONTEXT = 768
MAX_POINTS = 1000
MAGIC = 2801026
HEADER = 16
MATRIX_END = HEADER + 72
BANK_END = MATRIX_END + 9*32*32
CONTEXT_END = BANK_END + CONTEXT*CONTEXT
POINTS_END = CONTEXT_END + MAX_POINTS*2*4
FEATURE_SIZE = POINTS_END + MAX_POINTS*128*4
_RANSAC_LOCK = threading.Lock()


def local_features(pixels):
    sift = cv2.SIFT_create(nfeatures=MAX_POINTS, contrastThreshold=.02, edgeThreshold=10)
    keys, descriptors = sift.detectAndCompute(pixels, None)
    if descriptors is None:
        return np.empty((0, 2), np.float32), np.empty((0, 128), np.float32)
    keys, descriptors = keys[:MAX_POINTS], descriptors[:MAX_POINTS]
    descriptors = np.sqrt(descriptors/np.maximum(descriptors.sum(axis=1, keepdims=True), 1e-12))
    return np.asarray([k.pt for k in keys], np.float32), descriptors


def registration(left, right, *, diagnostics=None):
    """Return the unchanged similarity fit, optionally recording scalar gates.

    An unfinished or exceptional stage has no inferred rejection reason. The
    optional caller-owned mapping is reset on each call and contains no images,
    descriptors, identity labels or score/ROI selection instructions.
    """
    if diagnostics is not None:
        diagnostics.clear()
        diagnostics.update(schema='similarity-registration-v1', stage='input',
                           outcome='unknown', reason=None, failed_gates=[],
                           query_descriptors=None, enrollment_descriptors=None,
                           mutual_matches=None, inliers=None,
                           coverage=None, scale=None, angle_degrees=None)
    try:
        return _registration(left, right, diagnostics)
    except Exception as error:
        if diagnostics is not None:
            diagnostics.update(outcome='error', reason=None, error_type=type(error).__name__)
        raise


def _registration(left, right, diagnostics=None):
    pa, da = left
    pb, db = right
    if diagnostics is not None:
        diagnostics.update(stage='descriptor_count', query_descriptors=len(da),
                           enrollment_descriptors=len(db))
    if len(da) < 4 or len(db) < 4:
        if diagnostics is not None:
            diagnostics.update(outcome='rejected', reason='insufficient_descriptors')
        return None
    if diagnostics is not None:
        diagnostics['stage'] = 'correspondence'
    forward = cv2.BFMatcher().knnMatch(da, db, k=2)
    reverse = cv2.BFMatcher().knnMatch(db, da, k=1)
    good = [a for a, b in forward if a.distance < .85*b.distance
            and reverse[a.trainIdx][0].trainIdx == a.queryIdx]
    if diagnostics is not None:
        diagnostics['mutual_matches'] = len(good)
    if len(good) < 4:
        if diagnostics is not None:
            diagnostics.update(outcome='rejected', reason='insufficient_mutual_matches')
        return None
    p = np.asarray([pa[m.queryIdx] for m in good], np.float32)
    q = np.asarray([pb[m.trainIdx] for m in good], np.float32)
    if diagnostics is not None:
        diagnostics['stage'] = 'similarity_fit'
    with _RANSAC_LOCK:
        cv2.setRNGSeed(20261028)
        transform, mask = cv2.estimateAffinePartial2D(p, q, method=cv2.RANSAC,
                                                   ransacReprojThreshold=3., maxIters=2000,
                                                   confidence=.99, refineIters=10)
    if transform is None or not np.isfinite(transform).all():
        if diagnostics is not None:
            diagnostics.update(outcome='rejected', reason='no_transform' if transform is None else 'nonfinite_transform')
        return None
    if diagnostics is not None:
        diagnostics['stage'] = 'inlier_count'
    keep = mask.ravel().astype(bool)
    if diagnostics is not None:
        diagnostics['inliers'] = int(keep.sum())
    if keep.sum() < 4:
        if diagnostics is not None:
            diagnostics.update(outcome='rejected', reason='insufficient_inliers')
        return None
    coverage = min(cv2.contourArea(cv2.convexHull(v[keep])) for v in (p, q))/(SIDE*SIDE)
    scale = float(np.hypot(transform[0, 0], transform[1, 0]))
    angle = float(np.rad2deg(np.arctan2(transform[1, 0], transform[0, 0])))
    if diagnostics is not None:
        diagnostics.update(stage='geometry', coverage=float(coverage), scale=scale, angle_degrees=angle)
    if coverage < .02 or not .5 <= scale <= 2 or abs(angle) > 40:
        if diagnostics is not None:
            failed = []
            if coverage < .02:
                failed.append('coverage')
            if not .5 <= scale <= 2:
                failed.append('scale')
            if abs(angle) > 40:
                failed.append('angle')
            diagnostics.update(outcome='rejected', reason='geometry_limits', failed_gates=failed)
        return None
    if diagnostics is not None:
        diagnostics.update(stage='complete', outcome='accepted', reason='accepted')
    return np.vstack([transform, [0., 0., 1.]])


class FastCCRegisteredMatcher(FastCCPoseMatcher):
    name = NAME
    registration = staticmethod(registration)
    local_features = staticmethod(local_features)

    @staticmethod
    def _pack(bank, context=None, matrix=None, size=(0, 0), points=None, descriptors=None):
        result = np.zeros(FEATURE_SIZE, np.uint8)
        count = 0 if points is None else len(points)
        result[:HEADER] = np.asarray([MAGIC, count, *size], '<i4').view(np.uint8)
        result[HEADER:MATRIX_END] = np.asarray(np.eye(3) if matrix is None else matrix, '<f8').ravel().view(np.uint8)
        result[MATRIX_END:BANK_END] = bank.ravel().view(np.uint8)
        if context is not None:
            result[BANK_END:CONTEXT_END] = context.ravel()
        if count:
            result[CONTEXT_END:CONTEXT_END+count*8] = np.asarray(points, '<f4').ravel().view(np.uint8)
            result[POINTS_END:POINTS_END+count*512] = np.asarray(descriptors, '<f4').ravel().view(np.uint8)
        return result

    @staticmethod
    def _unpack(feature):
        f = np.asarray(feature)
        if f.dtype != np.uint8 or f.shape != (FEATURE_SIZE,):
            raise ValueError('Incompatible registered template shape or dtype')
        magic, count, width, height = f[:HEADER].view('<i4')
        if magic != MAGIC or not 0 <= count <= MAX_POINTS or min(width, height) < 0:
            raise ValueError('Invalid registered template header')
        bank = f[MATRIX_END:BANK_END].view(np.int8).reshape(9, 32, 32)
        FastCCPoseMatcher._validate(bank)
        matrix = f[HEADER:MATRIX_END].view('<f8').reshape(3, 3)
        context = f[BANK_END:CONTEXT_END].reshape(CONTEXT, CONTEXT)
        points = f[CONTEXT_END:CONTEXT_END+count*8].view('<f4').reshape(count, 2)
        desc = f[POINTS_END:POINTS_END+count*512].view('<f4').reshape(count, 128)
        if (not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-12
                or not np.isfinite(points).all() or not np.isfinite(desc).all()
                or (points < 0).any() or (points >= SIDE).any() or (desc < 0).any()
                or (count and (width == 0 or height == 0))):
            raise ValueError('Invalid registered template data')
        return bank, context, matrix, (int(width), int(height)), points, desc

    def extract(self, roi):
        return self._pack(FastCCPoseMatcher.extract(self, roi))

    def extract_with_context(self, full: Image.Image, quad, normalized_roi):
        # The base implementation calls self.extract; use a separate pose adapter
        # so its internal bank remains 9x32x32 instead of this packed format.
        pose = FastCCPoseMatcher(self.base)
        bank = pose.extract_with_context(full, quad, normalized_roi)
        q = np.asarray(quad, np.float32)
        dst = np.asarray([[SIDE, 0], [0, 0], [0, SIDE], [SIDE, SIDE]]
                         if self.geometry.isAntiClock(q[:3].reshape(-1))
                         else [[0, 0], [SIDE, 0], [SIDE, SIDE], [0, SIDE]], np.float32)
        matrix = cv2.getPerspectiveTransform(q, dst)
        gray = cv2.cvtColor(np.asarray(full.convert('RGB')), cv2.COLOR_RGB2GRAY)
        pixels = normalize_roi_pixels(cv2.warpPerspective(gray, matrix, (SIDE, SIDE)))
        points, desc = self.local_features(pixels)
        offset = np.asarray([[1., 0., SIDE/2], [0., 1., SIDE/2], [0., 0., 1.]])
        context = cv2.warpPerspective(gray, offset@matrix, (CONTEXT, CONTEXT))
        return self._pack(bank, context, matrix, full.size, points, desc)

    def match(self, probe, candidate):
        return self._match_parts(self._unpack(probe), self._unpack(candidate))

    def _match_parts(self, left, right, additional=()):
        bank, context, source, size, points, desc = left
        other, _, _, _, other_points, other_desc = right
        score = FastCCPoseMatcher.match(self, bank, other)
        pairs = [((points, desc), (other_points, other_desc)), *additional]
        for a, b in pairs:
            transform = self.registration(a, b)
            if transform is not None:
                score = min(score, self._aligned_score(context, source, size, other, transform, score))
        return score

    def _aligned_score(self, context, source, size, other, transform, fallback):
        scale = np.diag([128/SIDE, 128/SIDE, 1.])
        unoffset = np.asarray([[1., 0., -SIDE/2], [0., 1., -SIDE/2], [0., 0., 1.]])
        warp = scale@transform@unoffset
        corners = np.asarray([[0., 0., 1.], [128., 0., 1.], [128., 128., 1.], [0., 128., 1.]])
        for matrix, bounds in [(warp, (CONTEXT, CONTEXT)), (scale@transform@source, size)]:
            mapped = corners@np.linalg.inv(matrix).T
            mapped = mapped[:, :2]/mapped[:, 2:]
            if (not np.isfinite(mapped).all() or (mapped < 1).any()
                    or (mapped[:, 0] >= bounds[0]-1).any() or (mapped[:, 1] >= bounds[1]-1).any()):
                return fallback
        aligned = cv2.warpPerspective(context, warp, (128, 128))
        try:
            normalized = normalize_roi_pixels(aligned)
        except ValueError:
            return fallback
        return float(self.base.match(self.base.extract(normalized), other[0].astype(bool)))

    def score_enrollment(self, probe, enrolled):
        if not len(enrolled):
            raise ValueError('At least one enrollment feature is required')
        scores = sorted(self.match(probe, feature) for feature in enrolled)
        return float(np.mean(scores[:2]))


DUAL_SIZE = FEATURE_SIZE + 8 + MAX_POINTS*130*4
DUAL_MAGIC = MAGIC + 1


class FastCCDualRegisteredMatcher(FastCCRegisteredMatcher):
    """Two fixed descriptor views; final pixels always retain original exposure."""
    name = 'FastCCRegisteredBest2-v2'

    @staticmethod
    def _append_view(base, points=None, desc=None):
        result = np.zeros(DUAL_SIZE, np.uint8)
        result[:FEATURE_SIZE] = base
        count = 0 if points is None else len(points)
        result[FEATURE_SIZE:FEATURE_SIZE+8] = np.asarray([DUAL_MAGIC, count], '<i4').view(np.uint8)
        if count:
            result[FEATURE_SIZE+8:FEATURE_SIZE+8+count*8] = np.asarray(points, '<f4').ravel().view(np.uint8)
            start = FEATURE_SIZE+8+MAX_POINTS*8
            result[start:start+count*512] = np.asarray(desc, '<f4').ravel().view(np.uint8)
        return result

    def extract(self, roi):
        return self._append_view(FastCCRegisteredMatcher.extract(self, roi))

    def extract_with_context(self, full, quad, normalized_roi):
        base = FastCCRegisteredMatcher.extract_with_context(self, full, quad, normalized_roi)
        context = FastCCRegisteredMatcher._unpack(base)[1]
        pixels = normalize_roi_pixels(context[192:576, 192:576])
        points, desc = self.local_features(cv2.GaussianBlur(pixels, (0, 0), 2.))
        return self._append_view(base, points, desc)

    @staticmethod
    def _views(feature):
        feature = np.asarray(feature)
        if feature.dtype != np.uint8 or feature.shape != (DUAL_SIZE,):
            raise ValueError('Incompatible dual registered template shape or dtype')
        base = FastCCRegisteredMatcher._unpack(feature[:FEATURE_SIZE])
        magic, count = feature[FEATURE_SIZE:FEATURE_SIZE+8].view('<i4')
        if magic != DUAL_MAGIC or not 0 <= count <= MAX_POINTS:
            raise ValueError('Invalid dual registered template header')
        points = feature[FEATURE_SIZE+8:FEATURE_SIZE+8+count*8].view('<f4').reshape(count, 2)
        start = FEATURE_SIZE+8+MAX_POINTS*8
        desc = feature[start:start+count*512].view('<f4').reshape(count, 128)
        if (not np.isfinite(points).all() or not np.isfinite(desc).all()
                or (points < 0).any() or (points >= SIDE).any() or (desc < 0).any()
                or (count and min(base[3]) <= 0)):
            raise ValueError('Invalid dual registered descriptors')
        return base, (points, desc)

    def match(self, probe, candidate):
        left, second_left = self._views(probe)
        right, second_right = self._views(candidate)
        return self._match_parts(left, right, [(second_left, second_right)])
