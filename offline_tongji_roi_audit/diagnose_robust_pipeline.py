"""Offline diagnostics for the upstream RobustPalmRoi pre-detector stages."""

from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT.parent / "code" / "data" / "debug_capture" / "20260916T152121Z"
TONGJI = ROOT / "raw_extract" / "session1"
OUT = ROOT / "robust_capture_results" / "diagnostics"


def pipeline(path: Path) -> tuple[dict[str, object], np.ndarray]:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"cv2.imread failed: {path}")
    image = cv2.resize(image, (512, 384), interpolation=cv2.INTER_LINEAR)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.int32)
    image = cv2.filter2D(image, 0, kernel)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    _, binary = cv2.threshold(ycrcb[:, :, 1], 0, 255, cv2.THRESH_OTSU)
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, element)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    areas = sorted((float(cv2.contourArea(c)) for c in contours), reverse=True)
    row: dict[str, object] = {
        "input": str(path),
        "input_size": [int(image.shape[1]), int(image.shape[0])],
        "binary_white_pct": float(np.mean(binary > 0) * 100.0),
        "contour_count": len(contours),
        "contour_areas_top3": areas[:3],
    }
    if contours:
        index = int(np.argmax([cv2.contourArea(c) for c in contours]))
        contour = contours[index]
        x, y, w, h = cv2.boundingRect(contour)
        row.update({
            "largest_bbox": [int(x), int(y), int(w), int(h)],
            "largest_area_pct": float(cv2.contourArea(contour) / (binary.shape[0] * binary.shape[1]) * 100.0),
            "touches_left": bool(x <= 0),
            "touches_top": bool(y <= 0),
            "touches_right": bool(x + w >= binary.shape[1]),
            "touches_bottom": bool(y + h >= binary.shape[0]),
            "contour_points": int(len(contour)),
        })
        mask = np.zeros(binary.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
        row["largest_mask_white_pct"] = float(np.mean(mask > 0) * 100.0)
        outline = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(outline, [contour], -1, (0, 0, 255), 2)
    else:
        outline = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    return row, outline


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [(f"capture_{p.parent.name}", p) for p in sorted(CAPTURE.glob("sample_*/raw.png"))]
    paths.append(("tongji_00001", TONGJI / "00001.tiff"))
    rows: list[dict[str, object]] = []
    for name, path in paths:
        row, outline = pipeline(path)
        row["name"] = name
        rows.append(row)
        cv2.imwrite(str(OUT / f"{name}_binary_contour.png"), outline)
    fields = sorted({key for row in rows for key in row})
    with (OUT / "pipeline_diagnostics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
