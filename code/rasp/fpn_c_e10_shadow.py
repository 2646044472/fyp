#!/usr/bin/env python3
"""Explicit CPU shadow check for the frozen FPN+C E10 pipeline; never an access decision."""

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path


PIPELINE = "fpn-c-e10-frozen"
ASSETS = {"fpn", "c"}
MAX_CHECKPOINT_BYTES = 256 << 20
MAX_IMAGE_FILE_BYTES = 64 << 20


class ShadowFailure(Exception):
    """A typed failure with a safe diagnostic, never a path or sample identifier."""


def keys_equal(data, expected):
    return isinstance(data, dict) and set(data) == expected


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def checksum(path):
    sha = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def parse_manifest(path):
    try:
        with Path(path).open("rb") as file:
            text = file.read(32769)
        if len(text) > 32768:
            raise ValueError("oversize")
        config = json.loads(text.decode("utf-8"), object_pairs_hook=unique_object)
    except (OSError, ValueError, RecursionError) as error:
        raise ShadowFailure("manifest_missing_or_invalid") from error

    if (not keys_equal(config, {"schema", "pipeline", "assets"})
            or type(config["schema"]) is not int
            or config["schema"] != 1
            or config["pipeline"] != PIPELINE
            or not keys_equal(config["assets"], ASSETS)):
        raise ShadowFailure("manifest_contract_mismatch")

    base = Path(path).resolve().parent
    checked = {}
    for role in sorted(ASSETS):
        entry = config["assets"][role]
        if not keys_equal(entry, {"file", "sha256"}):
            raise ShadowFailure("asset_contract_mismatch_" + role)
        name, digest = entry["file"], entry["sha256"]
        if (not isinstance(name, str)
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.safetensors", name)
                or not isinstance(digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise ShadowFailure("asset_contract_mismatch_" + role)

        candidate = base / name
        try:
            if candidate.is_symlink() or not candidate.is_file():
                raise ShadowFailure("asset_not_regular_file_" + role)
            if not 1 <= candidate.stat().st_size <= MAX_CHECKPOINT_BYTES:
                raise ShadowFailure("asset_size_invalid_" + role)
            if checksum(candidate) != digest:
                raise ShadowFailure("asset_digest_mismatch_" + role)
        except OSError as error:
            raise ShadowFailure("asset_unreadable_" + role) from error
        checked[role] = (candidate, digest)
    if checked["c"][1] == checked["fpn"][1]:
        raise ShadowFailure("assets_are_identical")
    return checked


def load_pipeline(config, backend):
    try:
        fpn_asset, c_asset = config["fpn"], config["c"]
        return backend.load_fpn(*fpn_asset, device="cpu"), backend.load_c(*c_asset, device="cpu")
    except Exception as error:
        raise ShadowFailure("backend_checkpoint_or_dependency_error") from error


def image_from_file(path, np):
    from PIL import Image, ImageOps
    try:
        with Image.open(path) as image:
            if image.width <= 0 or image.height <= 0 or image.width * image.height > 24_000_000:
                raise ShadowFailure("image_dimensions_invalid")
            return np.asarray(ImageOps.exif_transpose(image).convert("RGB"), dtype=np.uint8)
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        raise ShadowFailure("image_decode_failed") from error


def check_image_set(query, enroll):
    try:
        paths = [Path(p).resolve(strict=True) for p in [query, *enroll]]
        if len(paths) != 6 or any(not p.is_file() or not 1 <= p.stat().st_size <= MAX_IMAGE_FILE_BYTES for p in paths):
            raise ShadowFailure("image_type_or_size_invalid")
        if len({checksum(p) for p in paths}) != 6:
            raise ShadowFailure("requires_one_query_and_five_distinct_images")
        return paths
    except OSError as error:
        raise ShadowFailure("image_missing_or_unreadable") from error


def score_single_palm(query, enroll, models, backend, np):
    rgb_paths = check_image_set(query, enroll)
    crops = []
    for i, path in enumerate(rgb_paths):
        rgb = image_from_file(path, np)
        try:
            crop, _reason, _quad = backend.crop_gray(models[0], rgb, device="cpu")
        except Exception as error:
            raise ShadowFailure("roi_backend_error") from error
        if crop is None:
            raise ShadowFailure("roi_unavailable_query" if i == 0 else "roi_unavailable_enrollment")
        if not isinstance(crop, np.ndarray) or crop.shape != (128, 128) or crop.dtype != np.uint8:
            raise ShadowFailure("roi_contract_mismatch")
        crops.append(crop)

    try:
        inputs = np.stack(crops)
        features = np.asarray(backend.encode_c(models[1], inputs, device="cpu"))
        if features.shape != (6, 512) or features.dtype != np.float32:
            raise ShadowFailure("feature_contract_mismatch")
        features = features.astype(np.float64)
        norm = np.linalg.norm(features, axis=1, keepdims=True)
        if not np.isfinite(features).all() or not np.isfinite(norm).all() or np.any(norm <= 0):
            raise ShadowFailure("score_nonfinite_or_empty")
        features /= norm
        scores = features[1:] @ features[0]
        if not np.isfinite(scores).all() or np.any(np.abs(scores) > 1 + 1e-12):
            raise ShadowFailure("score_nonfinite_or_out_of_range")
        return float(np.clip(scores.max(), -1.0, 1.0))
    except ShadowFailure:
        raise
    except Exception as error:
        raise ShadowFailure("scoring_backend_error") from error


def main(argv=None, *, backend=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Local manifest beside approved safetensors; never commit it")
    subparsers = parser.add_subparsers(dest="mode", required=True)
    subparsers.add_parser("preflight", help="Validate and load both checkpoints on CPU; no image or unlock decision")
    scoring = subparsers.add_parser("shadow-score", help="One image against five fixed enrollment images, score only")
    scoring.add_argument("--query", required=True)
    scoring.add_argument("--enroll", nargs=5, required=True)
    args = parser.parse_args(argv)

    try:
        config = parse_manifest(args.manifest)
        if backend is None:
            backend = importlib.import_module("frozen_fpn_c_e10")
        models = load_pipeline(config, backend)
        result = {"pipeline": PIPELINE, "mode": args.mode, "status": "ok"}
        if args.mode == "shadow-score":
            import numpy as np
            result["max_cosine"] = score_single_palm(args.query, args.enroll, models, backend, np)
    except ShadowFailure as error:
        print(json.dumps({"pipeline": PIPELINE, "mode": args.mode, "status": "error", "reason": str(error)}), file=sys.stderr)
        return 2
    except Exception:
        print(json.dumps({"pipeline": PIPELINE, "mode": args.mode, "status": "error", "reason": "backend_or_dependency_unavailable"}), file=sys.stderr)
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
