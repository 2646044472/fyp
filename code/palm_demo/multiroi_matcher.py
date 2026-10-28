"""Versioned query-hypothesis matching with one-pass native-pixel resampling."""
from __future__ import annotations

import cv2
import numpy as np

from pklnet_roi import normalize_roi
from registered_matcher import DUAL_SIZE, MAX_POINTS, FastCCDualRegisteredMatcher, local_features, registration

NAME = 'FastCCMultiROI-v3'
MAGIC = 2801028
NATIVE_SIDE = 1536
MAX_VIEWS = 8
HEADER_END = DUAL_SIZE + 24
PIXELS_END = HEADER_END + NATIVE_SIDE*NATIVE_SIDE
VIEW_SIZE = 16 + 72 + MAX_POINTS*130*4
FEATURE_SIZE = PIXELS_END + MAX_VIEWS*VIEW_SIZE


class FastCCMultiROIMatcher:
    name = NAME

    def __init__(self, base):
        self.base = base
        self.legacy = FastCCDualRegisteredMatcher(base)
        self.geometry = self.legacy.geometry

    def extract(self, roi):
        result = np.zeros(FEATURE_SIZE, np.uint8)
        result[:DUAL_SIZE] = self.legacy.extract(roi)
        result[DUAL_SIZE:HEADER_END] = np.asarray([MAGIC, 0, 0, 0, 0, 0], '<i4').view(np.uint8)
        return result

    def extract_with_context(self, full, quad, normalized_roi):
        return self.extract_with_hypotheses(full, quad, normalized_roi, [{'quad': quad, 'valid': True}])

    def extract_with_hypotheses(self, full, quad, normalized_roi, hypotheses):
        result = np.zeros(FEATURE_SIZE, np.uint8)
        result[:DUAL_SIZE] = self.legacy.extract_with_context(full, quad, normalized_roi)
        gray = cv2.cvtColor(np.asarray(full.convert('RGB')), cv2.COLOR_RGB2GRAY)
        quads = []
        for candidate in hypotheses:
            if not candidate.get('valid', True):
                continue
            q = np.asarray(candidate['quad'], np.float32)
            if (q.shape != (4, 2) or not np.isfinite(q).all() or (q < 0).any()
                    or (q[:, 0] >= full.width).any() or (q[:, 1] >= full.height).any()
                    or cv2.contourArea(q) < 1):
                continue
            if not any(np.array_equal(q, previous) for previous in quads):
                quads.append(q)
        if not quads:
            quads = [np.asarray(quad, np.float32)]
        if len(quads) > 2:
            raise ValueError('At most original and gamma hypotheses are supported')
        coordinates = np.concatenate(quads)
        low, high = coordinates.min(0), coordinates.max(0)
        center = (low+high)/2
        side = min(NATIVE_SIDE, max(128, int(np.ceil(max(high-low)*3))))
        x0, y0 = np.maximum(0, np.floor(center-side/2)).astype(int)
        x1, y1 = min(full.width, x0+side), min(full.height, y0+side)
        native = gray[y0:y1, x0:x1]
        result[HEADER_END:PIXELS_END].reshape(NATIVE_SIDE, NATIVE_SIDE)[:native.shape[0], :native.shape[1]] = native
        view_count = 0
        for h, q in enumerate(quads):
            destination = np.asarray([[384, 0], [0, 0], [0, 384], [384, 384]]
                                     if self.geometry.isAntiClock(q[:3].reshape(-1))
                                     else [[0, 0], [384, 0], [384, 384], [0, 384]], np.float32)
            source = cv2.getPerspectiveTransform(q, destination)
            for field, (size, offset) in enumerate([(384, 0), (768, 192)]):
                shift = np.asarray([[1., 0, offset], [0, 1, offset], [0, 0, 1.]])
                raw = cv2.warpPerspective(gray, shift@source, (size, size))
                try:
                    pixels = normalize_roi(raw)[0]
                except ValueError:
                    continue
                for sigma_id, sigma in enumerate([0, 2]):
                    points, desc = local_features(cv2.GaussianBlur(pixels, (0, 0), sigma) if sigma else pixels)
                    points = points-offset
                    start = PIXELS_END+view_count*VIEW_SIZE
                    result[start:start+16] = np.asarray([len(points), sigma_id, field, h], '<i4').view(np.uint8)
                    result[start+16:start+88] = np.asarray(source, '<f8').ravel().view(np.uint8)
                    result[start+88:start+88+len(points)*8] = np.asarray(points, '<f4').ravel().view(np.uint8)
                    dstart = start+88+MAX_POINTS*8
                    result[dstart:dstart+len(points)*512] = np.asarray(desc, '<f4').ravel().view(np.uint8)
                    view_count += 1
        result[DUAL_SIZE:HEADER_END] = np.asarray([MAGIC, native.shape[1], native.shape[0], x0, y0, view_count], '<i4').view(np.uint8)
        return result

    def _unpack(self, feature):
        f = np.asarray(feature)
        if f.dtype != np.uint8 or f.shape != (FEATURE_SIZE,):
            raise ValueError('Incompatible multi-ROI template shape or dtype')
        primary, secondary = self.legacy._views(f[:DUAL_SIZE])
        magic, width, height, x0, y0, count = map(int, f[DUAL_SIZE:HEADER_END].view('<i4'))
        if (magic != MAGIC or not 0 <= count <= MAX_VIEWS or not 0 <= width <= NATIVE_SIDE
                or not 0 <= height <= NATIVE_SIDE or min(x0, y0) < 0 or (count and min(width, height) == 0)):
            raise ValueError('Invalid multi-ROI header')
        full_width, full_height = primary[3]
        if x0+width > full_width or y0+height > full_height:
            raise ValueError('Invalid multi-ROI header: native crop outside original image')
        native = f[HEADER_END:PIXELS_END].reshape(NATIVE_SIDE, NATIVE_SIDE)[:height, :width]
        views = []
        for index in range(count):
            start = PIXELS_END+index*VIEW_SIZE
            n, sigma, field, hypothesis = map(int, f[start:start+16].view('<i4'))
            if not 0 <= n <= MAX_POINTS or sigma not in (0, 1) or field not in (0, 1) or hypothesis not in (0, 1):
                raise ValueError('Invalid multi-ROI view header')
            source = f[start+16:start+88].view('<f8').reshape(3, 3)
            points = f[start+88:start+88+n*8].view('<f4').reshape(n, 2)
            dstart = start+88+MAX_POINTS*8
            desc = f[dstart:dstart+n*512].view('<f4').reshape(n, 128)
            lower, upper = (-192, 576) if field else (0, 384)
            if (not np.isfinite(source).all() or abs(np.linalg.det(source)) < 1e-12
                    or not np.isfinite(points).all() or (points < lower).any() or (points >= upper).any()
                    or not np.isfinite(desc).all() or (desc < 0).any()):
                raise ValueError('Invalid multi-ROI view data')
            views.append((sigma, source, points, desc))
        return primary, secondary, native, (x0, y0), views

    def match(self, probe, candidate):
        query, _, native, origin, views = self._unpack(probe)
        gallery, smooth, _, _, _ = self._unpack(candidate)
        score = self.legacy.match(np.asarray(probe)[:DUAL_SIZE], np.asarray(candidate)[:DUAL_SIZE])
        gallery_views = [(gallery[4], gallery[5]), smooth]
        translate = np.asarray([[1., 0, origin[0]], [0, 1, origin[1]], [0, 0, 1.]])
        corners = np.asarray([[0., 0., 1.], [128., 0., 1.], [128., 128., 1.], [0., 128., 1.]])
        for sigma, source, points, desc in views:
            transform = registration((points, desc), gallery_views[sigma])
            if transform is None:
                continue
            warp = np.diag([1/3, 1/3, 1])@transform@source@translate
            mapped = corners@np.linalg.inv(warp).T
            mapped = mapped[:, :2]/mapped[:, 2:]
            if ((mapped < 1).any() or (mapped[:, 0] >= native.shape[1]-1).any()
                    or (mapped[:, 1] >= native.shape[0]-1).any()):
                continue
            raw = cv2.warpPerspective(native, warp, (128, 128))
            try:
                normalized = normalize_roi(raw)[0]
            except ValueError:
                continue
            score = min(score, float(self.base.match(self.base.extract(normalized), gallery[0][0].astype(bool))))
        return score

    def score_enrollment(self, probe, enrolled):
        if not len(enrolled):
            raise ValueError('At least one enrollment feature is required')
        return float(np.mean(sorted(self.match(probe, f) for f in enrolled)[:2]))
