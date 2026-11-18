from __future__ import annotations

import threading

import numpy as np
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
