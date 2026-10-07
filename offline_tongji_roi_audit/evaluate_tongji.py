"""Offline Tongji raw/ROI pairing and 7-point vs 21-point ROI audit.

This script is intentionally outside code/palm_demo.  It imports the existing
ROI geometry functions but does not modify runtime code or Fast-CC.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT.parent / "code" / "palm_demo"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(APP_DIR))

import palm_roi  # noqa: E402
from mp_handpose import MPHandPose  # noqa: E402


RAW_DIR = ROOT / "raw_extract" / "session1"
REF_DIR = ROOT / "roi_extract" / "session1"
OUT_DIR = ROOT / "results"
HAND_MODEL = APP_DIR / "models" / "palm_detection_mediapipe_2023feb.onnx"
POSE_MODEL = APP_DIR / "models" / "handpose_estimation_mediapipe_2023feb.onnx"
INPUT_SIZE = (320, 240)
WIDTH_SCALE = palm_roi.RUNTIME_ROI_WIDTH_SCALE
HEIGHT_SCALE = palm_roi.RUNTIME_ROI_HEIGHT_SCALE
MIN_SPAN = max(palm_roi.RUNTIME_MIN_PALM_SPAN_FLOOR_PX, INPUT_SIZE[0] * palm_roi.RUNTIME_MIN_PALM_SPAN_RATIO)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scale_quad(quad: np.ndarray, raw_size: tuple[int, int]) -> np.ndarray:
    return quad * np.asarray((raw_size[0] / INPUT_SIZE[0], raw_size[1] / INPUT_SIZE[1]), dtype=np.float32)


def make_hand_mask(image: Image.Image) -> np.ndarray:
    """Approximate hand foreground against Tongji's dark background."""
    rgb = np.asarray(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # The Tongji originals use a dark display background.  Otsu plus a low
    # floor is intentionally conservative; this is a diagnostic proxy, not GT.
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = np.where(gray > max(12, int(_)), 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = np.where(labels == keep, 255, 0).astype(np.uint8)
    return mask


def warp_mask(mask: np.ndarray, quad: np.ndarray) -> np.ndarray:
    pil = Image.fromarray(mask, mode="L")
    return np.asarray(palm_roi.warp_palm_roi(pil, quad), dtype=np.uint8)


def normalize_for_display(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgb = image.convert("RGB")
    arr = np.asarray(rgb, dtype=np.float32)
    lo, hi = np.percentile(arr, (1, 99))
    if hi > lo:
        arr = np.clip((arr - lo) * 255.0 / (hi - lo), 0, 255).astype(np.uint8)
        rgb = Image.fromarray(arr, mode="RGB")
    rgb.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#111827")
    canvas.paste(rgb, ((size[0] - rgb.width) // 2, (size[1] - rgb.height) // 2))
    return canvas


def roi_display(image: Image.Image | None, size: tuple[int, int] = (220, 220)) -> Image.Image:
    if image is None:
        out = Image.new("RGB", size, "#5b1b1b")
        ImageDraw.Draw(out).text((12, size[1] // 2 - 8), "FAIL", fill="white")
        return out
    rgb = image.convert("L").resize(size, Image.Resampling.NEAREST)
    return Image.merge("RGB", (rgb, rgb, rgb))


def draw_quad(image: Image.Image, quad: np.ndarray | None, color: tuple[int, int, int], label: str) -> None:
    if quad is None:
        return
    draw = ImageDraw.Draw(image)
    pts = [tuple(map(float, p)) for p in quad]
    draw.line(pts + [pts[0]], fill=color, width=max(2, image.width // 400))
    draw.text((int(min(p[0] for p in pts)) + 4, int(min(p[1] for p in pts)) + 4), label, fill=color)


def geometry_metrics(mask_warp: np.ndarray, quad: np.ndarray, raw_size: tuple[int, int], *, reference: np.ndarray | None = None) -> dict[str, float | None]:
    fg = mask_warp > 0
    total = int(fg.sum())
    upper = int(fg[:24, :].sum())
    # Diagnostic proxies: occupancy of the normalized ROI, and occupancy in
    # its finger-side top band.  They do not replace a hand/palm segmentation GT.
    metrics: dict[str, float | None] = {
        "roi_foreground_coverage_pct": 100.0 * total / fg.size,
        "finger_intrusion_proxy_pct": 100.0 * upper / max(total, 1),
        "roi_quad_area_pct_of_image": 100.0 * abs(cv2.contourArea(quad.astype(np.float32))) / (raw_size[0] * raw_size[1]),
    }
    if reference is not None:
        a = cv2.resize(mask_warp.astype(np.float32), (128, 128)).ravel()
        b = np.asarray(reference, dtype=np.float32).ravel()
        if np.std(a) > 1e-6 and np.std(b) > 1e-6:
            metrics["mask_correlation_to_reference"] = float(np.corrcoef(a, b)[0, 1])
        else:
            metrics["mask_correlation_to_reference"] = None
    return metrics


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sample_ids = list(range(1, 16))
    detector = cv2.dnn.readNet(str(HAND_MODEL))
    detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    pose = MPHandPose(
        str(POSE_MODEL),
        confThreshold=0.62,
        backendId=cv2.dnn.DNN_BACKEND_OPENCV,
        targetId=cv2.dnn.DNN_TARGET_CPU,
    )

    rows: list[dict[str, object]] = []
    pair_rows: list[dict[str, object]] = []
    sheets: list[Image.Image] = []
    colors = {"7": (255, 92, 64), "21": (47, 210, 120)}

    for index in sample_ids:
        stem = f"{index:05d}"
        raw_path = RAW_DIR / f"{stem}.tiff"
        ref_path = REF_DIR / f"{stem}.bmp"
        raw = Image.open(raw_path).convert("RGB")
        reference = Image.open(ref_path).convert("L")
        raw_size = raw.size
        resized = raw.resize(INPUT_SIZE, Image.Resampling.BILINEAR)
        rgb = np.asarray(resized, dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        mask = make_hand_mask(raw)

        result: dict[str, object] = {
            "sample": stem,
            "raw_file": raw_path.name,
            "reference_roi_file": ref_path.name,
            "raw_sha256": sha256(raw_path),
            "reference_sha256": sha256(ref_path),
            "raw_size": list(raw.size),
            "reference_size": list(reference.size),
            "palm_id": 1 if index <= 10 else 2,
        }
        overlay = normalize_for_display(raw, (520, 390))

        first = None
        quad7 = None
        try:
            # Existing 7-point path: palm detector -> shared palm geometry.
            first = _infer_detector(detector, bgr)
            if first is None:
                raise ValueError("detector_below_threshold_or_invalid")
            points7, score7, box7 = first
            quad_input = palm_roi.palm_detection_to_palm_quad(
                points7 / np.asarray(INPUT_SIZE, dtype=np.float32),
                INPUT_SIZE,
                width_scale=WIDTH_SCALE,
                height_scale=HEIGHT_SCALE,
                min_span_px=MIN_SPAN,
                fit_to_frame=True,
            )
            quad7 = scale_quad(quad_input, raw_size)
            warped7 = palm_roi.warp_palm_roi(raw, quad7)
            mask7 = warp_mask(mask, quad7)
            result.update({"roi7_status": "ok", "roi7_detector_score": score7, "roi7_quad": quad7.astype(float).tolist()})
            result.update({f"roi7_{k}": v for k, v in geometry_metrics(mask7, quad7, raw_size, reference=np.asarray(reference)).items()})
        except Exception as exc:  # diagnostic record, never a silent fallback
            warped7 = None
            result.update({"roi7_status": "failure", "roi7_failure": f"{type(exc).__name__}: {exc}"})

        quad21 = None
        try:
            if first is None:
                raise ValueError("requires_successful_7_point_palm_detection")
            points7, score7, box7 = first
            palm = np.concatenate((box7, points7.reshape(-1)))
            hand = pose.infer(bgr, palm)
            if hand is None:
                raise ValueError("handpose_below_threshold")
            points21 = hand[4:67].reshape(21, 3)[:, :2]
            quad_input = palm_roi.landmarks_to_palm_quad(
                points21 / np.asarray(INPUT_SIZE, dtype=np.float32),
                INPUT_SIZE,
                width_scale=WIDTH_SCALE,
                height_scale=HEIGHT_SCALE,
                min_span_px=MIN_SPAN,
                fit_to_frame=True,
            )
            quad21 = scale_quad(quad_input, raw_size)
            warped21 = palm_roi.warp_palm_roi(raw, quad21)
            mask21 = warp_mask(mask, quad21)
            result.update({"roi21_status": "ok", "roi21_confidence": float(hand[-1]), "roi21_quad": quad21.astype(float).tolist()})
            result.update({f"roi21_{k}": v for k, v in geometry_metrics(mask21, quad21, raw_size, reference=np.asarray(reference)).items()})
        except Exception as exc:
            warped21 = None
            result.update({"roi21_status": "failure", "roi21_failure": f"{type(exc).__name__}: {exc}"})

        if quad7 is not None and quad21 is not None:
            span = max(float(np.linalg.norm(quad7[1] - quad7[0])), 1.0)
            center_delta = float(np.linalg.norm(quad7.mean(axis=0) - quad21.mean(axis=0)) / span)
            axis7 = quad7[1] - quad7[0]
            axis21 = quad21[1] - quad21[0]
            cross = float(axis7[0] * axis21[1] - axis7[1] * axis21[0])
            angle = abs(float(np.degrees(np.arctan2(cross, np.dot(axis7, axis21)))))
            result.update({"alignment_status": "ok", "alignment_center_delta_over_width": center_delta, "alignment_angle_delta_deg": angle, "alignment_width_delta_pct": float(100.0 * (np.linalg.norm(quad21[1] - quad21[0]) / max(np.linalg.norm(quad7[1] - quad7[0]), 1e-6) - 1.0))})
        else:
            result["alignment_status"] = "not_computable"

        overlay = overlay.copy()
        # Map raw quads into the displayed raw panel coordinates.
        sx, sy = overlay.width / raw.width, overlay.height / raw.height
        for key, quad in (("7", quad7), ("21", quad21)):
            if quad is not None:
                display_quad = quad * np.asarray((sx, sy), dtype=np.float32)
                draw_quad(overlay, display_quad, colors[key], key)

        label_h = 28
        cell_w, cell_h = 520, 420
        row_sheet = Image.new("RGB", (cell_w * 4, cell_h), "white")
        panels = [
            ("RAW + 7/21 overlays", overlay),
            ("REFERENCE ROI", roi_display(reference)),
            ("7-POINT ROI", roi_display(warped7)),
            ("21-POINT ROI", roi_display(warped21)),
        ]
        for col, (label, panel) in enumerate(panels):
            target = Image.new("RGB", (cell_w, cell_h), "white")
            ImageDraw.Draw(target).text((10, 6), f"{stem}  {label}", fill="black")
            body = panel.copy()
            body.thumbnail((cell_w - 20, cell_h - label_h - 12), Image.Resampling.LANCZOS)
            target.paste(body, ((cell_w - body.width) // 2, label_h + (cell_h - label_h - body.height) // 2))
            row_sheet.paste(target, (col * cell_w, 0))
        row_sheet.save(OUT_DIR / f"sample_{index:03d}_comparison.png")
        sheets.append(row_sheet)
        rows.append(result)
        pair_rows.append({
            "sample": stem,
            "raw_file": raw_path.name,
            "roi_file": ref_path.name,
            "same_stem": raw_path.stem == ref_path.stem,
            "raw_bytes": raw_path.stat().st_size,
            "roi_bytes": ref_path.stat().st_size,
            "raw_sha256": result["raw_sha256"],
            "roi_sha256": result["reference_sha256"],
            "raw_size": result["raw_size"],
            "roi_size": result["reference_size"],
        })

    sheet = Image.new("RGB", (2080, 420 * len(sheets)), "white")
    for i, row_sheet in enumerate(sheets):
        sheet.paste(row_sheet, (0, i * 420))
    sheet.save(OUT_DIR / "tongji_15_sample_comparison_sheet.png")

    with (OUT_DIR / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        fields = sorted({k for row in rows for k in row})
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    with (OUT_DIR / "pairing_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        fields = sorted({k for row in pair_rows for k in row})
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pair_rows)

    summary = summarize(rows)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def _infer_detector(detector: cv2.dnn.Net, bgr: np.ndarray) -> tuple[np.ndarray, float, np.ndarray] | None:
    height, width = bgr.shape[:2]
    model_width, model_height = palm_roi.PALM_DETECTOR_INPUT_SIZE
    ratio = min(model_height / height, model_width / width)
    resized_shape = (np.asarray((height, width), dtype=np.float32) * ratio).astype(np.int32)
    resized = cv2.resize(bgr, (int(resized_shape[1]), int(resized_shape[0])))
    pad_h = model_height - int(resized_shape[0])
    pad_w = model_width - int(resized_shape[1])
    left, top = pad_w // 2, pad_h // 2
    padded = cv2.copyMakeBorder(resized, top, pad_h - top, left, pad_w - left, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    detector.setInput(rgb[np.newaxis, ...])
    outputs = detector.forward(detector.getUnconnectedOutLayersNames())
    logits = outputs[1][0, :, 0].astype(np.float64)
    scores = 1.0 / (1.0 + np.exp(-logits))
    best = int(np.argmax(scores))
    score = float(scores[best])
    if score < 0.42:
        return None
    anchors = palm_roi.HandLandmarkTracker._load_anchors()
    box_delta = outputs[0][0, :, 0:4]
    landmark_delta = outputs[0][0, :, 4:]
    input_size = np.asarray(palm_roi.PALM_DETECTOR_INPUT_SIZE, dtype=np.float32)
    scale = float(max(width, height))
    center_delta = box_delta[:, :2] / input_size
    size_delta = box_delta[:, 2:] / input_size
    box = np.concatenate(((center_delta[best] - size_delta[best] / 2 + anchors[best]) * scale, (center_delta[best] + size_delta[best] / 2 + anchors[best]) * scale))
    points = landmark_delta[best].reshape(7, 2) / input_size
    points = (points + anchors[best]) * scale
    pad_bias = np.asarray((left, top), dtype=np.float32) / ratio
    points -= pad_bias
    box -= np.asarray((pad_bias[0], pad_bias[1], pad_bias[0], pad_bias[1]), dtype=np.float32)
    return points.astype(np.float32), score, box.astype(np.float32)


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    def vals(prefix: str, key: str) -> list[float]:
        out = []
        for row in rows:
            value = row.get(f"{prefix}_{key}")
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                out.append(float(value))
        return out

    def stats(prefix: str, key: str) -> dict[str, float | None]:
        data = vals(prefix, key)
        return {"mean": float(np.mean(data)) if data else None, "std": float(np.std(data, ddof=1)) if len(data) > 1 else None, "min": min(data) if data else None, "max": max(data) if data else None}

    ok7 = sum(row.get("roi7_status") == "ok" for row in rows)
    ok21 = sum(row.get("roi21_status") == "ok" for row in rows)
    paired = sum(row.get("alignment_status") == "ok" for row in rows)
    return {
        "dataset": "Tongji Contactless Palmprint Dataset",
        "sample_count": len(rows),
        "pairing": {"verified_same_stem": True, "raw_extension": ".tiff", "reference_extension": ".bmp", "samples": "session1/00001-00015"},
        "roi7": {"success": ok7, "failures": len(rows) - ok7, "failure_rate_pct": 100.0 * (len(rows) - ok7) / len(rows), "coverage_proxy": stats("roi7", "roi_foreground_coverage_pct"), "finger_intrusion_proxy": stats("roi7", "finger_intrusion_proxy_pct")},
        "roi21": {"success": ok21, "failures": len(rows) - ok21, "failure_rate_pct": 100.0 * (len(rows) - ok21) / len(rows), "coverage_proxy": stats("roi21", "roi_foreground_coverage_pct"), "finger_intrusion_proxy": stats("roi21", "finger_intrusion_proxy_pct")},
        "alignment_7_vs_21": {"paired_successes": paired, "center_delta_over_7_width": stats("alignment", "center_delta_over_width"), "angle_delta_deg": stats("alignment", "angle_delta_deg"), "width_delta_pct": stats("alignment", "width_delta_pct")},
        "interpretation": "coverage and finger intrusion are thresholded-dark-background proxies; no pixel-level hand/palm ground-truth mask was released with the paired Tongji files.",
    }


if __name__ == "__main__":
    run()
