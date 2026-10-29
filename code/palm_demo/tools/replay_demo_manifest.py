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


def correct_identification(probe):
    result=probe['result']
    return (probe['http_status']==200 and result.get('status')=='MATCH'
            and result.get('user_id')==probe['identity'].replace(':','-')
            and result.get('score') is not None
            and (result.get('second_score') is None or result['score']<result['second_score']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--opencv-threads', type=int)
    parser.add_argument('--onnx-threads', type=int, default=2)
    parser.add_argument('--localizer-root', type=Path, help='Explicit isolated model directory; default remains unchanged')
    parser.add_argument('--restoration', action='store_true')
    parser.add_argument('--demo-matcher', default='FastCCDemo-v6')
    parser.add_argument('--native-registration', type=Path, help='Explicit experimental ARM64 library; disabled by default')
    parser.add_argument('--native-threads', type=int, choices=(1,2,4), default=4)
    args = parser.parse_args()
    if args.opencv_threads is not None:
        cv2.setNumThreads(args.opencv_threads)
    rows = json.loads(args.manifest.read_text())
    groups = {r['identity'] for r in rows}
    assert groups and len(rows) == 10 * len(groups)
    assert all(sorted(r['index'] for r in rows if r['identity'] == g) == list(range(1, 11)) for g in groups)
    def unchanged():
        return all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
    assert unchanged()
    args.output.mkdir(parents=True, exist_ok=False)
    save_json(args.output / 'input-manifest.json', rows)
    engine = (PKLNetROI(threads=args.onnx_threads) if args.localizer_root is None else
              PKLNetROI(root=args.localizer_root, weights=args.localizer_root/'net_params_500.pth', threads=args.onnx_threads))
    start = time.perf_counter()
    result = demo_roundtrip(rows, engine, args.output, args.demo_matcher,
                            native_registration=args.native_registration,native_threads=args.native_threads)
    save_json(args.output / 'demo.json', result)
    correct = sum(correct_identification(p) for p in result['probes'])
    times = lambda path: [r['ms'] for r in result['http_trace'] if r['route'] == path]
    summary = dict(host=platform.node(), platform=platform.platform(), matcher=args.demo_matcher, correct=correct, total=5*len(groups),
                   elapsed_s=time.perf_counter()-start, opencv_threads=cv2.getNumThreads(),
                   onnx_threads=args.onnx_threads, peak_rss_bytes=peak_rss_bytes(),
                   originals_unchanged=unchanged(), payment=result['payment'], live_camera_tested=False)
    summary['localizer_root'] = str(engine.root.resolve())
    summary['localizer_sha256'] = hashlib.sha256((engine.root/'pklnet-keypoints-diagnostics.onnx').read_bytes()).hexdigest()
    summary['acceptance_budget_ms'] = 2500
    summary['native_registration'] = None if args.native_registration is None else dict(
        path=str(args.native_registration),sha256=hashlib.sha256(args.native_registration.read_bytes()).hexdigest(),threads=args.native_threads)
    for name in ('enroll', 'identify'):
        values = times('/api/demo/' + name)
        summary[name] = dict(n=len(values), median_ms=float(np.median(values)), p95_ms=float(np.percentile(values,95)), max_ms=max(values), first_ms=values[0], within_2s=sum(v<=2000 for v in values), within_2_5s=sum(v<=2500 for v in values))
    timed = [p['result']['timing_ms'] for p in result['probes'] if 'timing_ms' in p['result']]
    summary['timed_probes'] = len(timed)
    summary['failures'] = [p for p in result['probes'] if not correct_identification(p)]
    summary['stages_median_ms'] = {k:float(np.median([p[k] for p in timed])) for k in timed[0]} if timed else {}
    identify_trace = [r for r in result['http_trace'] if r['route'] == '/api/demo/identify']
    summary['correct_within_2s'] = sum(correct_identification(p) and t['ms']<=2000 for p,t in zip(result['probes'],identify_trace))
    summary['correct_within_2_5s'] = sum(correct_identification(p) and t['ms']<=2500 for p,t in zip(result['probes'],identify_trace))
    summary['over_2s'] = [dict(sample=p['sample'],identity=p['identity'],ms=t['ms'],
                              route=p['result'].get('recognition_route'),http_status=p['http_status'])
                         for p,t in zip(result['probes'],identify_trace) if t['ms']>2000]
    from collections import Counter
    summary['recognition_routes'] = dict(Counter(p['result'].get('recognition_route','unspecified') for p in result['probes']))
    save_json(args.output / 'summary.json', summary)
    if args.restoration:
        summary['restoration'] = restoration_roundtrip(rows, args.output)
        save_json(args.output / 'summary.json', summary)
    print(json.dumps(summary), flush=True)
    assert correct == 5*len(groups) and len(result['enrollments']) == len(groups)
    assert all(r['http_status'] == 200 for r in result['enrollments'])
    assert summary['originals_unchanged'] and result['payment']['transactions'] == len(groups)


if __name__ == '__main__':
    main()
