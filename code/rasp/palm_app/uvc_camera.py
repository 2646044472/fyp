"""Explicitly selected UVC camera for local development on X."""
from __future__ import annotations

import hashlib
from pathlib import Path

import cv2
import numpy as np


class UvcCamera:
    def __init__(self, device: Path, width: int, height: int,
                 native_size: tuple[int, int] | None = None) -> None:
        self.device = Path(device)
        if not self.device.is_absolute() or not str(self.device).startswith("/dev/v4l/by-id/"):
            raise ValueError("UVC mode requires an explicit /dev/v4l/by-id device path")
        if not self.device.exists():
            raise FileNotFoundError(self.device)
        self.capture = cv2.VideoCapture(str(self.device), cv2.CAP_V4L2)
        if not self.capture.isOpened():
            self.capture.release()
            raise RuntimeError(f"Cannot open UVC camera: {self.device.name}")
        try:
            self.analysis_size = (width, height)
            if native_size is not None:
                self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                width, height = native_size
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
            actual_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_width < width or actual_height < height:
                raise RuntimeError(
                    f"UVC camera negotiated {actual_width}x{actual_height}, below requested {width}x{height}"
                )
            self.width, self.height = actual_width, actual_height
            fourcc_value = int(self.capture.get(cv2.CAP_PROP_FOURCC))
            fourcc = "".join(chr((fourcc_value >> (8 * i)) & 0xFF) for i in range(4)).strip("\x00 ")
            self.fourcc = fourcc or None
            if native_size is not None and (
                (self.width, self.height) != native_size or self.fourcc != "MJPG"
                or not self.capture.set(cv2.CAP_PROP_CONVERT_RGB, 0)
            ):
                raise RuntimeError("UVC camera did not provide the requested native MJPEG mode")
            self.device_key = hashlib.sha256(str(self.device).encode("utf-8")).hexdigest()[:10]
        except Exception:
            self.capture.release()
            raise

    @property
    def capture_profile(self) -> str:
        fmt = self.fourcc or "unknown"
        return f"uvc-{self.device_key}-{fmt}-{self.width}x{self.height}"

    @property
    def capture_source(self) -> str:
        return f"uvc-stream-frame-{self.fourcc or 'unknown'}-{self.width}x{self.height}"

    def read_bgr(self):
        ok, frame = self.capture.read()
        if not ok or frame is None:
            raise RuntimeError("UVC frame read failed")
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            raise RuntimeError("UVC frame size changed after startup")
        return frame

    def read_native(self):
        """Return the analysis image and untouched JPEG from the same exposure."""
        ok, frame = self.capture.read()
        if not ok or frame is None or frame.dtype != np.uint8 or frame.ndim != 2 or 1 not in frame.shape:
            raise RuntimeError("UVC did not return a native MJPEG frame")
        jpeg = frame.tobytes()
        if not jpeg.startswith(b"\xff\xd8") or not jpeg.rstrip(b"\x00").endswith(b"\xff\xd9"):
            raise RuntimeError("UVC returned invalid MJPEG data")
        step = 2 if self.width >= 2 * self.analysis_size[0] and self.height >= 2 * self.analysis_size[1] else 1
        decode = cv2.IMREAD_REDUCED_COLOR_2 if step == 2 else cv2.IMREAD_COLOR
        bgr = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), decode)
        if bgr is None or bgr.shape[:2] != ((self.height + step - 1) // step, (self.width + step - 1) // step):
            raise RuntimeError("UVC native JPEG does not match the negotiated resolution")
        return cv2.resize(bgr, self.analysis_size, interpolation=cv2.INTER_AREA), jpeg

    def close(self) -> None:
        self.capture.release()
