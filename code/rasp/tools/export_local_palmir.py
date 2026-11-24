"""Export a completed local RIA checkpoint for CPU-only Pi inference."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=Path)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.experiment / "palmir/models.py"
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    kind = checkpoint.get("kind")
    if kind not in ("restorer", "matcher"):
        raise ValueError("Expected a trained restorer or matcher checkpoint")
    if checkpoint["provenance"]["source_sha256"]["models.py"] != digest(source):
        raise ValueError("Model implementation differs from training provenance")
    spec = importlib.util.spec_from_file_location("local_palmir_models", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model = (module.build_restorer(checkpoint["model_config"]) if kind == "restorer" else
             module.build_matcher(checkpoint["model_config"], num_classes=len(checkpoint["class_to_index"]))).eval()
    model.load_state_dict(checkpoint["model"], strict=True)
    size = checkpoint["config"].get("image_size", 128)
    torch.set_num_threads(2)
    torch.manual_seed(41)
    sample = torch.rand(1, 3, size, size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(model, sample, str(args.output), input_names=["image"],
                    output_names=["restored" if kind == "restorer" else "embedding"], opset_version=17, dynamo=False)
    session = ort.InferenceSession(str(args.output), providers=["CPUExecutionProvider"])
    errors = []
    with torch.no_grad():
        for tensor in [sample, torch.zeros_like(sample), torch.ones_like(sample)]:
            expected = model(tensor).numpy()
            actual = session.run(None, {"image": tensor.numpy()})[0]
            # GroupNorm reductions differ across runtimes. Require less than
            # a quarter of one 8-bit level, and at most one rounded level.
            np.testing.assert_allclose(actual, expected, atol=1 / 1024, rtol=0)
            assert np.max(np.abs(np.rint(actual * 255) - np.rint(expected * 255))) <= 1
            errors.append(float(np.max(np.abs(actual - expected))))
    manifest = dict(label="Local PalmIR-style RIA" if kind == "restorer" else "Local clean PalmMatcher",
                    architecture="CompactRestorer" if kind == "restorer" else "PalmMatcher", kind=kind,
                    training_dataset="PolyU-II palm-class ROI", seed=checkpoint["config"]["seed"],
                    checkpoint_epoch=int(checkpoint["epoch"]) + 1,
                    checkpoint_sha256=digest(args.checkpoint), source_sha256=digest(source),
                    onnx_sha256=digest(args.output), input_size=size,
                    preprocessing="RGB, PIL bilinear resize, float32 NCHW /255",
                    model_config=checkpoint["model_config"],
                    training_matcher_checkpoint_sha256=checkpoint.get("provenance", {}).get("matcher_checkpoint_sha256"),
                    export_max_abs_error=max(errors),
                    runtime_warning="Random/constant parity is insufficient: low-contrast blur can be numerically sensitive. Do not transfer acceptance thresholds across runtimes without calibration.",
                    limitations="Local controlled baseline, not official PalmIR. Live camera domain is unvalidated.")
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
