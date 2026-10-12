"""PKLNet-backed palm ROI extraction.

PKLNet is kept behind a lazy loader because the Pi runtime may not have
PyTorch installed yet. Its preprocessing and coordinate unwarping follow the
upstream ``test.py`` and ``roiExtractor.py`` implementation.
"""

from __future__ import annotations

import sys
import threading
import types
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image


_APP_ROOT = Path(__file__).resolve().parent
PKLNET_ROOT = _APP_ROOT.parent / "pklnet" if (_APP_ROOT.parent / "pklnet").is_dir() else _APP_ROOT / "pklnet"
PKLNET_WEIGHTS = PKLNET_ROOT / "net_params_500.pth"
ROI_GEOMETRY_VERSION = "pklnet-palmkit-native-v1"
MIN_KEYPOINT_SPAN_RATIO = 0.10


class PKLNetUnavailable(RuntimeError):
    """Raised when PKLNet cannot be loaded in the current environment."""


class PKLNetROI:
    """Load PKLNet once and turn its two keypoints into a 128x128 ROI."""

    _load_lock = threading.Lock()

    def __init__(self, root: Path = PKLNET_ROOT, weights: Path = PKLNET_WEIGHTS) -> None:
        self.root = Path(root)
        self.weights = Path(weights)
        self._torch: Any | None = None
        self._model: Any | None = None
        self._roi_extractor: Any | None = None
        self._inference_lock = threading.Lock()

    @property
    def available(self) -> bool:
        try:
            self._ensure_loaded()
        except PKLNetUnavailable:
            return False
        return True

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            if not self.root.is_dir() or not self.weights.is_file():
                raise PKLNetUnavailable(f"PKLNet files are missing under {self.root}")
            try:
                import torch
            except Exception as error:  # pragma: no cover - depends on deployment image
                raise PKLNetUnavailable("PyTorch is not installed for PKLNet") from error

            root_text = str(self.root)
            if root_text not in sys.path:
                sys.path.insert(0, root_text)
            try:
                # Upstream targets the old torchvision.models.utils location.
                from torch.hub import load_state_dict_from_url
                compatibility = types.ModuleType("torchvision.models.utils")
                compatibility.load_state_dict_from_url = load_state_dict_from_url
                sys.modules.setdefault("torchvision.models.utils", compatibility)
                from lib.models.nets.pklnet import pklnet
                import roiExtractor

                model = pklnet()
                try:
                    state = torch.load(self.weights, map_location="cpu", weights_only=False)
                except TypeError:  # PyTorch versions before weights_only
                    state = torch.load(self.weights, map_location="cpu")
                model.load_state_dict(state)
                model.eval()
                torch.set_num_threads(2)
            except Exception as error:  # pragma: no cover - model environment dependent
                raise PKLNetUnavailable(f"PKLNet failed to load: {error}") from error
            self._torch = torch
            self._model = model
            self._roi_extractor = roiExtractor

    @staticmethod
    def _prepare(image: Image.Image) -> tuple[Any, tuple[int, int], tuple[int, int], tuple[float, float]]:
        """Match PKLNet's TestLoader: rotate landscape input and pad to 400x300."""

        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        original_h, original_w = bgr.shape[:2]
        rotated = cv2.rotate(bgr, cv2.ROTATE_90_CLOCKWISE) if original_w > original_h else bgr
        h, w = rotated.shape[:2]
        standard = np.zeros((400, 300, 3), dtype=np.uint8)
        if float(h / w) > 4 / 3:
            converted_w = int(400.0 * w / h)
            converted_h = 400
            ratio = float(h) / 400.0
        else:
            converted_w = 300
            converted_h = int(300.0 * h / w)
            ratio = float(w) / 300.0
        resized = cv2.resize(rotated, (converted_w, converted_h), interpolation=cv2.INTER_LINEAR)
        standard[:converted_h, :converted_w] = resized

        tensor = standard.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = (tensor - np.array([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )[:, None, None]
        return tensor[None, ...], (original_h, original_w), (h, w), (w / converted_w, h / converted_h)

    @staticmethod
    def _unrotate_keypoints(kp: np.ndarray, original_size: tuple[int, int], rotated_size: tuple[int, int], ratio: tuple[float, float]) -> np.ndarray:
        scaled = (kp.reshape(-1, 2) * np.asarray(ratio)).reshape(-1).astype(np.float32)
        original_h, original_w = original_size
        if original_w > original_h:
            # Inverse of cv2.ROTATE_90_CLOCKWISE, matching PKLNet test.py.
            x = scaled[1::2].copy()
            y = original_h - 1 - scaled[0::2]
            out = np.empty_like(scaled)
            out[0::2] = x
            out[1::2] = y
            return out
        return scaled

    def extract(self, image: Image.Image, *, side: int = 128) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
        self._ensure_loaded()
        assert self._torch is not None and self._model is not None and self._roi_extractor is not None
        tensor, original_size, rotated_size, ratio = self._prepare(image)
        torch = self._torch
        with self._inference_lock, torch.inference_mode():
            output = self._model(torch.from_numpy(tensor))
        kp = output[0][0].detach().cpu().numpy().astype(np.float32)
        if kp.size < 6 or not np.isfinite(kp).all():
            raise PKLNetUnavailable(f"PKLNet returned only {kp.size} keypoint values")
        kp = self._unrotate_keypoints(kp, original_size, rotated_size, ratio)
        p1 = kp[0:2]
        p2 = kp[2:4]
        anticlock = self._roi_extractor.isAntiClock(np.r_[p1, p2, kp[4:6]])
        roi_points = self._roi_extractor.getROIckp(p1, p2, anticlock)
        if roi_points is None:
            raise PKLNetUnavailable("PKLNet returned degenerate ROI keypoints")
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        roi = self._roi_extractor.getROIimg(bgr, roi_points, side=side, ratio=1.0)
        if roi is None or roi.shape != (side, side):
            raise PKLNetUnavailable("PKLNet ROI perspective transform failed")
        quad = np.asarray(roi_points, dtype=np.float32)
        in_bounds = bool((quad[:, 0] >= 0).all() and (quad[:, 0] < image.width).all() and (quad[:, 1] >= 0).all() and (quad[:, 1] < image.height).all())
        span_ratio = float(np.linalg.norm(p2 - p1) / min(image.size))
        geometry_reason = "roi_out_of_bounds" if not in_bounds else "pklnet_keypoint_span_too_small" if span_ratio < MIN_KEYPOINT_SPAN_RATIO else None
        diagnostics = {
            "roi_source": "pklnet",
            "roi_geometry": ROI_GEOMETRY_VERSION,
            "pklnet_preprocessing": "BGR, clockwise landscape rotation, 400x300 top-left padding, ImageNet channel normalization",
            "pklnet_keypoints": kp.tolist(),
            "roi_quad_full": quad.tolist(),
            "roi_in_bounds": in_bounds,
            "pklnet_keypoint_span_ratio": span_ratio,
            "roi_geometry_valid": geometry_reason is None,
            "roi_geometry_reason": geometry_reason,
            "min_keypoint_span_ratio": MIN_KEYPOINT_SPAN_RATIO,
        }
        return roi.astype(np.uint8), quad, diagnostics


def normalize_roi(roi: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    """Apply the live matcher's fixed percentile normalization to PKLNet pixels."""
    array = np.asarray(roi, dtype=np.float32)
    quality = {"contrast": float(array.std()), "sharpness": float(np.hypot(*np.gradient(array)).var())}
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise ValueError("PKLNet crop has no usable intensity range")
    return np.clip((array - low) * 255 / (high - low), 0, 255).astype(np.uint8), quality
