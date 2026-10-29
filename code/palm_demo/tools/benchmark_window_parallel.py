"""Compare sequential and two-worker window localization; not HTTP latency."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI
from window_roi import window_candidates


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    cv2.setNumThreads(2)
    import onnxruntime as ort
    original = ort.SessionOptions
    def options():
        v = original()
        v.add_session_config_entry('session.intra_op.allow_spinning', '0')
        v.add_session_config_entry('session.inter_op.allow_spinning', '0')
        return v
    ort.SessionOptions = options
    serial = PKLNetROI(threads=4, policy='heatmap')
    serial._ensure_loaded()
    local = threading.local()
    barrier = threading.Barrier(2)
    def initialize():
        local.engine = PKLNetROI(threads=2, policy='heatmap')
        local.engine._ensure_loaded()
        barrier.wait(timeout=120)
    class Proxy:
        def extract(self, view):
            return local.engine.extract(view)
    rows = json.loads(args.manifest.read_text())
    result = dict(end_to_end=False, threads=[4, 2], parallel_workers=2, rows=[])
    with ThreadPoolExecutor(max_workers=2, initializer=initialize) as pool:
        # Force both worker initializers/model loads outside timed extraction.
        list(pool.map(lambda _: None, range(2)))
        for index, row in enumerate(rows):
            assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
            image = Image.open(row['original']).convert('RGB')
            outputs, durations = [None, None], [None, None]
            for which in ((0, 1) if index % 2 == 0 else (1, 0)):
                start = time.perf_counter()
                outputs[which] = window_candidates(image, serial) if which == 0 else window_candidates(image, Proxy(), map_jobs=pool.map)
                durations[which] = time.perf_counter()-start
            assert len(outputs[0]) == len(outputs[1])
            delta = max((float(np.max(np.abs(np.asarray(a['quad'])-b['quad']))) for a,b in zip(*outputs)), default=0.)
            valid_equal = all(a['valid']==b['valid'] and a['box']==b['box'] and a['gamma']==b['gamma'] for a,b in zip(*outputs))
            result['rows'].append(dict(sample=row['sample'], seconds=durations, maximum_quad_delta=delta,
                                       valid_equal=valid_equal, windows=len(outputs[0])))
            args.output.write_text(json.dumps(result, indent=2))
            print(index+1, durations, delta, valid_equal, flush=True)
    result['summary'] = dict(median_seconds=np.median([r['seconds'] for r in result['rows']],axis=0).tolist(),
                            maximum_quad_delta=max(r['maximum_quad_delta'] for r in result['rows']),
                            all_valid_equal=all(r['valid_equal'] for r in result['rows']))
    args.output.write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
