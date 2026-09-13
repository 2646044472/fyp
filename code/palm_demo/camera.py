from __future__ import annotations

import io
import threading
import time
from pathlib import Path

from PIL import Image

from roi import DEFAULT_CROP, normalize_crop


def capture_image(camera_index: int, width: int, height: int, warmup: float) -> Image.Image:
    try:
        from picamera2 import Picamera2
    except ImportError as error:
        raise RuntimeError("Picamera2 is unavailable. Install it with install_pi.sh or use --image.") from error
    camera = Picamera2(camera_index)
    config = camera.create_still_configuration(main={"size": (width, height), "format": "RGB888"})
    camera.configure(config)
    camera.start()
    try:
        time.sleep(warmup)
        return Image.fromarray(camera.capture_array("main"), mode="RGB")
    finally:
        camera.stop()
        camera.close()


class CameraFeed:
    def __init__(self, camera_index: int, width: int, height: int) -> None:
        try:
            from picamera2 import Picamera2
        except ImportError as error:
            raise RuntimeError("Picamera2 is unavailable. Install it with install_pi.sh.") from error
        self.camera = Picamera2(camera_index)
        config = self.camera.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
        self.camera.configure(config)
        self.camera.start()
        self.lock = threading.Lock()
        self.latest: Image.Image | None = None
        self.jpeg: bytes | None = None
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self) -> None:
        while self.running:
            try:
                image = Image.fromarray(self.camera.capture_array("main"), mode="RGB")
                output = io.BytesIO()
                image.save(output, format="JPEG", quality=82)
                with self.lock:
                    self.latest = image
                    self.jpeg = output.getvalue()
            except Exception:
                time.sleep(0.2)

    def frame(self) -> Image.Image:
        with self.lock:
            if self.latest is None:
                raise RuntimeError("Waiting for the first camera frame")
            return self.latest.copy()

    def jpeg_frame(self) -> bytes:
        with self.lock:
            if self.jpeg is None:
                raise RuntimeError("Waiting for the first camera frame")
            return self.jpeg

    def roi_frame(self) -> bytes:
        roi, _ = normalize_crop(self.frame(), DEFAULT_CROP)
        output = io.BytesIO()
        Image.fromarray(roi, mode="L").resize((384, 384), Image.Resampling.NEAREST).save(output, format="JPEG", quality=88)
        return output.getvalue()

    def close(self) -> None:
        self.running = False
        self.thread.join(timeout=2)
        self.camera.stop()
        self.camera.close()
