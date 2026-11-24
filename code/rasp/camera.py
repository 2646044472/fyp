from __future__ import annotations

import io
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

from roi import DEFAULT_CROP, normalize_crop

PREVIEW_CAPTURE_FPS = 12


def _picamera2_array_to_rgb(array):
    """Convert Picamera2 RGB888's BGR-ordered bytes to PIL RGB."""
    return Image.fromarray(array[:, :, ::-1].copy(), mode="RGB")


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
        return _picamera2_array_to_rgb(camera.capture_array("main"))
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
        self._jpeg_lock = threading.Lock()
        self.latest: Image.Image | None = None
        self.jpeg: bytes | None = None
        self._jpeg_frame_id = -1
        self._frame_id = 0
        self._latest_captured_ns: int | None = None
        self._served_context: dict[str, int | str | float | None] = {}
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self) -> None:
        frame_interval = 1.0 / PREVIEW_CAPTURE_FPS
        while self.running:
            frame_started = time.monotonic()
            try:
                image = _picamera2_array_to_rgb(self.camera.capture_array("main"))
                captured_ns = time.time_ns()
                with self.lock:
                    self.latest = image
                    self._frame_id += 1
                    self._latest_captured_ns = captured_ns
            except Exception:
                time.sleep(0.2)
                continue
            time.sleep(max(0.0, frame_interval - (time.monotonic() - frame_started)))

    def frame(self) -> Image.Image:
        with self.lock:
            if self.latest is None:
                raise RuntimeError("Waiting for the first camera frame")
            captured_ns = self._latest_captured_ns
            self._served_context = {
                "frame_id": self._frame_id,
                "captured_at": datetime.fromtimestamp((captured_ns or time.time_ns()) / 1e9, tz=UTC).isoformat(),
                "captured_at_ns": captured_ns,
            }
            return self.latest.copy()

    def capture_context(self) -> dict[str, int | str | float | None]:
        """Return metadata for the frame most recently returned by ``frame``."""
        with self.lock:
            context = dict(self._served_context)
        captured_ns = context.get("captured_at_ns")
        if isinstance(captured_ns, int):
            context["age_ms"] = max(0.0, (time.time_ns() - captured_ns) / 1_000_000)
        return context

    def jpeg_frame(self) -> bytes:
        with self._jpeg_lock:
            with self.lock:
                if self.latest is None:
                    raise RuntimeError("Waiting for the first camera frame")
                if self.jpeg is not None and self._jpeg_frame_id == self._frame_id:
                    return self.jpeg
                frame = self.latest.copy()
                frame_id = self._frame_id
            output = io.BytesIO()
            frame.save(output, format="JPEG", quality=82)
            jpeg = output.getvalue()
            with self.lock:
                if self._frame_id == frame_id:
                    self.jpeg = jpeg
                    self._jpeg_frame_id = frame_id
            return jpeg

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
