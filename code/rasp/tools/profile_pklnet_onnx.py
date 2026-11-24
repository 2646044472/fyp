"""Compare FP32 ONNX CPU latency and ROI output against a saved PyTorch run."""
import argparse
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI, PKLNET_ROOT

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("manifest", type=Path)
parser.add_argument("model", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
rows = json.loads(args.manifest.read_text())
spec = importlib.util.spec_from_file_location("roiExtractor", PKLNET_ROOT / "roiExtractor.py")
roi_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roi_module)

def session(threads):
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return ort.InferenceSession(str(args.model), sess_options=options, providers=["CPUExecutionProvider"])

image = Image.open(rows[0]["original"]).convert("RGB")
tensor, _, _, _ = PKLNetROI._prepare(image)
sweep = []
for threads in (1, 2, 4):
    runtime = session(threads)
    times = []
    for iteration in range(4):
        start = time.perf_counter()
        result = runtime.run(["keypoints"], {"image": tensor})[0]
        elapsed = (time.perf_counter() - start) * 1000
        if iteration:
            times.append(elapsed)
        print(json.dumps({"threads": threads, "warmup": iteration == 0, "model_ms": elapsed}), flush=True)
    sweep.append({"threads": threads, "model_median_ms": statistics.median(times)})
best = min(sweep, key=lambda r: r["model_median_ms"])["threads"]
runtime = session(best)
results = []
for row in rows:
    image = Image.open(row["original"]).convert("RGB")
    start = time.perf_counter()
    tensor, original, rotated, scales = PKLNetROI._prepare(image)
    kp = runtime.run(["keypoints"], {"image": tensor})[0][0]
    kp = PKLNetROI._unrotate_keypoints(kp, original, rotated, scales)
    quad = np.asarray(roi_module.getROIckp(kp[:2], kp[2:4], roi_module.isAntiClock(kp[:6])), dtype=np.float32)
    roi = roi_module.getROIimg(cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR), quad)
    elapsed = (time.perf_counter() - start) * 1000
    old_roi = np.asarray(Image.open(Path(row["roi"]).with_name("roi_raw_128.png")), dtype=np.float32)
    result = {"sample": row["sample"], "ms": elapsed, "keypoints": kp.tolist(),
        "keypoint_max_abs_delta_px": float(np.max(np.abs(kp - np.asarray(row["pklnet_keypoints"])))),
        "quad_max_abs_delta_px": float(np.max(np.abs(quad - np.asarray(row["roi_quad_full"])))),
        "roi_pixel_mae": float(np.abs(roi.astype(np.float32) - old_roi).mean()),
        "roi_pixel_max_delta": float(np.abs(roi.astype(np.float32) - old_roi).max()),
        "geometry_valid": bool(np.linalg.norm(kp[2:4] - kp[:2]) / min(image.size) >= .1
            and (quad >= 0).all() and (quad[:, 0] < image.width).all() and (quad[:, 1] < image.height).all())}
    results.append(result)
    print(json.dumps(result), flush=True)
report = {"platform": sys.platform, "onnxruntime_version": ort.__version__, "thread_sweep": sweep,
    "best_threads": best, "median_ms": statistics.median(r["ms"] for r in results),
    "max_keypoint_delta_px": max(r["keypoint_max_abs_delta_px"] for r in results),
    "max_roi_pixel_mae": max(r["roi_pixel_mae"] for r in results), "rows": results}
args.output.write_text(json.dumps(report, indent=2))
print(json.dumps({k:v for k,v in report.items() if k != "rows"}), flush=True)
