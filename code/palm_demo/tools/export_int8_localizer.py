"""Fixed Conv-only QDQ INT8 pilot; calibrate original-split enrollment images.

No query/holdout calibration, identity labels, threshold tuning or retraining.
Repeated development splits are not independent validation after calibration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import CalibrationDataReader, QuantFormat, QuantType, quantize_static
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI, illumination_pixels


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('records', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.source/'pklnet-keypoints-diagnostics.onnx'
    metadata = json.loads(source.with_suffix('.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata['onnx_sha256']
    rows = json.loads(args.records.read_text())
    calibration = [r for r in rows if r['index'] <= 5]
    assert len(rows) == 80 and len(calibration) == 40
    manifest = []
    for row in calibration:
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest() == row['sha256']
        manifest.append(dict(sha256=row['sha256'], index=row['index'], cohort=row['cohort']))
    class Reader(CalibrationDataReader):
        def __init__(self):
            self.jobs = iter((r, gamma) for r in calibration for gamma in (False, True))
        def get_next(self):
            job = next(self.jobs, None)
            if job is None:
                return None
            row, gamma = job
            image = Image.open(row['original']).convert('RGB')
            if gamma:
                image = Image.fromarray(illumination_pixels(np.asarray(image)))
            tensor, *_ = PKLNetROI._prepare(image)
            return {'image': tensor}
    output = args.output/source.name
    quantize_static(str(source), str(output), Reader(), quant_format=QuantFormat.QDQ,
                    op_types_to_quantize=['Conv'], per_channel=True,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8,
                    extra_options={'ActivationSymmetric': False, 'WeightSymmetric': True})
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    session = ort.InferenceSession(str(output), sess_options=options, providers=['CPUExecutionProvider'])
    values = session.run(None, {'image': np.zeros((1, 3, 400, 300), np.float32)})
    assert all(v.shape == (1, 6) and np.isfinite(v).all() for v in values)
    for name in ('net_params_500.pth', 'roiExtractor.py'):
        shutil.copy2(args.source/name, args.output/name)
    metadata.update(source_onnx_sha256=metadata['onnx_sha256'],
        onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        experimental_localizer='conv-qdq-int8-v1', calibration_used=True,
        calibration_images=manifest, original_split_query_calibration=False, reserved_holdout_used=False,
        retrained=False, conversion_runtime=ort.__version__, synthetic_smoke_passed=True)
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    print('exported', output, flush=True)


if __name__ == '__main__':
    main()
