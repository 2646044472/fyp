#!/usr/bin/env python3
"""Calculate a development-only Fast-CC threshold from a prepared PolyU P_F subset."""

from __future__ import annotations

import argparse
import csv
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from palm_demo import DEFAULT_BASELINE, crop_and_normalize, load_fastcc


def equal_error_threshold(genuine: np.ndarray, impostor: np.ndarray) -> tuple[float, float, float]:
    candidates = np.unique(np.concatenate((genuine, impostor)))
    best = min(
        ((abs(float(np.mean(genuine > threshold)) - float(np.mean(impostor <= threshold))), threshold) for threshold in candidates),
        key=lambda item: item[0],
    )[1]
    fnmr = float(np.mean(genuine > best))
    fmr = float(np.mean(impostor <= best))
    return float(best), fmr, fnmr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed" / "palmbigdata-dev")
    parser.add_argument("--baseline-path", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "palmbigdata-dev" / "calibration.json")
    args = parser.parse_args()
    manifest = args.data / "manifest.csv"
    if not manifest.is_file():
        parser.error("No manifest. Run prepare_palmbigdata.py first.")
    algorithm = load_fastcc(args.baseline_path)
    groups: dict[str, list[np.ndarray]] = {}
    with manifest.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            image = Image.open(args.data / row["file"])
            roi, _ = crop_and_normalize(image, (0, 0, 1, 1))
            groups.setdefault(row["identity"], []).append(algorithm.extract(roi))
    genuine = np.array([algorithm.match(left, right) for features in groups.values() for left, right in combinations(features, 2)])
    representatives = [features[0] for features in groups.values()]
    impostor = np.array([algorithm.match(left, right) for left, right in combinations(representatives, 2)])
    threshold, fmr, fnmr = equal_error_threshold(genuine, impostor)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "{\n"
        f"  \"algorithm\": \"FastCC\",\n  \"threshold_eer\": {threshold:.8f},\n"
        f"  \"fmr\": {fmr:.8f},\n  \"fnmr\": {fnmr:.8f},\n"
        f"  \"genuine_pairs\": {len(genuine)},\n  \"impostor_pairs\": {len(impostor)}\n}}\n",
        encoding="utf-8",
    )
    print(args.output.read_text(encoding="utf-8"))
    print("Development-data threshold only. Do not use it as a Pi-camera performance claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
