import io
from pathlib import Path
import sys
import threading
import time
from types import ModuleType

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import camera


def _bgr_frame():
    frame = np.zeros((64, 64, 3), dtype=np.uint8)
    frame[:, :32] = (0, 20, 240)     # BGR red
    frame[:, 32:] = (240, 20, 0)     # BGR blue
    return frame


class FakePicamera2:
    def __init__(self, index):
        self.index = index
        self.array = _bgr_frame()
        self.first_capture = threading.Event()
        self.config = None
        self.started = 0
        self.stopped = 0
        self.closed = 0

    def create_still_configuration(self, **kwargs):
        return ("still", kwargs)

    def create_video_configuration(self, **kwargs):
        return ("video", kwargs)

    def configure(self, config):
        self.config = config

    def start(self):
        self.started += 1

    def capture_array(self, stream):
        assert stream == "main"
        self.first_capture.set()
        return self.array.copy()

    def stop(self):
        self.stopped += 1

    def close(self):
        self.closed += 1


def _install_fake(monkeypatch):
    camera_instance = FakePicamera2(0)
    module = ModuleType("picamera2")
    module.Picamera2 = lambda index: camera_instance
    monkeypatch.setitem(sys.modules, "picamera2", module)
    return camera_instance


def test_capture_image_uses_picamera2_rgb888_channel_order(monkeypatch):
    fake = _install_fake(monkeypatch)

    image = camera.capture_image(0, 64, 64, warmup=0)

    assert image.mode == "RGB"
    assert image.getpixel((16, 32)) == (240, 20, 0)
    assert image.getpixel((48, 32)) == (0, 20, 240)
    assert fake.config == ("still", {"main": {"size": (64, 64), "format": "RGB888"}})
    assert fake.started == fake.stopped == fake.closed == 1


def test_camera_feed_preview_preserves_capture_frame_size(monkeypatch):
    fake = _install_fake(monkeypatch)
    fake.array = np.zeros((480, 640, 3), dtype=np.uint8)
    feed = camera.CameraFeed(0, 640, 480)
    try:
        assert fake.first_capture.wait(timeout=1.0), "feed did not capture its first frame"
        feed.running = False
        feed.thread.join(timeout=1.0)
        frame = feed.frame()
        assert frame.size == (640, 480)
        jpeg = Image.open(io.BytesIO(feed.jpeg_frame()))
        assert jpeg.size == (640, 480)
        assert frame.size == (640, 480)
    finally:
        feed.close()


def test_camera_feed_frame_and_jpeg_use_picamera2_rgb888_channel_order(monkeypatch):
    fake = _install_fake(monkeypatch)
    jpeg_encodes = []
    original_save = Image.Image.save

    def count_jpeg_encode(image, output, format=None, **kwargs):
        if format == "JPEG":
            jpeg_encodes.append(True)
        return original_save(image, output, format=format, **kwargs)

    monkeypatch.setattr(Image.Image, "save", count_jpeg_encode)
    feed = camera.CameraFeed(0, 64, 64)
    try:
        assert fake.first_capture.wait(timeout=1.0), "feed did not capture its first frame"
        deadline = time.monotonic() + 1.0
        while feed.latest is None and time.monotonic() < deadline:
            time.sleep(0.001)

        frame = feed.frame()
        assert frame.mode == "RGB"
        assert frame.getpixel((16, 32)) == (240, 20, 0)
        assert frame.getpixel((48, 32)) == (0, 20, 240)

        feed.running = False
        feed.thread.join(timeout=1.0)
        assert not feed.thread.is_alive()
        assert feed.jpeg is None
        assert jpeg_encodes == []

        jpeg_bytes = feed.jpeg_frame()
        assert jpeg_encodes == [True]
        assert feed.jpeg_frame() == jpeg_bytes
        assert jpeg_encodes == [True]
        jpeg = Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
        red = jpeg.getpixel((16, 32))
        blue = jpeg.getpixel((48, 32))
        assert red[0] > red[2] * 3
        assert blue[2] > blue[0] * 3
        assert fake.config == ("video", {"main": {"size": (64, 64), "format": "RGB888"}})
    finally:
        feed.close()

    assert fake.started == fake.stopped == fake.closed == 1
