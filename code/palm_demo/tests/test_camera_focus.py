from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from palm_app import camera_focus


def test_continuous_focus_status_is_not_claimed_as_convergence(monkeypatch):
    monkeypatch.setattr(camera_focus, "find_device", lambda: "/dev/mock-camera")
    monkeypatch.setattr(camera_focus, "command", lambda *args:
                        "focus_automatic_continuous: 1\nfocus_absolute: 4\n")
    result = camera_focus.status()
    assert result["supported"] and result["continuous"]
    assert result["position"] == 4
    assert "does not prove" in result["note"]


def test_unavailable_camera_reports_unsupported(monkeypatch):
    def unavailable():
        raise RuntimeError("Camera missing")
    monkeypatch.setattr(camera_focus, "find_device", unavailable)
    result = camera_focus.status()
    assert result["supported"] is False
    assert result["message"] == "Camera missing"
