#!/usr/bin/env python3
"""Offline ROI geometry diagnosis for debug-capture datasets.

This tool deliberately does not change the runtime ROI configuration.  It
reconstructs the detector geometry from the saved evidence, evaluates a small
set of geometry-only alternatives on the same frames, and writes images/CSV
that make boundary fitting visible.

Legacy samples that predate the diagnostic fields are marked as reconstructed:
their detector keypoints are available, but accepted landmarks and the exact
pre-fit quad were not saved at capture time.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageDraw

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from palm_app import common  # noqa: E402
from palm_app import palm_roi  # noqa: E402


@dataclass
class SampleRecord:
    path: Path
    raw_image: Image.Image
    roi_image: Image.Image
    metadata: dict[str, Any]
    landmarks: np.ndarray | None
    diagnostics: dict[str, Any] | None
    missing: list[str]
    reconstructed: bool


def _finite_points(value: Any, count: int = 5) -> np.ndarray | None:
    try:
        points = np.asarray(value, dtype=np.float32)
    except (TypeError, ValueError):
        return None
    if points.ndim != 2 or points.shape[0] < count or points.shape[1] < 2:
        return None
    if not np.isfinite(points[:, :2]).all():
        return None
    return points[:, :2]


def _detector_landmarks_from_metadata(metadata: dict[str, Any], raw_size: tuple[int, int]) -> tuple[np.ndarray | None, list[str], bool]:
    status = metadata.get("roi_status", {})
    diagnostics = status.get("roi_diagnostics", {}) if isinstance(status, dict) else {}
    accepted = _finite_points(diagnostics.get("accepted_landmarks_source_px"), count=18)
    if accepted is not None:
        width, height = raw_size
        return accepted / np.asarray((width, height), dtype=np.float32), [], False

    raw = _finite_points(diagnostics.get("raw_detector_landmarks_source_px"), count=5)
    if raw is None:
        raw = _finite_points(diagnostics.get("raw_detector_landmarks_input_px"), count=5)
        if raw is not None:
            source_size = diagnostics.get("source_size") or metadata.get("camera_settings", {}).get("detector_input_size")
            if not (isinstance(source_size, list) and len(source_size) == 2):
                return None, ["raw_detector_landmarks_source_px", "detector_input_size"], True
            raw = raw / np.asarray(source_size, dtype=np.float32) * np.asarray(raw_size, dtype=np.float32)
    if raw is None:
        raw = _finite_points(diagnostics.get("decoded_points"), count=5)
        if raw is not None:
            source_size = diagnostics.get("source_size")
            if not (isinstance(source_size, list) and len(source_size) == 2):
                return None, ["decoded_points_source_size"], True
            raw = raw / np.asarray(source_size, dtype=np.float32) * np.asarray(raw_size, dtype=np.float32)
    if raw is None:
        return None, ["raw_detector_landmarks"], True

    width, height = raw_size
    normalized = raw / np.asarray((width, height), dtype=np.float32)
    synthetic = np.zeros((18, 2), dtype=np.float32)
    # The first five detector points are wrist, index MCP, middle MCP, ring
    # MCP, pinky MCP.  palm_detection_to_palm_quad uses the same mapping.
    synthetic[[0, 5, 9, 13, 17]] = normalized[:5]
    return synthetic, ["accepted_landmarks_source_px", "raw_quad_at_capture"], True


def load_samples(dataset: Path) -> list[SampleRecord]:
    sample_dirs = sorted(path for path in dataset.rglob("sample_*") if path.is_dir())
    records: list[SampleRecord] = []
    for sample_dir in sample_dirs:
        metadata_path = sample_dir / "metadata.json"
        raw_path = sample_dir / "raw.png"
        roi_path = sample_dir / "roi_128.png"
        if not metadata_path.is_file() or not raw_path.is_file() or not roi_path.is_file():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        raw_image = Image.open(raw_path).convert("RGB")
        roi_image = Image.open(roi_path).convert("L")
        landmarks, missing, reconstructed = _detector_landmarks_from_metadata(metadata, raw_image.size)
        saved_geometry = metadata.get("roi_geometry_diagnostics")
        if not saved_geometry:
            saved_geometry = metadata.get("roi_status", {}).get("roi_geometry_diagnostics")
        diagnostics = saved_geometry if isinstance(saved_geometry, dict) else None
        if diagnostics is None:
            missing.append("roi_geometry_diagnostics")
        records.append(SampleRecord(sample_dir, raw_image, roi_image, metadata, landmarks, diagnostics, missing, reconstructed))
    return records


def _point_inside_convex(point: np.ndarray, quad: np.ndarray) -> bool:
    edges = np.roll(quad, -1, axis=0) - quad
    vectors = point - quad
    cross = edges[:, 0] * vectors[:, 1] - edges[:, 1] * vectors[:, 0]
    return bool(np.all(cross >= -1e-4) or np.all(cross <= 1e-4))


def _cv(values: Iterable[float]) -> float | None:
    data = np.asarray(list(values), dtype=np.float64)
    if data.size < 2 or abs(float(data.mean())) < 1e-9:
        return None
    return float(data.std(ddof=1) / data.mean())


def _angle_delta_deg(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    radians = np.radians(values)
    return float(np.degrees(np.std(np.unwrap(radians), ddof=1)))


def evaluate_record(record: SampleRecord, *, width_scale: float, height_scale: float, center_offset: float, fit_to_frame: bool) -> dict[str, Any]:
    row: dict[str, Any] = {
        "sample": str(record.path),
        "sample_index": record.metadata.get("sample_index"),
        "frame_id": record.metadata.get("frame_id"),
        "fit_to_frame": fit_to_frame,
        "width_scale": width_scale,
        "height_scale": height_scale,
        "center_offset": center_offset,
        "reconstructed_from_legacy": record.reconstructed,
        "missing_fields": ";".join(record.missing),
        "valid": False,
    }
    if record.landmarks is None:
        row["invalid_reason"] = "missing_landmarks"
        return row
    try:
        geometry = palm_roi.landmarks_to_palm_quad_diagnostics(
            record.landmarks,
            record.raw_image.size,
            width_scale=width_scale,
            height_scale=height_scale,
            center_offset=center_offset,
            min_span_px=max(palm_roi.RUNTIME_MIN_PALM_SPAN_FLOOR_PX, record.raw_image.width * palm_roi.RUNTIME_MIN_PALM_SPAN_RATIO),
            fit_to_frame=True,
        )
    except palm_roi.PalmROIError as error:
        row["invalid_reason"] = str(error)
        return row

    # fit_to_frame=False is evaluated from the same raw geometry, so an
    # out-of-frame sample is rejected rather than changing the geometry path.
    if not fit_to_frame and geometry.out_of_frame:
        row["invalid_reason"] = "out_of_frame"
        row["out_of_frame"] = True
        row["raw_quad"] = json.dumps(geometry.raw_quad.astype(float).tolist(), separators=(",", ":"))
        row["mcp_span_px"] = geometry.mcp_span_px
        return row

    final_quad = geometry.final_quad if fit_to_frame else geometry.raw_quad
    saved_quad = record.metadata.get("roi_quad")
    saved_delta = None
    try:
        saved_delta = float(np.max(np.abs(np.asarray(saved_quad, dtype=np.float32) - final_quad)))
    except (TypeError, ValueError):
        pass
    row.update(
        {
            "valid": True,
            "out_of_frame": geometry.out_of_frame,
            "fit_factor": geometry.fit_factor if fit_to_frame else 1.0,
            "fit_applied": geometry.fit_applied if fit_to_frame else False,
            "mcp_span_px": geometry.mcp_span_px,
            "center_x_px": float(geometry.center[0]),
            "center_y_px": float(geometry.center[1]),
            "angle_deg": geometry.angle_deg,
            "raw_width_px": geometry.raw_width_px,
            "raw_height_px": geometry.raw_height_px,
            "final_width_px": geometry.raw_width_px * (geometry.fit_factor if fit_to_frame else 1.0),
            "final_height_px": geometry.raw_height_px * (geometry.fit_factor if fit_to_frame else 1.0),
            "final_width_over_mcp_span": geometry.raw_width_px * (geometry.fit_factor if fit_to_frame else 1.0) / max(geometry.mcp_span_px, 1e-6),
            "mcp_inside_ratio": float(
                sum(
                    _point_inside_convex(point, final_quad)
                    for point in record.landmarks[[0, 5, 9, 13, 17]] * np.asarray(record.raw_image.size, dtype=np.float32)
                )
            ) / 5.0,
            "saved_final_quad_max_delta_px": saved_delta,
            "raw_quad": json.dumps(geometry.raw_quad.astype(float).tolist(), separators=(",", ":")),
            "final_quad": json.dumps(final_quad.astype(float).tolist(), separators=(",", ":")),
        }
    )
    return row


def summarize(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    valid = [row for row in rows if row.get("valid")]
    fit_values = [float(row["fit_factor"]) for row in valid if row.get("fit_factor") is not None]
    return {
        "configuration": name,
        "samples": len(rows),
        "valid_rois": len(valid),
        "invalid_rois": len(rows) - len(valid),
        "boundary_fit_percent": 100.0 * sum(bool(row.get("fit_applied")) for row in valid) / len(valid) if valid else None,
        "fit_factor_min": min(fit_values) if fit_values else None,
        "fit_factor_mean": float(np.mean(fit_values)) if fit_values else None,
        "fit_factor_max": max(fit_values) if fit_values else None,
        "mcp_span_cv": _cv(float(row["mcp_span_px"]) for row in valid if row.get("mcp_span_px") is not None),
        "raw_width_cv": _cv(float(row["raw_width_px"]) for row in valid if row.get("raw_width_px") is not None),
        "final_width_cv": _cv(float(row["final_width_px"]) for row in valid if row.get("final_width_px") is not None),
        "final_width_over_mcp_span_cv": _cv(float(row["final_width_over_mcp_span"]) for row in valid if row.get("final_width_over_mcp_span") is not None),
        "center_x_std_px": float(np.std([float(row["center_x_px"]) for row in valid], ddof=1)) if len(valid) > 1 else None,
        "center_y_std_px": float(np.std([float(row["center_y_px"]) for row in valid], ddof=1)) if len(valid) > 1 else None,
        "angle_std_deg": _angle_delta_deg([float(row["angle_deg"]) for row in valid if row.get("angle_deg") is not None]),
        "mcp_inside_ratio_mean": float(np.mean([float(row["mcp_inside_ratio"]) for row in valid])) if valid else None,
        "region_exclusion_assessment": "not_identifiable_without_palm_segmentation_or_full_landmarks; mcp_inside_ratio is only a proxy",
    }


def _draw_quad(draw: ImageDraw.ImageDraw, quad: Any, color: tuple[int, int, int], width: int = 3) -> None:
    points = [tuple(float(value) for value in point) for point in np.asarray(quad)]
    draw.line(points + [points[0]], fill=color, width=width)


def make_overlay(records: list[SampleRecord], rows: list[dict[str, Any]], output: Path) -> None:
    if not records:
        return
    cells: list[Image.Image] = []
    for record, row in zip(records, rows):
        image = record.raw_image.copy()
        draw = ImageDraw.Draw(image)
        try:
            raw_quad = json.loads(row["raw_quad"])
            _draw_quad(draw, raw_quad, (255, 60, 40))
            if row.get("valid"):
                _draw_quad(draw, json.loads(row["final_quad"]), (40, 220, 80))
        except (KeyError, TypeError, json.JSONDecodeError):
            pass
        image.thumbnail((480, 360))
        cells.append(image)
    cell_w, cell_h = 480, 390
    sheet = Image.new("RGB", (cell_w * 5, cell_h * math.ceil(len(cells) / 5)), "white")
    for index, image in enumerate(cells):
        x, y = (index % 5) * cell_w, (index // 5) * cell_h
        sheet.paste(image, (x, y))
        ImageDraw.Draw(sheet).text((x + 6, y + 365), f"{index + 1:02d} raw / green fitted", fill="black")
    sheet.save(output)


def make_roi_sheet(records: list[SampleRecord], output: Path) -> None:
    if not records:
        return
    cell = 160
    sheet = Image.new("L", (cell * 5, cell * math.ceil(len(records) / 5)), 20)
    for index, record in enumerate(records):
        roi = record.roi_image.resize((128, 128), Image.Resampling.NEAREST)
        x, y = (index % 5) * cell + 16, (index // 5) * cell + 16
        sheet.paste(roi, (x, y))
    sheet.convert("RGB").save(output)


def make_config_roi_sheet(records: list[SampleRecord], rows: list[dict[str, Any]], output: Path) -> None:
    """Render one 2x5 comparison sheet for one offline configuration."""

    cell = 160
    sheet = Image.new("L", (cell * 5, cell * math.ceil(len(records) / 5)), 20)
    for index, (record, row) in enumerate(zip(records, rows)):
        roi = Image.new("L", (128, 128), 24)
        if row.get("valid"):
            try:
                quad = np.asarray(json.loads(row["final_quad"]), dtype=np.float32)
                warped = palm_roi.warp_palm_roi(record.raw_image, quad)
                array = np.asarray(warped, dtype=np.float32)
                low, high = np.percentile(array, (1, 99))
                if high > low:
                    roi = Image.fromarray(np.clip((array - low) * 255.0 / (high - low), 0, 255).astype(np.uint8))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError, palm_roi.PalmROIError):
                pass
        x, y = (index % 5) * cell + 16, (index // 5) * cell + 16
        sheet.paste(roi.resize((128, 128), Image.Resampling.NEAREST), (x, y))
    sheet.convert("RGB").save(output)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def build_configurations(args: argparse.Namespace) -> list[tuple[str, float, float, float, bool]]:
    configurations = [
        ("A_current_fit", args.width_scale, args.height_scale, args.center_offset, True),
        ("B_current_reject_oob", args.width_scale, args.height_scale, args.center_offset, False),
    ]
    for scale in args.smaller_scales:
        configurations.append((f"C_smaller_{scale:g}", scale, scale, args.center_offset, True))
    for offset in args.center_offsets:
        if abs(offset - args.center_offset) > 1e-9:
            configurations.append((f"D_offset_{offset:g}", args.width_scale, args.height_scale, offset, True))
    return configurations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--width-scale", type=float, default=palm_roi.RUNTIME_ROI_WIDTH_SCALE)
    parser.add_argument("--height-scale", type=float, default=palm_roi.RUNTIME_ROI_HEIGHT_SCALE)
    parser.add_argument("--center-offset", type=float, default=0.30)
    parser.add_argument("--smaller-scales", type=float, nargs="+", default=[1.75, 1.50])
    parser.add_argument("--center-offsets", type=float, nargs="+", default=[0.0, 0.30, 0.60])
    args = parser.parse_args()
    dataset = args.dataset.resolve()
    output = (args.output_dir or dataset / "roi_geometry_analysis").resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = load_samples(dataset)
    if not records:
        raise SystemExit(f"No complete sample directories found below {dataset}")

    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for name, width, height, offset, fit in build_configurations(args):
        rows = [evaluate_record(record, width_scale=width, height_scale=height, center_offset=offset, fit_to_frame=fit) for record in records]
        for row in rows:
            row["configuration"] = name
        all_rows.extend(rows)
        summaries.append(summarize(rows, name))
        if name == "A_current_fit":
            make_overlay(records, rows, output / "raw_and_fitted_quads.png")
        make_config_roi_sheet(records, rows, output / f"{name}_roi_comparison_2x5.png")
    write_csv(output / "roi_geometry_results.csv", all_rows)
    write_csv(output / "roi_geometry_config_summary.csv", summaries)
    write_csv(output / "missing_fields.csv", [
        {"sample": str(record.path), "missing_fields": ";".join(record.missing), "reconstructed_from_legacy": record.reconstructed}
        for record in records if record.missing
    ])
    make_roi_sheet(records, output / "final_roi_comparison_2x5.png")

    report_lines = [f"# ROI geometry analysis: `{dataset}`", "", f"Samples read: {len(records)}", "", "The green quadrilateral in `raw_and_fitted_quads.png` is the reconstructed final quad; red is pre-fit. `mcp_inside_ratio` is only a detector-MCP proxy, not a palm-region segmentation result.", "", "| Configuration | Valid | Fit % | Fit factor min/mean/max | MCP span CV | Final width CV | Center std (x,y) px | Angle std deg |", "|---|---:|---:|---|---:|---:|---|---:|"]
    for summary in summaries:
        report_lines.append(
            f"| {summary['configuration']} | {summary['valid_rois']}/{summary['samples']} | {summary['boundary_fit_percent']} | {summary['fit_factor_min']}/{summary['fit_factor_mean']}/{summary['fit_factor_max']} | {summary['mcp_span_cv']} | {summary['final_width_cv']} | {summary['center_x_std_px']}, {summary['center_y_std_px']} | {summary['angle_std_deg']} |"
        )
    report_lines += ["", "## Missing or reconstructed evidence", "", "Legacy samples without runtime diagnostics are reconstructed from saved detector keypoints. The exact accepted/smoothed landmarks, pre-fit quad and fit factor cannot be recovered from the old metadata; see `missing_fields.csv`.", ""]
    (output / "README.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps({"dataset": str(dataset), "output": str(output), "samples": len(records), "summaries": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
