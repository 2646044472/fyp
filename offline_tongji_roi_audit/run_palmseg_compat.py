"""PalmSeg-compatible Python run for the Tongji audit subset.

The upstream PalmSeg repository is MATLAB code.  This runner mirrors its
Tongji configuration and core geometry in Python so it can be executed in
this environment without MATLAB: HSV/V preprocessing, Otsu hand mask,
largest-component cleanup, radial contour valley detection, PalmSeg's
three-valley rejection geometry, orientation, and adaptive ROI sizing.
Fast-CC and the directed pair manifest are unchanged.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, uniform_filter1d
from scipy.signal import find_peaks
from skimage.filters import threshold_otsu

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw_extract" / "session1"
PAIR_FILE = ROOT / "results" / "palm_roi_fastcc" / "shared_pair_manifest_and_scores.csv"
OUT_DIR = ROOT / "results" / "palmseg_compat"

sys.path.insert(0, str(ROOT / "palm_roi_env"))
sys.path.insert(0, str(ROOT))
from run_palm_roi_fastcc import fastcc_input, write_csv  # noqa: E402
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


def largest_filled_component(mask: np.ndarray) -> np.ndarray:
    mask_u8 = (mask.astype(np.uint8) * 255)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask_u8, 8)
    if num <= 1:
        raise RuntimeError("no_foreground_component")
    label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    component = (labels == label).astype(np.uint8) * 255
    flood = component.copy()
    flood_mask = np.zeros((component.shape[0] + 2, component.shape[1] + 2), np.uint8)
    cv2.floodFill(flood, flood_mask, (0, 0), 255)
    holes = cv2.bitwise_not(flood)
    return cv2.bitwise_or(component, holes) > 0


def segment_palms_like_palmseg(rgb: np.ndarray) -> np.ndarray:
    """Mirror segmentPalms.m for the Tongji parameter file."""
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    value = hsv[:, :, 2].astype(np.float32) / 255.0
    lo, hi = np.percentile(value, (1, 99))
    value = np.clip((value - lo) / max(hi - lo, 1e-6), 0.0, 1.0)
    value = (value - value.min()) / max(value.max() - value.min(), 1e-6)
    blurred = gaussian_filter(value, sigma=2.0, truncate=2.0)
    threshold = threshold_otsu(blurred)
    mask = blurred > max(0.0, threshold - 0.10)  # thSegmRed = -0.10
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel) > 0
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, kernel) > 0
    mask = largest_filled_component(mask)
    if int(mask.sum()) < int(mask.size * 0.08):
        raise RuntimeError("segmentation_too_small")
    return mask


def resampled_contour(mask: np.ndarray, n: int = 3000) -> np.ndarray:
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise RuntimeError("no_contour")
    contour = max(contours, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    if cv2.contourArea(contour.astype(np.int32)) <= 0:
        raise RuntimeError("empty_contour")
    closed = np.vstack([contour, contour[:1]])
    deltas = np.diff(closed, axis=0)
    lengths = np.linalg.norm(deltas, axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(lengths)])
    samples = np.linspace(0.0, cumulative[-1], n, endpoint=False)
    x = np.interp(samples, cumulative, closed[:, 0])
    y = np.interp(samples, cumulative, closed[:, 1])
    return np.column_stack((x, y)).astype(np.float32)


def contour_valleys(mask: np.ndarray) -> tuple[np.ndarray, list[tuple[int, int, float]]]:
    contour = resampled_contour(mask)
    moments = cv2.moments(mask.astype(np.uint8))
    centroid = np.asarray((moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]), dtype=np.float32)
    distances = np.linalg.norm(contour - centroid, axis=1)
    smooth = uniform_filter1d(-distances, size=151, mode="wrap")
    peaks, props = find_peaks(smooth, distance=50, prominence=5.0)
    candidates: list[tuple[int, int, float]] = []
    for index, prominence in zip(peaks, props.get("prominences", [])):
        point = np.rint(contour[index]).astype(int)
        candidates.append((int(point[0]), int(point[1]), float(prominence)))
    return contour, candidates


def triangle_angles(points: np.ndarray) -> np.ndarray:
    angles = []
    for i in range(3):
        a = points[(i + 1) % 3] - points[i]
        b = points[(i + 2) % 3] - points[i]
        denom = max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-8)
        angles.append(np.degrees(np.arccos(np.clip(np.dot(a, b) / denom, -1.0, 1.0))))
    return np.asarray(angles)


def extension_is_inside(mask: np.ndarray, central: np.ndarray, other: np.ndarray) -> bool:
    samples = np.linspace(central + 0.1 * (other - central), other, 10)
    h, w = mask.shape
    valid = [(int(round(p[1])), int(round(p[0]))) for p in samples if 0 <= p[0] < w and 0 <= p[1] < h]
    return bool(valid) and (sum(bool(mask[y, x]) for y, x in valid) > len(valid) * 0.3)


def choose_palmseg_valleys(mask: np.ndarray, candidates: list[tuple[int, int, float]]) -> np.ndarray:
    if len(candidates) < 3:
        raise RuntimeError(f"too_few_radial_valleys:{len(candidates)}")
    points = np.asarray([(x, y) for x, y, _ in candidates], dtype=np.float32)
    h, w = mask.shape
    best: tuple[float, np.ndarray] | None = None
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            for k in range(j + 1, len(points)):
                triple = points[[i, j, k]]
                angles = np.sort(triangle_angles(triple))
                if int(np.sum(angles < 35.0)) < 2:
                    continue
                poly = np.rint(triple).astype(np.int32)
                tri_mask = np.zeros_like(mask, dtype=np.uint8)
                cv2.fillPoly(tri_mask, [poly], 1)
                area = tri_mask > 0
                if not area.any() or float(np.mean(~mask[area])) > 0.30:
                    continue
                dists = np.linalg.norm(triple[:, None, :] - triple[None, :, :], axis=2)
                central_index = int(np.argmin(dists.mean(axis=1)))
                others = [q for q in range(3) if q != central_index]
                if not all(extension_is_inside(mask, triple[central_index], triple[q]) for q in others):
                    continue
                if np.any(triple < 50) or np.any(triple[:, 0] > w - 50) or np.any(triple[:, 1] > h - 50):
                    continue
                score = float(np.min(dists.mean(axis=1)) + np.mean(angles))
                if best is None or score < best[0]:
                    best = (score, triple)
    if best is None:
        raise RuntimeError("no_valid_three_valley_geometry")
    return best[1][np.argsort(best[1][:, 1])]


def rotate_expand(image: np.ndarray, angle: float) -> tuple[np.ndarray, np.ndarray]:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos, sin = abs(matrix[0, 0]), abs(matrix[0, 1])
    new_w, new_h = int(np.ceil(h * sin + w * cos)), int(np.ceil(h * cos + w * sin))
    matrix[0, 2] += new_w / 2.0 - center[0]
    matrix[1, 2] += new_h / 2.0 - center[1]
    rotated = cv2.warpAffine(image, matrix, (new_w, new_h), flags=cv2.INTER_LINEAR, borderValue=0)
    return rotated, matrix


def transform_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    homogeneous = np.column_stack((points, np.ones(len(points))))
    return homogeneous @ matrix.T


def crop_palmseg_roi(gray: np.ndarray, mask: np.ndarray, valleys: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    distances = np.linalg.norm(valleys[:, None, :] - valleys[None, :, :], axis=2)
    i, j = np.unravel_index(np.argmax(distances), distances.shape)
    if i == j:
        raise RuntimeError("invalid_valley_pair")
    p1, p2 = valleys[i], valleys[j]
    distance = float(np.linalg.norm(p2 - p1))
    roisz_x = int(round(distance * 1.4))
    roisz_y = int(round(distance * 1.4))
    x_offset = int(round(roisz_x / 2.0 + distance * 0.2))
    grad = -90.0 - np.degrees(np.arctan2(float(p2[1] - p1[1]), float(p2[0] - p1[0])))

    choices = []
    for refined in (False, True):
        angle = grad + (180.0 if refined else 0.0)
        rot_gray, matrix = rotate_expand(gray, -angle)
        rot_mask, _ = rotate_expand(mask.astype(np.uint8) * 255, -angle)
        rp = transform_points(np.vstack((p1, p2)), matrix)
        top, bottom = rp[0], rp[1]
        center = np.asarray(((top[0] + bottom[0]) / 2.0 + x_offset, (top[1] + bottom[1]) / 2.0))
        min_x = int(round(center[0] - roisz_x / 2.0 + 1))
        max_x = int(round(center[0] + roisz_x / 2.0))
        min_y = int(round(center[1] - roisz_y / 2.0 + 1))
        max_y = int(round(center[1] + roisz_y / 2.0))
        if min_x <= 0 or min_y <= 0 or max_x >= rot_gray.shape[1] or max_y >= rot_gray.shape[0]:
            continue
        crop_mask = rot_mask[min_y:max_y + 1, min_x:max_x + 1] > 0
        black_fraction = float(np.mean(~crop_mask))
        if black_fraction <= 0.30:
            crop = rot_gray[min_y:max_y + 1, min_x:max_x + 1]
            choices.append((black_fraction, crop, np.asarray((min_x, min_y, max_x, max_y))))
    if not choices:
        raise RuntimeError("roi_out_of_bounds_or_too_much_background")
    choices.sort(key=lambda item: item[0])
    return choices[0][1], valleys, choices[0][2]


def palm_id(stem: str) -> int:
    return 1 if int(stem) <= 10 else 2


def run() -> None:
    for subdir in ("raw_150_gray", "raw_128_gray", "fastcc_inputs", "overlays"):
        (OUT_DIR / subdir).mkdir(parents=True, exist_ok=True)
    old_pairs = list(csv.DictReader(PAIR_FILE.open(encoding="utf-8")))
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    for raw_path in sorted(RAW_DIR.glob("*.tiff")):
        stem = raw_path.stem
        rgb = np.asarray(Image.open(raw_path).convert("RGB"), dtype=np.uint8)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        row: dict[str, object] = {"sample": stem, "palm_id": palm_id(stem), "raw_file": raw_path.name}
        try:
            mask = segment_palms_like_palmseg(rgb)
            contour, candidates = contour_valleys(mask)
            valleys = choose_palmseg_valleys(mask, candidates)
            roi150, _, crop_box = crop_palmseg_roi(gray, mask, valleys)
            roi128 = cv2.resize(roi150, (128, 128), interpolation=cv2.INTER_CUBIC)
            fast = fastcc_input(Image.fromarray(roi128, mode="L"))
            Image.fromarray(roi150, mode="L").save(OUT_DIR / "raw_150_gray" / f"{stem}.png")
            Image.fromarray(roi128, mode="L").save(OUT_DIR / "raw_128_gray" / f"{stem}.png")
            Image.fromarray(fast, mode="L").save(OUT_DIR / "fastcc_inputs" / f"{stem}.png")
            features[stem] = algorithm.extract(fast)

            overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            contour_int = np.rint(contour).astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(overlay, [contour_int], True, (70, 180, 70), 2)
            for x, y, prominence in candidates:
                cv2.circle(overlay, (x, y), 6, (255, 160, 0), -1)
                cv2.putText(overlay, f"{prominence:.0f}", (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 160, 0), 1, cv2.LINE_AA)
            for x, y in valleys.astype(int):
                cv2.circle(overlay, (x, y), 10, (0, 0, 255), -1)
            cv2.imwrite(str(OUT_DIR / "overlays" / f"{stem}.png"), overlay)
            row.update({"status": "ok", "candidate_count": len(candidates), "valley_points": valleys.tolist(), "crop_box_rotated": crop_box.tolist(), "roi_size": list(roi150.shape[::-1])})
        except Exception as error:
            row.update({"status": "failure", "failure": f"{type(error).__name__}: {error}", "candidate_count": len(locals().get("candidates", []))})
        rows.append(row)
    write_csv(OUT_DIR / "extraction_manifest.csv", rows)

    scored: list[dict[str, object]] = []
    for old in old_pairs:
        row = dict(old)
        probe, gallery = old["probe"], old["gallery"]
        row["palmseg_compat_distance"] = float(algorithm.match(features[probe], features[gallery])) if probe in features and gallery in features else ""
        scored.append(row)
    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", scored)
    values = [row for row in scored if row["palmseg_compat_distance"] != ""]
    genuine = np.asarray([float(row["palmseg_compat_distance"]) for row in values if row["pair_type"] == "genuine"], dtype=float)
    impostor = np.asarray([float(row["palmseg_compat_distance"]) for row in values if row["pair_type"] == "impostor"], dtype=float)
    threshold = 0.28
    summary = {
        "algorithm": "FastCC",
        "roi_method": "PalmSeg MATLAB pipeline compatibility port based on external/PalmSeg",
        "upstream_repo": "https://github.com/AngeloUNIMI/PalmSeg",
        "input_size": [128, 128],
        "input_mode": "8-bit grayscale",
        "threshold": threshold,
        "requested_pair_count": len(old_pairs),
        "scored_pair_count": len(values),
        "successful_roi_samples": len(features),
        "failed_samples": [row["sample"] for row in rows if row["status"] != "ok"],
        "pairing": "reused exactly from results/palm_roi_fastcc/shared_pair_manifest_and_scores.csv; self-pairs excluded",
        "branches": {"palmseg_compat": {
            "genuine_pairs": int(genuine.size),
            "impostor_pairs": int(impostor.size),
            "fmr_at_threshold": float(np.mean(impostor <= threshold)) if impostor.size else None,
            "fnmr_at_threshold": float(np.mean(genuine > threshold)) if genuine.size else None,
            "genuine_median": float(np.median(genuine)) if genuine.size else None,
            "impostor_median": float(np.median(impostor)) if impostor.size else None,
            "genuine_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
            "impostor_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
        }},
        "warning": "The upstream repo is MATLAB; this run uses a documented Python compatibility port because MATLAB/Octave was unavailable. This is a small same-session subset, not a cross-session Tongji benchmark.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
