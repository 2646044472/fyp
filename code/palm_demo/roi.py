from __future__ import annotations

import time
from typing import Any

import numpy as np
from PIL import Image
from scipy import ndimage

from models import ROIResult


DEFAULT_CROP = (0.19, 0.15, 0.81, 0.85)


def normalize_crop(image: Image.Image, crop: tuple[float, float, float, float]) -> tuple[np.ndarray, dict[str, float]]:
    gray = image.convert("L")
    width, height = gray.size
    box = (round(crop[0] * width), round(crop[1] * height), round(crop[2] * width), round(crop[3] * height))
    roi = gray.crop(box).resize((128, 128), Image.Resampling.LANCZOS)
    array = np.asarray(roi, dtype=np.float32)
    contrast = float(array.std())
    gradient = np.hypot(*np.gradient(array))
    sharpness = float(gradient.var())
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise RuntimeError("Frame has no usable intensity range. Reposition the hand and light.")
    normalized = np.clip((array - low) * 255.0 / (high - low), 0, 255).astype(np.uint8)
    return normalized, {"contrast": contrast, "sharpness": sharpness}


class FixedGuideROI:
    def __init__(self, crop: tuple[float, float, float, float] = DEFAULT_CROP, min_contrast: float = 0.0) -> None:
        self.crop = crop
        self.min_contrast = min_contrast

    def extract(self, image: Image.Image) -> ROIResult:
        started = time.perf_counter()
        try:
            roi, quality = normalize_crop(image, self.crop)
        except (RuntimeError, ValueError) as error:
            return ROIResult("RETRY", None, "LOW_CONTRAST", {}, (time.perf_counter() - started) * 1000)
        if quality["contrast"] < self.min_contrast:
            return ROIResult("RETRY", None, "LOW_CONTRAST", quality, (time.perf_counter() - started) * 1000)
        return ROIResult("OK", roi, None, quality, (time.perf_counter() - started) * 1000)


class AutomaticPalmROI:
    def __init__(
        self,
        background: Image.Image | np.ndarray | None = None,
        *,
        difference_threshold: float = 18.0,
        min_area_ratio: float = 0.03,
        max_area_ratio: float = 0.85,
        min_contrast: float = 8.0,
        min_sharpness: float = 8.0,
        ambiguity_ratio: float = 0.75,
    ) -> None:
        self.background = None if background is None else self._gray(background)
        self.difference_threshold = difference_threshold
        self.min_area_ratio = min_area_ratio
        self.max_area_ratio = max_area_ratio
        self.min_contrast = min_contrast
        self.min_sharpness = min_sharpness
        self.ambiguity_ratio = ambiguity_ratio

    @staticmethod
    def _gray(image: Image.Image | np.ndarray) -> np.ndarray:
        if isinstance(image, Image.Image):
            return np.asarray(image.convert("L"), dtype=np.float32)
        array = np.asarray(image)
        if array.ndim == 3:
            array = np.mean(array[..., :3], axis=2)
        return array.astype(np.float32)

    def extract(self, image: Image.Image | np.ndarray) -> ROIResult:
        started = time.perf_counter()
        current = self._gray(image)
        if current.ndim != 2 or current.size == 0:
            return self._retry("NO_FOREGROUND", started)
        background = self.background
        if background is None:
            border = np.concatenate((current[0], current[-1], current[:, 0], current[:, -1]))
            background = np.full_like(current, np.median(border))
        if background.shape != current.shape:
            return self._retry("BACKGROUND_SHAPE", started)
        raw_mask = np.abs(current - background) > self.difference_threshold
        if not raw_mask.any():
            return self._retry("NO_FOREGROUND", started)
        touches_edge = bool(raw_mask[0].any() or raw_mask[-1].any() or raw_mask[:, 0].any() or raw_mask[:, -1].any())
        mask = raw_mask
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
        mask = ndimage.binary_closing(mask, structure=np.ones((7, 7)))
        labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
        if count == 0:
            return self._retry("NO_FOREGROUND", started)
        sizes = np.bincount(labels.ravel())[1:]
        order = np.argsort(sizes)[::-1]
        largest = int(sizes[order[0]])
        total = current.size
        if largest / total < self.min_area_ratio:
            return self._retry("HAND_TOO_SMALL", started)
        if largest / total > self.max_area_ratio:
            return self._retry("HAND_TOO_LARGE", started)
        if len(order) > 1 and sizes[order[1]] / largest >= self.ambiguity_ratio:
            return self._retry("MULTIPLE_OBJECTS", started)
        component = labels == (order[0] + 1)
        ys, xs = np.where(component)
        if touches_edge or xs.min() == 0 or ys.min() == 0 or xs.max() == current.shape[1] - 1 or ys.max() == current.shape[0] - 1:
            return self._retry("HAND_CLIPPED", started)
        distance = ndimage.distance_transform_edt(component)
        cy, cx = np.unravel_index(int(np.argmax(distance)), distance.shape)
        radius = float(distance[cy, cx])
        if radius < 3:
            return self._retry("PALM_CENTER_UNCLEAR", started)
        side = max(8.0, min(float(max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)) * 0.62, radius * 4.0))
        half = side / 2.0
        left, top, right, bottom = cx - half, cy - half, cx + half, cy + half
        if left < 0 or top < 0 or right > current.shape[1] or bottom > current.shape[0]:
            return self._retry("ROI_OUTSIDE_IMAGE", started)
        crop = Image.fromarray(np.clip(current[int(round(top)):int(round(bottom)), int(round(left)):int(round(right))], 0, 255).astype(np.uint8))
        try:
            roi, quality = normalize_crop(crop, (0.0, 0.0, 1.0, 1.0))
        except RuntimeError:
            return self._retry("LOW_CONTRAST", started)
        if quality["contrast"] < self.min_contrast:
            return self._retry("LOW_CONTRAST", started, quality)
        if quality["sharpness"] < self.min_sharpness:
            return self._retry("LOW_SHARPNESS", started, quality)
        return ROIResult("OK", roi, None, quality, (time.perf_counter() - started) * 1000)

    @staticmethod
    def _retry(reason: str, started: float, quality: dict[str, float] | None = None) -> ROIResult:
        return ROIResult("RETRY", None, reason, quality or {}, (time.perf_counter() - started) * 1000)
