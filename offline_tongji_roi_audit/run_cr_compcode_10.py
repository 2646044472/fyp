"""Run the official CR_CompCode port on the ten extracted samples 00001-00010."""

from __future__ import annotations

import json
from pathlib import Path

from run_cr_compcode import classify_branch, make_gabor_array, write_csv


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "results" / "cr_compcode_10"
SAMPLES = [f"{index:05d}" for index in range(1, 11)]


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = {sample: 1 for sample in SAMPLES}
    pairs = [
        {
            "probe": probe,
            "gallery": gallery,
            "probe_palm_id": 1,
            "gallery_palm_id": 1,
            "pair_type": "genuine",
        }
        for probe in SAMPLES
        for gallery in SAMPLES
        if probe != gallery
    ]
    gabor = make_gabor_array()
    merged_pairs = pairs
    branch_data = {}
    for branch in ("reference", "palm_roi"):
        branch_pairs, data = classify_branch(branch, SAMPLES, labels, pairs, gabor)
        merged_pairs = branch_pairs if branch == "reference" else [
            {**reference_row, f"{branch}_cr_compcode_residual": palm_row[f"{branch}_cr_compcode_residual"]}
            for reference_row, palm_row in zip(merged_pairs, branch_pairs)
        ]
        branch_data[branch] = data
        (OUT_DIR / f"{branch}_rank1_predictions.json").write_text(json.dumps(data["predictions"], indent=2) + "\n", encoding="utf-8")
    write_csv(OUT_DIR / "pair_manifest_and_scores.csv", merged_pairs)
    summary = {
        "algorithm": "CR_CompCode / CRC_RLS",
        "samples": SAMPLES,
        "sample_count": len(SAMPLES),
        "identity_count": 1,
        "pair_count": len(pairs),
        "genuine_pairs": len(pairs),
        "impostor_pairs": 0,
        "warning": "00001-00010 are the ten images of the same Tongji palm; this run cannot measure impostor separation.",
        "branches": {branch: branch_data[branch]["summary"] for branch in branch_data},
        "source_full_run": str(ROOT / "results" / "cr_compcode" / "summary.json"),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
