"""Select five quality-preserving enrollment photos from a bounded candidate set.

Candidates must share the same image dimensions and ROI/texture conventions.
The feature scaling and greedy rule are engineering choices, not learned model
parameters; real-person recognition impact still requires separate validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True)
class PhotoCandidate:
    """One already localized enrollment proposal and its stable metadata."""

    frame_id: int
    sharpness: float
    contrast: float
    roi_quad: np.ndarray
    texture: np.ndarray
    frame_size: tuple[int, int]  # width, height
    payload: Any = None


class EnrollmentPhotoSelector:
    """Keep a bounded proposal window and greedily select quality/diversity."""

    def __init__(self, *, capacity: int = 20, select_count: int = 5) -> None:
        if capacity < 1 or select_count < 1 or select_count > capacity:
            raise ValueError("require 1 <= select_count <= capacity")
        self.capacity = int(capacity)
        self.select_count = int(select_count)
        self._candidates: list[PhotoCandidate] = []

    @property
    def candidates(self) -> tuple[PhotoCandidate, ...]:
        return tuple(self._candidates)

    def add(self, candidate: PhotoCandidate) -> bool:
        """Add an eligible candidate. Return False for invalid/low-quality input."""
        if len(self._candidates) >= self.capacity:
            raise OverflowError("candidate window is full")
        if not self._valid(candidate):
            return False
        self._candidates.append(candidate)
        return True

    def select(self) -> list[PhotoCandidate]:
        """Select at most ``select_count`` candidates with deterministic ties."""
        items = sorted(self._candidates, key=lambda item: item.frame_id)
        if len(items) <= self.select_count:
            return items

        quality = np.asarray([self._quality(item) for item in items], dtype=np.float64)
        pose = np.stack([self._pose(item) for item in items])
        texture = np.stack([self._texture(item.texture) for item in items])
        pose_distance = self._pairwise_euclidean(pose)
        texture_distance = self._pairwise_cosine(texture)
        pose_distance = self._scale_distances(pose_distance)
        texture_distance = self._scale_distances(texture_distance)
        diversity = (pose_distance + texture_distance) * 0.5

        # Start with the sharpest/highest-contrast frame. Quality has priority;
        # pose/texture diversity breaks near-quality ties and broadens coverage.
        chosen = [int(np.argmax(quality))]
        while len(chosen) < self.select_count:
            nearest = np.min(diversity[:, chosen], axis=1)
            nearest[chosen] = -1.0
            utility = 0.75 * quality + 0.25 * nearest
            utility[chosen] = -1.0
            chosen.append(int(np.argmax(utility)))
        return [items[index] for index in sorted(chosen, key=lambda i: items[i].frame_id)]

    def _valid(self, candidate: PhotoCandidate) -> bool:
        if not (math.isfinite(float(candidate.sharpness)) and math.isfinite(float(candidate.contrast))):
            return False
        if candidate.sharpness < 2.0 or candidate.contrast < 12.0:
            return False
        width, height = candidate.frame_size
        quad = np.asarray(candidate.roi_quad, dtype=np.float64)
        texture = np.asarray(candidate.texture, dtype=np.float64)
        return (width > 0 and height > 0 and quad.shape == (4, 2)
                and np.isfinite(quad).all() and texture.ndim == 1
                and texture.size > 0 and np.isfinite(texture).all()
                and np.linalg.norm(texture) > 0)

    @staticmethod
    def _quality(candidate: PhotoCandidate) -> float:
        # Saturating normalization avoids allowing one unbounded metric to
        # dominate; values below the current gate are rejected in _valid.
        sharpness = min(float(candidate.sharpness) / 12.0, 1.0)
        contrast = min(float(candidate.contrast) / 48.0, 1.0)
        return 0.5 * (sharpness + contrast)

    @staticmethod
    def _pose(candidate: PhotoCandidate) -> np.ndarray:
        quad = np.asarray(candidate.roi_quad, dtype=np.float64)
        width, height = candidate.frame_size
        center = quad.mean(axis=0)
        edge_a = quad[1] - quad[0]
        edge_b = quad[2] - quad[1]
        len_a, len_b = float(np.linalg.norm(edge_a)), float(np.linalg.norm(edge_b))
        area = abs(float(np.dot(quad[:, 0], np.roll(quad[:, 1], -1))
                       - np.dot(quad[:, 1], np.roll(quad[:, 0], -1)))) / 2.0
        angle = math.atan2(float(edge_a[1]), float(edge_a[0]))
        return np.asarray([
            center[0] / width,
            center[1] / height,
            math.log(max(area / (width * height), 1e-9)),
            math.log(max(len_a / max(len_b, 1e-9), 1e-9)),
            math.sin(2.0 * angle),
            math.cos(2.0 * angle),
        ], dtype=np.float64)

    @staticmethod
    def _texture(value: np.ndarray) -> np.ndarray:
        vector = np.asarray(value, dtype=np.float64)
        return vector / np.linalg.norm(vector)

    @staticmethod
    def _pairwise_euclidean(values: np.ndarray) -> np.ndarray:
        delta = values[:, None, :] - values[None, :, :]
        return np.sqrt(np.sum(delta * delta, axis=2))

    @staticmethod
    def _pairwise_cosine(values: np.ndarray) -> np.ndarray:
        return np.clip(1.0 - values @ values.T, 0.0, 2.0)

    @staticmethod
    def _scale_distances(values: np.ndarray) -> np.ndarray:
        positive = values[values > 1e-12]
        scale = float(np.median(positive)) if positive.size else 1.0
        return np.clip(values / scale, 0.0, 1.0)


def select_enrollment_photos(
    candidates: Iterable[PhotoCandidate], *, capacity: int = 20, select_count: int = 5,
) -> list[PhotoCandidate]:
    """Convenience entry point for a finite candidate window."""
    selector = EnrollmentPhotoSelector(capacity=capacity, select_count=select_count)
    for candidate in candidates:
        selector.add(candidate)
    return selector.select()


def is_near_duplicate(
    first: PhotoCandidate,
    second: PhotoCandidate,
    *,
    max_pose_distance: float = 0.05,
    min_texture_similarity: float = 0.995,
) -> bool:
    """Detect same-content frames despite global brightness changes.

    Thresholds are for capture de-duplication, not matcher scoring. Pose uses
    frame-normalized ROI geometry; texture uses centered grayscale samples.
    """
    if first.frame_size != second.frame_size:
        return False
    if not (math.isfinite(max_pose_distance) and max_pose_distance >= 0):
        raise ValueError("max_pose_distance must be finite and non-negative")
    if not (math.isfinite(min_texture_similarity) and -1 <= min_texture_similarity <= 1):
        raise ValueError("min_texture_similarity must be finite and in [-1, 1]")
    first_texture = np.asarray(first.texture, dtype=np.float64)
    second_texture = np.asarray(second.texture, dtype=np.float64)
    if first_texture.shape != second_texture.shape:
        return False
    first_texture = first_texture - first_texture.mean()
    second_texture = second_texture - second_texture.mean()
    first_norm, second_norm = np.linalg.norm(first_texture), np.linalg.norm(second_texture)
    if first_norm <= 1e-12 or second_norm <= 1e-12:
        return False
    similarity = float(np.clip((first_texture @ second_texture) / (first_norm * second_norm), -1.0, 1.0))
    if similarity < min_texture_similarity:
        return False
    first_pose = EnrollmentPhotoSelector._pose(first)
    second_pose = EnrollmentPhotoSelector._pose(second)
    return float(np.linalg.norm(first_pose - second_pose)) <= max_pose_distance
