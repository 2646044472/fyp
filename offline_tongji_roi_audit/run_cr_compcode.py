"""Official Tongji CR_CompCode port for the existing ROI comparison subset.

The formulas and parameters follow the official MATLAB source linked from the
Tongji project page.  The gallery/probe sample pairs are reused exactly from
the Fast-CC experiment, while CR_CompCode is evaluated in its native 1:N
CRC-RLS classification form.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
PREVIOUS_DIR = ROOT / "results" / "palm_roi_fastcc"
OUT_DIR = ROOT / "results" / "cr_compcode"

PATCH_SIZE = 14
ROI_SIZE = 128
LAMBDA = 1.35
SIGMA = 4.85
RATIO = 1.92
WAVELENGTH = 14.1
ORIENTATIONS = 6


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_gabor_array() -> np.ndarray:
    """Port gaborArray.m, including its circular support mask and FFT padding."""
    axis = np.arange(-17, 18, dtype=np.float64)
    x, y = np.meshgrid(axis, axis)
    rows, cols = np.indices((35, 35))
    mask = (((rows - 17) ** 2 + (cols - 17) ** 2) <= 289).astype(np.float64)
    out: list[np.ndarray] = []
    for orientation in range(ORIENTATIONS):
        theta = np.pi / 6.0 * orientation
        x_theta = x * np.cos(theta) + y * np.sin(theta)
        y_theta = -x * np.sin(theta) + y * np.cos(theta)
        gb = np.exp(-0.5 * (x_theta**2 / SIGMA**2 + y_theta**2 / (RATIO * SIGMA) ** 2))
        gb *= np.cos(2.0 * np.pi / WAVELENGTH * x_theta)
        mean_inner = float(np.sum(gb * mask) / np.sum(mask))
        gb = (gb - mean_inner) * mask
        out.append(np.fft.fft2(gb, s=(ROI_SIZE + 34, ROI_SIZE + 34)))
    return np.stack(out, axis=2)


def compete_code(image: np.ndarray, gabor: np.ndarray) -> np.ndarray:
    """Port CompeteCode.m; values are 1..6 like MATLAB min(...,[],3)."""
    image = np.asarray(image, dtype=np.float64)
    image_fft = np.fft.fft2(image, s=(ROI_SIZE + 34, ROI_SIZE + 34))
    responses = []
    for orientation in range(ORIENTATIONS):
        response = np.fft.ifft2(image_fft * gabor[:, :, orientation]).real
        responses.append(response[17:17 + ROI_SIZE, 17:17 + ROI_SIZE])
    return np.argmin(np.stack(responses, axis=2), axis=2) + 1


def create_cc_feature(image: np.ndarray, gabor: np.ndarray) -> np.ndarray:
    """Port createCCFeature.m: 9x9 patches, 6-bin local histograms."""
    code = compete_code(image, gabor)
    patches_per_row = ROI_SIZE // PATCH_SIZE
    used = patches_per_row * PATCH_SIZE
    trim = (ROI_SIZE - used) // 2
    code = code[trim:trim + used, trim:trim + used]
    features: list[np.ndarray] = []
    for patch_row in range(patches_per_row):
        for patch_col in range(patches_per_row):
            patch = code[
                patch_row * PATCH_SIZE:(patch_row + 1) * PATCH_SIZE,
                patch_col * PATCH_SIZE:(patch_col + 1) * PATCH_SIZE,
            ]
            histogram = np.bincount(patch.ravel(), minlength=ORIENTATIONS + 1)[1:ORIENTATIONS + 1]
            features.append(histogram.astype(np.float64) / (PATCH_SIZE**2))
    return np.concatenate(features)


def normalized_feature(path: Path, gabor: np.ndarray) -> np.ndarray:
    image = np.asarray(Image.open(path).convert("L"), dtype=np.float64)
    if image.shape != (ROI_SIZE, ROI_SIZE):
        raise ValueError(f"expected 128x128 ROI, got {image.shape} from {path}")
    feature = create_cc_feature(image, gabor)
    norm = float(np.linalg.norm(feature))
    if norm <= 0:
        raise ValueError(f"zero feature norm for {path}")
    return feature / norm


def branch_paths(branch: str) -> Path:
    if branch == "reference":
        return PREVIOUS_DIR / "reference_128_gray"
    if branch == "palm_roi":
        return PREVIOUS_DIR / "palm_roi_128_gray"
    raise ValueError(branch)


def classify_branch(branch: str, samples: list[str], labels: dict[str, int], pairs: list[dict[str, str]], gabor: np.ndarray) -> tuple[list[dict[str, object]], dict[str, object]]:
    directory = branch_paths(branch)
    features = {sample: normalized_feature(directory / f"{sample}.png", gabor) for sample in samples}
    classes = sorted(set(labels.values()))
    residual_by_probe_gallery: dict[tuple[str, str], float] = {}
    predictions: list[dict[str, object]] = []

    for probe in samples:
        gallery = [sample for sample in samples if sample != probe]
        dictionary = np.column_stack([features[sample] for sample in gallery])
        projection = np.linalg.solve(
            dictionary.T @ dictionary + LAMBDA * np.eye(dictionary.shape[1]),
            dictionary.T,
        )
        x0 = projection @ features[probe]
        residuals: dict[int, float] = {}
        for class_id in classes:
            positions = [index for index, sample in enumerate(gallery) if labels[sample] == class_id]
            partial_dictionary = dictionary[:, positions]
            partial_x0 = x0[positions]
            residuals[class_id] = float(np.sum((partial_dictionary @ partial_x0 - features[probe]) ** 2))
        predicted = min(residuals, key=residuals.get)
        predictions.append({"probe": probe, "true_class": labels[probe], "predicted_class": predicted, "correct": predicted == labels[probe], "residuals": residuals})
        for gallery_sample in gallery:
            residual_by_probe_gallery[(probe, gallery_sample)] = residuals[labels[gallery_sample]]

    output_pairs: list[dict[str, object]] = []
    for original in pairs:
        row = dict(original)
        row[f"{branch}_cr_compcode_residual"] = residual_by_probe_gallery[(original["probe"], original["gallery"])]
        output_pairs.append(row)
    genuine = np.asarray([row[f"{branch}_cr_compcode_residual"] for row in output_pairs if row["pair_type"] == "genuine"], dtype=float)
    impostor = np.asarray([row[f"{branch}_cr_compcode_residual"] for row in output_pairs if row["pair_type"] == "impostor"], dtype=float)
    summary = {
        "genuine_pairs": int(genuine.size),
        "impostor_pairs": int(impostor.size),
        "rank1_correct": int(sum(item["correct"] for item in predictions)),
        "rank1_total": len(predictions),
        "rank1_accuracy": float(np.mean([item["correct"] for item in predictions])),
        "genuine_residual_median": float(np.median(genuine)) if genuine.size else None,
        "impostor_residual_median": float(np.median(impostor)) if impostor.size else None,
        "genuine_residual_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
        "impostor_residual_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
        "pairwise_ordering_fraction": float(np.mean(genuine < np.median(impostor))) if genuine.size and impostor.size else None,
    }
    return output_pairs, {"summary": summary, "predictions": predictions}


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pairs = list(csv.DictReader((PREVIOUS_DIR / "shared_pair_manifest_and_scores.csv").open(encoding="utf-8")))
    samples = sorted({row["probe"] for row in pairs} | {row["gallery"] for row in pairs})
    labels = {row["probe"]: int(row["probe_palm_id"]) for row in pairs}
    gabor = make_gabor_array()
    branch_data: dict[str, object] = {}
    merged_pairs = pairs
    for branch in ("reference", "palm_roi"):
        branch_pairs, data = classify_branch(branch, samples, labels, pairs, gabor)
        merged_pairs = branch_pairs if branch == "reference" else [
            {**reference_row, f"{branch}_cr_compcode_residual": palm_row[f"{branch}_cr_compcode_residual"]}
            for reference_row, palm_row in zip(merged_pairs, branch_pairs)
        ]
        branch_data[branch] = data
        (OUT_DIR / f"{branch}_rank1_predictions.json").write_text(json.dumps(data["predictions"], indent=2) + "\n", encoding="utf-8")

    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", merged_pairs)
    summary = {
        "algorithm": "CR_CompCode / CRC_RLS",
        "official_source": "https://cslinzhang.github.io/ContactlessPalm/CR_CompCode.rar",
        "official_parameters": {
            "patch_size": PATCH_SIZE,
            "lambda": LAMBDA,
            "sigma": SIGMA,
            "ratio": RATIO,
            "wavelength": WAVELENGTH,
            "gabor_orientations": ORIENTATIONS,
            "roi_size": [ROI_SIZE, ROI_SIZE],
            "feature_dimension": (ROI_SIZE // PATCH_SIZE) ** 2 * ORIENTATIONS,
        },
        "gallery_samples_per_probe": len(samples) - 1,
        "probe_samples": len(samples),
        "shared_pair_count": len(pairs),
        "pairing": "reused exactly from results/palm_roi_fastcc/shared_pair_manifest_and_scores.csv; self-pairs excluded",
        "warning": "This is a small same-session subset. The official Tongji protocol uses session1 as gallery and session2 as probe; this workspace subset has only session1 images.",
        "branches": {branch: branch_data[branch]["summary"] for branch in branch_data},
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
