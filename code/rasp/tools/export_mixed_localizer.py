"""Experimental ORT mixed-FP16 conversion without calibration or retraining."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import onnx
import onnxruntime as ort
import numpy as np
from onnxruntime.transformers.float16 import convert_float_to_float16, DEFAULT_OP_BLOCK_LIST
from onnxruntime.transformers.onnx_model import OnnxModel


def deduplicate_identical_casts(graph):
    """ORT converter may emit the same shared FP32 input cast twice."""
    producers, nodes = {}, []
    for node in graph.node:
        previous = producers.get(node.output[0]) if len(node.output) == 1 else None
        if previous is not None:
            if not (node.op_type == previous.op_type == 'Cast' and list(node.input) == list(previous.input)
                    and list(node.output) == list(previous.output)
                    and [a.SerializeToString() for a in node.attribute] == [a.SerializeToString() for a in previous.attribute]):
                raise ValueError('Converter produced conflicting output definitions')
            continue
        for name in node.output:
            producers[name] = node
        for attr in node.attribute:
            if attr.type == onnx.AttributeProto.GRAPH:
                deduplicate_identical_casts(attr.g)
        nodes.append(node)
    del graph.node[:]
    graph.node.extend(nodes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--front-only', action='store_true', help='Keep KCR coordinate/control-flow head in FP32')
    parser.add_argument('--simplify', action='store_true', help='Fold static shape/control-flow with ORT BASIC first')
    args = parser.parse_args()
    source = args.source_root/'pklnet-keypoints-diagnostics.onnx'
    metadata = json.loads(source.with_suffix('.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == metadata['onnx_sha256']
    args.output.mkdir(parents=True, exist_ok=False)
    conversion_source = source
    if args.simplify:
        conversion_source = args.output/'source-basic.onnx'
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        options.optimized_model_filepath = str(conversion_source)
        ort.InferenceSession(str(source), sess_options=options, providers=['CPUExecutionProvider'])
    graph = onnx.load(str(conversion_source))
    blocked = []
    if args.front_only:
        def collect(nodes):
            for node in nodes:
                if not node.name.startswith(('/model/backbone/', '/model/bre_segment/')):
                    blocked.append(node.name)
                for attr in node.attribute:
                    if attr.type == onnx.AttributeProto.GRAPH:
                        collect(attr.g.node)
        collect(graph.graph.node)
    # Keep reductions and sampling geometry in FP32. A minimal AffineGrid
    # reproducer fails in FP16 on the tested ORT CPU build, independently of
    # images, while the same graph succeeds in FP32.
    operator_blocks = DEFAULT_OP_BLOCK_LIST + ['LayerNormalization', 'Softmax', 'AffineGrid', 'GridSample',
                                              'AveragePool', 'MaxPool']
    graph = convert_float_to_float16(graph, keep_io_types=True, node_block_list=blocked,
                                    op_block_list=operator_blocks)
    deduplicate_identical_casts(graph.graph)
    OnnxModel(graph).topological_sort()
    onnx.checker.check_model(graph)
    output = args.output/source.name
    onnx.save(graph, str(output))
    smoke_options = ort.SessionOptions()
    smoke_options.intra_op_num_threads = 4
    smoke = ort.InferenceSession(str(output), sess_options=smoke_options, providers=['CPUExecutionProvider'])
    values = smoke.run(None, {'image': np.zeros((1, 3, 400, 300), np.float32)})
    assert all(v.shape == (1, 6) and np.isfinite(v).all() for v in values)
    for name in ('net_params_500.pth', 'roiExtractor.py'):
        shutil.copy2(args.source_root/name, args.output/name)
    metadata.update(source_onnx_sha256=metadata['onnx_sha256'],
                    onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                    experimental_localizer='ort-front-fp16-v1' if args.front_only else 'ort-mixed-fp16-v1',
                    calibration_used=False, retrained=False, fp32_head=args.front_only,
                    simplified_before_conversion=args.simplify, conversion_runtime=ort.__version__,
                    fp32_operator_block_list=operator_blocks, synthetic_smoke_passed=True)
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()
