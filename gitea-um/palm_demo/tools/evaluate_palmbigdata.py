#!/usr/bin/env python3
"""Fixed enrollment/query split for the local Fast-CC development subset."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from palm_demo import DEFAULT_BASELINE, crop_and_normalize, load_fastcc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed" / "palmbigdata-dev")
    parser.add_argument("--enroll-per-identity", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.28)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "palmbigdata-dev" / "fixed_split_results.json")
    args = parser.parse_args()
    rows = list(csv.DictReader((args.data / "manifest.csv").open(encoding="utf-8")))
    groups: dict[str, list[Path]] = {}
    for row in rows:
        groups.setdefault(row["identity"], []).append(args.data / row["file"])
    algorithm = load_fastcc(DEFAULT_BASELINE)
    features: dict[str, list[np.ndarray]] = {}
    extraction_ms: list[float] = []
    for identity, paths in sorted(groups.items()):
        values: list[np.ndarray] = []
        for path in sorted(paths):
            started = time.perf_counter()
            roi, _ = crop_and_normalize(Image.open(path), (0, 0, 1, 1))
            values.append(algorithm.extract(roi))
            extraction_ms.append((time.perf_counter() - started) * 1000)
        features[identity] = values
    genuine: list[float] = []
    impostor: list[float] = []
    for identity, values in features.items():
        enrollment = values[: args.enroll_per_identity]
        for probe in values[args.enroll_per_identity :]:
            genuine.append(float(np.median([algorithm.match(probe, item) for item in enrollment])))
            for other, other_values in features.items():
                if other != identity:
                    impostor.append(float(np.median([algorithm.match(probe, item) for item in other_values[: args.enroll_per_identity]])))
    genuine_array = np.asarray(genuine)
    impostor_array = np.asarray(impostor)
    result = {
        "algorithm": "FastCC",
        "identities": len(features),
        "enrollment_per_identity": args.enroll_per_identity,
        "queries_per_identity": max(len(next(iter(features.values()))) - args.enroll_per_identity, 0),
        "genuine_pairs": len(genuine),
        "impostor_pairs": len(impostor),
        "threshold": args.threshold,
        "fmr_at_threshold": float(np.mean(impostor_array <= args.threshold)),
        "fnmr_at_threshold": float(np.mean(genuine_array > args.threshold)),
        "genuine_median": float(np.median(genuine_array)),
        "impostor_median": float(np.median(impostor_array)),
        "genuine_p95": float(np.percentile(genuine_array, 95)),
        "impostor_p05": float(np.percentile(impostor_array, 5)),
        "feature_extraction_ms_mean": float(np.mean(extraction_ms)),
        "feature_extraction_ms_p95": float(np.percentile(extraction_ms, 95)),
        "warning": "Development subset and fixed split only; not a Pi-camera or generalisation claim.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
