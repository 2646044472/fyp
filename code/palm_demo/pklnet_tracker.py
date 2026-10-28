"""Use the hand detector for presence and PKLNet for the matcher ROI geometry."""
from __future__ import annotations

import time
from typing import Any

import numpy as np
from PIL import Image

import palm_roi
from pklnet_roi import PKLNetROI, ROI_GEOMETRY_VERSION, normalize_roi


class PKLNetStatus(palm_roi.ROIStatus):
    def as_dict(self) -> dict[str, Any]:
        result = super().as_dict()
        result.update(roi_mode="pklnet", roi_geometry=ROI_GEOMETRY_VERSION)
        return result


class PKLNetTracker:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.extractor = PKLNetROI(threads=kwargs.pop("pklnet_threads", None))
        self.extractor._ensure_loaded()
        self.detector = palm_roi.HandLandmarkTracker(*args, **kwargs)
        self._status = PKLNetStatus(None, "starting")
        self._timestamp_ms: int | None = None
        self._roi: np.ndarray | None = None
        self._quality: dict[str, float] = {}

    def submit(self, image: Image.Image, timestamp_ms: int) -> None:
        self._timestamp_ms = timestamp_ms
        self._roi = None
        self.detector.submit(image, timestamp_ms)
        presence = self.detector.roi_status(image.size, frame_timestamp_ms=timestamp_ms)
        evidence = {"presence_detector": presence.as_dict(), "frame_timestamp_ms": timestamp_ms}
        if presence.status != "tracking" or presence.quad is None:
            self._status = PKLNetStatus(None, presence.status, hand_score=presence.hand_score, reason=presence.reason, diagnostics=evidence)
            return
        started = time.perf_counter()
        try:
            raw, quad, details = self.extractor.extract(image)
            evidence.update(details)
            evidence["pklnet_inference_ms"] = round((time.perf_counter() - started) * 1000, 2)
            if not details["roi_geometry_valid"]:
                raise ValueError(details["roi_geometry_reason"])
            self._roi, self._quality = normalize_roi(raw)
            self._status = PKLNetStatus(quad, "tracking", hand_score=presence.hand_score, span_px=float(np.linalg.norm(quad[1] - quad[0])), diagnostics=evidence)
        except Exception as error:
            self._status = PKLNetStatus(None, "pklnet_error", hand_score=presence.hand_score, reason=str(error), diagnostics=evidence)

    def roi_status(self, image_size: tuple[int, int], *, frame_timestamp_ms: int | None = None) -> PKLNetStatus:
        del image_size
        if frame_timestamp_ms is not None and frame_timestamp_ms != self._timestamp_ms:
            return PKLNetStatus(None, "tracking_stale", reason="PKLNet result belongs to a different frame")
        return self._status

    def processing_roi(self) -> tuple[np.ndarray, dict[str, float]]:
        if self._roi is None:
            raise RuntimeError("No PKLNet ROI for the current frame")
        return self._roi.copy(), dict(self._quality)

    def reset_background(self) -> None:
        self.detector.reset_background()
        self._roi = None
        self._timestamp_ms = None
        self._status = PKLNetStatus(None, "no_hand", reason="manual_reset")

    def close(self) -> None:
        self.detector.close()
