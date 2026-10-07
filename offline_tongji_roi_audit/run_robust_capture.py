"""Run the isolated Windows RobustPalmRoi DLL on local debug captures."""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT.parent / "code" / "data" / "debug_capture" / "20260916T152121Z"
OUT = ROOT / "robust_capture_results"
REPO = ROOT / "RobustPalmRoi"
sys.path.insert(0, str(ROOT))
from run_robust_fastcc import WindowsHandlerChain, lossless_bmp_transport  # noqa: E402


def make_sheet(rows: list[dict[str, str]], robust_files: dict[str, Path]) -> None:
    raw_size = (320, 240)
    roi_size = (160, 160)
    status_width = 270
    margin = 12
    header_h = 28
    row_h = 270
    width = margin * 5 + raw_size[0] + roi_size[0] * 2 + status_width
    height = header_h + margin + row_h * len(rows)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    xs = [margin, margin * 2 + raw_size[0], margin * 3 + raw_size[0] + roi_size[0], margin * 4 + raw_size[0] + roi_size[0] * 2]
    for x, text in zip(xs, ["raw capture", "existing ROI 128", "RobustPalmRoi ROI", "status"]):
        draw.text((x, 6), text, fill="black")
    sample_dir = OUT / "comparison_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)
    for index, row in enumerate(rows):
        y = header_h + margin + index * row_h
        sample = row["sample"]
        with Image.open(CAPTURE / sample / "raw.png") as image:
            sheet.paste(image.convert("RGB").resize(raw_size, Image.Resampling.LANCZOS), (xs[0], y))
        with Image.open(CAPTURE / sample / "roi_128.png") as image:
            sheet.paste(image.convert("L").resize(roi_size, Image.Resampling.NEAREST).convert("RGB"), (xs[1], y))
        if sample in robust_files:
            with Image.open(robust_files[sample]) as image:
                sheet.paste(image.convert("L").resize(roi_size, Image.Resampling.NEAREST).convert("RGB"), (xs[2], y))
        else:
            draw.rectangle((xs[2], y, xs[2] + roi_size[0], y + roi_size[1]), fill=(242, 242, 242), outline=(180, 180, 180))
            draw.multiline_text((xs[2] + 8, y + 50), "extraction\nfailed", fill=(160, 0, 0), spacing=4)
        draw.text((xs[3], y + 8), f"{sample}", fill="black")
        draw.multiline_text((xs[3], y + 32), row["status"] + ("\n" + row.get("failure", "") if row.get("failure") else ""), fill=(0, 110, 0) if row["status"] == "ok" else (160, 0, 0), spacing=4)
        sheet.crop((0, y, width, min(y + row_h, height))).save(sample_dir / f"{sample}.png", format="PNG")
    sheet.save(OUT / "robust_capture_comparison_sheet.png", format="PNG")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = OUT / "robust_raw"
    normalized_dir = OUT / "robust_roi_128"
    raw_dir.mkdir(exist_ok=True)
    normalized_dir.mkdir(exist_ok=True)
    library = REPO / "build_win" / "robust-palm-roi.dll"
    config = REPO / "samples" / "config.yaml"
    chain = WindowsHandlerChain(library, config)
    rows: list[dict[str, str]] = []
    robust_files: dict[str, Path] = {}
    sample_dirs = sorted(CAPTURE.glob("sample_*/"))
    for sample_dir in sample_dirs:
        sample = sample_dir.name
        raw_path = sample_dir / "raw.png"
        row = {"sample": sample, "input": str(raw_path), "reference_roi": str(sample_dir / "roi_128.png")}
        try:
            roi_bytes = chain.process_bytes(lossless_bmp_transport(raw_path))
            raw_out = raw_dir / f"{sample}.png"
            raw_out.write_bytes(roi_bytes)
            with Image.open(io.BytesIO(roi_bytes)) as image:
                normalized = image.convert("L").resize((128, 128), Image.Resampling.LANCZOS)
                normalized_path = normalized_dir / f"{sample}.png"
                normalized.save(normalized_path, format="PNG")
            robust_files[sample] = normalized_path
            row.update({"status": "ok", "robust_raw": str(raw_out), "robust_roi_128": str(normalized_path)})
        except Exception as exc:
            row.update({"status": "failure", "failure": f"{type(exc).__name__}: {exc}"})
        rows.append(row)
    make_sheet(rows, robust_files)
    with (OUT / "robust_capture_extraction.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "capture_dir": str(CAPTURE),
        "config": str(config),
        "native_library": str(library),
        "requested_samples": len(rows),
        "successes": len(robust_files),
        "failures": len(rows) - len(robust_files),
        "failure_samples": [row for row in rows if row["status"] != "ok"],
        "input_transport": "Pillow decodes capture PNG and losslessly encodes identical RGB pixels as BMP bytes for the isolated OpenCV DLL.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
