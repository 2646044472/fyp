import threading
import zipfile
from io import BytesIO
import re
import subprocess
import sys
import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def make_app(tmp_path, monkeypatch, *, quality_status="NO_HAND"):
    from palm_app import debug_ui

    monkeypatch.setattr(debug_ui.common, "RUNTIME", tmp_path)
    app = debug_ui.App.__new__(debug_ui.App)
    app.camera = SimpleNamespace(
        roi_mode="dynamic",
        status=lambda: {"quality_status": quality_status},
        reset_roi_background=lambda: None,
    )
    app.lock = threading.Lock()
    app.debug_writer = None
    app.debug_sample_index = 1
    app.debug_last_frame_id = None
    app.debug_requires_removal = False
    return app


def test_debug_page_javascript_parses_so_buttons_can_run():
    from palm_app import debug_ui

    script = re.search(r"<script>(.*?)</script>", debug_ui.HTML, re.DOTALL).group(1)
    result = subprocess.run(
        ["node", "--check"], input=script, text=True, capture_output=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_repeatability_start_requires_a_new_session_and_waits_for_empty_view(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch)

    message = app.start_repeatability("test01", placements=30)

    assert "test01" in message
    state = app.status()["repeatability"]
    assert state["phase"] == "await_empty"
    assert state["next_placement"] == 1
    assert state["total_placements"] == 30
    assert (tmp_path / "repeatability" / "test01").is_dir()

    with pytest.raises(RuntimeError, match="already exists"):
        app.start_repeatability("test01", placements=30)


def test_repeatability_confirm_empty_then_capture_writes_one_sample(tmp_path, monkeypatch):
    from palm_app import debug_ui

    raw = Image.new("RGB", (8, 8), color="white")
    roi = np.full((128, 128), 42, dtype=np.uint8)
    quad = np.array([[1, 1], [7, 1], [7, 7], [1, 7]], dtype=np.float32)
    current = {"quality_status": "NO_HAND"}

    class Camera:
        roi_mode = "dynamic"

        def status(self):
            return dict(current)

        def reset_roi_background(self):
            return None

        def reset_quality_gate(self):
            current["quality_status"] = "NO_HAND"

        def capture_settings(self):
            return {"camera": 0, "width": 8, "height": 8, "format": "RGB888"}

        def snapshot(self, **kwargs):
            return raw.copy(), roi.copy(), quad.copy(), {
                "quality_status": "READY",
                "roi_status": "tracking",
                "quality": {"contrast": 20.0},
            }, 17

    app = make_app(tmp_path, monkeypatch)
    app.camera = Camera()
    app.start_repeatability("test01", placements=1)
    app.confirm_repeatability_empty()
    current["quality_status"] = "READY"

    message = app.capture_repeatability_placement()

    sample_dir = tmp_path / "repeatability" / "test01" / "placement_001" / "sample_001"
    assert "complete" in message.lower()
    assert (sample_dir / "raw.png").exists()
    assert (sample_dir / "roi_128.png").exists()
    assert (sample_dir / "metadata.json").exists()
    assert app.status()["repeatability"]["phase"] == "complete"


def test_completed_repeatability_download_contains_saved_images(tmp_path, monkeypatch):
    app = make_app(tmp_path, monkeypatch)
    root = tmp_path / "repeatability" / "quick10"
    sample = root / "placement_001" / "sample_001"
    sample.mkdir(parents=True)
    (sample / "raw.png").write_bytes(b"raw-image")
    (sample / "roi_128.png").write_bytes(b"roi-image")
    (sample / "metadata.json").write_text("{}", encoding="utf-8")
    app.repeatability_root = root
    app.repeatability_phase = "complete"

    filename, payload = app.download_repeatability()

    assert filename == "quick10.zip"
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        assert sorted(archive.namelist()) == [
            "quick10/placement_001/sample_001/metadata.json",
            "quick10/placement_001/sample_001/raw.png",
            "quick10/placement_001/sample_001/roi_128.png",
        ]
        assert archive.read("quick10/placement_001/sample_001/roi_128.png") == b"roi-image"


def test_repeatability_http_api_controls_the_collection_state():
    from palm_app import debug_ui

    messages = []

    class App:
        def status(self):
            return {"quality_status": "NO_HAND", "repeatability": {"phase": "idle"}}

        def start_repeatability(self, session, *, placements):
            messages.append(("start", session, placements))
            return "started"

        def confirm_repeatability_empty(self):
            messages.append(("confirm",))
            return "confirmed"

        def capture_repeatability_placement(self):
            messages.append(("capture",))
            return "captured"

    server = ThreadingHTTPServer(("127.0.0.1", 0), debug_ui.make_handler(App()))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection(*server.server_address)
        payload = json.dumps({"session": "test01", "placements": 30}).encode()
        connection.request("POST", "/api/start-repeatability", payload, {"Content-Type": "application/json"})
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["message"] == "started"

        connection.request("POST", "/api/confirm-repeatability-empty", b"{}")
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["message"] == "confirmed"

        connection.request("POST", "/api/capture-repeatability", b"{}")
        response = connection.getresponse()
        assert response.status == 200
        assert json.loads(response.read())["message"] == "captured"
        assert messages == [("start", "test01", 30), ("confirm",), ("capture",)]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
