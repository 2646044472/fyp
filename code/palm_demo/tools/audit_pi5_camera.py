"""Replay a frozen camera benchmark, diagnose ROI orientation, and test RIA.

Never changes originals, labels, enrollment, or deployed thresholds. Rotation
variants are diagnostics, not a label-selected replacement ROI policy.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP / "vendor/palmprint-recognition-python"))
from pklnet_roi import PKLNetROI, normalize_roi
from palmprint.algorithms.registry import get_algorithm


def evaluate(records, algorithms, output):
    results, scores = [], []
    identities = sorted({r["identity"] for r in records})
    for algorithm_name in algorithms:
        algorithm = get_algorithm(algorithm_name)
        for r in records:
            r["features"] = {k: algorithm.extract(v) for k, v in r["pixels"].items()}
        for subset in ("all", "geometry_pass"):
            selected = [r for r in records if subset == "all" or r["valid"]]
            gallery = {k: [r for r in selected if r["identity"] == k and r["index"] <= 5] for k in identities}
            if not all(gallery.values()):
                continue
            for branch in records[0]["pixels"]:
                for enrollment in (["raw"] if branch == "raw" else ["raw", branch]):
                    trials = []
                    for r in selected:
                        if r["index"] <= 5:
                            continue
                        distances = {k: float(np.median([algorithm.match(r["features"][branch], g["features"][enrollment]) for g in refs])) for k, refs in gallery.items()}
                        own = distances[r["identity"]]
                        other = min(v for k, v in distances.items() if k != r["identity"])
                        trial = dict(algorithm=algorithm_name, subset=subset, probe_branch=branch,
                                     enrollment_branch=enrollment, sample=r["sample"], identity=r["identity"],
                                     index=r["index"], distances=distances, correct=own < other,
                                     own_distance=own, nearest_other_distance=other)
                        trials.append(trial)
                        scores.append(trial)
                    result = dict(algorithm=algorithm_name, subset=subset, probe_branch=branch,
                                  enrollment_branch=enrollment, correct=sum(r["correct"] for r in trials),
                                  probes=len(trials), gallery_sizes={k: len(v) for k, v in gallery.items()})
                    results.append(result)
                    print(json.dumps(result), flush=True)
    (output / "recognition.json").write_text(json.dumps(results, indent=2))
    (output / "scores.json").write_text(json.dumps(scores, indent=2))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("originals", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--experiment", type=Path, help="Also evaluate original PyTorch RIA and PKLNet parity")
    parser.add_argument("--rotations", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((args.benchmark / "extraction_manifest.json").read_text())
    extractor = PKLNetROI(threads=2, policy="legacy")
    extractor._ensure_loaded()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    model_path = APP / "models/local-palmir-ria.onnx"
    model_meta = json.loads(model_path.with_suffix(".json").read_text())
    assert hashlib.sha256(model_path.read_bytes()).hexdigest() == model_meta["onnx_sha256"]
    restorer = ort.InferenceSession(str(model_path), sess_options=options, providers=["CPUExecutionProvider"])
    original_model = None
    if args.experiment:
        import torch
        torch.set_num_threads(2)
        source = args.experiment / "palmir/models.py"
        assert hashlib.sha256(source.read_bytes()).hexdigest() == model_meta["source_sha256"]
        checkpoint_path = args.experiment / "runs/polyu_palm/ria/best.pt"
        assert hashlib.sha256(checkpoint_path.read_bytes()).hexdigest() == model_meta["checkpoint_sha256"]
        spec = importlib.util.spec_from_file_location("ria_definitions", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        original_model = module.build_restorer(checkpoint["model_config"]).eval()
        original_model.load_state_dict(checkpoint["model"], strict=True)
    records, diagnostics, panels = [], [], []
    for entry in manifest:
        path = args.originals / entry["sample"] / "full.jpg"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["original_sha256"]
        image = Image.open(path).convert("RGB")
        replay, quad, detail = extractor.extract(image)
        keypoint_replay_error = float(np.max(np.abs(np.asarray(detail["pklnet_keypoints"])-entry["pklnet_keypoints"])))
        # Compare restoration on the exact Pi crop. Recomputing on another
        # host/OpenCV build can change interpolation and a borderline rank.
        frozen = args.benchmark / "rois" / entry["sample"] / "roi_raw_128.png"
        raw = np.asarray(Image.open(frozen).convert("L"))
        replay_pixel_max_error = int(np.abs(raw.astype(int)-replay.astype(int)).max())
        quad = np.asarray(entry["roi_quad_full"], dtype=np.float32)
        detail = {key:value for key,value in entry.items() if key.startswith(("pklnet_","roi_","min_keypoint"))}
        tensor = np.repeat(raw[None, None], 3, axis=1).astype(np.float32) / 255
        start = time.perf_counter()
        restored = restorer.run(None, {"image": tensor})[0]
        restoration_ms = (time.perf_counter() - start) * 1000
        tensors = {"ria_onnx": restored}
        parity = None
        if original_model:
            with torch.inference_mode():
                reference = original_model(torch.from_numpy(tensor)).numpy()
            tensors["ria_pytorch"] = reference
            parity = float(np.max(np.abs(reference-restored)))
        pixels = {"raw": normalize_roi(raw)[0]}
        for name, value in tensors.items():
            rgb = np.rint(value[0].transpose(1, 2, 0).clip(0, 1)*255).astype(np.uint8)
            pixels[name] = normalize_roi(np.asarray(Image.fromarray(rgb).convert("L")))[0]
        identity = entry["subject"] + ":" + entry["hand"]
        folder = args.output / "rois" / identity.replace(":", "_") / str(entry["sample_index"])
        folder.mkdir(parents=True)
        Image.fromarray(raw).save(folder / "raw.png")
        for name, value in tensors.items():
            Image.fromarray(np.rint(value[0].transpose(1, 2, 0).clip(0, 1)*255).astype(np.uint8)).save(folder / (name+".png"))
        records.append(dict(identity=identity, sample=entry["sample"], index=int(entry["sample_index"]),
                            valid=detail["roi_geometry_valid"], pixels=pixels))
        row = dict(sample=entry["sample"], identity=identity, index=entry["sample_index"],
                   raw_std=float(raw.std()), raw_laplacian_variance=float(cv2.Laplacian(raw,cv2.CV_64F).var()),
                   restoration_ms=restoration_ms, onnx_pytorch_max_error=parity, native=detail,
                   keypoint_replay_max_error=keypoint_replay_error, replay_pixel_max_error=replay_pixel_max_error,
                   frozen_roi_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest())
        variants = [("native", image, raw, quad, detail)]
        if args.rotations:
            for name, variant in (("rotate180", image.transpose(Image.Transpose.ROTATE_180)),
                                  ("swap_red_blue_diagnostic", Image.fromarray(np.asarray(image)[:, :, ::-1]))):
                crop, corners, diagnostic = extractor.extract(variant)
                row[name] = diagnostic
                variants.append((name, variant, crop, corners, diagnostic))
        panel = Image.new("RGB", (400*len(variants)+400, 360), "white")
        draw = ImageDraw.Draw(panel)
        for col, (name, variant, crop, corners, diagnostic) in enumerate(variants):
            overlay = variant.copy()
            od = ImageDraw.Draw(overlay)
            points = [tuple(map(float, p)) for p in corners]
            od.line(points+[points[0]], fill="lime", width=8)
            for x,y in np.asarray(diagnostic["pklnet_keypoints"]).reshape(-1,2):
                od.ellipse((x-8,y-8,x+8,y+8),fill="red")
            overlay.thumbnail((380,214))
            panel.paste(overlay,(col*400+8,30))
            panel.paste(Image.fromarray(crop).resize((108,108)),(col*400+8,244))
            draw.text((col*400+8,8),f"{identity} #{entry['sample_index']} {name}",fill="black")
            draw.text((col*400+122,265),f"valid={diagnostic['roi_geometry_valid']}\nspan={diagnostic['pklnet_keypoint_span_ratio']:.3f}",fill="black")
        col=len(variants)
        draw.text((col*400+8,8),"raw / RIA ONNX",fill="black")
        panel.paste(Image.fromarray(raw).resize((180,180)),(col*400+8,65))
        panel.paste(Image.open(folder/'ria_onnx.png').resize((180,180)),(col*400+204,65))
        panels.append(panel)
        diagnostics.append(row)
        print(f"IMAGE {len(records)}/{len(manifest)} {identity} #{entry['sample_index']}",flush=True)
    sheet = Image.new("RGB", (panels[0].width, len(panels)*360),"white")
    for i,panel in enumerate(panels):
        sheet.paste(panel,(0,i*360))
        panel.save(args.output / f"sample-{i+1:02d}.jpg",quality=94)
    sheet.save(args.output / "diagnostic.jpg",quality=92)
    results=evaluate(records,["DoN","FastCC"],args.output)
    summary=dict(host=platform.node(), machine=platform.machine(), model=model_meta, diagnostics=diagnostics,
                 recognition=results, protocol="Frozen 40 images; raw index1-5 gallery, index6-10 probe; median directed probe-to-gallery distance. RIA also tested with RIA enrollment. All images retained; geometry_pass separately conditional. No threshold tuning or deployment.",
                 warning="Same-burst 2-person experiment, not population accuracy. ONNX numerical differences remain explicit. Rotations and color swap are diagnostic only, not chosen by recognition accuracy.")
    (args.output / "summary.json").write_text(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
