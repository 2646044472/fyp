#!/usr/bin/env python3
"""Replay local saved camera samples; no camera or sample collection required."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import palm_roi
from debug_ui import CameraFeed
from live_roi import LiveROIOverlay


def motion_check(image, quad, status, output):
    """Check known pixel translations of a saved photo, not a live-motion claim."""
    import cv2

    overlay = LiveROIOverlay()
    captured = SimpleNamespace(image=image, frame_id=1, captured_monotonic=0.0)
    processed = SimpleNamespace(captured=captured, roi_quad=quad, roi_status=status)
    center = quad.mean(axis=0)
    direction = np.where(center < np.array(image.size) / 2, 1, -1)
    frames = []
    errors = []
    for index in range(10):
        offset = direction * index * 1.5
        transform = np.float32(((1, 0, offset[0]), (0, 1, offset[1])))
        moved = Image.fromarray(cv2.warpAffine(np.asarray(image), transform, image.size))
        actual, preview = overlay.update(moved, index + 1, index * 0.1, processed)
        if actual is None:
            return {"passed": False, "frame": index, "reason": preview.get("roi_reason")}
        errors.append(float(np.linalg.norm(actual - (quad + offset), axis=1).max()))
        frames.append(CameraFeed._annotate_roi(moved, actual, preview))
    if output is not None:
        frames[0].save(output, save_all=True, append_images=frames[1:], duration=100, loop=0)
    return {"passed": max(errors) < 2.0, "max_corner_error_px": round(max(errors), 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path)
    parser.add_argument("--legacy-bgr", action="store_true", help="Correct only samples saved before the RGB888 byte-order fix.")
    parser.add_argument("--motion-check", action="store_true", help="Test known translations of each photo and export one preview GIF.")
    parser.add_argument("--output", type=Path, default=ROOT / "runtime" / "roi_replay")
    args = parser.parse_args()
    paths = sorted(args.samples.glob("*.jpg"))
    if not paths:
        parser.error("No JPEG samples found")
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        if args.legacy_bgr:
            image = Image.fromarray(np.asarray(image)[:, :, ::-1].copy())
        tracker = palm_roi.HandLandmarkTracker(
            ROOT / "models" / "palm_detection_mediapipe_2023feb.onnx",
            smoothing_alpha=1.0, recovery_pass=True,
        )
        timestamp = int(time.monotonic() * 1000)
        start = time.perf_counter()
        tracker.submit(image, timestamp)
        elapsed = (time.perf_counter() - start) * 1000
        result = tracker.roi_status(image.size, frame_timestamp_ms=timestamp)
        status = result.as_dict()
        CameraFeed._annotate_roi(image, result.quad, status).save(args.output / path.name)
        if result.quad is not None:
            palm_roi.warp_palm_roi(image, result.quad).save(args.output / (path.stem + '-roi.png'))
        row = {"sample": path.name, "elapsed_ms": round(elapsed, 2), **status}
        if args.motion_check and result.quad is not None:
            row["motion_test"] = motion_check(
                image, result.quad, status,
                args.output / "simulated_motion.gif" if not rows else None,
            )
        rows.append(row)
        tracker.close()
    report = {
        "samples": len(rows),
        "tracking": sum(row["roi_status"] == "tracking" for row in rows),
        "legacy_bgr_corrected": args.legacy_bgr,
        "motion_checks_passed": sum(row.get("motion_test", {}).get("passed", False) for row in rows),
        "rows": rows,
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
