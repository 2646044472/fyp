"""Exploratory comparison of Pi palm ROI geometry on saved full stills.

The two batches have one subject and correlated photos. Results diagnose the
local implementation; they are not estimates of biometric accuracy.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import palm_demo  # noqa: E402
import palm_roi  # noqa: E402
from biometric import load_algorithm  # noqa: E402

DATA = ROOT / "data/processed/pi-own-captures/highres-2026-10-06"
OLD = DATA / "highres_capture"
NEW = DATA / "white-continuous-2026-10-06"
OUTPUT = NEW / "roi-variant-comparison.json"


def images():
    old = defaultdict(list)
    for folder in OLD.iterdir():
        metadata_file = folder / "metadata.json"
        if metadata_file.is_file():
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            if metadata.get("hand") in ("left", "right") and (folder / "full.jpg").is_file():
                old[metadata["hand"]].append(folder)
    for hand, folders in old.items():
        for index, folder in enumerate(sorted(folders), 1):
            yield "old", hand, index, folder / "full.jpg"
    for hand, session in (("left", "20261006T035537011048Z-05a19b1d"), ("right", "20261006T040847950968Z-c9b9f00a")):
        for index, folder in enumerate(sorted((NEW / session).glob("sample_*")), 1):
            yield "new", hand, index, folder / "full.jpg"


def crop(full, quad, size):
    gray = palm_roi.warp_palm_roi(full, quad, (size, size))
    array = np.asarray(gray, dtype=np.float32)
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise ValueError("flat crop")
    return np.clip((array - low) * 255 / (high - low), 0, 255).astype(np.uint8)


def rank(features, algorithm):
    out = {}
    for name, gallery_batch, probe_batch, probe_min in (("old", "old", "old", 6), ("new", "new", "new", 6), ("old_to_new", "old", "new", 1), ("new_to_old", "new", "old", 1)):
        gallery = {hand: [features[(gallery_batch, hand, i)] for i in range(1, 6) if (gallery_batch, hand, i) in features] for hand in ("left", "right")}
        probes = [(key, feature) for key, feature in features.items() if key[0] == probe_batch and key[2] >= probe_min]
        rows = []
        for key, feature in probes:
            if not all(gallery.values()):
                continue
            scores = {hand: float(np.median([algorithm.match(feature, target) for target in targets])) for hand, targets in gallery.items()}
            hand = key[1]
            rows.append({"hand": hand, "index": key[2], "same": scores[hand], "other": scores["right" if hand == "left" else "left"], "correct": scores[hand] < scores["right" if hand == "left" else "left"]})
        out[name] = {"probes": len(rows), "correct": sum(row["correct"] for row in rows), "median_margin": float(np.median([row["other"] - row["same"] for row in rows])) if rows else None, "rows": rows}
    return out


def main():
    algorithm = load_algorithm(palm_demo.DEFAULT_BASELINE, "DoN")
    alt = load_algorithm(palm_demo.DEFAULT_BASELINE, "FastCC")
    features = {name: {alg: {} for alg in ("DoN", "FastCC")} for name in ("detector_broad128", "detector_core128", "pose_broad128", "pose_core128", "pose_core128_clahe", "pose_core256")}
    detections = []
    for batch, hand, index, path in images():
        full = Image.open(path).convert("RGB")
        resized = full.resize((480, 360), Image.Resampling.LANCZOS)
        key = (batch, hand, index)
        detection_row = {"batch": batch, "hand": hand, "index": index}
        for refine in (False, True):
            tracker = palm_roi.HandLandmarkTracker(
                ROOT / "models/palm_detection_mediapipe_2023feb.onnx",
                ROOT / "models/handpose_estimation_mediapipe_2023feb.onnx" if refine else None,
                input_size=(320, 240), smoothing_alpha=1.0,
                recovery_pass=True, refine_pose=refine,
            )
            try:
                timestamp = int(time.monotonic() * 1000)
                tracker.submit(resized, timestamp)
                result = tracker.roi_status(resized.size, frame_timestamp_ms=timestamp)
                label = "pose" if refine else "detector"
                detection_row[label] = {"status": result.status, "source": result.diagnostics.get("tracking_source"), "reason": result.reason}
                if result.quad is None:
                    continue
                landmarks = tracker._landmarks
                if landmarks is None:
                    continue
                for suffix, width, height, size in (("broad128", 2.0, 2.0, 128), ("core128", 1.3, 1.3, 128), ("core256", 1.3, 1.3, 256)):
                    name = f"{label}_{suffix}"
                    if name not in features:
                        continue
                    quad = palm_roi.landmarks_to_palm_quad(landmarks, resized.size, width_scale=width, height_scale=height, min_span_px=32, fit_to_frame=True)
                    quad *= np.array([full.width / resized.width, full.height / resized.height], dtype=np.float32)
                    roi = crop(full, quad, size)
                    if name in ("pose_core128", "pose_core256"):
                        Image.fromarray(roi).save(NEW / f"compare-{batch}-{hand}-{index:02d}-{name}.png")
                    for alg_name, alg in (("DoN", algorithm), ("FastCC", alt)):
                        features[name][alg_name][key] = alg.extract(roi)
                        if name == "pose_core128":
                            import cv2
                            enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(roi)
                            features["pose_core128_clahe"][alg_name][key] = alg.extract(enhanced)
            finally:
                tracker.close()
        detections.append(detection_row)
        print(batch, hand, index, detection_row.get("detector"), detection_row.get("pose"), flush=True)
    report = {"detections": detections, "matches": {variant: {name: rank(values, algorithm if name == "DoN" else alt) for name, values in methods.items()} for variant, methods in features.items()}}
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for variant, methods in report["matches"].items():
        for name, batches in methods.items():
            print(variant, name, {batch: (entry["correct"], entry["probes"], entry["median_margin"]) for batch, entry in batches.items()})


if __name__ == "__main__":
    main()
