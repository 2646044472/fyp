"""Run RobustPalmRoi on the Tongji pairs and compare unchanged Fast-CC scores.

All outputs stay below offline_tongji_roi_audit.  The RobustPalmRoi Windows
loader is local to this script because the upstream Python wrapper only names
Linux/macOS library suffixes; the native algorithm and config are unchanged.
"""

from __future__ import annotations

import ctypes
import csv
import hashlib
import io
import json
import platform
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT / "RobustPalmRoi"
RAW_DIR = ROOT / "raw_extract" / "session1"
REF_DIR = ROOT / "roi_extract" / "session1"
OUT = ROOT / "robust_fastcc_results"
FASTCC_ROOT = ROOT.parent / "code" / "palm_demo" / "vendor" / "palmprint-recognition-python"
sys.path.insert(0, str(FASTCC_ROOT))
from palmprint.algorithms.fastcc import FastCCAlgorithm  # noqa: E402


class WindowsHandlerChain:
    """ctypes binding matching the upstream pypackage/rpr.py ABI."""

    def __init__(self, library: Path, config: Path) -> None:
        self.library = library
        self.config = config
        self._lib = ctypes.cdll.LoadLibrary(str(library))
        self._lib.init_chain.argtypes = [ctypes.c_char_p]
        self._lib.init_chain.restype = ctypes.c_void_p
        self._lib.chain_process_bytes.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_long),
            ctypes.c_char_p,
        ]
        self._lib.chain_process_bytes.restype = None
        self._chain = self._lib.init_chain(str(config).encode("utf-8"))
        if not self._chain:
            raise RuntimeError("RobustPalmRoi init_chain returned null")

    def process_bytes(self, data: bytes) -> bytes:
        out_capacity = 1024 * 1024
        out = ctypes.create_string_buffer(out_capacity)
        out_size = ctypes.c_long(0)
        status = ctypes.create_string_buffer(128)
        self._lib.chain_process_bytes(
            self._chain,
            data,
            len(data),
            out,
            out_capacity,
            ctypes.byref(out_size),
            status,
        )
        if status.raw[0] != 0:
            raise RuntimeError(status.raw[1:].split(b"\0", 1)[0].decode("utf-8", errors="replace"))
        if out_size.value <= 0:
            raise RuntimeError("RobustPalmRoi returned an empty ROI")
        return out.raw[: out_size.value]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lossless_bmp_transport(path: Path) -> bytes:
    """Encode the decoded TIFF pixels as BMP for this OpenCV Windows build.

    The vcpkg OpenCV image-codecs build used by the isolated DLL accepts BMP
    but not TIFF/PNG.  BMP is lossless here; no pixels or image dimensions are
    changed before RobustPalmRoi receives the bytes.
    """
    with Image.open(path) as image:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="BMP")
        return buffer.getvalue()


def equal_error_threshold(genuine: np.ndarray, impostor: np.ndarray) -> tuple[float, float, float]:
    candidates = np.unique(np.concatenate((genuine, impostor)))
    best = min(
        ((abs(float(np.mean(genuine > t)) - float(np.mean(impostor <= t))), float(t)) for t in candidates),
        key=lambda item: item[0],
    )[1]
    return best, float(np.mean(impostor <= best)), float(np.mean(genuine > best))


def score_variant(variant: str, files: dict[str, Path], sample_ids: list[int]) -> dict[str, Any]:
    algorithm = FastCCAlgorithm()
    features: dict[str, np.ndarray] = {}
    for sample_id in sample_ids:
        with Image.open(files[f"{sample_id:05d}"]).convert("L") as image:
            if image.size != (128, 128):
                raise ValueError(f"{variant} sample {sample_id:05d} is not 128x128: {image.size}")
            features[f"{sample_id:05d}"] = np.asarray(image, dtype=np.uint8)

    # Same deterministic gallery/probe split for both variants: first three
    # samples of each Tongji palm are gallery; remaining samples are probes.
    identities = {
        "palm_1": [f"{i:05d}" for i in range(1, 11) if i in sample_ids],
        "palm_2": [f"{i:05d}" for i in range(11, 21) if i in sample_ids],
    }
    gallery: dict[str, list[str]] = {}
    probes: dict[str, list[str]] = {}
    for identity, ids in identities.items():
        gallery[identity] = ids[:3]
        probes[identity] = ids[3:]

    genuine: list[dict[str, Any]] = []
    impostor: list[dict[str, Any]] = []
    for identity, probe_ids in probes.items():
        other_identity = "palm_2" if identity == "palm_1" else "palm_1"
        for probe_id in probe_ids:
            probe_feature = algorithm.extract(features[probe_id])
            same_scores = [float(algorithm.match(probe_feature, algorithm.extract(features[g]))) for g in gallery[identity]]
            genuine.append({"variant": variant, "identity": identity, "probe": probe_id, "gallery": ";".join(gallery[identity]), "score": float(np.median(same_scores))})
            for gallery_id in gallery[other_identity]:
                impostor_feature = algorithm.extract(features[gallery_id])
                impostor.append({"variant": variant, "identity": identity, "probe": probe_id, "gallery_identity": other_identity, "gallery": gallery_id, "score": float(algorithm.match(probe_feature, impostor_feature))})

    genuine_scores = np.asarray([r["score"] for r in genuine], dtype=float)
    impostor_scores = np.asarray([r["score"] for r in impostor], dtype=float)
    threshold, fmr, fnmr = equal_error_threshold(genuine_scores, impostor_scores) if len(genuine_scores) and len(impostor_scores) else (None, None, None)
    return {
        "variant": variant,
        "sample_ids": sample_ids,
        "gallery": gallery,
        "probe_counts": {identity: len(ids) for identity, ids in probes.items()},
        "genuine_pairs": genuine,
        "impostor_pairs": impostor,
        "scores": {
            "genuine_count": len(genuine),
            "impostor_count": len(impostor),
            "genuine_mean": float(np.mean(genuine_scores)) if len(genuine_scores) else None,
            "genuine_median": float(np.median(genuine_scores)) if len(genuine_scores) else None,
            "genuine_p95": float(np.percentile(genuine_scores, 95)) if len(genuine_scores) else None,
            "impostor_mean": float(np.mean(impostor_scores)) if len(impostor_scores) else None,
            "impostor_median": float(np.median(impostor_scores)) if len(impostor_scores) else None,
            "impostor_p05": float(np.percentile(impostor_scores, 5)) if len(impostor_scores) else None,
            "eer_threshold": threshold,
            "fmr_at_eer_threshold": fmr,
            "fnmr_at_eer_threshold": fnmr,
        },
    }


def make_comparison_sheet(
    extraction_rows: list[dict[str, Any]],
    robust_files: dict[str, Path],
    output_path: Path,
) -> None:
    """Create a contact sheet without inventing a RobustPalmRoi image on failure."""
    from PIL import ImageDraw

    raw_size = (320, 240)
    roi_size = (160, 160)
    status_size = (220, 160)
    margin = 12
    header_h = 28
    row_h = 270
    width = margin * 5 + raw_size[0] + roi_size[0] * 2 + status_size[0]
    height = header_h + margin + row_h * len(extraction_rows)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    per_sample_dir = output_path.parent / "robust_comparison_samples"
    per_sample_dir.mkdir(parents=True, exist_ok=True)
    headers = ["raw Tongji image", "reference ROI", "RobustPalmRoi ROI", "status"]
    x_positions = [margin, margin * 2 + raw_size[0], margin * 3 + raw_size[0] + roi_size[0], margin * 4 + raw_size[0] + roi_size[0] * 2]
    for x, header in zip(x_positions, headers):
        draw.text((x, 6), header, fill="black")

    for row_index, row in enumerate(extraction_rows):
        y = header_h + margin + row_index * row_h
        sample = row["sample"]
        raw_path = RAW_DIR / f"{sample}.tiff"
        ref_path = REF_DIR / f"{sample}.bmp"
        with Image.open(raw_path) as raw:
            raw_preview = raw.convert("RGB").resize(raw_size, Image.Resampling.LANCZOS)
        sheet.paste(raw_preview, (x_positions[0], y))
        with Image.open(ref_path) as reference:
            reference_preview = reference.convert("L").resize(roi_size, Image.Resampling.NEAREST).convert("RGB")
        sheet.paste(reference_preview, (x_positions[1], y))
        if sample in robust_files:
            with Image.open(robust_files[sample]) as robust:
                robust_preview = robust.convert("L").resize(roi_size, Image.Resampling.NEAREST).convert("RGB")
            sheet.paste(robust_preview, (x_positions[2], y))
        else:
            draw.rectangle((x_positions[2], y, x_positions[2] + roi_size[0], y + roi_size[1]), fill=(242, 242, 242), outline=(180, 180, 180))
            draw.multiline_text((x_positions[2] + 8, y + 50), "extraction\nfailed", fill=(160, 0, 0), spacing=4)
        draw.text((x_positions[3], y + 8), f"sample {sample}", fill="black")
        if row["status"] == "ok":
            draw.text((x_positions[3], y + 32), "OK", fill=(0, 110, 0))
        else:
            draw.multiline_text((x_positions[3], y + 32), row.get("failure", "failure"), fill=(160, 0, 0), spacing=4)
        sheet.crop((0, y, width, min(y + row_h, height))).save(per_sample_dir / f"sample_{sample}.png", format="PNG")
    sheet.save(output_path, format="PNG")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    library = REPO / "build_win" / "robust-palm-roi.dll"
    if not library.is_file():
        raise SystemExit(f"Native RobustPalmRoi DLL not found: {library}")
    config = REPO / "samples" / "config.yaml"
    chain = WindowsHandlerChain(library, config)
    robust_files: dict[str, Path] = {}
    extraction_rows: list[dict[str, Any]] = []
    raw_output_dir = OUT / "robust_raw"
    normalized_dir = OUT / "robust_roi_128"
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    for sample_id in range(1, 16):
        stem = f"{sample_id:05d}"
        raw_path = RAW_DIR / f"{stem}.tiff"
        try:
            roi_bytes = chain.process_bytes(lossless_bmp_transport(raw_path))
            raw_roi_path = raw_output_dir / f"{stem}.png"
            raw_roi_path.write_bytes(roi_bytes)
            with Image.open(io.BytesIO(roi_bytes)) as roi:
                gray128 = roi.convert("L").resize((128, 128), Image.Resampling.LANCZOS)
                normalized_path = normalized_dir / f"{stem}.png"
                gray128.save(normalized_path, format="PNG")
            robust_files[stem] = normalized_path
            extraction_rows.append({"sample": stem, "status": "ok", "input_transport": "lossless RGB BMP bytes from decoded Tongji TIFF", "raw_output": str(raw_roi_path), "normalized_output": str(normalized_path), "output_bytes": len(roi_bytes), "output_sha256": sha256(raw_roi_path)})
        except Exception as exc:
            extraction_rows.append({"sample": stem, "status": "failure", "failure": f"{type(exc).__name__}: {exc}"})

    requested_ids = list(range(1, 16))
    complete_ids = sorted(int(stem) for stem in robust_files)
    reference_files = {f"{sample_id:05d}": REF_DIR / f"{sample_id:05d}.bmp" for sample_id in requested_ids}
    variant_results = [score_variant("tongji_reference", reference_files, requested_ids)]
    if complete_ids:
        variant_results.append(score_variant("robust_palm_roi", robust_files, complete_ids))

    make_comparison_sheet(extraction_rows, robust_files, OUT / "robust_vs_reference_sheet.png")

    with (OUT / "robust_extraction.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = sorted({key for row in extraction_rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(extraction_rows)
    pair_rows = []
    for sample_id in complete_ids:
        stem = f"{sample_id:05d}"
        pair_rows.append({"sample": stem, "raw": str(RAW_DIR / f"{stem}.tiff"), "reference_roi": str(REF_DIR / f"{stem}.bmp"), "robust_roi_128": str(robust_files[stem]), "reference_size": list(Image.open(REF_DIR / f"{stem}.bmp").size), "robust_size": list(Image.open(robust_files[stem]).size)})
    with (OUT / "roi_pair_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = sorted({key for row in pair_rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(pair_rows)
    with (OUT / "genuine_impostor_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        rows = []
        for result in variant_results:
            rows.extend(result["genuine_pairs"])
            rows.extend(result["impostor_pairs"])
        fields = sorted({key for row in rows for key in row}) if rows else ["variant"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "platform": platform.platform(),
        "robust_palm_roi_repo": str(REPO),
        "robust_palm_roi_config": str(config),
        "native_library": str(library),
        "fastcc_source": str(FASTCC_ROOT / "palmprint" / "algorithms" / "fastcc.py"),
        "fastcc_source_sha256": sha256(FASTCC_ROOT / "palmprint" / "algorithms" / "fastcc.py"),
        "requested_samples": 15,
        "robust_successes": len(complete_ids),
        "robust_failures": 15 - len(complete_ids),
        "paired_sample_ids": complete_ids,
        "paired_fastcc_comparison_available": bool(complete_ids),
        "failure_samples": [row for row in extraction_rows if row["status"] != "ok"],
        "gallery_rule": "first 3 samples per Tongji palm; remaining samples are probes",
        "input_transport": "Pillow decodes the original TIFF; identical RGB pixels are losslessly encoded as BMP bytes because the isolated Windows OpenCV build accepts BMP but not TIFF/PNG.",
        "variants": variant_results,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
