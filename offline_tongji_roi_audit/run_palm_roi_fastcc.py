"""Run PyPI palm-roi on the Tongji raw subset and compare Fast-CC inputs.

The landmark detector and the Fast-CC implementation are deliberately kept
unchanged.  Only the crop implementation changes between the reference-ROI
and palm-roi branches; the directed pair manifest is shared by both branches.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

# Bootstrap the isolated PyPI dependency path before importing OpenCV.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_BOOTSTRAP_ROOT / "palm_roi_env"))

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT.parent / "code" / "palm_demo"
RAW_DIR = ROOT / "raw_extract" / "session1"
REFERENCE_DIR = ROOT / "roi_extract" / "session1"
OUT_DIR = ROOT / "results" / "palm_roi_fastcc"
PYPI_ENV = ROOT / "palm_roi_env"
FASTCC_DIR = APP_DIR / "vendor" / "palmprint-recognition-python"
DETECTOR_MODEL = APP_DIR / "models" / "palm_detection_mediapipe_2023feb.onnx"
POSE_MODEL = APP_DIR / "models" / "handpose_estimation_mediapipe_2023feb.onnx"

# The PyPI package is isolated in palm_roi_env so the app's local palm_roi.py
# cannot be imported accidentally.
sys.path.insert(0, str(PYPI_ENV))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(FASTCC_DIR))

import palm_roi as pypi_palm_roi  # noqa: E402
from mp_handpose import MPHandPose  # noqa: E402
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_anchors() -> np.ndarray:
    anchors: list[list[float]] = []
    for y in range(24):
        for x in range(24):
            anchors.extend([[(x + 0.5) / 24.0, (y + 0.5) / 24.0]] * 2)
    for y in range(12):
        for x in range(12):
            anchors.extend([[(x + 0.5) / 12.0, (y + 0.5) / 12.0]] * 6)
    return np.asarray(anchors, dtype=np.float32)


def infer_detector(net: cv2.dnn.Net, bgr: np.ndarray) -> tuple[np.ndarray, float, np.ndarray] | None:
    height, width = bgr.shape[:2]
    model_width, model_height = 192, 192
    ratio = min(model_height / height, model_width / width)
    resized_shape = (np.asarray((height, width), dtype=np.float32) * ratio).astype(np.int32)
    resized = cv2.resize(bgr, (int(resized_shape[1]), int(resized_shape[0])))
    pad_h = model_height - int(resized_shape[0])
    pad_w = model_width - int(resized_shape[1])
    left, top = pad_w // 2, pad_h // 2
    padded = cv2.copyMakeBorder(resized, top, pad_h - top, left, pad_w - left, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    net.setInput(rgb[np.newaxis, ...])
    outputs = net.forward(net.getUnconnectedOutLayersNames())
    logits = outputs[1][0, :, 0].astype(np.float64)
    scores = 1.0 / (1.0 + np.exp(-logits))
    best = int(np.argmax(scores))
    score = float(scores[best])
    if score < 0.42:
        return None

    anchors = load_anchors()
    box_delta = outputs[0][0, :, 0:4]
    landmark_delta = outputs[0][0, :, 4:]
    input_size = np.asarray((192, 192), dtype=np.float32)
    scale = float(max(width, height))
    center_delta = box_delta[:, :2] / input_size
    size_delta = box_delta[:, 2:] / input_size
    box = np.concatenate(((center_delta[best] - size_delta[best] / 2 + anchors[best]) * scale,
                          (center_delta[best] + size_delta[best] / 2 + anchors[best]) * scale))
    points = landmark_delta[best].reshape(7, 2) / input_size
    points = (points + anchors[best]) * scale
    pad_bias = np.asarray((left, top), dtype=np.float32) / ratio
    points -= pad_bias
    box -= np.asarray((pad_bias[0], pad_bias[1], pad_bias[0], pad_bias[1]), dtype=np.float32)
    return points.astype(np.float32), score, box.astype(np.float32)


def standardize_gray(image: Image.Image) -> Image.Image:
    return image.convert("L").resize((128, 128), Image.Resampling.LANCZOS)


def fastcc_input(image: Image.Image) -> np.ndarray:
    """Keep the existing palm_demo full-frame normalization before Fast-CC."""
    gray = image.convert("L").resize((128, 128), Image.Resampling.LANCZOS)
    array = np.asarray(gray, dtype=np.float32)
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise RuntimeError("ROI has no usable intensity range")
    return np.clip((array - low) * 255.0 / (high - low), 0, 255).astype(np.uint8)


def palm_roi_extract(raw: Image.Image, hand: np.ndarray) -> tuple[Image.Image, str | None]:
    width, height = raw.size
    gray = np.asarray(raw.convert("L"), dtype=np.uint8)
    index_mcp = tuple((hand[5] / np.asarray((width, height), dtype=np.float32)).tolist())
    pinky_mcp = tuple((hand[17] / np.asarray((width, height), dtype=np.float32)).tolist())
    wrist = tuple((hand[0] / np.asarray((width, height), dtype=np.float32)).tolist())
    roi, error = pypi_palm_roi.extract(gray, index_mcp, pinky_mcp, wrist)
    return Image.fromarray(np.asarray(roi, dtype=np.uint8), mode="L"), error


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for subdir in ("palm_roi_extracted", "palm_roi_128_gray", "reference_128_gray", "fastcc_inputs/palm_roi", "fastcc_inputs/reference"):
        (OUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

    detector = cv2.dnn.readNet(str(DETECTOR_MODEL))
    detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    pose = MPHandPose(str(POSE_MODEL), confThreshold=0.62, backendId=cv2.dnn.DNN_BACKEND_OPENCV, targetId=cv2.dnn.DNN_TARGET_CPU)
    algorithm = FastCCAlgorithm()

    features: dict[str, dict[str, np.ndarray]] = {"reference": {}, "palm_roi": {}}
    labels: dict[str, int] = {}
    extraction_rows: list[dict[str, object]] = []
    raw_paths = sorted(RAW_DIR.glob("*.tiff"))

    for raw_path in raw_paths:
        stem = raw_path.stem
        sample_index = int(stem)
        palm_id = 1 if sample_index <= 10 else 2
        labels[stem] = palm_id
        reference_path = REFERENCE_DIR / f"{stem}.bmp"
        raw = Image.open(raw_path).convert("RGB")
        reference_128 = standardize_gray(Image.open(reference_path))
        reference_128.save(OUT_DIR / "reference_128_gray" / f"{stem}.png")

        row: dict[str, object] = {
            "sample": stem,
            "palm_id": palm_id,
            "raw_file": raw_path.name,
            "raw_sha256": sha256(raw_path),
            "reference_file": reference_path.name,
            "reference_sha256": sha256(reference_path),
            "reference_status": "ok",
        }
        bgr = cv2.cvtColor(np.asarray(raw, dtype=np.uint8), cv2.COLOR_RGB2BGR)
        detection = infer_detector(detector, bgr)
        try:
            if detection is None:
                raise RuntimeError("detector_below_threshold_or_invalid")
            palm_points, detector_score, box = detection
            hand = pose.infer(bgr, np.concatenate((box, palm_points.reshape(-1))))
            if hand is None:
                raise RuntimeError("handpose_below_threshold")
            landmarks = hand[4:67].reshape(21, 3)[:, :2]
            extracted, error = palm_roi_extract(raw, landmarks)
            if error:
                raise RuntimeError(error)
            extracted.save(OUT_DIR / "palm_roi_extracted" / f"{stem}.png")
            palm_128 = standardize_gray(extracted)
            palm_128.save(OUT_DIR / "palm_roi_128_gray" / f"{stem}.png")
            row.update({
                "palm_roi_status": "ok",
                "detector_score": detector_score,
                "handpose_confidence": float(hand[-1]),
                "extracted_size": list(extracted.size),
            })
        except Exception as error:
            row.update({"palm_roi_status": "failure", "palm_roi_failure": f"{type(error).__name__}: {error}"})
            extraction_rows.append(row)
            continue

        ref_input = fastcc_input(reference_128)
        palm_input = fastcc_input(palm_128)
        Image.fromarray(ref_input, mode="L").save(OUT_DIR / "fastcc_inputs/reference" / f"{stem}.png")
        Image.fromarray(palm_input, mode="L").save(OUT_DIR / "fastcc_inputs/palm_roi" / f"{stem}.png")
        features["reference"][stem] = algorithm.extract(ref_input)
        features["palm_roi"][stem] = algorithm.extract(palm_input)
        row.update({"fastcc_reference_status": "ok", "fastcc_palm_roi_status": "ok"})
        extraction_rows.append(row)

    write_csv(OUT_DIR / "extraction_manifest.csv", extraction_rows)

    common_samples = sorted(set(features["reference"]) & set(features["palm_roi"]))
    pair_rows: list[dict[str, object]] = []
    for probe in common_samples:
        for gallery in common_samples:
            if probe == gallery:
                continue
            pair_type = "genuine" if labels[probe] == labels[gallery] else "impostor"
            row = {"probe": probe, "gallery": gallery, "pair_type": pair_type, "probe_palm_id": labels[probe], "gallery_palm_id": labels[gallery]}
            for branch in ("reference", "palm_roi"):
                row[f"{branch}_distance"] = float(algorithm.match(features[branch][probe], features[branch][gallery]))
            pair_rows.append(row)
    write_csv(OUT_DIR / "shared_pair_manifest_and_scores.csv", pair_rows)

    threshold = 0.28
    metrics: dict[str, object] = {
        "algorithm": "FastCC",
        "fastcc_baseline": str(FASTCC_DIR),
        "palm_roi_package": {"name": "palm-roi", "version": importlib.metadata.version("palm-roi")},
        "input_size": [128, 128],
        "input_mode": "8-bit grayscale",
        "threshold": threshold,
        "gallery_samples": len(common_samples),
        "probe_samples": len(common_samples),
        "shared_pair_count": len(pair_rows),
        "pairing": "directed all-other-image pairs over the 15-image subset; self-pairs excluded",
        "identity_labels": "existing audit convention: 00001-00010=palm 1, 00011-00015=palm 2",
        "warning": "This is a small same-session subset and is not a cross-session Tongji benchmark.",
        "branches": {},
    }
    for branch in ("reference", "palm_roi"):
        genuine = np.asarray([row[f"{branch}_distance"] for row in pair_rows if row["pair_type"] == "genuine"], dtype=float)
        impostor = np.asarray([row[f"{branch}_distance"] for row in pair_rows if row["pair_type"] == "impostor"], dtype=float)
        metrics["branches"][branch] = {
            "genuine_pairs": int(genuine.size),
            "impostor_pairs": int(impostor.size),
            "fmr_at_threshold": float(np.mean(impostor <= threshold)) if impostor.size else None,
            "fnmr_at_threshold": float(np.mean(genuine > threshold)) if genuine.size else None,
            "genuine_median": float(np.median(genuine)) if genuine.size else None,
            "impostor_median": float(np.median(impostor)) if impostor.size else None,
            "genuine_p95": float(np.percentile(genuine, 95)) if genuine.size else None,
            "impostor_p05": float(np.percentile(impostor, 5)) if impostor.size else None,
        }
    (OUT_DIR / "summary.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    run()
