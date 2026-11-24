from pathlib import Path
import sys
import pytest

onnx = pytest.importorskip('onnx')
pytest.importorskip('onnxruntime')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from export_mixed_localizer import deduplicate_identical_casts


def test_shared_identical_cast_is_reused():
    nodes = [onnx.helper.make_node('Cast', ['x'], ['y'], name=name, to=onnx.TensorProto.FLOAT)
             for name in ('first', 'second')]
    graph = onnx.helper.make_graph(nodes, 'test', [], [])
    deduplicate_identical_casts(graph)
    assert len(graph.node) == 1
    assert list(graph.node[0].input) == ['x']


def test_conflicting_cast_output_is_not_silently_deduplicated():
    nodes = [onnx.helper.make_node('Cast', ['x'], ['y'], to=dtype)
             for dtype in (onnx.TensorProto.FLOAT, onnx.TensorProto.FLOAT16)]
    graph = onnx.helper.make_graph(nodes, 'test', [], [])
    with pytest.raises(ValueError, match='conflicting'):
        deduplicate_identical_casts(graph)
