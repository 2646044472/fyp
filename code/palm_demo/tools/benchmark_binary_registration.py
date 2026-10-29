"""Isolated binary-feature compute screen. Cached geometry makes this NOT end-to-end.

Export on the original-data host, copy the bundle to Pi, then measure there.
Every query recomputes its descriptors; enrollment descriptors alone are reused.
"""
import argparse
import json
from pathlib import Path
import time

from audit_binary_registration import (cv2, np, load_algorithm, FastCCDemoMatcher,
    AcceleratedFastCC, binary_registration, query_geometry, extract_binary_geometry)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['export', 'measure'])
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--detector', choices=['orb', 'akaze', 'akaze_half'], default='orb')
    parser.add_argument('--scope', choices=['full', 'context'], default='full')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cv2.setNumThreads(4)
    app = Path(__file__).resolve().parents[1]
    algorithm = FastCCDemoMatcher(AcceleratedFastCC(load_algorithm(app/'vendor/palmprint-recognition-python', 'FastCC')))
    algorithm.registration = algorithm.legacy.registration = binary_registration
    try:
        if args.mode == 'export':
            cases = json.loads((args.source/'single-device/runtime-v5/results.json').read_text())
            cases = [c for c in cases if c['case'].endswith('_original')]
            samples = sorted({s for c in cases for ids in c['gallery'].values() for s in ids}
                             | {t['sample'] for c in cases for t in c['trials']})
            for sample in samples:
                with np.load(args.source/'single-device/runtime-v5'/f'{sample}.npz', allow_pickle=False) as z:
                    f = z['feature']
                f[:4] = np.asarray([algorithm.magic], '<i4').view(np.uint8)
                np.savez_compressed(args.output/f'{sample}.npz', **query_geometry(algorithm, f))
            (args.output/'cases.json').write_text(json.dumps(cases))
            print('exported', len(samples), flush=True)
            return
        cases = json.loads((args.source/'cases.json').read_text())
        output = dict(end_to_end=False, excludes=['camera', 'upload', 'queue', 'image decode',
                      'ROI inference including candidate discovery', 'pose-bank extraction', 'HTTP return'],
                      includes=['binary descriptor extraction from pixels', 'all gallery comparisons', 'aggregation'],
                      opencv=cv2.__version__, detector=args.detector, scope=args.scope, passes=[])
        def geometry(sample):
            with np.load(args.source/f'{sample}.npz', allow_pickle=False) as z:
                return dict(z)
        for case in cases:
            gallery = {u: [extract_binary_geometry(**geometry(s), detector=args.detector, scope=args.scope) for s in ids]
                       for u, ids in case['gallery'].items()}
            for repeat in range(2):
                trials = []
                for trial in case['trials']:
                    inputs = geometry(trial['sample'])
                    start = time.perf_counter()
                    probe = extract_binary_geometry(**inputs, detector=args.detector, scope=args.scope)
                    extracted = time.perf_counter()
                    scores = {u: algorithm.score_prepared(probe, enrolled) for u, enrolled in gallery.items()}
                    elapsed = time.perf_counter()-start
                    ranking = sorted(scores.values())
                    correct = scores[trial['identity']] < min(v for u, v in scores.items() if u != trial['identity'])
                    trials.append(dict(sample=trial['sample'], seconds=elapsed,
                                       extraction_seconds=extracted-start, scores=scores, correct=bool(correct),
                                       confident=bool(ranking[0] <= .32 and ranking[1]-ranking[0] >= .08)))
                    print(case['case'], repeat, trial['sample'], round(elapsed, 3), correct, flush=True)
                seconds = [t['seconds'] for t in trials]
                output['passes'].append(dict(case=case['case'], repeat=repeat, trials=trials,
                    correct=sum(t['correct'] for t in trials), p50=float(np.median(seconds)),
                    p95=float(np.percentile(seconds, 95)), maximum=max(seconds),
                    over_2s=sum(s>2 for s in seconds), over_2_5s=sum(s>2.5 for s in seconds)))
                (args.output/'results.json').write_text(json.dumps(output, indent=2))
    finally:
        algorithm.close()


if __name__ == '__main__':
    main()
