"""Compare crop appearance and a fixed HOG baseline across two Pi bursts."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from skimage.feature import hog

BASE = Path(__file__).resolve().parents[1] / "data/processed/pi-own-captures/highres-2026-10-06/white-continuous-2026-10-06"


def feature(image: np.ndarray) -> np.ndarray:
    value = hog(image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), block_norm="L2-Hys", feature_vector=True)
    return value / max(np.linalg.norm(value), 1e-9)


def score(left: np.ndarray, right: np.ndarray) -> float:
    return float(1 - np.dot(left, right))


def main() -> None:
    features = defaultdict(dict)
    stats = defaultdict(list)
    for size in (128, 256):
        for batch in ("old", "new"):
            for hand in ("left", "right"):
                for path in sorted(BASE.glob(f"compare-{batch}-{hand}-*-pose_core{size}.png")):
                    index = int(path.name.split("-")[3])
                    image = np.asarray(Image.open(path).convert("L"))
                    middle = image[size // 8:7 * size // 8, size // 8:7 * size // 8]
                    stats[(size, batch, hand)].append({
                        "mean": float(middle.mean()), "contrast": float(middle.std()),
                        "laplacian_var": float(cv2.Laplacian(middle, cv2.CV_64F).var()),
                        "gradient_mean": float(np.hypot(*np.gradient(middle.astype(float))).mean()),
                    })
                    features[size][(batch, hand, index)] = feature(image)
    result = {"appearance": {}, "hog": {}}
    for key, values in stats.items():
        result["appearance"]["-".join(map(str, key))] = {
            measure: float(np.median([row[measure] for row in values])) for measure in values[0]
        }
    for size in (128, 256):
        result["hog"][str(size)] = {}
        f = features[size]
        for label, gallery_batch, probe_batch, minimum in (("old", "old", "old", 6), ("new", "new", "new", 6), ("old_to_new", "old", "new", 1), ("new_to_old", "new", "old", 1)):
            gallery = {hand: [f[(gallery_batch, hand, i)] for i in range(1, 6) if (gallery_batch, hand, i) in f] for hand in ("left", "right")}
            rows = []
            for (batch, hand, index), probe in f.items():
                if batch != probe_batch or index < minimum or not all(gallery.values()):
                    continue
                scores = {target: float(np.median([score(probe, candidate) for candidate in values])) for target, values in gallery.items()}
                other = "right" if hand == "left" else "left"
                rows.append({"hand": hand, "index": index, "same": scores[hand], "other": scores[other], "correct": scores[hand] < scores[other]})
            result["hog"][str(size)][label] = {"correct": sum(row["correct"] for row in rows), "probes": len(rows), "median_margin": float(np.median([row["other"] - row["same"] for row in rows])), "rows": rows}
    output = BASE / "cross-group-check.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"appearance": result["appearance"], "hog": {size: {batch: {k: value[k] for k in ("correct", "probes", "median_margin")} for batch, value in data.items()} for size, data in result["hog"].items()}}, indent=2))


if __name__ == "__main__":
    main()
