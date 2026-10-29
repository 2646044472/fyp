"""Paired Pi localization timings/geometry on every image in explicit manifests.

No recognition accuracy claim. Timings include extraction, exclude JPEG decoding
and model loading, and report first calls separately. No saved query outputs reused.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import cv2
import numpy as np
from PIL import Image
from replay_pi_pipeline import save_json
from pklnet_roi import PKLNetROI


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('manifests', type=Path, nargs='+')
    parser.add_argument('--opencv-candidate', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    import onnxruntime as ort
    default = ort.SessionOptions
    def options():
        value = default()
        value.add_session_config_entry('session.intra_op.allow_spinning', '0')
        value.log_severity_level = 3
        return value
    ort.SessionOptions = options
    cv2.setNumThreads(4)
    engines, loads = [], []
    for index, root in enumerate((args.baseline, args.candidate)):
        start = time.perf_counter()
        engine_class = PKLNetROI
        if index == 1 and args.opencv_candidate:
            from opencv_localizer import OpenCVDNNROI
            engine_class = OpenCVDNNROI
        engine = engine_class(root=root, weights=root/'net_params_500.pth', threads=4)
        engine._ensure_loaded()
        loads.append((time.perf_counter()-start)*1000)
        engines.append(engine)
    result = dict(runtime_version=ort.__version__, opencv_version=cv2.__version__, opencv_candidate=args.opencv_candidate,
                  model_loading_ms=loads, onnx_threads=4,
                  spinning=False, decoding_included=False, recognition_tested=False, rows=[])
    records = [r for path in args.manifests for r in json.loads(path.read_text())]
    assert len(records) == 80
    for i, record in enumerate(records):
        assert hashlib.sha256(Path(record['original']).read_bytes()).hexdigest() == record['sha256']
        image = Image.open(record['original']).convert('RGB')
        outputs = [None, None]
        for index in ((0, 1) if i % 2 == 0 else (1, 0)):
            start = time.perf_counter()
            try:
                raw, quad, detail = engines[index].extract(image)
                outputs[index] = dict(ms=(time.perf_counter()-start)*1000, valid=bool(detail['roi_geometry_valid']),
                                      quad=np.asarray(quad).tolist(), details=detail)
            except Exception as error:
                outputs[index] = dict(ms=(time.perf_counter()-start)*1000, valid=False, error=str(error))
        entry = dict(sample=record['sample'], baseline=outputs[0], candidate=outputs[1])
        if all('quad' in o for o in outputs):
            a, b = [np.asarray(o['quad'], np.float32) for o in outputs]
            intersection = max(0., cv2.intersectConvexConvex(a, b)[0])
            entry['quad_iou'] = intersection/max(1e-8, cv2.contourArea(a)+cv2.contourArea(b)-intersection)
            entry['max_corner_shift_px'] = float(np.max(np.linalg.norm(a-b, axis=1)))
        result['rows'].append(entry)
        save_json(args.output, result)
        print(i+1, outputs[0]['ms'], outputs[1]['ms'], outputs[1]['valid'], entry.get('quad_iou'), flush=True)
    result['summary'] = {name: dict(valid=sum(r[name]['valid'] for r in result['rows']),
        n=len(result['rows']), first_ms=result['rows'][0][name]['ms'],
        median_ms=float(np.median([r[name]['ms'] for r in result['rows']])),
        p95_ms=float(np.percentile([r[name]['ms'] for r in result['rows']], 95)),
        max_ms=max(r[name]['ms'] for r in result['rows'])) for name in ('baseline', 'candidate')}
    save_json(args.output, result)
    print(json.dumps(result['summary']), flush=True)


if __name__ == '__main__':
    main()
