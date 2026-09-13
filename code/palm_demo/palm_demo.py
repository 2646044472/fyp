#!/usr/bin/env python3
"""Fixed-stand, local-only 1:1 palm verification demo for Raspberry Pi.

This is a capture-and-matching baseline, not a liveness detector, access-control
product, cross-device benchmark, or security claim. Keep the hand, distance, and
lighting stable during enrollment and verification.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from biometric import extract_feature, load_fastcc as _load_fastcc
from camera import capture_image as _capture_image
from gallery import Gallery, load_policy
from roi import AutomaticPalmROI, normalize_crop
from templates import TemplateStore, safe_user_id


ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
DEFAULT_BASELINE = ROOT / "vendor" / "palmprint-recognition-python"
DEFAULT_CROP = (0.19, 0.15, 0.81, 0.85)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def load_fastcc(baseline_path: Path) -> Any:
    return _load_fastcc(baseline_path)


def parse_crop(value: str) -> tuple[float, float, float, float]:
    try:
        crop = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("crop must be left,top,right,bottom") from error
    if len(crop) != 4 or not (0 <= crop[0] < crop[2] <= 1 and 0 <= crop[1] < crop[3] <= 1):
        raise argparse.ArgumentTypeError("crop values must be ordered fractions between 0 and 1")
    return crop


def crop_and_normalize(image: Image.Image, crop: tuple[float, float, float, float]) -> tuple[np.ndarray, dict[str, float]]:
    return normalize_crop(image, crop)


def capture_image(args: argparse.Namespace) -> Image.Image:
    if args.image:
        return Image.open(args.image).copy()
    return _capture_image(args.camera, args.width, args.height, args.warmup)


def capture_feature(args: argparse.Namespace, algorithm: Any) -> tuple[np.ndarray, dict[str, float], float]:
    started = time.perf_counter()
    image = capture_image(args)
    if getattr(args, "roi_mode", "fixed") == "auto":
        roi_result = AutomaticPalmROI(min_contrast=args.min_contrast).extract(image)
        if roi_result.status != "OK" or roi_result.roi is None:
            raise RuntimeError(roi_result.reason or "ROI extraction failed")
        roi, quality = roi_result.roi, roi_result.quality
    else:
        roi, quality = crop_and_normalize(image, args.crop)
    if quality["contrast"] < args.min_contrast:
        raise RuntimeError(f"Low contrast ({quality['contrast']:.1f} < {args.min_contrast:.1f}); improve lighting or hand position.")
    feature = extract_feature(algorithm, roi).astype(bool)
    duration_ms = (time.perf_counter() - started) * 1000
    if args.save_crop:
        Path(args.save_crop).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(roi).save(args.save_crop)
    return feature.astype(bool), quality, duration_ms


def template_paths(user: str) -> tuple[Path, Path]:
    return TemplateStore(RUNTIME / "templates").paths(user)


def write_log(event: dict[str, Any]) -> None:
    path = RUNTIME / "logs" / f"{datetime.now().date().isoformat()}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp"] = utc_now()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def wait_for_sample(index: int, total: int, interactive: bool, delay: float) -> None:
    if interactive:
        input(f"Place palm in the fixed guide, then press Enter for sample {index}/{total} ... ")
    elif index > 1:
        time.sleep(delay)


def enroll(args: argparse.Namespace) -> int:
    if args.image is None and not args.authorized_local_biometric:
        raise RuntimeError(
            "Persistent camera enrollment requires --authorized-local-biometric after institutional approval and participant consent. "
            "Use --image for an authorised offline-data smoke test."
        )
    algorithm = load_fastcc(args.baseline_path)
    features: list[np.ndarray] = []
    qualities: list[dict[str, float]] = []
    timings: list[float] = []
    for index in range(1, args.samples + 1):
        wait_for_sample(index, args.samples, args.interactive, args.delay)
        feature, quality, timing = capture_feature(args, algorithm)
        features.append(feature)
        qualities.append(quality)
        timings.append(timing)
        print(f"Captured {index}/{args.samples}: contrast={quality['contrast']:.1f}, pipeline={timing:.1f} ms")

    data_path, meta_path = template_paths(args.user)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(data_path, features=np.stack(features))
    metadata = {
        "user": args.user,
        "created_at": utc_now(),
        "algorithm": "FastCC",
        "camera": args.camera,
        "capture_profile": args.capture_profile,
        "threshold": args.threshold,
        "samples": args.samples,
        "crop": args.crop,
        "min_contrast": args.min_contrast,
        "quality": qualities,
        "pipeline_ms": {"mean": float(np.mean(timings)), "max": float(np.max(timings))},
        "host": platform.platform(),
        "warning": "Provisional threshold until calibrated on development data and verified on the same fixed capture setup.",
    }
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_log(
        {
            "event": "enroll",
            "user": args.user,
            "camera": args.camera,
            "capture_profile": args.capture_profile,
            "samples": args.samples,
            "pipeline_ms_mean": metadata["pipeline_ms"]["mean"],
        }
    )
    print(f"Enrollment complete. Saved template samples only: {data_path}")
    print(f"Provisional threshold: {args.threshold:.3f}. Run calibrate_palmbigdata.py before reporting any result.")
    return 0


def verify(args: argparse.Namespace) -> int:
    if args.image is None and not args.authorized_local_biometric:
        raise RuntimeError(
            "Camera verification requires --authorized-local-biometric after institutional approval and participant consent."
        )
    algorithm = load_fastcc(args.baseline_path)
    data_path, meta_path = template_paths(args.user)
    if not data_path.exists() or not meta_path.exists():
        raise RuntimeError(f"No template for {args.user}. Enroll first.")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    if metadata.get("capture_profile") != args.capture_profile:
        raise RuntimeError(
            f"Template was enrolled as {metadata.get('capture_profile')!r}, but this run is {args.capture_profile!r}. "
            "Do not mix RGB and NoIR+IR templates. Enroll a separate test identity for each profile."
        )
    threshold = args.threshold if args.threshold is not None else float(metadata["threshold"])
    feature, quality, pipeline_ms = capture_feature(args, algorithm)
    stored = np.load(data_path)["features"]
    scores = [float(algorithm.match(feature, candidate)) for candidate in stored]
    score = float(np.median(scores))
    accepted = score <= threshold
    event = {
        "event": "verify",
        "user": args.user,
        "decision": "ACCEPT" if accepted else "REJECT",
        "score": score,
        "threshold": threshold,
        "camera": args.camera,
        "capture_profile": args.capture_profile,
        "quality": quality,
        "pipeline_ms": pipeline_ms,
    }
    write_log(event)
    print(f"{event['decision']}: distance={score:.4f}, threshold={threshold:.4f}, pipeline={pipeline_ms:.1f} ms")
    return 0 if accepted else 2


def list_users(_: argparse.Namespace) -> int:
    users = TemplateStore(RUNTIME / "templates").list_users()
    print("\n".join(users) if users else "No enrolled users.")
    return 0


def identify(args: argparse.Namespace) -> int:
    if args.image is None and not args.authorized_local_biometric:
        raise RuntimeError("Camera identification requires --authorized-local-biometric after institutional approval and participant consent.")
    policy = load_policy(args.policy_path)
    algorithm = load_fastcc(args.baseline_path)
    gallery = Gallery(TemplateStore(RUNTIME / "templates"), algorithm, policy["threshold"], policy["min_margin"])
    feature, quality, pipeline_ms = capture_feature(args, algorithm)
    result = gallery.identify(feature, args.capture_profile)
    write_log({"event": "identify", "result": result.status, "user_id": result.user_id, "score": result.score, "second_score": result.second_score, "gallery_size": gallery.size, "capture_profile": args.capture_profile, "quality": quality, "pipeline_ms": pipeline_ms, "search_ms": result.search_ms})
    print(f"{result.status}: user={result.user_id or 'none'} distance={result.score if result.score is not None else 'n/a'} search={result.search_ms:.1f} ms")
    return 0 if result.status == "MATCH" else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local-only fixed-stand palm verification baseline")
    parser.add_argument("--baseline-path", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--image", type=Path, help="Use an existing image instead of the Pi camera")
    parser.add_argument("--camera", type=int, default=0, help="Camera index from rpicam-hello --list")
    parser.add_argument(
        "--capture-profile",
        choices=("rgb", "noir-ir"),
        default="rgb",
        help="Records the optical setup and prevents RGB/NoIR template mixing",
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--warmup", type=float, default=1.5)
    parser.add_argument("--crop", type=parse_crop, default=DEFAULT_CROP)
    parser.add_argument("--min-contrast", type=float, default=12.0)
    parser.add_argument("--save-crop", type=Path, help="Optional local debug ROI; never enable for released data")
    parser.add_argument("--roi-mode", choices=("fixed", "auto"), default="fixed")
    parser.add_argument("--policy-path", type=Path, default=RUNTIME / "identification_policy.json")
    parser.add_argument(
        "--authorized-local-biometric",
        action="store_true",
        help="Required before a camera capture is persisted or compared to a local template",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    enroll_parser = commands.add_parser("enroll", help="Capture several template samples")
    enroll_parser.add_argument("--user", required=True)
    enroll_parser.add_argument("--samples", type=int, default=5)
    enroll_parser.add_argument("--threshold", type=float, default=0.28)
    enroll_parser.add_argument("--interactive", action="store_true", help="Wait for Enter before every capture")
    enroll_parser.add_argument("--delay", type=float, default=1.5)
    enroll_parser.set_defaults(func=enroll)
    verify_parser = commands.add_parser("verify", help="Capture and compare one 1:1 probe")
    verify_parser.add_argument("--user", required=True)
    verify_parser.add_argument("--threshold", type=float, help="Override enrolled threshold for one run")
    verify_parser.set_defaults(func=verify)
    users_parser = commands.add_parser("users", help="List local template identifiers")
    users_parser.set_defaults(func=list_users)
    identify_parser = commands.add_parser("identify", help="Identify a palm against the local 1:N gallery")
    identify_parser.set_defaults(func=identify)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (RuntimeError, ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
