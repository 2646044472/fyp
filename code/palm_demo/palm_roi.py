#!/usr/bin/env python3
"""Palm detection and geometry-based palm ROI extraction.

The Pi 4 runtime uses the small OpenCV DNN palm detector. It is the detector
stage from the MediaPipe Hands pipeline, exported as an ONNX model, so the
runtime does not depend on a MediaPipe wheel compiled for newer ARM crypto
extensions. The geometry tests and fixed-ROI path remain usable without the
optional detector model.
"""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from PIL import Image


WRIST = 0
INDEX_MCP = 5
MIDDLE_MCP = 9
PINKY_MCP = 17
DEFAULT_OUTPUT_SIZE = (128, 128)
ROI_GEOMETRY_VERSION = "palm-detector-mcp-v2"
PALM_DETECTOR_INPUT_SIZE = (192, 192)
PALM_DETECTOR_LANDMARKS = (0, 5, 9, 13, 17, 1, 2)
RUNTIME_ROI_WIDTH_SCALE = 2.0
RUNTIME_ROI_HEIGHT_SCALE = 2.0


class PalmROIError(ValueError):
    """Raised when landmarks cannot define a safe palm crop."""


@dataclass(frozen=True)
class ROIStatus:
    quad: np.ndarray | None
    status: str
    hand_score: float | None = None
    age_ms: float | None = None
    span_px: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "roi_mode": "dynamic",
            "roi_geometry": ROI_GEOMETRY_VERSION,
            "roi_status": self.status,
            "hand_score": self.hand_score,
            "roi_age_ms": self.age_ms,
            "roi_span_px": self.span_px,
        }


def landmarks_to_palm_quad(
    landmarks: Sequence[Sequence[float]] | np.ndarray,
    image_size: tuple[int, int],
    *,
    width_scale: float = 1.15,
    height_scale: float = 1.25,
    center_offset: float = 0.30,
    min_span_px: float = 80.0,
) -> np.ndarray:
    """Return an oriented (top-left, top-right, bottom-right, bottom-left) quad.

    Landmark coordinates are MediaPipe-normalized coordinates. The horizontal
    axis follows the index-MCP to pinky-MCP line. The vertical axis points from
    the MCP line toward the wrist, so the crop follows translation, scale, and
    hand rotation while keeping finger bases near the top edge.
    """

    points = np.asarray(landmarks, dtype=np.float32)
    if points.ndim != 2 or points.shape[0] <= PINKY_MCP or points.shape[1] < 2:
        raise PalmROIError("at least 18 landmarks with x/y coordinates are required")
    if not np.isfinite(points[:, :2]).all():
        raise PalmROIError("landmarks contain non-finite coordinates")

    width, height = image_size
    if width <= 0 or height <= 0:
        raise PalmROIError("image size must be positive")

    scale = np.array([float(width), float(height)], dtype=np.float32)
    wrist, index_mcp, middle_mcp, pinky_mcp = (
        points[index, :2] * scale
        for index in (WRIST, INDEX_MCP, MIDDLE_MCP, PINKY_MCP)
    )

    across = pinky_mcp - index_mcp
    span_px = float(np.linalg.norm(across))
    if not np.isfinite(span_px) or span_px < min_span_px:
        raise PalmROIError(f"palm span is too small ({span_px:.1f}px)")
    axis_x = across / span_px

    toward_wrist = wrist - middle_mcp
    toward_wrist -= axis_x * float(np.dot(toward_wrist, axis_x))
    direction_norm = float(np.linalg.norm(toward_wrist))
    if not np.isfinite(direction_norm) or direction_norm < min_span_px * 0.25:
        raise PalmROIError("wrist and MCP landmarks do not define a stable axis")
    axis_y = toward_wrist / direction_norm

    center = (index_mcp + pinky_mcp) * 0.5 + axis_y * span_px * center_offset
    half_width = span_px * width_scale * 0.5
    half_height = span_px * height_scale * 0.5
    quad = np.stack(
        (
            center - axis_x * half_width - axis_y * half_height,
            center + axis_x * half_width - axis_y * half_height,
            center + axis_x * half_width + axis_y * half_height,
            center - axis_x * half_width + axis_y * half_height,
        )
    ).astype(np.float32)

    # Do not silently pad or clip a hand that is partly outside the camera.
    if (
        float(quad[:, 0].min()) < 0
        or float(quad[:, 1].min()) < 0
        or float(quad[:, 0].max()) >= width
        or float(quad[:, 1].max()) >= height
    ):
        raise PalmROIError("dynamic palm ROI is outside the frame")
    return quad


def palm_detection_to_palm_quad(
    palm_landmarks: Sequence[Sequence[float]] | np.ndarray,
    image_size: tuple[int, int],
    **kwargs: float,
) -> np.ndarray:
    """Convert the detector's seven palm keypoints to the shared ROI geometry.

    The detector returns seven points in this order: wrist, index MCP, middle
    MCP, ring MCP, pinky MCP, thumb CMC and thumb MCP. The first five points
    are enough to construct the palm crop, while the remaining two are kept by
    the detector for compatibility with the upstream palm model.
    """

    points = np.asarray(palm_landmarks, dtype=np.float32)
    if points.ndim != 2 or points.shape[0] < 5 or points.shape[1] < 2:
        raise PalmROIError("seven palm detector landmarks with x/y are required")
    synthetic = np.zeros((18, points.shape[1]), dtype=np.float32)
    for source, target in zip((0, 1, 2, 3, 4), (WRIST, INDEX_MCP, MIDDLE_MCP, 13, PINKY_MCP)):
        synthetic[target] = points[source]
    return landmarks_to_palm_quad(synthetic, image_size, **kwargs)


def _perspective_coefficients(
    source_quad: np.ndarray, output_size: tuple[int, int]
) -> tuple[float, ...]:
    """Build PIL's output-to-source perspective coefficients."""

    output_width, output_height = output_size
    destination = np.array(
        (
            (0.0, 0.0),
            (float(output_width - 1), 0.0),
            (float(output_width - 1), float(output_height - 1)),
            (0.0, float(output_height - 1)),
        ),
        dtype=np.float64,
    )
    source = np.asarray(source_quad, dtype=np.float64)
    if source.shape != (4, 2):
        raise PalmROIError("source quad must have shape (4, 2)")

    matrix: list[list[float]] = []
    values: list[float] = []
    for (x, y), (u, v) in zip(destination, source):
        matrix.append([x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y])
        values.append(u)
        matrix.append([0.0, 0.0, 0.0, x, y, 1.0, -v * x, -v * y])
        values.append(v)
    try:
        coefficients = np.linalg.solve(np.asarray(matrix), np.asarray(values))
    except np.linalg.LinAlgError as error:
        raise PalmROIError("dynamic palm ROI is degenerate") from error
    return tuple(float(value) for value in coefficients)


def warp_palm_roi(
    image: Image.Image,
    source_quad: np.ndarray,
    output_size: tuple[int, int] = DEFAULT_OUTPUT_SIZE,
) -> Image.Image:
    """Perspective-warp an oriented source quadrilateral to a fixed ROI."""

    if output_size[0] < 2 or output_size[1] < 2:
        raise PalmROIError("output size must be at least 2x2")
    gray = image.convert("L")
    return gray.transform(
        output_size,
        Image.Transform.PERSPECTIVE,
        _perspective_coefficients(source_quad, output_size),
        resample=Image.Resampling.BILINEAR,
    )


class HandLandmarkTracker:
    """Palm tracker with an OpenCV DNN detector and NoIR foreground fallback."""

    def __init__(
        self,
        model_path: Path,
        *,
        input_size: tuple[int, int] = (640, 360),
        stale_after_ms: float = 500.0,
        smoothing_alpha: float = 0.18,
        min_hand_detection_confidence: float = 0.5,
        min_hand_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        if not model_path.is_file():
            raise RuntimeError(f"Palm detector model not found: {model_path}")
        if not (0.0 < smoothing_alpha <= 1.0):
            raise ValueError("smoothing_alpha must be in (0, 1]")

        try:
            import cv2
        except ImportError as error:
            raise RuntimeError(
                "Dynamic ROI requires OpenCV with the DNN module; run install_pi.sh first."
            ) from error

        self._cv = cv2
        self._input_size = input_size
        self._stale_after_ms = stale_after_ms
        self._smoothing_alpha = smoothing_alpha
        self._min_detection_confidence = min_hand_detection_confidence
        self._lock = threading.Lock()
        self._landmarks: np.ndarray | None = None
        self._last_seen_monotonic: float | None = None
        self._last_submit_monotonic: float | None = None
        self._hand_score: float | None = None
        self._tracking_source: str | None = None
        self._closed = False
        self._last_error: str | None = None
        self._background_gray: np.ndarray | None = None
        self._detector = self._cv.dnn.readNet(str(model_path))
        self._detector.setPreferableBackend(self._cv.dnn.DNN_BACKEND_OPENCV)
        self._detector.setPreferableTarget(self._cv.dnn.DNN_TARGET_CPU)
        self._anchors = self._load_anchors()

    @staticmethod
    def _load_anchors() -> np.ndarray:
        """Generate the 2016 anchors used by MediaPipe's 192px palm model."""

        anchors: list[list[float]] = []
        for y in range(24):
            for x in range(24):
                center = [(x + 0.5) / 24.0, (y + 0.5) / 24.0]
                anchors.extend([center, center.copy()])
        for y in range(12):
            for x in range(12):
                center = [(x + 0.5) / 12.0, (y + 0.5) / 12.0]
                anchors.extend([center] * 6)
        return np.asarray(anchors, dtype=np.float32)

    def _infer(self, image: np.ndarray) -> tuple[np.ndarray, float] | None:
        """Run the palm detector and return seven points in source pixels."""

        cv = self._cv
        height, width = image.shape[:2]
        model_width, model_height = PALM_DETECTOR_INPUT_SIZE
        ratio = min(model_height / height, model_width / width)
        resized_shape = (np.asarray((height, width), dtype=np.float32) * ratio).astype(np.int32)
        resized = cv.resize(image, (int(resized_shape[1]), int(resized_shape[0])))
        pad_h = model_height - int(resized_shape[0])
        pad_w = model_width - int(resized_shape[1])
        left = pad_w // 2
        top = pad_h // 2
        padded = cv.copyMakeBorder(
            resized,
            top,
            pad_h - top,
            left,
            pad_w - left,
            cv.BORDER_CONSTANT,
            value=(0, 0, 0),
        )
        rgb = cv.cvtColor(padded, cv.COLOR_BGR2RGB).astype(np.float32) / 255.0
        self._detector.setInput(rgb[np.newaxis, ...])
        outputs = self._detector.forward(self._detector.getUnconnectedOutLayersNames())

        scores = outputs[1][0, :, 0].astype(np.float64)
        scores = 1.0 / (1.0 + np.exp(-scores))
        best = int(np.argmax(scores))
        score = float(scores[best])
        if score < self._min_detection_confidence:
            return None

        box_delta = outputs[0][0, :, 0:4]
        landmark_delta = outputs[0][0, :, 4:]
        input_size = np.asarray(PALM_DETECTOR_INPUT_SIZE, dtype=np.float32)
        # Decode in square model pixels, then undo letterbox padding and resize
        # independently for x/y. A scalar max(width, height) stretches y on
        # 16:9 frames and rejects valid detections as bad geometry.
        center_delta = box_delta[:, :2] / input_size
        size_delta = box_delta[:, 2:] / input_size
        # Decode the box as well. This keeps the model output interpretation
        # explicit and makes it easy to add a box sanity check later.
        _box = np.concatenate(
            (
                (center_delta[best] - size_delta[best] / 2.0 + self._anchors[best]) * input_size,
                (center_delta[best] + size_delta[best] / 2.0 + self._anchors[best]) * input_size,
            )
        )
        points = landmark_delta[best].reshape(7, 2) / input_size
        points = (points + self._anchors[best]) * input_size
        points -= np.asarray((left, top), dtype=np.float32)
        points /= ratio
        if not np.isfinite(points).all():
            return None
        return points.astype(np.float32), score

    def _foreground_landmarks(self, image: np.ndarray) -> np.ndarray | None:
        """Return normalized pseudo-landmarks for a hand entering a static NoIR view.

        The DNN model is trained on RGB hand images and can miss a hand under
        IR illumination. This fallback learns the empty, fixed camera view,
        segments the foreground by contrast, then uses the thickest part of the
        connected component as the palm centre. It is deliberately used only
        when the model does not produce a geometrically valid palm.
        """

        cv = self._cv
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY).astype(np.float32)
        height, width = gray.shape
        if self._background_gray is None:
            self._background_gray = gray
            return None

        delta = gray - self._background_gray
        # Camera auto-exposure can shift the whole image when a hand enters.
        # Remove that global shift before looking for local foreground change.
        delta -= float(np.median(delta))
        difference = np.clip(np.abs(delta), 0, 255).astype(np.uint8)
        mask = cv.threshold(difference, 24, 255, cv.THRESH_BINARY)[1]
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, np.ones((13, 13), np.uint8))
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        minimum_area = max(900.0, float(width * height) * 0.008)
        candidates = [contour for contour in contours if cv.contourArea(contour) >= minimum_area]
        if not candidates:
            # Update only on genuinely empty frames, so a held hand does not
            # become part of the reference background.
            self._background_gray = 0.96 * self._background_gray + 0.04 * gray
            return None

        contour = max(candidates, key=cv.contourArea)
        component = np.zeros((height, width), dtype=np.uint8)
        cv.drawContours(component, [contour], -1, 255, thickness=cv.FILLED)
        distance = cv.distanceTransform(component, cv.DIST_L2, 5)
        _, radius, _, centre_xy = cv.minMaxLoc(distance)
        minimum_radius = max(14.0, min(width, height) * 0.035)
        if radius < minimum_radius:
            return None

        center = np.asarray(centre_xy, dtype=np.float32)
        ys, xs = np.nonzero(component)
        coordinates = np.column_stack((xs, ys)).astype(np.float32)
        local = coordinates[np.linalg.norm(coordinates - center, axis=1) <= radius * 2.4]
        if len(local) >= 10:
            eigenvalues, eigenvectors = np.linalg.eigh(np.cov(local, rowvar=False))
            axis_y = eigenvectors[:, int(np.argmax(eigenvalues))].astype(np.float32)
        else:
            axis_y = np.asarray((0.0, 1.0), dtype=np.float32)

        # Prefer the direction toward the nearest image edge as the wrist side.
        edge_vectors = (
            np.asarray((-center[0], 0.0), dtype=np.float32),
            np.asarray((width - 1.0 - center[0], 0.0), dtype=np.float32),
            np.asarray((0.0, -center[1]), dtype=np.float32),
            np.asarray((0.0, height - 1.0 - center[1]), dtype=np.float32),
        )
        wrist_direction = min(edge_vectors, key=lambda vector: float(np.linalg.norm(vector)))
        if float(np.dot(axis_y, wrist_direction)) < 0:
            axis_y = -axis_y
        axis_y /= max(float(np.linalg.norm(axis_y)), 1e-6)
        axis_x = np.asarray((-axis_y[1], axis_y[0]), dtype=np.float32)

        # The inscribed-circle radius is conservative. Include component
        # extent so a full hand does not collapse into a tiny central crop.
        x0, y0, component_width, component_height = cv.boundingRect(contour)
        del x0, y0
        extent = min(float(component_width), float(component_height))
        span = max(radius * 2.0, extent * 0.72, min(width, height) * 0.16, 64.0)
        mcp_midpoint = center - axis_y * span * 0.30
        points = np.zeros((7, 2), dtype=np.float32)
        points[0] = center + axis_y * span * 0.50  # wrist
        points[1] = mcp_midpoint - axis_x * span * 0.50  # index MCP
        points[2] = mcp_midpoint  # middle MCP
        points[3] = mcp_midpoint + axis_x * span * 0.25  # ring MCP
        points[4] = mcp_midpoint + axis_x * span * 0.50  # pinky MCP
        points[5] = mcp_midpoint - axis_x * span * 0.65  # thumb CMC
        points[6] = mcp_midpoint - axis_x * span * 0.45  # thumb MCP
        return points / np.asarray((width, height), dtype=np.float32)

    def submit(self, image: Image.Image, timestamp_ms: int) -> None:
        """Run detection on a downscaled RGB frame, throttled to the camera rate."""

        del timestamp_ms
        now = time.monotonic()
        with self._lock:
            if self._closed:
                return
            if self._last_submit_monotonic is not None and now - self._last_submit_monotonic < 0.08:
                return
            self._last_submit_monotonic = now
        try:
            resized = image.resize(self._input_size, Image.Resampling.BILINEAR)
            rgb = np.asarray(resized.convert("RGB"), dtype=np.uint8)
            bgr = self._cv.cvtColor(rgb, self._cv.COLOR_RGB2BGR)
            detected = self._infer(bgr)
            fallback = None
            points: np.ndarray | None = None
            score: float | None = None
            source: str | None = None
            if detected is not None:
                detected_points, detected_score = detected
                detected_points = detected_points / np.asarray(self._input_size, dtype=np.float32)
                try:
                    palm_detection_to_palm_quad(detected_points, self._input_size, width_scale=RUNTIME_ROI_WIDTH_SCALE, height_scale=RUNTIME_ROI_HEIGHT_SCALE)
                except PalmROIError:
                    pass
                else:
                    points, score, source = detected_points, detected_score, "dnn"
            if points is None:
                fallback = self._foreground_landmarks(bgr)
            if points is None and fallback is not None:
                points, source = fallback, "foreground"
            with self._lock:
                if points is None:
                    self._last_error = None
                    return
                if self._landmarks is None or source != self._tracking_source:
                    self._landmarks = points
                else:
                    alpha = self._smoothing_alpha
                    self._landmarks = alpha * points + (1.0 - alpha) * self._landmarks
                self._last_seen_monotonic = now
                self._hand_score = score
                self._tracking_source = source
                self._last_error = None
        except Exception as error:
            with self._lock:
                self._last_error = str(error)

    def roi_status(self, image_size: tuple[int, int]) -> ROIStatus:
        with self._lock:
            landmarks = None if self._landmarks is None else self._landmarks.copy()
            last_seen = self._last_seen_monotonic
            hand_score = self._hand_score
            tracking_source = self._tracking_source
            last_error = self._last_error
        if landmarks is None:
            return ROIStatus(None, "no_hand", hand_score=hand_score)
        age_ms = None if last_seen is None else (time.monotonic() - last_seen) * 1000.0
        if age_ms is None or age_ms > self._stale_after_ms:
            return ROIStatus(None, "tracking_lost", hand_score=hand_score, age_ms=age_ms)
        try:
            quad = palm_detection_to_palm_quad(landmarks, image_size, width_scale=RUNTIME_ROI_WIDTH_SCALE, height_scale=RUNTIME_ROI_HEIGHT_SCALE)
        except PalmROIError:
            return ROIStatus(None, "bad_geometry", hand_score=hand_score, age_ms=age_ms)
        if tracking_source == "foreground":
            status = "tracking_fallback" if age_ms <= 150.0 else "tracking_fallback_stale"
        else:
            status = "tracking" if age_ms <= 150.0 else "tracking_stale"
        if last_error:
            status = "tracker_error"
        return ROIStatus(
            quad,
            status,
            hand_score=hand_score,
            age_ms=age_ms,
            span_px=float(np.linalg.norm(quad[1] - quad[0]) / RUNTIME_ROI_WIDTH_SCALE),
        )

    def reset_background(self) -> None:
        """Discard the NoIR foreground reference before a new framing attempt."""

        with self._lock:
            self._background_gray = None
            self._landmarks = None
            self._last_seen_monotonic = None
            self._hand_score = None
            self._tracking_source = None
            self._last_error = None

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
        self._detector = None
