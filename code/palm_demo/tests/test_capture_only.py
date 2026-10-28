import io
import json
import re
import subprocess
import threading
import zipfile
import sys
import time
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from types import SimpleNamespace

from PIL import Image
import numpy as np
import pytest

from palm_app import debug_ui
from capture_page import HTML


def make_app(tmp_path, monkeypatch):
    monkeypatch.setattr(debug_ui.common, "RUNTIME", tmp_path)
    def forbidden(*args, **kwargs):
        raise AssertionError("ROI/recognition must not run during raw collection")
    monkeypatch.setattr(debug_ui, "load_algorithm", forbidden)
    monkeypatch.setattr(debug_ui, "DemoFlow", forbidden)
    camera = SimpleNamespace(capture_only=True, roi_mode="capture", snapshot=forbidden,
        status=lambda: {"mode": "capture_only", "roi_processing": False, "camera_ready": True, "capture_size": [3280, 2464]},
        capture_settings=lambda: {"roi_mode": "capture", "roi_processing": False},
        capture_highres=lambda: (Image.new("RGB", (480, 360)), Image.new("RGB", (3280, 2464), "#abcdef"), {"ExposureTime": 30000, "AnalogueGain": 2.0}))
    app = debug_ui.App(camera)
    app.detect_full_still = forbidden
    return app


def test_native_capture_saves_only_original_and_metadata_without_roi(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch)
    app.start_highres_batch({"subject": "p01", "hand": "left", "background": "existing"})
    result = app.capture_highres_batch("2026-10-12T12:00:00Z")
    folder = tmp_path / "highres_capture" / result["sample_id"]
    assert {p.name for p in folder.iterdir()} == {"full.jpg", "metadata.json"}
    with Image.open(folder / "full.jpg") as image:
        assert image.size == (3280, 2464)
    metadata = json.loads((folder / "metadata.json").read_text())
    assert metadata["roi_processing"] == "deferred"
    assert metadata["roi_available"] is False
    assert metadata["roi_error"] is None
    assert metadata["client_time_utc"] == "2026-10-12T12:00:00Z"
    assert app.algorithm is None and app.demo is None
    name, archive = app.download_highres_batch(result["session_id"])
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        assert len(bundle.namelist()) == 3
        assert all(p.endswith(("full.jpg", "metadata.json", "manifest.json")) for p in bundle.namelist())
    app.abandon_highres_batch()
    assert folder.is_dir()


def test_capture_page_and_status_work_but_recognition_is_disabled(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch)
    server = ThreadingHTTPServer(("127.0.0.1", 0), debug_ui.make_handler(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for route in ("/", "/collect"):
            connection = HTTPConnection(*server.server_address)
            connection.request("GET", route)
            response = connection.getresponse()
            assert response.status == 200
            assert response.read().decode() == HTML
            connection.close()
        for method, route in (("GET", "/roi.jpg"), ("GET", "/demo"), ("POST", "/api/enroll")):
            connection = HTTPConnection(*server.server_address)
            connection.request(method, route)
            assert connection.getresponse().status == 404
            connection.close()
        assert app.status()["roi_processing"] is False
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_capture_page_javascript_is_valid_and_has_no_roi_endpoint():
    script = re.search(r"<script>(.*?)</script>", HTML, re.DOTALL).group(1)
    result = subprocess.run(["node", "--check"], input=script, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "/roi.jpg" not in HTML and "/api/demo/" not in HTML


def test_camera_capture_only_starts_preview_without_inference_thread(monkeypatch):
    class Camera:
        camera_properties = {"PixelArraySize": (3280, 2464)}
        def __init__(self, *args, **kwargs):
            pass
        def create_video_configuration(self, **kwargs):
            return kwargs
        create_still_configuration = create_video_configuration
        def configure(self, config):
            pass
        def start(self):
            pass
        def capture_array(self, name):
            time.sleep(0.005)
            return np.full((360, 480, 3), 100, dtype=np.uint8)
        def stop(self):
            pass
        def close(self):
            pass
    def forbidden(*args, **kwargs):
        raise AssertionError("No model may be constructed in capture-only mode")
    monkeypatch.setitem(sys.modules, "picamera2", SimpleNamespace(Picamera2=Camera))
    monkeypatch.setattr(debug_ui, "PKLNetTracker", forbidden)
    monkeypatch.setattr(debug_ui.palm_roi, "HandLandmarkTracker", forbidden)
    feed = debug_ui.CameraFeed(0, 480, 360, roi_mode="pklnet", hand_model=None,
        hand_pose_model=None, refine_pose=False, inference_ms=800, input_size=(320, 240),
        recovery_pass=False, camera_tuning_file=None, capture_only=True)
    try:
        deadline = time.monotonic() + 2
        while not feed.status()["camera_ready"] and time.monotonic() < deadline:
            time.sleep(0.01)
        assert feed.status()["camera_ready"]
        assert feed.status()["roi_processing"] is False
        assert feed.processing_thread is None and feed.tracker is None
        assert feed.capture_settings()["roi_processing"] is False
    finally:
        feed.close()


def test_disconnected_camera_does_not_advertise_cached_frame_as_ready(monkeypatch):
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed.capture_only = True
    feed.jpeg = b"cached preview"
    feed.still_size = (2592, 1944)
    feed.latest_roi_status = {}
    feed.latest = debug_ui.CapturedFrame(17, Image.new("RGB", (4, 4)), 10.0)
    monkeypatch.setattr(debug_ui.time, "monotonic", lambda: 11.0)
    assert feed.status()["camera_ready"]
    assert feed.jpeg_frame() == b"cached preview"

    monkeypatch.setattr(debug_ui.time, "monotonic", lambda: 16.0)
    status = feed.status()
    assert not status["camera_ready"]
    assert status["latest_frame_age_ms"] == 6000
    assert "frames stopped" in status["error"]
    with pytest.raises(RuntimeError, match="frames stopped"):
        feed.jpeg_frame()
    # No camera_io_lock is installed: stale capture must fail before waiting on
    # the device lock, which may be held by the disconnected capture thread.
    with pytest.raises(RuntimeError, match="frames stopped"):
        feed.capture_highres()


def test_unavailable_preview_returns_http_503():
    def unavailable():
        raise RuntimeError("Camera frames stopped")

    app = SimpleNamespace(capture_only=True, camera=SimpleNamespace(jpeg_frame=unavailable))
    server = ThreadingHTTPServer(("127.0.0.1", 0), debug_ui.make_handler(app))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection(*server.server_address)
        connection.request("GET", "/frame.jpg")
        response = connection.getresponse()
        assert response.status == 503
        assert "frames stopped" in json.loads(response.read())["message"]
        connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
