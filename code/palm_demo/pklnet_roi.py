"""PKLNet-backed palm ROI extraction.

PKLNet is kept behind a lazy loader because the Pi runtime may not have
PyTorch installed yet. Its preprocessing and coordinate unwarping follow the
upstream ``test.py`` and ``roiExtractor.py`` implementation.
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image


PKLNET_ROOT = Path(__file__).resolve().parent.parent / "pklnet"
PKLNET_WEIGHTS = PKLNET_ROOT / "net_params_500.pth"


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
                from lib.models.nets.pklnet import pklnet
                import roiExtractor

                model = pklnet()
                try:
                    state = torch.load(self.weights, map_location="cpu", weights_only=False)
                except TypeError:  # PyTorch versions before weights_only
                    state = torch.load(self.weights, map_location="cpu")
                model.load_state_dict(state)
                model.eval()
            except Exception as error:  # pragma: no cover - model environment dependent
                raise PKLNetUnavailable(f"PKLNet failed to load: {error}") from error
            self._torch = torch
            self._model = model
            self._roi_extractor = roiExtractor

    @staticmethod
    def _prepare(image: Image.Image) -> tuple[Any, tuple[int, int], tuple[int, int], float]:
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
        resized = cv2.resize(rotated, (converted_w, converted_h), interpolation=cv2.INTER_CUBIC)
        standard[:converted_h, :converted_w] = resized

        tensor = standard.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = (tensor - np.array([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]) / np.array(
            [0.229, 0.224, 0.225], dtype=np.float32
        )[:, None, None]
        return tensor[None, ...], (original_h, original_w), (h, w), ratio

    @staticmethod
    def _unrotate_keypoints(kp: np.ndarray, original_size: tuple[int, int], rotated_size: tuple[int, int], ratio: float) -> np.ndarray:
        scaled = np.rint(kp * ratio).astype(np.float32)
        original_h, original_w = original_size
        rotated_h, _ = rotated_size
        if original_w > original_h:
            # Inverse of cv2.ROTATE_90_CLOCKWISE, matching PKLNet test.py.
            x = scaled[1::2].copy()
            y = rotated_h - scaled[0::2]
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
        with torch.no_grad():
            output = self._model(torch.from_numpy(tensor), (400, 300))
        kp = output[0][0].detach().cpu().numpy().astype(np.float32)
        if kp.size < 4:
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
        diagnostics = {
            "roi_source": "pklnet",
            "pklnet_keypoints": kp.tolist(),
            "roi_quad_full": quad.tolist(),
        }
        return roi.astype(np.uint8), quad, diagnostics
