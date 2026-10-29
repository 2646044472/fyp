"""Profile unchanged PKLNet graph on synthetic inputs; no biometric accuracy claim."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np
import onnxruntime as ort
from replay_pi_pipeline import save_json
from pklnet_roi import PKLNET_ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--threads', type=int, choices=(1, 2, 4), default=4)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = args.threads
    opts.inter_op_num_threads = 1
    opts.enable_profiling = True
    opts.profile_file_prefix = str(args.output.with_suffix(''))
    opts.add_session_config_entry('session.intra_op.allow_spinning', '0')
    model = PKLNET_ROOT / 'pklnet-keypoints-diagnostics.onnx'
    session = ort.InferenceSession(str(model), sess_options=opts, providers=['CPUExecutionProvider'])
    value = np.random.default_rng(20261029).random((1, 3, 400, 300), dtype=np.float32)
    timings = []
    for _ in range(5):
        start = time.perf_counter()
        session.run(None, {'image': value})
        timings.append((time.perf_counter()-start)*1000)
    profile = Path(session.end_profiling())
    events = json.loads(profile.read_text())
    operators, nodes = defaultdict(float), defaultdict(float)
    for event in events:
        if event.get('cat') == 'Node' and event['name'].endswith('_kernel_time'):
            operators[event['args']['op_name']] += event['dur']/5000
            nodes[event['name']] += event['dur']/5000
    result = dict(threads=args.threads, synthetic_input=True, instrumented_ms=timings,
                  operators_average_ms=dict(sorted(operators.items(), key=lambda x: -x[1])),
                  top_nodes_average_ms=dict(sorted(nodes.items(), key=lambda x: -x[1])[:30]),
                  raw_profile=str(profile))
    save_json(args.output, result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
