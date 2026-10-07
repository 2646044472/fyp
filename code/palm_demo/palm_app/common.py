"""Shared application paths, ROI normalization, templates and event logs."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from palm_app import palm_roi

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
DEFAULT_BASELINE = ROOT / "vendor" / "palmprint-recognition-python"
DEFAULT_CROP = (0.19, 0.15, 0.81, 0.85)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def crop_and_normalize(
    image: Image.Image,
    crop: tuple[float, float, float, float] = DEFAULT_CROP,
    roi_quad: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    gray = image.convert("L")
    if roi_quad is None:
        width, height = gray.size
        box = (round(crop[0] * width), round(crop[1] * height), round(crop[2] * width), round(crop[3] * height))
        roi = gray.crop(box).resize((128, 128), Image.Resampling.LANCZOS)
    else:
        roi = palm_roi.warp_palm_roi(gray, roi_quad)
    array = np.asarray(roi, dtype=np.float32)
    contrast = float(array.std())
    gradient = np.hypot(*np.gradient(array))
    sharpness = float(gradient.var())
    low, high = np.percentile(array, (1, 99))
    if high - low < 1:
        raise RuntimeError("Frame has no usable intensity range. Reposition the hand and light.")
    normalized = np.clip((array - low) * 255.0 / (high - low), 0, 255).astype(np.uint8)
    return normalized, {"contrast": contrast, "sharpness": sharpness}


def template_paths(user: str) -> tuple[Path, Path]:
    safe_user = "".join(char for char in user if char.isalnum() or char in "-_")
    if not safe_user:
        raise ValueError("user must contain a letter or number")
    templates = RUNTIME / "templates"
    return templates / f"{safe_user}.npz", templates / f"{safe_user}.json"


def write_log(event: dict[str, Any]) -> None:
    path = RUNTIME / "logs" / f"{datetime.now().date().isoformat()}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp"] = utc_now()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
