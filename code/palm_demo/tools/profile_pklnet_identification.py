"""Time saved full-resolution probes through PKLNet and the demo Gallery path."""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))
sys.path.insert(0, str(APP_ROOT / 'vendor' / 'palmprint-recognition-python'))
from gallery import Gallery
from templates import TemplateStore, safe_user_id
from pklnet_roi import PKLNetROI, ROI_GEOMETRY_VERSION, normalize_roi
from palmprint.algorithms.registry import get_algorithm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path, help='Isolated profiling directory; never use live templates here.')
    parser.add_argument('--algorithm', default='DoN')
    parser.add_argument('--roi-backend', choices=('onnx', 'torch'), default='onnx')
    parser.add_argument('--roi-threads', type=int, default=4)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = [r for r in json.loads(args.manifest.read_text())
               if r.get('roi') and r.get('subject') and r.get('hand') in ('left', 'right') and r.get('sample_index')]
    gallery_records = defaultdict(list)
    probes = []
    for record in records:
        if int(record['sample_index']) <= 5:
            gallery_records[(record['subject'], record['hand'])].append(record)
        else:
            probes.append(record)
    if len(gallery_records) < 2 or not probes:
        raise ValueError('Need at least two labelled palm galleries and saved probes.')
    algorithm = get_algorithm(args.algorithm)
    store = TemplateStore(args.output / 'templates')
    if store.list_users():
        raise ValueError('Profiling directory already contains templates; choose a fresh output directory.')
    user_ids = {}
    started = time.perf_counter()
    for label, group in sorted(gallery_records.items()):
        user = safe_user_id('-'.join(label))
        if user in user_ids.values():
            raise ValueError('Palm labels collide after template ID sanitization.')
        user_ids[label] = user
        features = [algorithm.extract(np.asarray(Image.open(r['roi']).convert('L'))) for r in group]
        store.save(user, np.stack(features), {'algorithm': algorithm.name, 'capture_profile': 'noir-ir',
                                            'roi_geometry': ROI_GEOMETRY_VERSION, 'samples': len(features)})
    gallery_build_ms = (time.perf_counter() - started) * 1000
    gallery = Gallery(store, algorithm, threshold=1.0,
                      required_metadata={'algorithm': algorithm.name, 'roi_geometry': ROI_GEOMETRY_VERSION})
    extractor = PKLNetROI(backend=args.roi_backend, threads=args.roi_threads)

    def process(record):
        timings = {}
        overall = time.perf_counter()
        stage = overall
        with Image.open(record['original']) as source:
            image = source.convert('RGB')
        timings['decode_ms'] = (time.perf_counter() - stage) * 1000
        stage = time.perf_counter()
        extractor._ensure_loaded()
        timings['model_load_ms'] = (time.perf_counter() - stage) * 1000
        stage = time.perf_counter()
        raw, quad, details = extractor.extract(image)
        timings['roi_ms'] = (time.perf_counter() - stage) * 1000
        if not details['roi_geometry_valid']:
            raise ValueError(f"Invalid ROI for {record['sample']}: {details['roi_geometry_reason']}")
        stage = time.perf_counter()
        roi, quality = normalize_roi(raw)
        timings['normalize_ms'] = (time.perf_counter() - stage) * 1000
        stage = time.perf_counter()
        feature = algorithm.extract(roi)
        timings['feature_ms'] = (time.perf_counter() - stage) * 1000
        stage = time.perf_counter()
        result = gallery.identify(feature, 'noir-ir')
        timings['gallery_ms'] = (time.perf_counter() - stage) * 1000
        timings['total_ms'] = (time.perf_counter() - overall) * 1000
        return {'sample': record['sample'], 'subject': record['subject'], 'hand': record['hand'],
                'sample_index': record['sample_index'], 'prediction': result.user_id,
                'correct': result.user_id == user_ids[(record['subject'], record['hand'])],
                'score': result.score, 'second_score': result.second_score, **timings}

    cold = process(probes[0])
    print('COLD', json.dumps(cold), flush=True)
    trials = []
    for record in probes:
        trial = process(record)
        trials.append(trial)
        print('WARM', json.dumps(trial), flush=True)
    stages = {}
    for name in ('decode_ms', 'model_load_ms', 'roi_ms', 'normalize_ms', 'feature_ms', 'gallery_ms', 'total_ms'):
        values = np.asarray([r[name] for r in trials])
        stages[name] = {'median': float(np.median(values)), 'mean': float(values.mean()),
                        'p95': float(np.percentile(values, 95)), 'min': float(values.min()), 'max': float(values.max())}
    report = {'timing_host': platform.node(), 'platform': platform.platform(), 'algorithm': algorithm.name,
              'roi_backend': extractor.backend_used, 'roi_threads': args.roi_threads,
              'gallery_classes': len(gallery_records), 'gallery_templates': sum(map(len, gallery_records.values())),
              'probe_count': len(probes), 'correct_count': sum(r['correct'] for r in trials),
              'capture_included': False, 'network_included': False, 'gallery_files_read_each_trial': True,
              'gallery_build_from_saved_roi_ms': gallery_build_ms, 'cold_start': cold, 'warm_stages': stages,
              'protocol': 'First five saved ROI features per palm form an isolated Gallery. Probes are decoded from original JPEGs and reprocessed with PKLNet, normalization and the selected matcher. Each recognition loads compatible template files and takes the median of each palm gallery. Cold model loading is measured separately from the 20 warm trials. Threshold 1.0 matches the demo ranking protocol and is not an open-set calibration.',
              'trials': trials}
    (args.output / 'results.json').write_text(json.dumps(report, indent=2))
    with (args.output / 'trials.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trials[0]))
        writer.writeheader()
        writer.writerows(trials)
    print('SUMMARY', json.dumps({k: v for k, v in report.items() if k not in ('trials', 'protocol')}), flush=True)


if __name__ == '__main__':
    main()
