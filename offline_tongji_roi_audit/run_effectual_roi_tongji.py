"""Run the Python Effectual Palm-RoI implementation on the Tongji subset.

The core operations follow the upstream notebook.  This batch wrapper adds
failure isolation, overlays, normalized 128x128 outputs, and unchanged
Fast-CC scoring so the ROI-location behavior can be inspected and compared.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw_extract" / "session1"
PAIR_FILE = ROOT / "results" / "palm_roi_fastcc" / "shared_pair_manifest_and_scores.csv"
OUT_DIR = ROOT / "results" / "effectual_palm_roi"

sys.path.insert(0, str(ROOT / "palm_roi_env"))
sys.path.insert(0, str(ROOT))
from run_palm_roi_fastcc import fastcc_input, write_csv  # noqa: E402
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


def convexity_valley_pair(threshold: np.ndarray) -> tuple[np.ndarray, list[tuple[int, int, float]]]:
    """Use contour defects to repair the notebook's fragile minima[-1] rule."""
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("no_hand_contour_for_valley_repair")
    contour = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(contour, returnPoints=False)
    defects = cv2.convexityDefects(contour, hull)
    if defects is None:
        raise RuntimeError("no_convexity_defects_for_valley_repair")
    candidates: list[tuple[int, int, float]] = []
    for start, end, far, depth in np.asarray(defects).reshape(-1, 4):
        depth_px = float(depth) / 256.0
        if depth_px >= 25.0:
            x, y = contour[int(far), 0]
            candidates.append((int(x), int(y), depth_px))
    candidates.sort(key=lambda item: item[2], reverse=True)
    selected: list[tuple[int, int, float]] = []
    for candidate in candidates:
        if all(np.hypot(candidate[0] - other[0], candidate[1] - other[1]) >= 24 for other in selected):
            selected.append(candidate)
    selected.sort(key=lambda item: item[0])
    if len(selected) >= 5:
        left, right = selected[1], selected[-2]
    elif len(selected) == 4:
        left, right = selected[1], selected[2]
    else:
        raise RuntimeError(f"insufficient_repaired_valleys:{len(selected)}")
    return np.asarray((left[:2], right[:2]), dtype=np.float32), selected


def run_one(gray: np.ndarray, repair_location: bool = False) -> tuple[np.ndarray, dict[str, object], np.ndarray]:
    """Return the 128x128 ROI, diagnostics, and visualization overlay."""
    source_h, source_w = gray.shape
    padded = np.zeros((source_h + 160, source_w), np.uint8)
    padded[80:-80, :] = gray
    h, w = padded.shape
    blur = cv2.GaussianBlur(padded, (5, 5), 0)
    _, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    moments = cv2.moments(threshold)
    if moments["m00"] == 0:
        raise RuntimeError("empty_otsu_mask")
    centroid = np.asarray((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]), dtype=np.float32)

    kernel = np.asarray([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    erosion = cv2.erode(threshold, kernel, iterations=1)
    boundary = cv2.subtract(threshold, erosion)
    contours, _ = cv2.findContours(boundary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise RuntimeError("no_boundary_contour")
    contour = max(contours, key=cv2.contourArea).reshape(-1, 2)
    if len(contour) < 20:
        raise RuntimeError("boundary_contour_too_small")
    left_id = int(np.argmin(contour.sum(axis=1)))
    contour = np.concatenate((contour[left_id:, :], contour[:left_id, :]), axis=0)

    distance = np.linalg.norm(contour.astype(np.float32) - centroid, axis=1)
    spectrum = np.fft.rfft(distance)
    cutoff = min(15, len(spectrum))
    filtered_spectrum = np.concatenate((spectrum[:cutoff], np.zeros(max(0, len(spectrum) - cutoff), dtype=spectrum.dtype)))
    smooth_distance = np.fft.irfft(filtered_spectrum, n=len(distance))
    derivative = np.diff(smooth_distance)
    sign_change = np.diff(np.sign(derivative)) / 2.0
    minima_indices = np.where(sign_change > 0)[0]
    if len(minima_indices) < 3 and not repair_location:
        raise RuntimeError(f"too_few_valleys:{len(minima_indices)}")

    if repair_location:
        repaired_pair, repaired_candidates = convexity_valley_pair(threshold)
        v1, v2 = repaired_pair
        selection_method = "convexityDefects_repair_of_effectual_location_rule"
        selected_valleys = repaired_candidates
    else:
        # This is the selection in the public notebook: last and third-last
        # minima in the contour traversal order.
        v1 = contour[minima_indices[-1]].astype(np.float32)
        v2 = contour[minima_indices[-3]].astype(np.float32)
        selection_method = "public_notebook_minima[-1],minima[-3]"
        selected_valleys = [tuple(point.tolist()) for point in contour[minima_indices].astype(int)]
    theta = float(np.degrees(np.arctan2((v2 - v1)[1], (v2 - v1)[0])))
    matrix = cv2.getRotationMatrix2D(tuple(v2), theta, 1.0)
    rotated = cv2.warpAffine(padded, matrix, (w, h))
    rv1 = (matrix[:, :2] @ v1 + matrix[:, 2]).astype(np.int32)
    rv2 = (matrix[:, :2] @ v2 + matrix[:, 2]).astype(np.int32)

    dx = int(rv2[0] - rv1[0])
    if abs(dx) < 4:
        raise RuntimeError(f"valley_pair_horizontal_span_too_small:{dx}")
    # Preserve the notebook's asymmetric y offsets, but make the crop axes
    # explicit and valid when the pair is traversed in the opposite direction.
    if rv1[0] >= rv2[0]:
        rv1, rv2 = rv2, rv1
        dx = -dx
    ux = int(rv1[0])
    lx = int(rv2[0])
    uy = int(round(min(rv1[1], rv2[1]) + abs(dx) / 3.0))
    ly = int(round(max(rv1[1], rv2[1]) + 4.0 * abs(dx) / 3.0))
    ux, lx = max(0, ux), min(w, lx)
    uy, ly = max(0, uy), min(h, ly)
    if lx - ux < 16 or ly - uy < 16:
        raise RuntimeError(f"roi_crop_too_small:{lx-ux}x{ly-uy}")
    roi = rotated[uy:ly, ux:lx]
    roi128 = cv2.resize(roi, (128, 128), interpolation=cv2.INTER_AREA)

    overlay = cv2.cvtColor(padded, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(overlay, [contour.reshape(-1, 1, 2).astype(np.int32)], -1, (70, 180, 70), 2)
    for idx in minima_indices:
        point = tuple(contour[idx].astype(int))
        cv2.circle(overlay, point, 5, (255, 170, 0), -1)
    cv2.circle(overlay, tuple(v1.astype(int)), 10, (0, 0, 255), -1)
    cv2.circle(overlay, tuple(v2.astype(int)), 10, (255, 0, 0), -1)
    quad = np.asarray([[ux, uy], [lx, uy], [lx, ly], [ux, ly]], dtype=np.float32)
    inv = cv2.invertAffineTransform(matrix)
    quad_source = np.column_stack((quad, np.ones(4))) @ inv.T
    cv2.polylines(overlay, [np.rint(quad_source).astype(np.int32)], True, (0, 0, 255), 3)
    cv2.line(overlay, tuple(v1.astype(int)), tuple(v2.astype(int)), (255, 255, 255), 2)
    diagnostics = {
        "contour_points": int(len(contour)),
        "valley_count": int(len(minima_indices)),
        "valleys": [point.tolist() for point in contour[minima_indices].astype(int)],
        "selection_method": selection_method,
        "selected_valley_candidates": selected_valleys,
        "selected_v1": v1.astype(int).tolist(),
        "selected_v2": v2.astype(int).tolist(),
        "rotation_degrees": theta,
        "crop_box_padded_rotated": [ux, uy, lx, ly],
        "roi_size_before_resize": [int(roi.shape[1]), int(roi.shape[0])],
        "centroid_padded": centroid.tolist(),
    }
    return roi128, diagnostics, overlay


def main(repair_location: bool = False) -> None:
    for name in ("roi_128_gray", "fastcc_inputs", "overlays"):
        (OUT_DIR / name).mkdir(parents=True, exist_ok=True)
    pair_rows = list(csv.DictReader(PAIR_FILE.open(encoding="utf-8")))
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    for raw_path in sorted(RAW_DIR.glob("*.tiff")):
        stem = raw_path.stem
        gray = cv2.imread(str(raw_path), cv2.IMREAD_GRAYSCALE)
        row: dict[str, object] = {"sample": stem, "raw_file": raw_path.name, "palm_id": 1 if int(stem) <= 10 else 2}
        try:
            roi, diagnostics, overlay = run_one(gray, repair_location=repair_location)
            fast = fastcc_input(Image.fromarray(roi, mode="L"))
            Image.fromarray(roi, mode="L").save(OUT_DIR / "roi_128_gray" / f"{stem}.png")
            Image.fromarray(fast, mode="L").save(OUT_DIR / "fastcc_inputs" / f"{stem}.png")
            cv2.imwrite(str(OUT_DIR / "overlays" / f"{stem}.png"), overlay)
            features[stem] = algorithm.extract(fast)
            row.update({"status": "ok", **diagnostics})
        except Exception as error:
            row.update({"status": "failure", "failure": f"{type(error).__name__}: {error}"})
        rows.append(row)
    write_csv(OUT_DIR / "extraction_manifest.csv", rows)

    scored: list[dict[str, object]] = []
    for old in pair_rows:
        row = dict(old)
        probe, gallery = old["probe"], old["gallery"]
        row["effectual_distance"] = float(algorithm.match(features[probe], features[gallery])) if probe in features and gallery in features else ""
        scored.append(row)
    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", scored)
    values = [row for row in scored if row["effectual_distance"] != ""]
    genuine = np.asarray([float(row["effectual_distance"]) for row in values if row["pair_type"] == "genuine"], dtype=float)
    impostor = np.asarray([float(row["effectual_distance"]) for row in values if row["pair_type"] == "impostor"], dtype=float)
    threshold = 0.28
    summary = {
        "algorithm": "FastCC",
        "roi_method": "Effectual-Palm-RoI-Extraction public notebook with convexity-defect valley-location repair" if repair_location else "Effectual-Palm-RoI-Extraction public notebook, batch wrapper",
        "upstream_repo": "https://github.com/safwankdb/Effectual-Palm-RoI-Extraction",
        "input_size": [128, 128],
        "input_mode": "8-bit grayscale",
        "threshold": threshold,
        "requested_pair_count": len(pair_rows),
        "scored_pair_count": len(values),
        "successful_roi_samples": len(features),
        "failed_samples": [row["sample"] for row in rows if row["status"] != "ok"],
        "pairing": "reused exactly from results/palm_roi_fastcc/shared_pair_manifest_and_scores.csv; self-pairs excluded",
        "branches": {"effectual": {
            "genuine_pairs": int(genuine.size),
            "impostor_pairs": int(impostor.size),
            "fmr_at_threshold": float(np.mean(impostor <= threshold)) if impostor.size else None,
            "fnmr_at_threshold": float(np.mean(genuine > threshold)) if genuine.size else None,
            "genuine_median": float(np.median(genuine)) if genuine.size else None,
            "impostor_median": float(np.median(impostor)) if impostor.size else None,
            "genuine_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
            "impostor_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
        }},
        "warning": "This is a small same-session subset, not a cross-session Tongji benchmark. The convexity-defect repair changes only valley-point selection; the Effectual rotation/crop geometry and Fast-CC remain unchanged." if repair_location else "This is a small same-session subset, not a cross-session Tongji benchmark. The original notebook's ROI location rule is kept visible in extraction_manifest and overlays for diagnosis.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
