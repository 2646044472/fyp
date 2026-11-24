"""Isolated mixed-precision pilot: FP16 convolutions, all other operators FP32.

No calibration images, retraining or identity-dependent settings. Predictions
may change and must be audited; CPU support and speed are measured separately.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import onnx
from onnx import helper, numpy_helper, TensorProto
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    source = args.source_root/'pklnet-keypoints-diagnostics.onnx'
    metadata = json.loads(source.with_suffix('.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata['onnx_sha256']
    args.output.mkdir(parents=True, exist_ok=False)
    graph = onnx.load(str(source))
    initializers = {t.name: t for t in graph.graph.initializer}
    nodes, added, converted = [], [], {}
    for index, node in enumerate(graph.graph.node):
        if node.op_type != 'Conv':
            nodes.append(node)
            continue
        for slot, name in enumerate(node.input):
            if not name:
                continue
            target = f'conv16_{index}_{slot}'
            if name in initializers:
                if name not in converted:
                    value = numpy_helper.to_array(initializers[name])
                    assert value.dtype == np.float32 and np.isfinite(value).all() and np.max(np.abs(value)) <= 65504
                    added.append(numpy_helper.from_array(value.astype(np.float16), target))
                    converted[name] = target
                target = converted[name]
            else:
                nodes.append(helper.make_node('Cast', [name], [target], to=TensorProto.FLOAT16, name=target+'_cast'))
            node.input[slot] = target
        original = node.output[0]
        node.output[0] = f'conv16_{index}_output'
        nodes.append(node)
        nodes.append(helper.make_node('Cast', [node.output[0]], [original], to=TensorProto.FLOAT,
                                      name=f'conv16_{index}_restore'))
    del graph.graph.node[:]
    graph.graph.node.extend(nodes)
    graph.graph.initializer.extend(added)
    onnx.checker.check_model(graph)
    output = args.output/source.name
    onnx.save(graph, str(output))
    for name in ('net_params_500.pth', 'roiExtractor.py'):
        shutil.copy2(args.source_root/name, args.output/name)
    metadata.update(source_onnx_sha256=metadata['onnx_sha256'],
                    onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                    experimental_localizer='conv-fp16-other-fp32-v1', calibration_used=False,
                    retrained=False, fp16_operators=['Conv'])
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()
