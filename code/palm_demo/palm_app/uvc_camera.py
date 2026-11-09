"""Explicitly selected UVC camera for local development on X."""
from __future__ import annotations

import hashlib
from pathlib import Path

import cv2


class UvcCamera:
    def __init__(self, device: Path, width: int, height: int) -> None:
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

    def close(self) -> None:
        self.capture.release()
