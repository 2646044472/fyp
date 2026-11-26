"""Move a display-only ROI between detector frames using checked optical flow."""

from __future__ import annotations

import numpy as np
from PIL import Image


class LiveROIOverlay:
    def __init__(self, max_age_s: float = 1.5) -> None:
        import cv2

        self.cv = cv2
        self.max_age_s = max_age_s
        self.reset()

    def reset(self) -> None:
        self.seed_id = None
        self.gray = None
        self.quad = None
        self.points = None
        self.seed_time = 0.0

    def _gray(self, image: Image.Image) -> np.ndarray:
        width, height = image.size
        return np.asarray(image.convert("L").resize((320, round(height * 320 / width))))

    def _features(self, gray: np.ndarray, quad: np.ndarray) -> np.ndarray | None:
        mask = np.zeros_like(gray)
        self.cv.fillConvexPoly(mask, np.rint(quad).astype(np.int32), 255)
        return self.cv.goodFeaturesToTrack(gray, 70, 0.01, 6, mask=mask, blockSize=7)

    def update(self, image, frame_id, captured_at, processed):
        status = dict(processed.roi_status) if processed is not None else {"roi_status": "starting"}
        status.update({"preview_frame_id": frame_id, "overlay_source": "none"})
        if processed is None:
            return None, status
        source = processed.captured
        age = captured_at - source.captured_monotonic
        if processed.roi_quad is None or not 0 <= age <= self.max_age_s:
            self.reset()
            if processed.roi_quad is not None:
                status.update(roi_status="tracking_lost", roi_reason="preview_expired")
            return None, status
        current = self._gray(image)
        scale = np.array([320 / image.width, current.shape[0] / image.height], dtype=np.float32)
        if source.frame_id != self.seed_id:
            self.seed_id = source.frame_id
            self.seed_time = source.captured_monotonic
            self.gray = self._gray(source.image)
            self.quad = processed.roi_quad.astype(np.float32) * scale
            self.points = self._features(self.gray, self.quad)
        if self.quad is None:
            status.update(roi_status="tracking_lost", roi_reason="preview_motion_lost")
            return None, status
        if frame_id != source.frame_id:
            if not self._advance(current):
                self.quad = None
                status.update(roi_status="tracking_lost", roi_reason="preview_motion_lost")
                return None, status
            status["overlay_source"] = "optical_flow"
        else:
            status["overlay_source"] = "detector"
        status.update(overlay_frame_id=frame_id, overlay_seed_frame_id=source.frame_id)
        return self.quad / scale, status

    def _advance(self, current: np.ndarray) -> bool:
        cv = self.cv
        if self.points is None or len(self.points) < 6 or current.shape != self.gray.shape:
            return False
        forward, valid, _ = cv.calcOpticalFlowPyrLK(
            self.gray, current, self.points, None, winSize=(21, 21), maxLevel=3,
        )
        if forward is None:
            return False
        backward, back_valid, _ = cv.calcOpticalFlowPyrLK(
            current, self.gray, forward, None, winSize=(21, 21), maxLevel=3,
        )
        if backward is None:
            return False
        good = (valid.ravel() != 0) & (back_valid.ravel() != 0)
        good &= np.linalg.norm(backward - self.points, axis=2).ravel() < 1.5
        good &= np.isfinite(forward).all(axis=(1, 2))
        if good.sum() < 6:
            return False
        transform, inliers = cv.estimateAffinePartial2D(
            self.points[good], forward[good], method=cv.RANSAC, ransacReprojThreshold=2.5,
        )
        if transform is None or inliers is None or inliers.sum() < 6 or inliers.mean() < 0.6:
            return False
        zoom = np.linalg.norm(transform[:, 0])
        if not np.isfinite(transform).all() or not 0.8 <= zoom <= 1.25:
            return False
        quad = cv.transform(self.quad[None], transform)[0]
        height, width = current.shape
        if (quad < 0).any() or (quad[:, 0] >= width).any() or (quad[:, 1] >= height).any():
            return False
        self.gray, self.quad = current, quad
        self.points = forward[good][inliers.ravel().astype(bool)]
        if len(self.points) < 25:
            refreshed = self._features(current, quad)
            if refreshed is not None and len(refreshed) > len(self.points):
                self.points = refreshed
        return True
