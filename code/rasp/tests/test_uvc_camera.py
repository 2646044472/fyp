from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from palm_app.uvc_camera import UvcCamera


class FakeCapture:
    def __init__(self, device, backend):
        self.device = device
        self.backend = backend
        self.released = False
        self.width = 640
        self.height = 360
        self.max_width = 640

    def isOpened(self):
        return True

    def set(self, prop, value):
        if prop == 3:
            self.width = min(int(value), self.max_width)
        elif prop == 4:
            self.height = int(value)
        return True

    def get(self, prop):
        if prop == 3:
            return self.width
        if prop == 4:
            return self.height
        if prop == 6:
            return ord("Y") | ord("U") << 8 | ord("Y") << 16 | ord("V") << 24
        return 0

    def read(self):
        return True, np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def release(self):
        self.released = True


def test_uvc_camera_requires_explicit_stable_device_path():
    with pytest.raises(ValueError, match="by-id"):
        UvcCamera(Path("/dev/video2"), 640, 360)


def test_uvc_camera_reports_negotiated_format_without_exposing_device_path():
    opened = []

    def open_camera(device, backend):
        opened.append(FakeCapture(device, backend))
        return opened[-1]

    stable_path = Path("/dev/v4l/by-id/usb-test-video-index0")
    with patch("palm_app.uvc_camera.Path.exists", return_value=True), \
         patch("palm_app.uvc_camera.cv2.VideoCapture", side_effect=open_camera):
        camera = UvcCamera(stable_path, 640, 360)
        frame = camera.read_bgr()
        assert frame.shape == (360, 640, 3)
        assert camera.fourcc == "YUYV"
        assert camera.capture_profile.endswith("-YUYV-640x360")
        assert "usb-test" not in camera.capture_profile
        camera.close()

    assert opened[0].released


def test_uvc_camera_releases_device_when_negotiated_resolution_is_too_small():
    capture = FakeCapture("device", 0)
    capture.max_width = 320
    with patch("palm_app.uvc_camera.Path.exists", return_value=True), \
         patch("palm_app.uvc_camera.cv2.VideoCapture", return_value=capture):
        with pytest.raises(RuntimeError, match="below requested"):
            UvcCamera(Path("/dev/v4l/by-id/usb-test-video-index0"), 640, 360)
    assert capture.released
