"""Isolated HTTP replay to compare CPU scheduling without changing recognition.

Run each configuration in a fresh process. No production paths, payment calls,
query caches, changed thresholds, or per-sample configuration are supported.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera, http_app, debug_ui, save_json
from replay_demo_manifest import correct_identification, peak_rss_bytes
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration


def select_queries(rows, previous, tails_only):
    expected = {p['sample']: p['result'] for p in previous['probes']}
    selected = [r for r in sorted(rows, key=lambda r: (r['identity'], r['index']))
                if r['index'] > 5]
    if tails_only:
        selected = [r for r in selected
                    if expected[r['sample']].get('recognition_route') == 'exhaustive_fallback']
    return selected, expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('replays', type=Path, nargs='+')
    parser.add_argument('--native-registration', type=Path, required=True)
    parser.add_argument('--native-threads', type=int, choices=(1, 2, 4), default=4)
    parser.add_argument('--opencv-threads', type=int, choices=(1, 2, 4), default=4)
    parser.add_argument('--onnx-threads', type=int, choices=(1, 2, 4), default=4)
    parser.add_argument('--disable-spinning', action='store_true')
    parser.add_argument('--tails-only', action='store_true')
    parser.add_argument('--passes', type=int, choices=(1, 2, 3), default=2)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.disable_spinning:
        # Isolated process only; applies to both main and window sessions.
        import onnxruntime as ort
        original_options = ort.SessionOptions
        def options():
            value = original_options()
            value.add_session_config_entry('session.intra_op.allow_spinning', '0')
            value.add_session_config_entry('session.inter_op.allow_spinning', '0')
            return value
        ort.SessionOptions = options
    cv2.setNumThreads(args.opencv_threads)
    result = dict(configuration={k: str(v) if isinstance(v, Path) else v
                                 for k, v in vars(args).items() if k != 'replays'},
                  live_camera_tested=False, cohorts=[])
    for replay in args.replays:
        summary = json.loads((replay / 'summary.json').read_text())
        if summary.get('live_camera_tested') is not False:
            raise ValueError('Expected an isolated replay directory')
        rows = json.loads((replay / 'input-manifest.json').read_text())
        selected, expected = select_queries(rows, json.loads((replay / 'demo.json').read_text()), args.tails_only)
        assert selected
        assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest() == r['sha256'] for r in rows)
        debug_ui.common.RUNTIME = replay / 'demo_runtime'
        start = time.perf_counter()
        camera = ReplayCamera(False, PKLNetROI(threads=args.onnx_threads))
        app = debug_ui.App(camera, demo_matcher=summary['matcher'])
        enable_native_registration(app.demo_algorithm, args.native_registration, args.native_threads)
        cohort = dict(replay=str(replay), startup_s=time.perf_counter()-start, passes=[])
        result['cohorts'].append(cohort)
        transactions = app.demo.payments.transaction_count()
        with http_app(app) as (request, trace):
            for repeat in range(args.passes):
                trials = []
                for row in selected:
                    camera.select([row])
                    status, response = request('/api/demo/identify', {})
                    elapsed = trace[-1]['ms']
                    response.pop('roi_image', None)
                    reference = expected[row['sample']]
                    trial = dict(sample=row['sample'], ms=elapsed,
                                 correct=correct_identification(dict(http_status=status, result=response, identity=row['identity'])),
                                 reference_equal=all(response.get(k) == reference.get(k) for k in
                                     ('user_id', 'score', 'second_score', 'status', 'recognition_route')),
                                 result=response)
                    trials.append(trial)
                    if response.get('token'):
                        request('/api/demo/cancel', dict(token=response['token']), 200)
                    print(replay.name, repeat, row['sample'], elapsed, trial['reference_equal'], flush=True)
                times = [t['ms'] for t in trials]
                cohort['passes'].append(dict(repeat=repeat, n=len(trials), trials=trials,
                    correct=sum(t['correct'] for t in trials), exact=sum(t['reference_equal'] for t in trials),
                    correct_within_2s=sum(t['correct'] and t['ms'] <= 2000 for t in trials),
                    median_ms=float(np.median(times)), p95_ms=float(np.percentile(times, 95)), max_ms=max(times)))
                save_json(args.output, result)
            cohort['transactions_unchanged'] = app.demo.payments.transaction_count() == transactions
        app.demo_algorithm.close()
        result['peak_rss_bytes'] = peak_rss_bytes()
        save_json(args.output, result)
        assert cohort['transactions_unchanged']
    assert all(p['correct'] == p['n'] == p['exact'] for c in result['cohorts'] for p in c['passes'])


if __name__ == '__main__':
    main()
