"""Frozen 200x150 PKLNet front-end pilot; original weights and 400x300 keypoint head.

Changes predictions. Export into a fresh isolated directory, never production.
No training, calibration, sample identifiers, or recognition thresholds are used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI, MODEL_GEOMETRY_VERSION


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    extractor = PKLNetROI(backend='torch', policy='legacy', threads=4)
    extractor._ensure_loaded()
    torch = extractor._torch
    from torch.nn import functional as F
    from lib.models.nets import dsntnn

    class LowResolution(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self.model = model

        def forward(self, image):
            reduced = F.interpolate(image, size=(200, 150), mode='bilinear', align_corners=False)
            features = self.model.backbone(reduced)
            size = features[0].shape[2:]
            combined = torch.cat([features[0], *[
                F.interpolate(f, size=size, mode='bilinear', align_corners=True)
                for f in features[1:]]], dim=1)
            _, segmentation = self.model.bre_segment(combined)
            segmentation = F.interpolate(segmentation, size=(400, 300), mode='bilinear', align_corners=True)
            # Original KCR geometry and equations, exposing each diagnostic output.
            head = self.model.kcr
            transformed, theta = head.stn(head.bre_expend(segmentation))
            heatmaps = dsntnn.flat_softmax(head.hm(head.PPU(transformed)))
            coords = dsntnn.dsnt(heatmaps)
            coords[:, :, 0] = coords[:, :, 0] / (1 - 1. / heatmaps.size(2))
            coords[:, :, 1] = coords[:, :, 1] / (1 - 1. / heatmaps.size(3))
            heatmap = head.kp_coord(coords.reshape(coords.size(0), -1), theta, 300, 400)
            fc = head.kp_coord(head.kp_head(transformed), theta, 300, 400)
            return .5 * heatmap + .5 * fc, heatmap, fc

    model = LowResolution(extractor._model).eval()
    example = torch.zeros(1, 3, 400, 300)
    output = args.output / 'pklnet-keypoints-diagnostics.onnx'
    with torch.inference_mode():
        values = model(example)
        assert all(v.shape == (1, 6) and torch.isfinite(v).all() for v in values)
        torch.onnx.export(model, example, str(output), input_names=['image'],
                          output_names=['keypoints', 'heatmap_keypoints', 'fc_keypoints'],
                          opset_version=20, dynamo=False)
    import onnx
    onnx.checker.check_model(str(output))
    import numpy as np
    import onnxruntime as ort
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    session = ort.InferenceSession(str(output), sess_options=options, providers=['CPUExecutionProvider'])
    errors = []
    torch.manual_seed(20261029)
    for sample in (example, torch.rand(1, 3, 400, 300)):
        with torch.inference_mode():
            expected = [v.numpy() for v in model(sample)]
        actual = session.run(None, {'image': sample.numpy()})
        errors.append(max(float(np.max(np.abs(a-b))) for a, b in zip(actual, expected)))
        assert all(np.allclose(a, b, rtol=1e-4, atol=.01) for a, b in zip(actual, expected))
    shutil.copy2(extractor.weights, args.output / extractor.weights.name)
    shutil.copy2(extractor.root / 'roiExtractor.py', args.output / 'roiExtractor.py')
    metadata = dict(weights_sha256=hashlib.sha256(extractor.weights.read_bytes()).hexdigest(),
        onnx_sha256=hashlib.sha256(output.read_bytes()).hexdigest(), roi_geometry=MODEL_GEOMETRY_VERSION,
        input_shape=[1, 3, 400, 300], diagnostic_schema='pklnet-branches-v1',
        experimental_localizer='fixed-200x150-backbone-segmentation-v1',
        pretrained_weights_unchanged=True, training_performed=False,
        torch_version=torch.__version__, opset=20, export_check_max_coordinate_errors=errors)
    output.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__':
    main()
