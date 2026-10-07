"""Run the PKLNet ROI locator from code/pklnet on the Tongji audit subset."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
import types

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
PKLNET_DIR = PROJECT / "code" / "pklnet"
RAW_DIR = ROOT / "raw_extract" / "session1"
PAIR_FILE = ROOT / "results" / "palm_roi_fastcc" / "shared_pair_manifest_and_scores.csv"
OUT_DIR = ROOT / "results" / "pklnet"

sys.path.insert(0, str(PKLNET_DIR))
# PKLNet targets an older torchvision where this helper lived under
# torchvision.models.utils. Keep the upstream source untouched and provide
# the moved symbol only for this runner.
from torch.hub import load_state_dict_from_url
import torchvision.models
torchvision_legacy_utils = types.ModuleType("torchvision.models.utils")
torchvision_legacy_utils.load_state_dict_from_url = load_state_dict_from_url
sys.modules["torchvision.models.utils"] = torchvision_legacy_utils
from lib.models.nets.pklnet import pklnet  # noqa: E402
import roiExtractor  # noqa: E402

sys.path.insert(0, str(ROOT / "palm_roi_env"))
sys.path.insert(0, str(ROOT))
from run_palm_roi_fastcc import fastcc_input, write_csv  # noqa: E402
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


def standardize_for_pklnet(raw_bgr: np.ndarray) -> tuple[np.ndarray, dict[str, object]]:
    """Match TestLoader: rotate landscape input, resize, and pad to 400x300."""
    original_h, original_w = raw_bgr.shape[:2]
    rotated = original_w > original_h
    image = cv2.rotate(raw_bgr, cv2.ROTATE_90_CLOCKWISE) if rotated else raw_bgr.copy()
    h, w = image.shape[:2]
    canvas = np.zeros((400, 300, 3), dtype=np.uint8)
    if float(h / w) > 4.0 / 3.0:
        resized = cv2.resize(image, (int(400.0 * w / h), 400))
        canvas[:, :resized.shape[1]] = resized
        scale = (resized.shape[1] / w, 400.0 / h)
    else:
        resized = cv2.resize(image, (300, int(300.0 * h / w)))
        canvas[:resized.shape[0], :] = resized
        scale = (300.0 / w, resized.shape[0] / h)
    return canvas, {
        "original_size": [original_w, original_h],
        "rotated_landscape": rotated,
        "rotated_size": [int(image.shape[1]), int(image.shape[0])],
        "resized_size": [int(resized.shape[1]), int(resized.shape[0])],
        "scale_xy": [float(scale[0]), float(scale[1])],
    }


def preprocess(canvas_bgr: np.ndarray) -> torch.Tensor:
    array = canvas_bgr.transpose(2, 0, 1).astype(np.float32) / 255.0
    mean = np.asarray([0.485, 0.456, 0.406], dtype=np.float32)[:, None, None]
    std = np.asarray([0.229, 0.224, 0.225], dtype=np.float32)[:, None, None]
    return torch.from_numpy((array - mean) / std).unsqueeze(0)


def std_to_raw(point: tuple[float, float], meta: dict[str, object]) -> tuple[int, int]:
    x, y = point
    sx, sy = meta["scale_xy"]
    xr, yr = x / sx, y / sy
    if meta["rotated_landscape"]:
        original_w, original_h = meta["original_size"]
        # Inverse of cv2.ROTATE_90_CLOCKWISE.
        return int(round(yr)), int(round(original_h - 1 - xr))
    return int(round(xr)), int(round(yr))


def run() -> None:
    for name in ("standardized_inputs", "roi_128_gray", "fastcc_inputs", "overlays_standardized", "overlays_raw", "keypoints"):
        (OUT_DIR / name).mkdir(parents=True, exist_ok=True)

    model = pklnet()
    checkpoint = PKLNET_DIR / "net_params_500.pth"
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(state)
    model.eval()
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    with torch.inference_mode():
        for raw_path in sorted(RAW_DIR.glob("*.tiff")):
            stem = raw_path.stem
            raw_bgr = cv2.imread(str(raw_path), cv2.IMREAD_COLOR)
            row: dict[str, object] = {"sample": stem, "raw_file": raw_path.name, "palm_id": 1 if int(stem) <= 10 else 2}
            try:
                canvas, meta = standardize_for_pklnet(raw_bgr)
                input_tensor = preprocess(canvas)
                outputs = model(input_tensor)
                keypoints = outputs[0][0].detach().cpu().numpy().astype(np.float32)
                if keypoints.shape[0] < 4 or not np.isfinite(keypoints[:4]).all():
                    raise RuntimeError("invalid_predicted_keypoints")
                p1, p2 = keypoints[:2], keypoints[2:4]
                anticlock = roiExtractor.isAntiClock(keypoints[:6])
                corners = np.asarray(roiExtractor.getROIckp(p1, p2, anticlock), dtype=np.float32)
                roi = roiExtractor.getROIimg(canvas, corners, side=128)
                if roi is None or roi.shape != (128, 128):
                    raise RuntimeError("invalid_roi_output")
                roi = np.asarray(roi, dtype=np.uint8)
                fast = fastcc_input(Image.fromarray(roi, mode="L"))
                Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)).save(OUT_DIR / "standardized_inputs" / f"{stem}.png")
                Image.fromarray(roi, mode="L").save(OUT_DIR / "roi_128_gray" / f"{stem}.png")
                Image.fromarray(fast, mode="L").save(OUT_DIR / "fastcc_inputs" / f"{stem}.png")
                features[stem] = algorithm.extract(fast)

                standard_overlay = canvas.copy()
                roiExtractor.drawROI(standard_overlay, [int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), *corners.reshape(-1).astype(int).tolist()])
                cv2.imwrite(str(OUT_DIR / "overlays_standardized" / f"{stem}.png"), standard_overlay)

                raw_overlay = raw_bgr.copy()
                raw_points = [std_to_raw(tuple(point), meta) for point in np.vstack((p1, p2, corners))]
                raw_p1, raw_p2 = raw_points[:2]
                raw_corners = np.asarray(raw_points[2:], dtype=np.int32)
                cv2.polylines(raw_overlay, [raw_corners.reshape(-1, 1, 2)], True, (0, 220, 255), 4)
                cv2.line(raw_overlay, raw_p1, raw_p2, (255, 210, 50), 3)
                cv2.circle(raw_overlay, raw_p1, 9, (0, 0, 255), -1)
                cv2.circle(raw_overlay, raw_p2, 9, (0, 255, 0), -1)
                cv2.imwrite(str(OUT_DIR / "overlays_raw" / f"{stem}.png"), raw_overlay)
                (OUT_DIR / "keypoints" / f"{stem}.json").write_text(json.dumps({"keypoints_xy": keypoints.tolist(), "roi_corners_xy": corners.tolist(), "anticlock": bool(anticlock), "preprocessing": meta}, indent=2) + "\n", encoding="utf-8")
                row.update({"status": "ok", "predicted_keypoints": keypoints.tolist(), "roi_corners": corners.tolist(), "anticlock": bool(anticlock), "preprocessing": meta})
            except Exception as error:
                row.update({"status": "failure", "failure": f"{type(error).__name__}: {error}"})
            rows.append(row)

    write_csv(OUT_DIR / "extraction_manifest.csv", rows)
    old_pairs = list(csv.DictReader(PAIR_FILE.open(encoding="utf-8")))
    scored: list[dict[str, object]] = []
    for old in old_pairs:
        row = dict(old)
        probe, gallery = old["probe"], old["gallery"]
        row["pklnet_distance"] = float(algorithm.match(features[probe], features[gallery])) if probe in features and gallery in features else ""
        scored.append(row)
    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", scored)
    values = [row for row in scored if row["pklnet_distance"] != ""]
    genuine = np.asarray([float(row["pklnet_distance"]) for row in values if row["pair_type"] == "genuine"], dtype=float)
    impostor = np.asarray([float(row["pklnet_distance"]) for row in values if row["pair_type"] == "impostor"], dtype=float)
    threshold = 0.28
    summary = {
        "algorithm": "FastCC",
        "roi_method": "PKLNet learned keypoint localization + roiExtractor.py",
        "source": str(PKLNET_DIR),
        "weights": str(checkpoint),
        "input_size": [128, 128],
        "input_mode": "8-bit grayscale",
        "threshold": threshold,
        "requested_pair_count": len(old_pairs),
        "scored_pair_count": len(values),
        "successful_roi_samples": len(features),
        "failed_samples": [row["sample"] for row in rows if row["status"] != "ok"],
        "pairing": "reused exactly from results/palm_roi_fastcc/shared_pair_manifest_and_scores.csv; self-pairs excluded",
        "branches": {"pklnet": {
            "genuine_pairs": int(genuine.size),
            "impostor_pairs": int(impostor.size),
            "fmr_at_threshold": float(np.mean(impostor <= threshold)) if impostor.size else None,
            "fnmr_at_threshold": float(np.mean(genuine > threshold)) if genuine.size else None,
            "genuine_median": float(np.median(genuine)) if genuine.size else None,
            "impostor_median": float(np.median(impostor)) if impostor.size else None,
            "genuine_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
            "impostor_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
        }},
        "warning": "This is a small same-session subset, not a cross-session Tongji benchmark. PKLNet was trained for its documented PalmKit-style preprocessing; this run matches its TestLoader preprocessing on the available raw images.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
