"""Copied geometry functions; no application/runtime dependency."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any,Sequence
import numpy as np
from PIL import Image
WRIST=0
INDEX_MCP=5
MIDDLE_MCP=9
PINKY_MCP=17
DEFAULT_OUTPUT_SIZE=(128,128)

class PalmROIError(ValueError):
    """Raised when landmarks cannot define a safe palm crop."""

@dataclass(frozen=True)
class PalmQuadDiagnostics:
    """Geometry evidence for one landmark set and one source image."""

    raw_quad: np.ndarray
    final_quad: np.ndarray
    fit_factor: float
    fit_applied: bool
    out_of_frame: bool
    mcp_span_px: float
    center: np.ndarray
    angle_deg: float
    raw_width_px: float
    raw_height_px: float
    final_width_px: float
    final_height_px: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "raw_quad": self.raw_quad.astype(float).tolist(),
            "final_quad": self.final_quad.astype(float).tolist(),
            "fit_factor": float(self.fit_factor),
            "fit_applied": bool(self.fit_applied),
            "out_of_frame": bool(self.out_of_frame),
            "mcp_span_px": float(self.mcp_span_px),
            "center": self.center.astype(float).tolist(),
            "angle_deg": float(self.angle_deg),
            "raw_width_px": float(self.raw_width_px),
            "raw_height_px": float(self.raw_height_px),
            "final_width_px": float(self.final_width_px),
            "final_height_px": float(self.final_height_px),
        }

def landmarks_to_palm_quad_diagnostics(
    landmarks: Sequence[Sequence[float]] | np.ndarray,
    image_size: tuple[int, int],
    *,
    width_scale: float = 1.15,
    height_scale: float = 1.25,
    center_offset: float = 0.30,
    min_span_px: float = 80.0,
    fit_to_frame: bool = False,
) -> PalmQuadDiagnostics:
    """Return raw and final palm geometry without changing ROI behavior."""

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
    raw_quad = np.stack(
        (
            center - axis_x * half_width - axis_y * half_height,
            center + axis_x * half_width - axis_y * half_height,
            center + axis_x * half_width + axis_y * half_height,
            center - axis_x * half_width + axis_y * half_height,
        )
    ).astype(np.float32)

    out_of_frame = (
        float(raw_quad[:, 0].min()) < 0
        or float(raw_quad[:, 1].min()) < 0
        or float(raw_quad[:, 0].max()) >= width
        or float(raw_quad[:, 1].max()) >= height
    )
    if out_of_frame and not fit_to_frame:
        raise PalmROIError("dynamic palm ROI is outside the frame")

    fit_factor = 1.0
    final_quad = raw_quad.copy()
    if out_of_frame:
        ratios: list[float] = []
        for x, y in raw_quad:
            dx, dy = float(x - center[0]), float(y - center[1])
            if dx > 0:
                ratios.append((width - 1.0 - float(center[0])) / dx)
            elif dx < 0:
                ratios.append((0.0 - float(center[0])) / dx)
            if dy > 0:
                ratios.append((height - 1.0 - float(center[1])) / dy)
            elif dy < 0:
                ratios.append((0.0 - float(center[1])) / dy)
        fit_factor = min(1.0, max(0.05, 0.98 * min(ratios)))
        final_quad = center + (raw_quad - center) * fit_factor

    angle_deg = float(np.degrees(np.arctan2(axis_x[1], axis_x[0])))
    return PalmQuadDiagnostics(
        raw_quad=raw_quad,
        final_quad=final_quad.astype(np.float32),
        fit_factor=fit_factor,
        fit_applied=fit_factor != 1.0,
        out_of_frame=out_of_frame,
        mcp_span_px=span_px,
        center=center.astype(np.float32),
        angle_deg=angle_deg,
        raw_width_px=float(np.linalg.norm(raw_quad[1] - raw_quad[0])),
        raw_height_px=float(np.linalg.norm(raw_quad[3] - raw_quad[0])),
        final_width_px=float(np.linalg.norm(final_quad[1] - final_quad[0])),
        final_height_px=float(np.linalg.norm(final_quad[3] - final_quad[0])),
    )

def landmarks_to_palm_quad(
    landmarks: Sequence[Sequence[float]] | np.ndarray,
    image_size: tuple[int, int],
    *,
    width_scale: float = 1.15,
    height_scale: float = 1.25,
    center_offset: float = 0.30,
    min_span_px: float = 80.0,
    fit_to_frame: bool = False,
) -> np.ndarray:
    """Return an oriented (top-left, top-right, bottom-right, bottom-left) quad.

    Landmark coordinates are MediaPipe-normalized coordinates. The horizontal
    axis follows the index-MCP to pinky-MCP line. The vertical axis points from
    the MCP line toward the wrist, so the crop follows translation, scale, and
    hand rotation while keeping finger bases near the top edge.
    """

    return landmarks_to_palm_quad_diagnostics(
        landmarks,
        image_size,
        width_scale=width_scale,
        height_scale=height_scale,
        center_offset=center_offset,
        min_span_px=min_span_px,
        fit_to_frame=fit_to_frame,
    ).final_quad

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

def inverse_square(points, side, left, top, angle):
    """PIL pixel-center inverse; undo rotation BEFORE subtracting padding."""
    p = np.asarray(points, dtype=np.float64).copy()
    x, y = p[:, 0].copy(), p[:, 1].copy()
    if angle == 90:
        p[:, 0], p[:, 1] = side - 1 - y, x
    elif angle == 270:
        p[:, 0], p[:, 1] = y, side - 1 - x
    elif angle == 180:
        p[:, 0], p[:, 1] = side - 1 - x, side - 1 - y
    elif angle != 0:
        raise ValueError('Only cardinal rotations supported')
    return p - np.array([left, top])

def crop_original(original_rgb, quad):
    """128px grayscale, original unmodified source only; existing 1/99 contrast normalization."""
    arr = np.asarray(warp_palm_roi(original_rgb, np.asarray(quad)), dtype=np.float32)
    lo, hi = np.percentile(arr, (1, 99))
    if hi - lo < 1:
        raise ValueError('Original crop has no usable intensity range')
    return Image.fromarray(np.clip((arr-lo)*255/(hi-lo),0,255).astype(np.uint8))
