"""Export the trained PKLNet keypoint output for CPU ONNX Runtime inference."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI, MODEL_GEOMETRY_VERSION

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
extractor = PKLNetROI(backend="torch", policy="legacy")
extractor._ensure_loaded()
torch = extractor._torch

class Keypoints(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, image):
        return self.model(image)[0]

args.output.parent.mkdir(parents=True, exist_ok=True)
torch.onnx.export(Keypoints(extractor._model).eval(), torch.zeros(1, 3, 400, 300),
    str(args.output), input_names=["image"], output_names=["keypoints"],
    opset_version=20, dynamo=False)
import onnx
onnx.checker.check_model(str(args.output))
args.output.with_suffix(".json").write_text(json.dumps({
    "weights_sha256": hashlib.sha256(extractor.weights.read_bytes()).hexdigest(),
    "onnx_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    "roi_geometry": MODEL_GEOMETRY_VERSION, "input_shape": [1, 3, 400, 300],
    "opset": 20, "torch_version": torch.__version__,
    "output": "official fused keypoints; preprocessing and full-resolution crop unchanged",
}, indent=2), encoding="utf-8")
print(args.output)
