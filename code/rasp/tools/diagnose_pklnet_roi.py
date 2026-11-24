"""Inspect PKLNet predictions before coordinate mapping on difficult Pi stills."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pklnet_roi import PKLNetROI


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--samples", nargs="+", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    extractor = PKLNetROI(backend="torch", policy="legacy")
    extractor._ensure_loaded()
    onnx_extractor = PKLNetROI(backend="onnx", threads=2, policy="legacy")
    onnx_extractor._ensure_loaded()
    torch = extractor._torch
    captured = {}
    def capture(name, item):
        captured[name] = item.detach()
    extractor._model.bre_segment.register_forward_hook(lambda module, inputs, result: capture("bre_logits", result[1]))
    extractor._model.kcr.fc_loc.register_forward_hook(lambda module, inputs, result: capture("theta", result))
    extractor._model.kcr.hm.register_forward_hook(lambda module, inputs, result: capture("hm", result))
    extractor._model.kcr.kp_head.register_forward_hook(lambda module, inputs, result: capture("fc", result))
    dsntnn = sys.modules["lib.models.nets.dsntnn"]
    rows = []
    sheet = Image.new("RGB", (3 * 350, len(args.samples) * 460), "#eeeeee")
    draw = ImageDraw.Draw(sheet)
    for row_index, name in enumerate(args.samples):
        folder = args.captures / name
        original = Image.open(folder / "full.jpg").convert("RGB")
        metadata = json.loads((folder / "metadata.json").read_text())
        for column, (variant, image) in enumerate((("canonical", original), ("rotate180_diagnostic", original.transpose(Image.Transpose.ROTATE_180)), ("grayscale_diagnostic", original.convert("L").convert("RGB")))):
            tensor, original_size, rotated_size, scales = extractor._prepare(image)
            with torch.inference_mode():
                outputs = extractor._model(torch.from_numpy(tensor))
            keypoints = outputs[0][0].detach().cpu().numpy()
            native = extractor._unrotate_keypoints(keypoints, original_size, rotated_size, scales)
            p1, p2 = keypoints[:2], keypoints[2:4]
            corners = extractor._roi_extractor.getROIckp(p1, p2, extractor._roi_extractor.isAntiClock(keypoints[:6]))
            native_corners = extractor._roi_extractor.getROIckp(native[:2], native[2:4], extractor._roi_extractor.isAntiClock(native[:6]))
            probability = torch.softmax(captured["bre_logits"][0], dim=0).cpu().numpy()
            theta = captured["theta"].reshape(1, 2, 3)
            hm = dsntnn.flat_softmax(captured["hm"])
            hm_coords = dsntnn.dsnt(hm)
            hm_coords[:, :, 0] /= 1 - 1 / hm.size(2)
            hm_coords[:, :, 1] /= 1 - 1 / hm.size(3)
            hm_kp = extractor._model.kcr.kp_coord(hm_coords.reshape(1, -1), theta, 300, 400)[0].cpu().numpy()
            fc_kp = extractor._model.kcr.kp_coord(captured["fc"], theta, 300, 400)[0].cpu().numpy()
            hm_axis = hm_kp[2:4] - hm_kp[:2]
            fc_axis = fc_kp[2:4] - fc_kp[:2]
            branch_axis_cosine = float(np.dot(hm_axis, fc_axis) / max(np.linalg.norm(hm_axis)*np.linalg.norm(fc_axis), 1e-9))
            onnx_kp = onnx_extractor._session.run(["keypoints"], {"image": tensor})[0][0]
            canvas = tensor[0].transpose(1, 2, 0) * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
            canvas = np.clip(np.rint(canvas * 255), 0, 255).astype(np.uint8)
            preview = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            pd = ImageDraw.Draw(preview)
            points = [tuple(map(float, point)) for point in corners]
            pd.line(points + points[:1], fill=(0, 255, 0), width=2)
            for i, (x, y) in enumerate(keypoints.reshape(-1, 2), 1):
                pd.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 40, 40))
                pd.text((x + 5, y), str(i), fill="white")
            preview.save(args.output / f"{name}-{variant}-standardized.png")
            Image.fromarray(((probability.argmax(axis=0) == 1) * 255).astype(np.uint8)).save(args.output / f"{name}-{variant}-foreground.png")
            if variant == "canonical":
                branches = Image.new("RGB", (960, 450), "#eeeeee")
                bd = ImageDraw.Draw(branches)
                for c, (label, branch) in enumerate((("Fused (official 50/50)", keypoints), ("Heatmap branch", hm_kp), ("FC branch", fc_kp))):
                    tile = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
                    td = ImageDraw.Draw(tile)
                    polygon = extractor._roi_extractor.getROIckp(branch[:2], branch[2:4], extractor._roi_extractor.isAntiClock(branch[:6]))
                    pts = [tuple(map(float, p)) for p in polygon]
                    td.line(pts + pts[:1], fill=(0, 255, 0), width=2)
                    for i, (kx, ky) in enumerate(branch.reshape(-1, 2), 1):
                        td.ellipse((kx - 3, ky - 3, kx + 3, ky + 3), fill=(255, 40, 40))
                        td.text((kx + 5, ky), str(i), fill="white")
                    branches.paste(tile, (c * 320 + 10, 27))
                    bd.text((c * 320 + 10, 6), label, fill="black")
                    bd.text((c * 320 + 10, 430), f"gap {np.linalg.norm(branch[:2] - branch[2:4]):.1f}px", fill="black")
                branches.save(args.output / f"{name}-branch-comparison.png")
            native_overlay = image.copy()
            od = ImageDraw.Draw(native_overlay)
            native_points = [tuple(map(float, point)) for point in native_corners]
            od.line(native_points + native_points[:1], fill=(0, 255, 0), width=12)
            native_overlay.thumbnail((820, 616))
            native_overlay.save(args.output / f"{name}-{variant}-overlay.jpg")
            x, y = column * 350 + 25, row_index * 460
            draw.text((x, y + 5), f"{metadata['hand']} #{metadata['sample_index']} {variant}", fill="black")
            sheet.paste(preview, (x, y + 35))
            span = float(np.linalg.norm(p2 - p1))
            native_span = float(np.linalg.norm(native[2:4] - native[:2]))
            draw.text((x, y + 438), f"gap: {span:.1f}px / native {native_span:.1f}px", fill="black")
            rows.append({
                "sample": name, "hand": metadata["hand"], "sample_index": metadata["sample_index"],
                "variant": variant, "keypoints_standardized": keypoints.tolist(), "keypoints_native": native.tolist(),
                "standardized_keypoint_gap_px": span, "native_keypoint_gap_px": native_span,
                "native_span_ratio": native_span / min(image.size),
                "segmentation_foreground_fraction": float((probability.argmax(axis=0) == 1).mean()),
                "stn_affine_theta": theta[0].cpu().numpy().tolist(),
                "stn_affine_singular_values": np.linalg.svd(theta[0, :, :2].cpu().numpy(), compute_uv=False).tolist(),
                "heatmap_branch_keypoints": hm_kp.tolist(), "fc_branch_keypoints": fc_kp.tolist(),
                "heatmap_branch_gap_px": float(np.linalg.norm(hm_kp[:2] - hm_kp[2:4])),
                "fc_branch_gap_px": float(np.linalg.norm(fc_kp[:2] - fc_kp[2:4])),
                "branch_axis_cosine": branch_axis_cosine,
                "fused_reconstruction_max_error": float(np.max(np.abs(keypoints - .5*(hm_kp+fc_kp)))),
                "onnx_torch_keypoint_max_error_standardized_px": float(np.max(np.abs(onnx_kp-keypoints))),
                "exposure_ms": metadata.get("exposure_ms"), "analogue_gain": metadata.get("analogue_gain"),
                "focus_fom": metadata.get("camera_metadata", {}).get("FocusFoM"),
            })
    sheet.save(args.output / "standardized_keypoint_comparison.png")
    (args.output / "diagnosis.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps([{k: r[k] for k in ("hand", "sample_index", "variant", "standardized_keypoint_gap_px", "native_span_ratio", "exposure_ms", "analogue_gain")} for r in rows], indent=2))


if __name__ == "__main__":
    main()
