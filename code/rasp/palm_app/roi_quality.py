"""Quality gating and reproducible artifacts for dynamic palm ROI capture."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from PIL import Image


ROI_QUALITY_VERSION = "roi-quality-v1"
DEBUG_DATASET_SCHEMA_VERSION = "reliable-roi-debug-v1"
DEBUG_DATASET_SAMPLE_COUNT = 10


@dataclass(frozen=True)
class ROIQualityResult:
    """The decision for one processed camera frame."""

    state: str
    reason: str | None
    consecutive_frames: int
    required_frames: int
    roi_quad: np.ndarray | None
    quality: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "quality_status": self.state,
            "quality_reason": self.reason,
            "quality_consecutive_frames": self.consecutive_frames,
            "quality_required_frames": self.required_frames,
            "roi_quality_version": ROI_QUALITY_VERSION,
        }


class ROIQualityGate:
    """Require fresh, good and geometrically stable ROIs before capture."""

    NO_HAND_STATUSES = frozenset({"no_hand", "tracking_lost", "tracking_stale"})

    def __init__(
        self,
        *,
        required_frames: int = 5,
        max_age_ms: float = 1_200.0,
        min_contrast: float = 12.0,
        min_sharpness: float = 2.0,
        max_center_shift_ratio: float = 0.25,
        min_area_ratio: float = 0.65,
        max_area_ratio: float = 1.55,
        min_axis_similarity: float = 0.80,
    ) -> None:
        if required_frames < 1:
            raise ValueError("required_frames must be positive")
        self.required_frames = required_frames
        self.max_age_ms = float(max_age_ms)
        self.min_contrast = float(min_contrast)
        self.min_sharpness = float(min_sharpness)
        self.max_center_shift_ratio = float(max_center_shift_ratio)
        self.min_area_ratio = float(min_area_ratio)
        self.max_area_ratio = float(max_area_ratio)
        self.min_axis_similarity = float(min_axis_similarity)
        self._consecutive_frames = 0
        self._previous_quad: np.ndarray | None = None
        self._last_frame_id: int | None = None
        self._last_result = ROIQualityResult("NO_HAND", "starting", 0, required_frames, None, {})

    @property
    def last_result(self) -> ROIQualityResult:
        return self._last_result

    def config(self) -> dict[str, float | int]:
        return {
            "required_frames": self.required_frames,
            "max_age_ms": self.max_age_ms,
            "min_contrast": self.min_contrast,
            "min_sharpness": self.min_sharpness,
            "max_center_shift_ratio": self.max_center_shift_ratio,
            "min_area_ratio": self.min_area_ratio,
            "max_area_ratio": self.max_area_ratio,
            "min_axis_similarity": self.min_axis_similarity,
        }

    def reset(self, reason: str = "reset") -> ROIQualityResult:
        self._consecutive_frames = 0
        self._previous_quad = None
        self._last_frame_id = None
        self._last_result = ROIQualityResult("NO_HAND", reason, 0, self.required_frames, None, {})
        return self._last_result

    def update(
        self,
        *,
        frame_id: int,
        captured_monotonic_ms: float,
        now_monotonic_ms: float,
        image_size: tuple[int, int],
        roi_quad: np.ndarray | None,
        tracker_status: str,
        quality: Mapping[str, Any],
    ) -> ROIQualityResult:
        """Evaluate one detector output and update consecutive-frame state."""

        quality_values = self._numeric_quality(quality)
        if tracker_status in self.NO_HAND_STATUSES or roi_quad is None:
            return self._record("NO_HAND", tracker_status or "no_hand", None, quality_values)
        if tracker_status != "tracking":
            return self._record("LOW_QUALITY", f"tracker_status_{tracker_status}", None, quality_values)
        if now_monotonic_ms - captured_monotonic_ms > self.max_age_ms:
            return self._record("NO_HAND", "stale", None, quality_values)
        if self._last_frame_id is not None and frame_id <= self._last_frame_id:
            return self._record("LOW_QUALITY", "duplicate_frame", None, quality_values)

        quad = np.asarray(roi_quad, dtype=np.float32)
        geometry_reason = self._geometry_reason(quad, image_size)
        if geometry_reason is not None:
            return self._record("LOW_QUALITY", geometry_reason, None, quality_values)
        if not np.isfinite(quality_values.get("contrast", float("nan"))) or quality_values["contrast"] < self.min_contrast:
            return self._record("LOW_QUALITY", "contrast_below_minimum", None, quality_values)
        if not np.isfinite(quality_values.get("sharpness", float("nan"))) or quality_values["sharpness"] < self.min_sharpness:
            return self._record("LOW_QUALITY", "sharpness_below_minimum", None, quality_values)
        if self._previous_quad is not None and not self._is_stable(self._previous_quad, quad):
            return self._record("LOW_QUALITY", "roi_unstable", None, quality_values)

        self._consecutive_frames += 1
        self._previous_quad = quad.copy()
        self._last_frame_id = frame_id
        state = "READY" if self._consecutive_frames >= self.required_frames else "TRACKING"
        return self._record(state, None, quad, quality_values, keep_stability=True)

    def _record(
        self,
        state: str,
        reason: str | None,
        roi_quad: np.ndarray | None,
        quality: dict[str, float],
        *,
        keep_stability: bool = False,
    ) -> ROIQualityResult:
        if not keep_stability:
            self._consecutive_frames = 0
            self._previous_quad = None
            self._last_frame_id = None
        result = ROIQualityResult(
            state,
            reason,
            self._consecutive_frames,
            self.required_frames,
            None if roi_quad is None else roi_quad.copy(),
            quality,
        )
        self._last_result = result
        return result

    @staticmethod
    def _numeric_quality(quality: Mapping[str, Any]) -> dict[str, float]:
        values: dict[str, float] = {}
        for key in ("contrast", "sharpness"):
            try:
                values[key] = float(quality[key])
            except (KeyError, TypeError, ValueError):
                values[key] = float("nan")
        return values

    @staticmethod
    def _geometry_reason(quad: np.ndarray, image_size: tuple[int, int]) -> str | None:
        if quad.shape != (4, 2) or not np.isfinite(quad).all():
            return "roi_geometry_invalid"
        width, height = image_size
        if width <= 0 or height <= 0:
            return "image_size_invalid"
        if float(quad[:, 0].min()) < 0 or float(quad[:, 1].min()) < 0:
            return "roi_out_of_bounds"
        if float(quad[:, 0].max()) >= width or float(quad[:, 1].max()) >= height:
            return "roi_out_of_bounds"
        if np.linalg.norm(quad[1] - quad[0]) < 1 or np.linalg.norm(quad[3] - quad[0]) < 1:
            return "roi_geometry_degenerate"
        return None

    def _is_stable(self, previous: np.ndarray, current: np.ndarray) -> bool:
        previous_center = previous.mean(axis=0)
        current_center = current.mean(axis=0)
        previous_width = float(np.linalg.norm(previous[1] - previous[0]))
        previous_height = float(np.linalg.norm(previous[3] - previous[0]))
        center_shift = float(np.linalg.norm(current_center - previous_center))
        if center_shift > self.max_center_shift_ratio * max(previous_width, previous_height):
            return False
        previous_area = previous_width * previous_height
        current_width = float(np.linalg.norm(current[1] - current[0]))
        current_height = float(np.linalg.norm(current[3] - current[0]))
        current_area = current_width * current_height
        area_ratio = current_area / max(previous_area, 1e-6)
        if not self.min_area_ratio <= area_ratio <= self.max_area_ratio:
            return False
        previous_axis = previous[1] - previous[0]
        current_axis = current[1] - current[0]
        similarity = abs(float(np.dot(previous_axis, current_axis))) / max(
            float(np.linalg.norm(previous_axis) * np.linalg.norm(current_axis)), 1e-6
        )
        return similarity >= self.min_axis_similarity


class DebugDatasetWriter:
    """Write raw and exact matcher ROI pixels as one atomic sample record."""

    def __init__(
        self,
        root: Path,
        *,
        camera_settings: Mapping[str, Any],
        roi_algorithm_version: str,
    ) -> None:
        self.root = Path(root)
        self.camera_settings = dict(camera_settings)
        self.roi_algorithm_version = roi_algorithm_version
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        *,
        sample_index: int,
        raw_image: Image.Image,
        roi_128: np.ndarray,
        metadata: Mapping[str, Any],
    ) -> Path:
        if not 1 <= sample_index <= DEBUG_DATASET_SAMPLE_COUNT:
            raise ValueError(f"sample_index must be between 1 and {DEBUG_DATASET_SAMPLE_COUNT}")
        roi = np.asarray(roi_128)
        if roi.shape != (128, 128) or roi.dtype != np.uint8:
            raise ValueError("roi_128 must be an exact uint8 array with shape (128, 128)")
        sample_dir = self.root / f"sample_{sample_index:03d}"
        if sample_dir.exists():
            raise FileExistsError(f"debug sample already exists: {sample_dir}")
        sample_dir.mkdir(parents=False)
        raw_path = sample_dir / "raw.png"
        roi_path = sample_dir / "roi_128.png"
        metadata_path = sample_dir / "metadata.json"
        raw_image.save(raw_path, format="PNG")
        Image.fromarray(roi, mode="L").save(roi_path, format="PNG")
        payload = dict(metadata)
        payload.update(
            {
                "schema_version": DEBUG_DATASET_SCHEMA_VERSION,
                "sample_index": sample_index,
                "camera_settings": self.camera_settings,
                "roi_algorithm_version": self.roi_algorithm_version,
                "artifacts": {
                    "raw.png": {"sha256": self._sha256(raw_path), "mode": raw_image.mode, "size": list(raw_image.size)},
                    "roi_128.png": {"sha256": self._sha256(roi_path), "mode": "L", "size": [128, 128]},
                },
            }
        )
        metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return sample_dir

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
