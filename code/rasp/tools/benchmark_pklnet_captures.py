"""Re-extract saved Pi originals with PKLNet and benchmark the labelled subset.

Originals and old ROIs are never modified. Unlabelled captures get new ROIs but
are not assigned invented identity labels. Scores describe the supplied capture
snapshot, not population or cross-session accuracy.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor" / "palmprint-recognition-python"))
from pklnet_roi import PKLNetROI, PKLNET_WEIGHTS, ROI_GEOMETRY_VERSION, normalize_roi
from palmprint.algorithms.registry import get_algorithm, list_algorithms
from palmprint.core.metrics import compute_dprime, compute_roc_eer


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def extract(source: Path, output: Path, *, backend: str = "onnx", threads: int | None = None) -> list[dict]:
    extractor = PKLNetROI(backend=backend, threads=threads)
    extractor._ensure_loaded()
    rows = []
    runtime = source / "runtime" if (source / "runtime").is_dir() else source
    paths = sorted(set(runtime.rglob("full.jpg")) | set(runtime.rglob("raw.png")))
    for index, path in enumerate(paths, 1):
        relative = path.relative_to(runtime)
        if "calibration_capture" in relative.parts or "roi_replay" in relative.parts or "collection_trash" in relative.parts:
            continue
        metadata_path = path.parent / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
        target = output / "rois" / relative.parent
        target.mkdir(parents=True, exist_ok=True)
        row = {
            "sample": relative.parent.as_posix(), "original": str(path.resolve()),
            "original_sha256": digest(path), "subject": metadata.get("subject"),
            "hand": metadata.get("hand"), "session_id": metadata.get("session_id"),
            "sample_index": metadata.get("sample_index"),
            "captured_at_pi_utc": metadata.get("captured_at_pi_utc", metadata.get("captured_at")),
            "client_time_utc": metadata.get("client_time_utc"),
            "background": metadata.get("background"), "distance_cm": metadata.get("distance_cm"),
            "saved_old_roi": str(path.parent / "roi_128.png") if (path.parent / "roi_128.png").is_file() else None,
        }
        started = time.perf_counter()
        try:
            image = Image.open(path).convert("RGB")
            raw, quad, details = extractor.extract(image)
            row["extract_ms"] = (time.perf_counter() - started) * 1000
            Image.fromarray(raw).save(target / "roi_raw_128.png")
            normalized, quality = normalize_roi(raw)
            Image.fromarray(normalized).save(target / "roi_128.png")
            overlay = image.copy()
            draw = ImageDraw.Draw(overlay)
            points = [tuple(map(float, point)) for point in quad]
            draw.line(points + points[:1], fill=(30, 230, 90), width=max(2, image.width // 300))
            for x, y in np.asarray(details["pklnet_keypoints"]).reshape(-1, 2):
                radius = max(3, image.width // 200)
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 60, 60))
            overlay.thumbnail((820, 616))
            overlay.save(target / "overlay.jpg", quality=92)
            row.update(status="ok" if details["roi_geometry_valid"] else "invalid_geometry", roi=str((target / "roi_128.png").resolve()), **quality, **details)
        except Exception as error:
            row.update(status="failure", error=f"{type(error).__name__}: {error}")
        (target / "result.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
        rows.append(row)
        print(f"ROI {index}/{len(paths)} {row['sample']} {row['status']}", flush=True)
    if not rows:
        raise RuntimeError(f"No source originals found under {runtime}")
    (output / "extraction_manifest.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_csv(output / "extraction_manifest.csv", rows)
    return rows


def benchmark(rows: list[dict], output: Path, algorithms: list[str]) -> list[dict]:
    labelled = [r for r in rows if r.get("roi") and r.get("subject") and r.get("hand") in ("left", "right") and r.get("sample_index")]
    common = [r for r in labelled if r["saved_old_roi"]]
    passed = [r for r in labelled if r["status"] == "ok"]
    summaries, all_pairs, ranks = [], [], []
    cached_branches = {}
    for branch, records, roi_key in (("pklnet_all", labelled, "roi"), ("pklnet_shared", common, "roi"), ("old_saved_shared", common, "saved_old_roi"), ("pklnet_geometry_pass", passed, "roi")):
        labels = [(r["subject"], r["hand"]) for r in records]
        if len(set(labels)) < 2:
            continue
        cache_key = tuple((r["sample"], r[roi_key], labels[i], r["sample_index"], r["status"]) for i, r in enumerate(records))
        if cache_key in cached_branches:
            source_branch = cached_branches[cache_key]
            summaries.extend([{**r, "branch": branch, "timing_reused_from": source_branch} for r in summaries if r["branch"] == source_branch])
            all_pairs.extend([{**r, "branch": branch} for r in all_pairs if r["branch"] == source_branch])
            ranks.extend([{**r, "branch": branch} for r in ranks if r["branch"] == source_branch])
            (output / "benchmark_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
            write_csv(output / "benchmark_summary.csv", summaries)
            print(f"BENCH {branch}: identical images; reused {source_branch}", flush=True)
            continue
        cached_branches[cache_key] = branch
        images = [np.asarray(Image.open(r[roi_key]).convert("L")) for r in records]
        for name in algorithms:
            algorithm = get_algorithm(name)
            features, extraction_ms = [], []
            for image in images:
                started = time.perf_counter()
                features.append(algorithm.extract(image))
                extraction_ms.append((time.perf_counter() - started) * 1000)
            distances = np.zeros((len(records), len(records)))
            same, nonmate, same_person_other_hand, different_person, match_times = [], [], [], [], []
            for i in range(len(records)):
                for j in range(i + 1, len(records)):
                    started = time.perf_counter()
                    value = float(algorithm.match(features[i], features[j]))
                    match_times.append((time.perf_counter() - started) * 1000)
                    distances[i, j] = value
                    # Preserve matcher direction for gallery-to-probe trials.
                    distances[j, i] = float(algorithm.match(features[j], features[i]))
                    pair_type = "same_hand" if labels[i] == labels[j] else "different_hand"
                    pair_relation = "same_hand" if labels[i] == labels[j] else "same_person_other_hand" if labels[i][0] == labels[j][0] else "different_person"
                    (same if pair_type == "same_hand" else nonmate).append(value)
                    if pair_relation == "same_person_other_hand":
                        same_person_other_hand.append(value)
                    elif pair_relation == "different_person":
                        different_person.append(value)
                    all_pairs.append({"branch": branch, "algorithm": name, "first": records[i]["sample"], "second": records[j]["sample"], "pair_type": pair_type, "pair_relation": pair_relation, "distance": value})
            same, nonmate = np.asarray(same), np.asarray(nonmate)
            _, _, eer = compute_roc_eer(same, nonmate)
            gallery = {label: [i for i, r in enumerate(records) if labels[i] == label and int(r["sample_index"]) <= 5] for label in set(labels)}
            trials = []
            for i, record in enumerate(records):
                if int(record["sample_index"]) <= 5 or not all(gallery.values()):
                    continue
                scores = {label: float(np.median(distances[i, members])) for label, members in gallery.items()}
                own = scores[labels[i]]
                other, other_label = min((value, label) for label, value in scores.items() if label != labels[i])
                trial = {"branch": branch, "algorithm": name, "sample": record["sample"], "subject": record["subject"], "hand": record["hand"], "sample_index": record["sample_index"], "same_hand_distance": own, "opposite_hand_distance": other, "nearest_other_subject": other_label[0], "nearest_other_hand": other_label[1], "margin": other - own, "correct_rank1": own < other}
                trials.append(trial)
                ranks.append(trial)
            summary = {
                "branch": branch, "algorithm": name, "images": len(records), "classes": len(set(labels)),
                "pklnet_geometry_pass_images": sum(r["status"] == "ok" for r in records),
                "same_hand_pairs": len(same), "opposite_hand_pairs": len(nonmate),
                "nonmate_pairs": len(nonmate), "same_person_other_hand_pairs": len(same_person_other_hand), "different_person_pairs": len(different_person),
                "same_person_other_hand_eer_pct": compute_roc_eer(same, np.asarray(same_person_other_hand))[2] if same_person_other_hand else None,
                "different_person_eer_pct": compute_roc_eer(same, np.asarray(different_person))[2] if different_person else None,
                "boundary_gap": float(nonmate.min() - same.max()), "max_same_hand_distance": float(same.max()), "min_nonmate_distance": float(nonmate.min()),
                "exploratory_pair_eer_pct": eer, "d_prime": compute_dprime(same, nonmate),
                "same_hand_median": float(np.median(same)), "opposite_hand_median": float(np.median(nonmate)),
                "feature_extract_ms_mean_host": float(np.mean(extraction_ms)), "match_ms_mean_host": float(np.mean(match_times)),
                "gallery_sizes": {"/".join(label): len(members) for label, members in gallery.items()},
                "rank1_correct": sum(r["correct_rank1"] for r in trials), "rank1_probes": len(trials),
                "probe_same_hand_median": float(np.median([r["same_hand_distance"] for r in trials])),
                "probe_opposite_hand_median": float(np.median([r["opposite_hand_distance"] for r in trials])),
            }
            threshold = {"DoN": 0.15, "FastCC": 0.28}.get(name)
            if threshold is not None:
                summary.update(reference_threshold=threshold, same_hand_accepts=sum(r["same_hand_distance"] <= threshold for r in trials), opposite_hand_accepts=sum(r["opposite_hand_distance"] <= threshold for r in trials))
            summaries.append(summary)
            print(f"BENCH {branch} {name} EER={eer:.2f}% rank={summary['rank1_correct']}/{len(trials)}", flush=True)
            (output / "benchmark_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
            write_csv(output / "benchmark_summary.csv", summaries)
    write_csv(output / "pair_scores.csv", all_pairs)
    write_csv(output / "gallery_probe_scores.csv", ranks)
    return summaries


def contact_sheet(rows: list[dict], output: Path) -> None:
    labelled = sorted((r for r in rows if r.get("hand") in ("left", "right")), key=lambda r: (str(r.get("subject") or ""), r["hand"], int(r.get("sample_index") or 0), r["sample"]))
    if not labelled:
        return
    sheet = Image.new("RGB", (5 * 350, ((len(labelled) + 4) // 5) * 230), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    for index, record in enumerate(labelled):
        x, y = index % 5 * 350, index // 5 * 230
        old = record.get("saved_old_roi")
        overlay = Path(record["roi"]).with_name("overlay.jpg") if record.get("roi") else None
        source = old or (str(overlay) if overlay and overlay.is_file() else record.get("original"))
        for offset, path in ((8, source), (180, record.get("roi"))):
            if path:
                tile = Image.open(path).convert("RGB")
                tile.thumbnail((160, 160))
                sheet.paste(tile, (x + offset + (160 - tile.width) // 2, y + 36 + (160 - tile.height) // 2))
        draw.text((x + 8, y + 7), f"{record.get('subject') or '?'} {record['hand']} #{record.get('sample_index')} ({record['status']})", fill="black" if record["status"] == "ok" else "red")
        draw.text((x + 8, y + 201), "Old saved ROI" if old else "Source + ROI outline", fill="black")
        draw.text((x + 180, y + 201), "PKLNet ROI", fill="black")
    sheet.save(output / "roi_comparison.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--algorithms", nargs="+", default=list_algorithms())
    parser.add_argument("--reuse-extraction", action="store_true")
    parser.add_argument("--roi-backend", choices=("auto", "torch", "onnx"), default="onnx")
    parser.add_argument("--roi-threads", type=int)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = json.loads((args.output / "extraction_manifest.json").read_text()) if args.reuse_extraction else extract(args.source.resolve(), args.output.resolve(), backend=args.roi_backend, threads=args.roi_threads)
    contact_sheet(rows, args.output)
    summaries = benchmark(rows, args.output, args.algorithms)
    subjects = sorted({r["subject"] for r in rows if r.get("subject")})
    palms = {(r["subject"], r["hand"]) for r in rows if r.get("subject") and r.get("hand") in ("left", "right")}
    report = {
        "roi_geometry": ROI_GEOMETRY_VERSION, "weights_sha256": digest(PKLNET_WEIGHTS),
        "platform": platform.platform(), "timing_host": platform.node(), "timing_machine": platform.machine(), "original_count": len(rows),
        "roi_success_count": sum(r["status"] == "ok" for r in rows),
        "participant_count": len(subjects), "participant_labels": subjects, "palm_class_count": len(palms),
        "excluded_from_identity_benchmark": [r["sample"] for r in rows if not r.get("subject") or r.get("hand") not in ("left", "right") or not r.get("sample_index")],
        "failures": [r for r in rows if r["status"] != "ok"], "benchmarks": summaries,
        "protocol": "Explicit subject+hand labels only; first five sample indices per hand form the gallery, indices 6-10 are probes. Median score over each gallery. All unordered pairs use the vendor's fixed 0.001 EER sweep. Nonmate pairs include another hand of the same participant and all hands of other participants; pair_relation separates those groups. Legacy opposite_hand score columns denote all nonmates. Identical branch inputs reuse scores and timing measurements; distinct subsets are measured separately. Missing old ROIs are not imputed.",
        "limits": f"{len(subjects)} labelled participants and {len(palms)} palms in this snapshot, with correlated images from short capture groups. EER and rank are exploratory descriptors, not population accuracy or cross-session performance. Timings apply only to the reported execution host. No matcher threshold is tuned or deployed from this benchmark. Unfiltered branches retain all transformed ROIs including geometry failures to show complete scores; geometry_pass is conditional on an engineering span/bounds guard and must be read with extraction failure counts.",
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
