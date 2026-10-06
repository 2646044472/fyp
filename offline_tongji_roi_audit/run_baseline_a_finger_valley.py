"""Baseline A: contour finger-valley ROI with OpenCV, scored by unchanged Fast-CC."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

# Use the same isolated OpenCV runtime as the palm-roi experiment.
sys.path.insert(0, str(Path(__file__).resolve().parent / "palm_roi_env"))

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw_extract" / "session1"
REFERENCE_DIR = ROOT / "roi_extract" / "session1"
PREVIOUS_DIR = ROOT / "results" / "palm_roi_fastcc"
OUT_DIR = ROOT / "results" / "baseline_a_finger_valley"
sys.path.insert(0, str(ROOT))
from run_palm_roi_fastcc import fastcc_input, write_csv  # noqa: E402
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


def standardize_gray(image: Image.Image) -> Image.Image:
    return image.convert("L").resize((128, 128), Image.Resampling.LANCZOS)


def segment_hand(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the cleaned foreground mask and its largest external contour."""
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel_open = np.ones((5, 5), np.uint8)
    kernel_close = np.ones((9, 9), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("no_foreground_contour")
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < gray.size * 0.08:
        raise RuntimeError("foreground_contour_too_small")
    return mask, contour


def valley_candidates(contour: np.ndarray, *, min_depth_px: float = 25.0) -> list[tuple[int, int, float]]:
    hull = cv2.convexHull(contour, returnPoints=False)
    if hull is None or len(hull) < 3:
        return []
    defects = cv2.convexityDefects(contour, hull)
    if defects is None:
        return []
    candidates: list[tuple[int, int, float]] = []
    for start, end, far, depth in defects:
        depth_px = float(depth) / 256.0
        if depth_px < min_depth_px:
            continue
        x, y = (int(value) for value in contour[int(far), 0])
        candidates.append((x, y, depth_px))

    # Convexity defects can produce adjacent points for one gap. Keep the
    # deeper point in a 24-pixel neighbourhood, then order left-to-right.
    candidates.sort(key=lambda item: item[2], reverse=True)
    selected: list[tuple[int, int, float]] = []
    for candidate in candidates:
        if all(np.hypot(candidate[0] - other[0], candidate[1] - other[1]) >= 24 for other in selected):
            selected.append(candidate)
    return sorted(selected, key=lambda item: item[0])


def choose_inner_valleys(candidates: list[tuple[int, int, float]]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Choose the two interior gaps without using a learned hand model.

    With five or more ordered gaps, the outermost gaps are treated as thumb/
    little-finger boundary artefacts and the second and penultimate gaps are
    used. With four gaps, the two central gaps are used. This is intentionally
    a simple, frozen baseline rather than a tuned detector.
    """
    if len(candidates) >= 5:
        left, right = candidates[1], candidates[-2]
    elif len(candidates) == 4:
        left, right = candidates[1], candidates[2]
    else:
        raise RuntimeError(f"insufficient_finger_valleys:{len(candidates)}")
    if right[0] <= left[0]:
        raise RuntimeError("valleys_not_left_to_right")
    return (left[0], left[1]), (right[0], right[1])


def valley_quad(contour: np.ndarray, left: tuple[int, int], right: tuple[int, int], image_size: tuple[int, int]) -> np.ndarray:
    width, height = image_size
    a = np.asarray(left, dtype=np.float32)
    b = np.asarray(right, dtype=np.float32)
    across = b - a
    distance = float(np.linalg.norm(across))
    if not (0.12 * width <= distance <= 0.65 * width):
        raise RuntimeError(f"valley_spacing_out_of_range:{distance:.1f}px")
    x_axis = across / distance
    moments = cv2.moments(contour)
    if abs(moments["m00"]) < 1e-6:
        raise RuntimeError("invalid_contour_moments")
    centroid = np.asarray((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]), dtype=np.float32)
    midpoint = (a + b) * 0.5
    down = centroid - midpoint
    down -= x_axis * float(np.dot(down, x_axis))
    norm = float(np.linalg.norm(down))
    if norm < 0.15 * distance:
        down = np.asarray((-x_axis[1], x_axis[0]), dtype=np.float32)
        if float(np.dot(down, centroid - midpoint)) < 0:
            down = -down
        norm = float(np.linalg.norm(down))
    down /= norm
    if float(np.dot(down, centroid - midpoint)) < 0:
        down = -down

    # The top of the crop starts close to the valley line; most of the square
    # extends toward the palm centroid/wrist.
    center = midpoint + down * distance * 0.62
    half_width = distance * 0.68
    half_height = distance * 0.70
    quad = np.stack((
        center - x_axis * half_width - down * half_height,
        center + x_axis * half_width - down * half_height,
        center + x_axis * half_width + down * half_height,
        center - x_axis * half_width + down * half_height,
    )).astype(np.float32)
    # Keep the crop inside the image while preserving its orientation.
    fit = min(1.0, *(float(width - 1) / max(float(quad[:, 0].max()), 1.0),
                      float(height - 1) / max(float(quad[:, 1].max()), 1.0)))
    min_x, min_y = float(quad[:, 0].min()), float(quad[:, 1].min())
    if min_x < 0 or min_y < 0 or fit < 1.0:
        fit = min(fit, 0.98 * float(width - 1) / max(float(quad[:, 0].max() - center[0]), 1.0)) if quad[:, 0].max() > center[0] else fit
        fit = min(fit, 0.98 * float(height - 1) / max(float(quad[:, 1].max() - center[1]), 1.0)) if quad[:, 1].max() > center[1] else fit
        fit = max(0.20, fit)
        quad = center + (quad - center) * fit
        shift = np.asarray((max(0.0, -float(quad[:, 0].min())), max(0.0, -float(quad[:, 1].min()))), dtype=np.float32)
        quad += shift
    return quad


def warp_roi(gray: np.ndarray, quad: np.ndarray) -> np.ndarray:
    destination = np.asarray(((0, 0), (127, 0), (127, 127), (0, 127)), dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(quad.astype(np.float32), destination)
    return cv2.warpPerspective(gray, matrix, (128, 128), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def image_palm_id(stem: str) -> int:
    return 1 if int(stem) <= 10 else 2


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("raw_128_gray", "fastcc_inputs", "overlays"):
        (OUT_DIR / name).mkdir(parents=True, exist_ok=True)
    old_pairs = list(csv.DictReader((PREVIOUS_DIR / "shared_pair_manifest_and_scores.csv").open(encoding="utf-8")))
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    for raw_path in sorted(RAW_DIR.glob("*.tiff")):
        stem = raw_path.stem
        raw = cv2.imread(str(raw_path), cv2.IMREAD_GRAYSCALE)
        row: dict[str, object] = {"sample": stem, "palm_id": image_palm_id(stem), "raw_file": raw_path.name}
        try:
            mask, contour = segment_hand(raw)
            candidates = valley_candidates(contour)
            left, right = choose_inner_valleys(candidates)
            quad = valley_quad(contour, left, right, (raw.shape[1], raw.shape[0]))
            roi = warp_roi(raw, quad)
            Image.fromarray(roi, mode="L").save(OUT_DIR / "raw_128_gray" / f"{stem}.png")
            fast_input = fastcc_input(Image.fromarray(roi, mode="L"))
            Image.fromarray(fast_input, mode="L").save(OUT_DIR / "fastcc_inputs" / f"{stem}.png")
            features[stem] = algorithm.extract(fast_input)

            overlay = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(overlay, [contour], -1, (80, 180, 80), 2)
            for x, y, depth in candidates:
                cv2.circle(overlay, (x, y), 7, (255, 160, 0), -1)
                cv2.putText(overlay, f"{depth:.0f}", (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 160, 0), 1, cv2.LINE_AA)
            cv2.circle(overlay, left, 10, (0, 0, 255), -1)
            cv2.circle(overlay, right, 10, (0, 0, 255), -1)
            cv2.polylines(overlay, [quad.astype(np.int32)], True, (0, 0, 255), 3)
            cv2.imwrite(str(OUT_DIR / "overlays" / f"{stem}.png"), overlay)
            row.update({"status": "ok", "valley_count": len(candidates), "valley_candidates": candidates, "left_valley": left, "right_valley": right, "quad": quad.tolist()})
        except Exception as error:
            row.update({"status": "failure", "failure": f"{type(error).__name__}: {error}"})
        rows.append(row)
    write_csv(OUT_DIR / "extraction_manifest.csv", rows)

    scored: list[dict[str, object]] = []
    for old in old_pairs:
        row = dict(old)
        probe, gallery = old["probe"], old["gallery"]
        if probe in features and gallery in features:
            row["baseline_a_distance"] = float(algorithm.match(features[probe], features[gallery]))
        else:
            row["baseline_a_distance"] = ""
        scored.append(row)
    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", scored)

    values = [row for row in scored if row["baseline_a_distance"] != ""]
    genuine = np.asarray([float(row["baseline_a_distance"]) for row in values if row["pair_type"] == "genuine"], dtype=float)
    impostor = np.asarray([float(row["baseline_a_distance"]) for row in values if row["pair_type"] == "impostor"], dtype=float)
    threshold = 0.28
    summary = {
        "algorithm": "FastCC",
        "baseline": "A: OpenCV contour + convexityDefects finger-valley ROI",
        "input_size": [128, 128],
        "input_mode": "8-bit grayscale",
        "threshold": threshold,
        "requested_pair_count": len(old_pairs),
        "scored_pair_count": len(values),
        "successful_roi_samples": len(features),
        "failed_samples": [row["sample"] for row in rows if row["status"] != "ok"],
        "pairing": "reused exactly from results/palm_roi_fastcc/shared_pair_manifest_and_scores.csv; self-pairs excluded",
        "branches": {
            "baseline_a": {
                "genuine_pairs": int(genuine.size),
                "impostor_pairs": int(impostor.size),
                "fmr_at_threshold": float(np.mean(impostor <= threshold)) if impostor.size else None,
                "fnmr_at_threshold": float(np.mean(genuine > threshold)) if genuine.size else None,
                "genuine_median": float(np.median(genuine)) if genuine.size else None,
                "impostor_median": float(np.median(impostor)) if impostor.size else None,
                "genuine_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
                "impostor_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
            }
        },
        "warning": "This is a small same-session subset; the valley rule is a frozen conventional baseline, not a tuned or learned ROI model.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
