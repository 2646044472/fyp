"""Isolate two dominant FP32 convolutions before considering a hybrid backend.

Synthetic operator microbenchmark only: not ROI or recognition latency.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import time

import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['export', 'measure'])
    p.add_argument('source', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--fp16', action='store_true', help='Explicit OpenCV CPU FP16 target, when supported; outputs may differ')
    args = p.parse_args()
    if args.mode == 'export':
        import onnx
        from onnx import helper, TensorProto
        args.output.mkdir(parents=True, exist_ok=False)
        model = onnx.shape_inference.infer_shapes(onnx.load(str(args.source)))
        weights = {v.name:v for v in model.graph.initializer}
        values = {v.name:v for v in model.graph.value_info}
        selected = [n for n in model.graph.node if n.op_type=='Conv' and
            ('aux_head/aux_head.0' in n.name or 'conv3x3/conv3x3.0' in n.name)]
        assert len(selected) == 2
        manifest = []
        for index, original in enumerate(selected):
            shape = [d.dim_value for d in values[original.input[0]].type.tensor_type.shape.dim]
            assert shape == [1,224,100,75]
            node = copy.deepcopy(original)
            node.input[0] = 'image'
            node.output[0] = 'conv'
            graph = helper.make_graph([node,helper.make_node('Relu',['conv'],['output'])],
                'conv-relugate', [helper.make_tensor_value_info('image',TensorProto.FLOAT,shape)],
                [helper.make_tensor_value_info('output',TensorProto.FLOAT,shape)],
                [copy.deepcopy(weights[v]) for v in node.input[1:]])
            mini = helper.make_model(graph, opset_imports=list(model.opset_import))
            mini.ir_version = model.ir_version
            path = args.output/f'conv-{index}.onnx'
            onnx.checker.check_model(mini)
            onnx.save(mini,str(path))
            manifest.append(dict(node=original.name,path=path.name,shape=shape,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2))
        return
    import cv2
    import onnxruntime as ort
    if args.output.exists():
        raise FileExistsError(args.output)
    cv2.setNumThreads(4)
    if args.fp16 and cv2.dnn.DNN_TARGET_CPU_FP16 not in cv2.dnn.getAvailableTargets(cv2.dnn.DNN_BACKEND_OPENCV):
        raise RuntimeError('This OpenCV build does not advertise CPU FP16; refusing a silent FP32 fallback')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.add_session_config_entry('session.intra_op.allow_spinning','0')
    result = dict(synthetic=True,end_to_end=False,opencv=cv2.__version__,ort=ort.__version__,fp16=args.fp16,rows=[])
    for row in json.loads((args.source/'manifest.json').read_text()):
        path = args.source/row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
        baseline = ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])
        candidate = cv2.dnn.readNetFromONNX(str(path))
        candidate.enableWinograd(True)
        if args.fp16:
            candidate.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU_FP16)
        rng = np.random.default_rng(20261029)
        for index in range(3):
            value = rng.normal(size=row['shape']).astype(np.float32) if index else np.zeros(row['shape'],np.float32)
            def reference():
                return baseline.run(None,{'image':value})[0]
            def winograd():
                candidate.setInput(value)
                return candidate.forward()
            expected, actual = reference(),winograd()
            timings = [[],[]]
            for repeat in range(6):
                for which in ((0,1) if repeat%2==0 else (1,0)):
                    begin=time.perf_counter()
                    (reference if which==0 else winograd)()
                    timings[which].append((time.perf_counter()-begin)*1000)
            result['rows'].append(dict(node=row['node'],input=index,maximum_absolute_error=float(np.max(np.abs(expected-actual))),
                median_ms=[float(np.median(t)) for t in timings],timings_ms=timings))
            args.output.write_text(json.dumps(result,indent=2))
            print(result['rows'][-1]['median_ms'],flush=True)


if __name__=='__main__':
    main()
