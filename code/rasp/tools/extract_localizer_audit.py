"""Rebuild all 80 development templates for unchanged indexed-matcher split audits.

Model/backend is explicit. No holdout data, label-selected candidates, or query
answer caches. The resulting audit measures regression, not independent accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from biometric import load_algorithm
from pklnet_roi import PKLNetROI, normalize_roi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_audit', type=Path)
    parser.add_argument('model_root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--opencv', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    target = args.output/'single-device/runtime-v5'
    target.mkdir(parents=True)
    (args.output/'stability').mkdir()
    shutil.copy2(args.source_audit/'stability/records.json', args.output/'stability/records.json')
    shutil.copy2(args.source_audit/'single-device/runtime-v5/results.json', target/'results.json')
    rows = json.loads((args.output/'stability/records.json').read_text())
    assert len(rows) == 80
    engine_class = PKLNetROI
    if args.opencv:
        from opencv_localizer import OpenCVDNNROI
        import union_matcher
        engine_class = OpenCVDNNROI
        union_matcher.PKLNetROI = OpenCVDNNROI  # Isolated process: use same backend for all windows.
    cv2.setNumThreads(4)
    engine = engine_class(root=args.model_root, weights=args.model_root/'net_params_500.pth', threads=4)
    engine._ensure_loaded()
    algorithm = load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python',
                               'FastCCStagedIndex-v10-experimental')
    results = []
    for row in rows:
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
        start = time.perf_counter()
        entry = dict(sample=row['sample'])
        try:
            image = Image.open(row['original']).convert('RGB')
            raw, quad, details = engine.extract(image)
            if not details['roi_geometry_valid']:
                raise ValueError('Invalid ROI geometry: '+str(details['roi_geometry_reason']))
            hypotheses = algorithm.complete_hypotheses(image, details['pklnet_roi_candidates'], engine)
            feature = algorithm.extract_with_hypotheses(image, quad, normalize_roi(raw)[0], hypotheses)
            np.savez_compressed(target/(row['sample']+'.npz'), feature=feature)
            entry.update(ok=True, quad=np.asarray(quad).tolist(), hypotheses=hypotheses,
                         feature_sha256=hashlib.sha256(feature.tobytes()).hexdigest())
        except Exception as error:
            entry.update(ok=False, error=f'{type(error).__name__}: {error}')
        entry['local_extraction_ms'] = (time.perf_counter()-start)*1000
        results.append(entry)
        (args.output/'extraction.json').write_text(json.dumps(results, indent=2))
        print(len(results), row['sample'], entry['ok'], round(entry['local_extraction_ms']), flush=True)
    algorithm.close()
    summary = dict(total=len(results), extracted=sum(r['ok'] for r in results), independent_validation=False,
                   opencv_backend=args.opencv, opencv_version=cv2.__version__,
                   model_sha256=hashlib.sha256((args.model_root/'pklnet-keypoints-diagnostics.onnx').read_bytes()).hexdigest())
    (args.output/'extraction-summary.json').write_text(json.dumps(summary, indent=2))
    assert summary['extracted'] == summary['total'] == 80


if __name__ == '__main__':
    main()
