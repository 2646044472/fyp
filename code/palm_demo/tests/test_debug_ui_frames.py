from __future__ import annotations

import json
import threading
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

import debug_ui


def make_feed() -> debug_ui.CameraFeed:
    feed = debug_ui.CameraFeed.__new__(debug_ui.CameraFeed)
    feed.lock = threading.Lock()
    feed.frame_condition = threading.Condition(feed.lock)
    feed.roi_mode = "dynamic"
    feed.latest_roi_status = {"roi_status": "tracking"}
    feed.latest = debug_ui.CapturedFrame(9, Image.new("RGB", (8, 8), "red"), 2.0)
    processed_image = Image.new("RGB", (8, 8), "blue")
    feed.latest_processed = debug_ui.ProcessedFrame(
        debug_ui.CapturedFrame(7, processed_image, 1.0),
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        np.array(((1.0, 1.0), (6.0, 1.0), (6.0, 6.0), (1.0, 6.0))),
        {"roi_status": "tracking", "frame_id": 7},
    )
    return feed


def test_dynamic_snapshot_uses_the_detector_source_frame():
    feed = make_feed()

    image, _, quad, status, frame_id = feed.snapshot()

    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert frame_id == 7
    assert status["frame_id"] == 7
    assert quad is not None


def test_dynamic_snapshot_can_require_a_new_processed_frame():
    feed = make_feed()

    image, _, _, _, frame_id = feed.snapshot(after_frame_id=6)

    assert image.getpixel((0, 0)) == (0, 0, 255)
    assert frame_id == 7


def test_processed_debug_frame_uses_detector_source_image():
    feed = make_feed()

    image, _, _, frame_id, status = feed.processed_debug_frame()

    image = image.convert("RGB")
    red, green, blue = image.getpixel((0, 0))
    assert blue > red + 100
    assert blue > green + 100
    assert frame_id == 7
    assert status["frame_id"] == 7


def test_collection_session_manager_lists_and_deletes_one_session(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    session_id = "20261006T123456789012Z-a1b2c3d4"
    sample_id = "20261006T123457789012Z-e5f6a7b8"
    session_root = runtime / "highres_sessions" / session_id
    sample_root = runtime / "highres_capture" / sample_id
    session_root.mkdir(parents=True)
    sample_root.mkdir(parents=True)
    (sample_root / "full.jpg").write_bytes(b"full")
    (sample_root / "roi_128.png").write_bytes(b"roi")
    (sample_root / "metadata.json").write_text(json.dumps({"session_id": session_id}), encoding="utf-8")
    (session_root / "manifest.json").write_text(json.dumps({
        "session_id": session_id,
        "subject": "p01",
        "hand": "right",
        "background": "existing",
        "distance_cm": 30,
        "notes": "",
        "sample_ids": [sample_id],
        "phase": "await_hand",
    }), encoding="utf-8")

    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", runtime)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock()
    app.collection_lock = threading.Lock()
    app.collection_batch = {"session_id": session_id}

    sessions = app.list_highres_sessions()
    assert sessions[0]["session_id"] == session_id
    assert sessions[0]["sample_count"] == 1

    result = app.delete_highres_session(session_id)
    assert result == {"status": "DELETED", "session_id": session_id, "deleted_samples": 1, "recoverable": True}
    assert list((runtime / "collection_trash").rglob("full.jpg"))[0].read_bytes() == b"full"
    assert not session_root.exists()
    assert not sample_root.exists()
    assert app.collection_batch is None
    assert app.list_highres_sessions() == []


def test_collection_session_manager_rejects_invalid_session_id(tmp_path, monkeypatch):
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", tmp_path / "runtime")
    app = debug_ui.App.__new__(debug_ui.App)
    with pytest.raises(ValueError, match="Invalid session ID"):
        app.delete_highres_session("../runtime")


def test_delete_damaged_photos_keeps_others_and_allows_retake(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime"
    session_id = "20261029T123456000000Z-a1b2c3d4"
    ids = [f"20261029T12345600000{i}Z-{i:08x}" for i in range(1, 6)]
    root = runtime / "highres_sessions" / session_id
    root.mkdir(parents=True)
    batch = dict(session_id=session_id, subject="p01", hand="left", background="existing",
                 distance_cm=None, notes="", started_at_pi_utc="", client_time_utc="",
                 sample_ids=ids[:], phase="await_hand")
    (root / "manifest.json").write_text(json.dumps(batch), encoding="utf-8")
    for i, sample in enumerate(ids, 1):
        folder = runtime / "highres_capture" / sample
        folder.mkdir(parents=True)
        (folder / "full.jpg").write_bytes(b"original" if i <= 3 else b"")
        (folder / "metadata.json").write_text(json.dumps(dict(session_id=session_id, sample_id=sample, sample_index=i)) if i <= 3 else "", encoding="utf-8")
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", runtime)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock()
    app.collection_lock = threading.Lock()
    app.collection_batch = batch
    app.capture_only = True
    app.camera = SimpleNamespace(roi_mode="capture", capture_highres=lambda: (Image.new("RGB", (8, 8)), Image.new("RGB", (16, 16)), {}), capture_settings=lambda: {})
    assert app.latest_highres()["sample_id"] in ids[:3]
    assert app.delete_highres_sample(session_id, ids[3])["captured"] == 4
    assert (runtime / "highres_capture" / ids[4] / "metadata.json").read_bytes() == b""
    assert app.delete_highres_sample(session_id, ids[4])["captured"] == 3
    for sample in ids[:3]:
        assert (runtime / "highres_capture" / sample / "full.jpg").read_bytes() == b"original"
    assert len(list((runtime / "collection_trash").rglob("full.jpg"))) == 2
    result = app.capture_highres_batch()
    assert result["sample_index"] == 4
    assert app.highres_batch_status()["captured"] == 4


def test_cannot_delete_photo_owned_by_another_session(tmp_path, monkeypatch):
    session_id = "20261029T123456000000Z-a1b2c3d4"
    other = "20261029T123456000001Z-a1b2c3d4"
    sample = "20261029T123456000002Z-a1b2c3d4"
    root = tmp_path / "highres_sessions" / session_id
    photo = tmp_path / "highres_capture" / sample
    root.mkdir(parents=True); photo.mkdir(parents=True)
    (root / "manifest.json").write_text(json.dumps({"sample_ids": [sample]}))
    (photo / "metadata.json").write_text(json.dumps({"session_id": other}))
    monkeypatch.setattr(debug_ui.palm_demo, "RUNTIME", tmp_path)
    app = debug_ui.App.__new__(debug_ui.App)
    app.collection_batch_lock = threading.Lock();app.collection_lock = threading.Lock()
    with pytest.raises(ValueError, match="does not belong"):
        app.delete_highres_sample(session_id, sample)
    assert photo.is_dir()
