"""Expose existing branch tensors in a verified PKLNet ONNX export.

No weights or predictions are changed. Refuse other graph structures rather
than guessing which internal tensor is the heatmap or FC prediction.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import helper, numpy_helper, TensorProto


def expose(source: Path, output: Path):
    if output.exists() or output.with_suffix('.json').exists():
        raise FileExistsError(f"Output already exists: {output}")
    metadata = json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != metadata['onnx_sha256']:
        raise ValueError('Source ONNX checksum mismatch')
    graph = onnx.load(str(source))
    producers = {o: n for n in graph.graph.node for o in n.output}
    fused = producers['keypoints']
    if fused.op_type != 'Add' or len(fused.input) != 2:
        raise ValueError('Unsupported PKLNet fusion graph')
    expected = ('/model/kcr/Add_6_output_0', '/model/kcr/Add_7_output_0')
    outputs = ('heatmap_keypoints', 'fc_keypoints')
    for incoming, raw, name in zip(fused.input, expected, outputs):
        multiply = producers[incoming]
        if multiply.op_type != 'Mul' or multiply.input[0] != raw:
            raise ValueError('Unrecognized PKLNet branch layout; re-export and verify branch mapping')
        constant = producers[multiply.input[1]]
        if constant.op_type != 'Constant':
            raise ValueError('Expected constant fusion weight')
        value = numpy_helper.to_array(next(a.t for a in constant.attribute if a.name == 'value'))
        if value.size != 1 or not np.isclose(value.item(), .5):
            raise ValueError('Expected verified 50/50 fusion')
        graph.graph.node.append(helper.make_node('Identity', [raw], [name], name='diagnostic_'+name))
        graph.graph.output.append(helper.make_tensor_value_info(name, TensorProto.FLOAT, [1, 6]))
    onnx.checker.check_model(graph)
    output.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(graph, str(output))
    metadata.update(onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                    source_onnx_sha256=digest, diagnostic_schema='pklnet-branches-v1',
                    diagnostic_outputs=list(outputs),
                    output='Original fused keypoints plus unmodified heatmap and FC coordinates')
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(expose(args.source, args.output), indent=2))
