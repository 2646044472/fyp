"""Measure preprocessing/model/crop costs and CPU threading on saved Pi stills."""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("image", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
extractor = PKLNetROI(backend="torch")
extractor._ensure_loaded()
torch = extractor._torch
image = Image.open(args.image).convert("RGB")
tensor, _, _, _ = extractor._prepare(image)
x = torch.from_numpy(tensor)
rows = []
reference = None
for threads in (1, 2, 4):
    torch.set_num_threads(threads)
    for iteration in range(4):
        start = time.perf_counter()
        prepared, original, rotated, scales = extractor._prepare(image)
        prep_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        with torch.inference_mode():
            result = extractor._model(torch.from_numpy(prepared))[0][0].cpu().numpy()
        model_ms = (time.perf_counter() - start) * 1000
        kp = extractor._unrotate_keypoints(result, original, rotated, scales)
        if reference is None:
            reference = kp.copy()
        start = time.perf_counter()
        quad = extractor._roi_extractor.getROIckp(kp[:2], kp[2:4], extractor._roi_extractor.isAntiClock(kp[:6]))
        roi = extractor._roi_extractor.getROIimg(cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR), quad)
        crop_ms = (time.perf_counter() - start) * 1000
        row = dict(threads=threads, warmup=iteration == 0, preprocess_ms=prep_ms,
            model_ms=model_ms, crop_ms=crop_ms, total_ms=prep_ms + model_ms + crop_ms,
            keypoint_max_abs_delta_px=float(np.max(np.abs(kp - reference))))
        rows.append(row)
        print(json.dumps(row), flush=True)
summary = [{"threads": n, **{key: statistics.median(r[key] for r in rows if r["threads"] == n and not r["warmup"])
    for key in ("preprocess_ms", "model_ms", "crop_ms", "total_ms")}} for n in (1, 2, 4)]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps({"rows": rows, "summary": summary}, indent=2))
print(json.dumps(summary), flush=True)
