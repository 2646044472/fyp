from __future__ import annotations

import threading
import time
import unittest

import numpy as np
from PIL import Image

import palm_roi


class PalmROITest(unittest.TestCase):
    @staticmethod
    def landmarks(*, angle: float = 0.0, scale: float = 1.0, offset=(0.0, 0.0)) -> np.ndarray:
        # Synthetic open-hand landmarks in normalized image coordinates.
        points = np.zeros((21, 3), dtype=np.float32)
        points[palm_roi.WRIST, :2] = (0.50, 0.78)
        points[palm_roi.INDEX_MCP, :2] = (0.34, 0.42)
        points[palm_roi.MIDDLE_MCP, :2] = (0.50, 0.38)
        points[palm_roi.PINKY_MCP, :2] = (0.66, 0.44)
        center = np.array((0.50, 0.50), dtype=np.float32)
        rotation = np.array(
            ((np.cos(angle), -np.sin(angle)), (np.sin(angle), np.cos(angle))),
            dtype=np.float32,
        )
        points[:, :2] = ((points[:, :2] - center) @ rotation.T) * scale + center + np.asarray(offset)
        return points

    def test_dynamic_quad_follows_translation(self) -> None:
        first = palm_roi.landmarks_to_palm_quad(self.landmarks(), (1280, 720))
        second = palm_roi.landmarks_to_palm_quad(self.landmarks(offset=(0.08, -0.04)), (1280, 720))
        shift = second.mean(axis=0) - first.mean(axis=0)
        self.assertAlmostEqual(float(shift[0]), 0.08 * 1280, delta=2.0)
        self.assertAlmostEqual(float(shift[1]), -0.04 * 720, delta=2.0)

    def test_dynamic_quad_rotates_with_hand(self) -> None:
        quad = palm_roi.landmarks_to_palm_quad(self.landmarks(angle=0.20), (1280, 720))
        edge = quad[1] - quad[0]
        self.assertGreater(abs(float(edge[1])), 1.0)

    def test_palm_detector_points_use_the_same_geometry(self) -> None:
        points = self.landmarks()[[palm_roi.WRIST, palm_roi.INDEX_MCP, palm_roi.MIDDLE_MCP, 13, palm_roi.PINKY_MCP]]
        detector_points = np.vstack((points, np.zeros((2, 3), dtype=np.float32)))
        expected = palm_roi.landmarks_to_palm_quad(self.landmarks(), (1280, 720))
        actual = palm_roi.palm_detection_to_palm_quad(detector_points, (1280, 720))
        np.testing.assert_allclose(actual, expected, atol=1e-4)

    def test_detector_geometry_accepts_visible_runtime_palm_span(self) -> None:
        tracker = object.__new__(palm_roi.HandLandmarkTracker)
        tracker._input_size = (320, 240)
        points = np.array(
            ((160, 190), (130, 120), (160, 110), (175, 112), (170, 120), (145, 140), (150, 150)),
            dtype=np.float32,
        )

        accepted, diagnostics = tracker._detector_geometry(points)

        self.assertTrue(accepted)
        self.assertEqual(diagnostics["reason"], "geometry_ok")
        self.assertAlmostEqual(diagnostics["mcp_span_px"], 40.0)

    def test_detector_geometry_rejects_tiny_runtime_palm_span(self) -> None:
        tracker = object.__new__(palm_roi.HandLandmarkTracker)
        tracker._input_size = (320, 240)
        points = np.array(
            ((160, 190), (145, 120), (160, 110), (165, 112), (175, 120), (150, 140), (155, 150)),
            dtype=np.float32,
        )

        accepted, diagnostics = tracker._detector_geometry(points)

        self.assertFalse(accepted)
        self.assertEqual(diagnostics["reason"], "span_too_small")
        self.assertAlmostEqual(diagnostics["mcp_span_px"], 30.0)

    def test_submit_accepts_first_candidate_without_deadlocking(self) -> None:
        class FakeCV:
            COLOR_RGB2BGR = 0

            @staticmethod
            def cvtColor(array: np.ndarray, _: int) -> np.ndarray:
                return array

        tracker = object.__new__(palm_roi.HandLandmarkTracker)
        tracker._input_size = (320, 240)
        tracker._stale_after_ms = 1500.0
        tracker._lock = threading.Lock()
        tracker._closed = False
        tracker._last_submit_monotonic = None
        tracker._submit_interval_s = 0.0
        tracker._recovery_pass = False
        tracker._handpose = None
        tracker._smoothing_alpha = 0.22
        tracker._landmarks = None
        tracker._last_seen_monotonic = None
        tracker._hand_score = None
        tracker._tracking_source = None
        tracker._last_error = None
        tracker._last_diagnostics = {}
        tracker._max_center_jump = 0.18
        tracker._min_area_ratio = 0.55
        tracker._max_area_ratio = 1.80
        tracker._cv = FakeCV()
        points = np.array(
            ((160, 190), (130, 120), (160, 110), (175, 112), (170, 120), (145, 140), (150, 150)),
            dtype=np.float32,
        )
        result = palm_roi.DetectorResult(
            points,
            0.8,
            np.array((100, 80, 220, 220), dtype=np.float32),
            {"reason": "candidate", "detection_score": 0.8},
        )
        tracker._infer = lambda _image, detector_scale=1.0: result

        worker = threading.Thread(
            target=tracker.submit,
            args=(Image.new("RGB", tracker._input_size), 1000),
            daemon=True,
        )
        worker.start()
        worker.join(timeout=1.0)

        self.assertFalse(worker.is_alive(), "submit deadlocked while accepting a palm")
        status = tracker.roi_status(tracker._input_size)
        self.assertEqual(status.status, "tracking")
        self.assertIsNotNone(status.quad)

        tracker._last_seen_monotonic = time.monotonic() - 0.3
        self.assertEqual(tracker.roi_status((480, 360), frame_timestamp_ms=1000).status, "tracking")
        self.assertEqual(tracker.roi_status((480, 360), frame_timestamp_ms=1001).status, "tracking_stale")

    def test_stale_tracking_allows_reacquisition_at_a_new_position(self) -> None:
        tracker = object.__new__(palm_roi.HandLandmarkTracker)
        tracker._input_size = (320, 240)
        tracker._stale_after_ms = 1500.0
        tracker._lock = threading.Lock()
        tracker._landmarks = self.landmarks()
        tracker._last_seen_monotonic = time.monotonic() - 2.0
        tracker._max_center_jump = 0.18
        tracker._min_area_ratio = 0.55
        tracker._max_area_ratio = 1.80
        candidate = self.landmarks(offset=(0.30, 0.0))

        self.assertTrue(tracker._is_stable_candidate(candidate, "palm_detector"))

    def test_recent_roi_is_not_an_error_after_a_later_rejected_detector_pass(self) -> None:
        tracker = object.__new__(palm_roi.HandLandmarkTracker)
        tracker._input_size = (320, 240)
        tracker._stale_after_ms = 1500.0
        tracker._lock = threading.Lock()
        tracker._landmarks = self.landmarks()
        tracker._last_seen_monotonic = time.monotonic()
        tracker._hand_score = 0.8
        tracker._last_error = "below_threshold"
        tracker._last_diagnostics = {"reason": "no_candidate"}

        status = tracker.roi_status((320, 240))

        self.assertEqual(status.status, "tracking")

    def test_palm_detector_anchor_count(self) -> None:
        anchors = palm_roi.HandLandmarkTracker._load_anchors()
        self.assertEqual(anchors.shape, (2016, 2))
        self.assertTrue(np.all((anchors > 0.0) & (anchors < 1.0)))

    def test_warp_preserves_identity_gradient(self) -> None:
        image = Image.fromarray(np.tile(np.arange(100, dtype=np.uint8), (100, 1)), mode="L")
        quad = np.array(((0, 0), (99, 0), (99, 99), (0, 99)), dtype=np.float32)
        warped = np.asarray(palm_roi.warp_palm_roi(image, quad, (32, 32)), dtype=np.float32)
        self.assertLess(abs(float(warped[16, 16]) - 51.0), 4.0)

    def test_out_of_frame_quad_is_rejected(self) -> None:
        with self.assertRaises(palm_roi.PalmROIError):
            palm_roi.landmarks_to_palm_quad(self.landmarks(offset=(0.50, 0.0)), (1280, 720))


if __name__ == "__main__":
    unittest.main()
