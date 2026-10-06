"""Run official CR_CompCode on the user's ten debug-capture ROI images."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from run_cr_compcode import create_cc_feature, make_gabor_array, write_csv
from PIL import Image


CAPTURE_DIR = Path(r"D:\github\fyp\code\data\debug_capture\20260916T152121Z")
OUT_DIR = CAPTURE_DIR / "cr_compcode"
SAMPLES = [f"sample_{index:03d}" for index in range(1, 11)]
LAMBDA = 1.35


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gabor = make_gabor_array()
    features: dict[str, np.ndarray] = {}
    for sample in SAMPLES:
        path = CAPTURE_DIR / sample / "roi_128.png"
        image = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
        if image.shape != (128, 128):
            raise ValueError(f"expected 128x128 ROI, got {image.shape}: {path}")
        feature = create_cc_feature(image, gabor)
        features[sample] = feature / np.linalg.norm(feature)

    pair_rows: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    for probe in SAMPLES:
        gallery = [sample for sample in SAMPLES if sample != probe]
        dictionary = np.column_stack([features[sample] for sample in gallery])
        projection = np.linalg.solve(dictionary.T @ dictionary + LAMBDA * np.eye(len(gallery)), dictionary.T)
        x0 = projection @ features[probe]
        residual = float(np.sum((dictionary @ x0 - features[probe]) ** 2))
        predictions.append({"probe": probe, "true_class": 1, "predicted_class": 1, "correct": True, "residual": residual})
        for gallery_sample in gallery:
            pair_rows.append({
                "probe": probe,
                "gallery": gallery_sample,
                "pair_type": "genuine",
                "cr_compcode_residual": residual,
            })

    write_csv(OUT_DIR / "pair_manifest_and_scores.csv", pair_rows)
    (OUT_DIR / "rank1_predictions.json").write_text(json.dumps(predictions, indent=2) + "\n", encoding="utf-8")
    residuals = np.asarray([row["cr_compcode_residual"] for row in pair_rows], dtype=float)
    summary = {
        "algorithm": "CR_CompCode / CRC_RLS",
        "source_roi": str(CAPTURE_DIR),
        "samples": SAMPLES,
        "sample_count": len(SAMPLES),
        "feature_dimension": 486,
        "gallery_samples_per_probe": len(SAMPLES) - 1,
        "pair_count": len(pair_rows),
        "genuine_pairs": len(pair_rows),
        "impostor_pairs": 0,
        "rank1_correct": len(predictions),
        "rank1_total": len(predictions),
        "rank1_accuracy": 1.0,
        "genuine_residual_median": float(np.median(residuals)),
        "genuine_residual_p95": float(np.percentile(residuals, 95)),
        "warning": "All ten debug captures are one local capture sequence/class; no impostor measurement is possible.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
