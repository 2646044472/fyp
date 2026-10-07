"""Run PKLNet on the user's ten local debug captures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import torch

from run_pklnet_tongji import (
    PKLNET_DIR,
    preprocess,
    standardize_for_pklnet,
    std_to_raw,
    roiExtractor,
    pklnet,
)

from run_palm_roi_fastcc import fastcc_input, write_csv
from palmprint.algorithms.fastcc import FastCCAlgorithm

CAPTURE_DIR = Path(r"D:\github\fyp\code\data\debug_capture\20260916T152121Z")
OUT_DIR = CAPTURE_DIR / "pklnet"
SAMPLES = [f"sample_{index:03d}" for index in range(1, 11)]


def run() -> None:
    for name in ("roi_128_gray", "fastcc_inputs", "overlays_raw", "overlays_standardized", "keypoints"):
        (OUT_DIR / name).mkdir(parents=True, exist_ok=True)
    checkpoint = PKLNET_DIR / "net_params_500.pth"
    model = pklnet()
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=False))
    model.eval()
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    with torch.inference_mode():
        for sample in SAMPLES:
            raw_path = CAPTURE_DIR / sample / "raw.png"
            row: dict[str, object] = {"sample": sample, "raw_file": str(raw_path)}
            try:
                raw_bgr = cv2.imread(str(raw_path), cv2.IMREAD_COLOR)
                if raw_bgr is None:
                    raise RuntimeError("raw_image_unreadable")
                canvas, meta = standardize_for_pklnet(raw_bgr)
                outputs = model(preprocess(canvas))
                keypoints = outputs[0][0].detach().cpu().numpy().astype(np.float32)
                p1, p2 = keypoints[:2], keypoints[2:4]
                anticlock = roiExtractor.isAntiClock(keypoints[:6])
                corners = np.asarray(roiExtractor.getROIckp(p1, p2, anticlock), dtype=np.float32)
                roi = roiExtractor.getROIimg(canvas, corners, side=128)
                if roi is None or roi.shape != (128, 128):
                    raise RuntimeError("invalid_roi_output")
                roi = np.asarray(roi, dtype=np.uint8)
                fast = fastcc_input(Image.fromarray(roi, mode="L"))
                Image.fromarray(roi, mode="L").save(OUT_DIR / "roi_128_gray" / f"{sample}.png")
                Image.fromarray(fast, mode="L").save(OUT_DIR / "fastcc_inputs" / f"{sample}.png")
                features[sample] = algorithm.extract(fast)

                standard_overlay = canvas.copy()
                roiExtractor.drawROI(standard_overlay, [int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), *corners.reshape(-1).astype(int).tolist()])
                cv2.imwrite(str(OUT_DIR / "overlays_standardized" / f"{sample}.png"), standard_overlay)

                raw_overlay = raw_bgr.copy()
                raw_p1, raw_p2 = std_to_raw(tuple(p1), meta), std_to_raw(tuple(p2), meta)
                raw_corners = np.asarray([std_to_raw(tuple(point), meta) for point in corners], dtype=np.int32)
                cv2.polylines(raw_overlay, [raw_corners.reshape(-1, 1, 2)], True, (0, 220, 255), 3)
                cv2.line(raw_overlay, raw_p1, raw_p2, (255, 210, 50), 2)
                cv2.circle(raw_overlay, raw_p1, 7, (0, 0, 255), -1)
                cv2.circle(raw_overlay, raw_p2, 7, (0, 255, 0), -1)
                cv2.imwrite(str(OUT_DIR / "overlays_raw" / f"{sample}.png"), raw_overlay)

                (OUT_DIR / "keypoints" / f"{sample}.json").write_text(json.dumps({"keypoints_xy_standardized": keypoints.tolist(), "roi_corners_xy_standardized": corners.tolist(), "roi_corners_xy_raw": raw_corners.tolist(), "anticlock": bool(anticlock), "preprocessing": meta}, indent=2) + "\n", encoding="utf-8")
                row.update({"status": "ok", "raw_size": [int(raw_bgr.shape[1]), int(raw_bgr.shape[0])], "keypoints": keypoints.tolist(), "roi_corners_raw": raw_corners.tolist(), "preprocessing": meta})
            except Exception as error:
                row.update({"status": "failure", "failure": f"{type(error).__name__}: {error}"})
            rows.append(row)

    write_csv(OUT_DIR / "extraction_manifest.csv", rows)
    pair_rows: list[dict[str, object]] = []
    for probe in sorted(features):
        for gallery in sorted(features):
            if probe == gallery:
                continue
            pair_rows.append({"probe": probe, "gallery": gallery, "pair_type": "genuine", "fastcc_distance": float(algorithm.match(features[probe], features[gallery]))})
    write_csv(OUT_DIR / "pair_manifest_and_scores.csv", pair_rows)
    distances = np.asarray([row["fastcc_distance"] for row in pair_rows], dtype=float)
    summary = {
        "algorithm": "PKLNet + roiExtractor.py",
        "source": str(PKLNET_DIR),
        "weights": str(checkpoint),
        "capture_dir": str(CAPTURE_DIR),
        "sample_count": len(features),
        "failed_samples": [row["sample"] for row in rows if row["status"] != "ok"],
        "roi_size": [128, 128],
        "roi_mode": "8-bit grayscale",
        "fastcc_pair_count": len(pair_rows),
        "fastcc_genuine_median": float(np.median(distances)) if distances.size else None,
        "fastcc_genuine_p95": float(np.percentile(distances, 95)) if distances.size else None,
        "warning": "All ten debug captures are one local capture sequence/class; no impostor measurement is possible and rank-1 would be trivial.",
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
