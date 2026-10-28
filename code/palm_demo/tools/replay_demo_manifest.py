"""Replay fixed historical cohorts through real demo HTTP handlers on any host."""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import cv2
import numpy as np
from replay_pi_pipeline import demo_roundtrip, restoration_roundtrip, save_json
from pklnet_roi import PKLNetROI


def peak_rss_bytes():
    if platform.system() == 'Windows':
        return None  # resource is Unix-only; do not report an invented measurement.
    import resource
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if platform.system() == 'Darwin' else value * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--opencv-threads', type=int)
    parser.add_argument('--onnx-threads', type=int, default=2)
    parser.add_argument('--restoration', action='store_true')
    args = parser.parse_args()
    if args.opencv_threads is not None:
        cv2.setNumThreads(args.opencv_threads)
    rows = json.loads(args.manifest.read_text())
    groups = {r['identity'] for r in rows}
    assert len(rows) == 40 and len(groups) == 4
    assert all(sorted(r['index'] for r in rows if r['identity'] == g) == list(range(1, 11)) for g in groups)
    def unchanged():
        return all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    assert unchanged()
    args.output.mkdir(parents=True, exist_ok=False)
    save_json(args.output / 'input-manifest.json', rows)
    engine = PKLNetROI(threads=args.onnx_threads)
    start = time.perf_counter()
    result = demo_roundtrip(rows, engine, args.output, 'FastCCDemo-v6')
    save_json(args.output / 'demo.json', result)
    correct = sum(p['http_status'] == 200 and p['result'].get('user_id') == p['identity'].replace(':', '-') for p in result['probes'])
    times = lambda path: [r['ms'] for r in result['http_trace'] if r['route'] == path]
    summary = dict(host=platform.node(), platform=platform.platform(), correct=correct, total=20,
                   elapsed_s=time.perf_counter()-start, opencv_threads=cv2.getNumThreads(),
                   onnx_threads=args.onnx_threads, peak_rss_bytes=peak_rss_bytes(),
                   originals_unchanged=unchanged(), payment=result['payment'], live_camera_tested=False)
    for name in ('enroll', 'identify'):
        values = times('/api/demo/' + name)
        summary[name] = dict(n=len(values), median_ms=float(np.median(values)), p95_ms=float(np.percentile(values,95)), first_ms=values[0])
    summary['stages_median_ms'] = {k:float(np.median([p['result']['timing_ms'][k] for p in result['probes']])) for k in result['probes'][0]['result']['timing_ms']}
    save_json(args.output / 'summary.json', summary)
    if args.restoration:
        summary['restoration'] = restoration_roundtrip(rows, args.output)
        save_json(args.output / 'summary.json', summary)
    print(json.dumps(summary), flush=True)
    assert correct == 20 and len(result['enrollments']) == 4
    assert all(r['http_status'] == 200 for r in result['enrollments'])
    assert summary['originals_unchanged'] and result['payment']['transactions'] == 4


if __name__ == '__main__':
    main()

