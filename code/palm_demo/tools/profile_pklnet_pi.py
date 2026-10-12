"""Measure real PKLNet extraction on the Pi using saved originals, without capture."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import statistics
import sys
import time

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI, PKLNET_WEIGHTS

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("captures", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
extractor = PKLNetROI()
started = time.perf_counter()
extractor._ensure_loaded()
load_seconds = time.perf_counter() - started
rows = []
for path in sorted(args.captures.glob("*/full.jpg")):
    image = Image.open(path).convert("RGB")
    for label, frame in (("full", image), ("preview_replay", image.resize((480, 360), Image.Resampling.BILINEAR))):
        started = time.perf_counter()
        roi, quad, details = extractor.extract(frame)
        rows.append({"sample": path.parent.name, "input": label, "ms": (time.perf_counter() - started) * 1000, "roi_sha256": hashlib.sha256(roi.tobytes()).hexdigest(), "keypoints": details["pklnet_keypoints"], "valid": details["roi_geometry_valid"], "reason": details["roi_geometry_reason"]})
full = [r["ms"] for r in rows if r["input"] == "full"]
preview = [r["ms"] for r in rows if r["input"] == "preview_replay"]
report = {"load_seconds": load_seconds, "full_median_ms": statistics.median(full), "full_max_ms": max(full), "preview_median_ms": statistics.median(preview), "preview_max_ms": max(preview), "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, "weights_sha256": hashlib.sha256(PKLNET_WEIGHTS.read_bytes()).hexdigest(), "rows": rows}
args.output.write_text(json.dumps(report, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
