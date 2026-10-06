#!/usr/bin/env python3
"""Collect 10 independent placements x 5 accepted dynamic ROI frames on Pi.

The script intentionally uses the existing debug-ui CameraFeed and dataset
writer.  It does not change detector, ROI geometry, or matcher parameters.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import palm_demo  # noqa: E402
import palm_roi  # noqa: E402
from debug_ui import CameraFeed, DEFAULT_HAND_MODEL, DEFAULT_HAND_POSE_MODEL  # noqa: E402
from roi_quality import DebugDatasetWriter  # noqa: E402


def wait_for_state(feed: CameraFeed, state: str, timeout_s: float) -> dict:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        status = feed.status()
        if status.get("quality_status") == state:
            return status
        time.sleep(0.10)
    raise TimeoutError(f"Timed out waiting for quality_status={state}; last={feed.status()}")


def capture_placement(
    feed: CameraFeed,
    root: Path,
    placement: int,
    total_placements: int,
    frames_per_placement: int,
) -> None:
    placement_root = root / f"placement_{placement:03d}"
    writer = DebugDatasetWriter(
        placement_root,
        camera_settings=feed.capture_settings(),
        roi_algorithm_version=palm_roi.ROI_GEOMETRY_VERSION,
    )
    previous_frame_id: int | None = None
    for sample_index in range(1, frames_per_placement + 1):
        image, roi, quad, status, frame_id = feed.snapshot(after_frame_id=previous_frame_id, timeout_s=5.0)
        if status.get("quality_status") != "READY" or quad is None:
            raise RuntimeError(f"Frame {frame_id} was not accepted: {status}")
        writer.save(
            sample_index=sample_index,
            raw_image=image,
            roi_128=roi,
            metadata={
                "placement_index": placement,
                "captured_at": palm_demo.utc_now(),
                "frame_id": frame_id,
                "captured_monotonic_ms": status.get("captured_monotonic_ms"),
                "processed_monotonic_ms": status.get("processed_monotonic_ms"),
                "frame_timestamp_ms": status.get("roi_diagnostics", {}).get("frame_timestamp_ms"),
                "roi_quad": quad.tolist(),
                "tracking_status": status.get("quality_status"),
                "tracker_status": status.get("roi_status"),
                "quality": status.get("quality", {}),
                "roi_geometry_diagnostics": status.get("roi_geometry_diagnostics", {}),
                "roi_status": status,
                "source": "collect_roi_diagnostics",
                "image_color_order": "RGB",
                "camera_array_format": "RGB888_BGR_bytes",
            },
        )
        previous_frame_id = frame_id
        print(f"placement {placement:02d}/{total_placements:02d}: frame {sample_index}/{frames_per_placement} saved ({frame_id})", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New session directory")
    parser.add_argument("--placements", type=int, default=10)
    parser.add_argument("--frames-per-placement", type=int, default=5)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--width", type=int, default=480)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--hand-model", type=Path, default=DEFAULT_HAND_MODEL)
    parser.add_argument("--hand-pose-model", type=Path, default=DEFAULT_HAND_POSE_MODEL)
    parser.add_argument("--refine-pose", action="store_true")
    parser.add_argument("--inference-ms", type=float, default=800.0)
    parser.add_argument("--input-width", type=int, default=320)
    parser.add_argument("--input-height", type=int, default=240)
    parser.add_argument("--recovery-pass", action="store_true")
    parser.add_argument("--camera-tuning-file", type=Path)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    args = parser.parse_args()
    if args.placements < 1 or args.frames_per_placement < 1 or args.frames_per_placement > 10:
        raise SystemExit("placements must be positive and frames-per-placement must be between 1 and 10")
    args.output.mkdir(parents=True, exist_ok=True)

    feed = CameraFeed(
        args.camera,
        args.width,
        args.height,
        roi_mode="dynamic",
        hand_model=args.hand_model,
        hand_pose_model=args.hand_pose_model,
        refine_pose=args.refine_pose,
        inference_ms=args.inference_ms,
        input_size=(args.input_width, args.input_height),
        recovery_pass=args.recovery_pass,
        camera_tuning_file=args.camera_tuning_file,
    )
    try:
        print("Remove your hand. Waiting for NO_HAND before the first placement.", flush=True)
        wait_for_state(feed, "NO_HAND", args.timeout_s)
        for placement in range(1, args.placements + 1):
            if placement > 1:
                input(f"Placement {placement}: remove hand, then press Enter when ready to check NO_HAND: ")
                wait_for_state(feed, "NO_HAND", args.timeout_s)
            feed.reset_roi_background()
            input(f"Placement {placement}: place the hand again, then press Enter to wait for READY: ")
            wait_for_state(feed, "READY", args.timeout_s)
            capture_placement(feed, args.output, placement, args.placements, args.frames_per_placement)
            print("Remove the hand completely before continuing.", flush=True)
        print(f"Complete diagnostic session: {args.output.resolve()}", flush=True)
    finally:
        feed.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
