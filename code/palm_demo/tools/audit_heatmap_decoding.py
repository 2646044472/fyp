"""Fixed heatmap-decoding controls; no identity-conditioned selection or training."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
from pklnet_roi import PKLNetROI


def decode(logits, method):
    result = []
    for heatmap in logits:
        h, w = heatmap.shape
        yy, xx = np.mgrid[:h, :w]
        if method == "peak":
            py, px = np.unravel_index(heatmap.argmax(), heatmap.shape)
            selected = (abs(xx-px) <= 3) & (abs(yy-py) <= 3)
        else:
            selected = np.ones(heatmap.shape, dtype=bool)
        temperature = 2 if method == "sharpen" else 1
        weight = np.exp((heatmap-heatmap.max()) * temperature) * selected
        weight /= weight.sum()
        # Preserve the upstream DSNT grid and its normalization exactly;
        # only the probability support/temperature changes in these controls.
        x = np.sum(weight * ((2*xx+1)/w-1)) / (1-1/h)
        y = np.sum(weight * ((2*yy+1)/h-1)) / (1-1/w)
        result.append([x, y])
    return np.asarray(result, np.float32)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("benchmark", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/"plan.json").write_text(json.dumps(dict(
        methods=["mean", "sharpen", "peak"],
        definition="mean=existing DSNT; sharpen=logit scale2; peak=7x7 local expectation around argmax. Same rule on every image.",
        evaluation="Geometry against frozen assistant annotations first. Recognition only after geometry audit; all samples retained.",
        training="none", limitation="Repeatedly inspected development set; annotations are not independent human ground truth."
    ), indent=2))
    extractor = PKLNetROI(backend="torch", threads=2, policy="heatmap")
    extractor._ensure_loaded()
    torch = extractor._torch
    capture = {}
    extractor._model.kcr.hm.register_forward_hook(lambda m, i, o: capture.update(hm=o.detach().cpu().numpy()))
    extractor._model.kcr.fc_loc.register_forward_hook(lambda m, i, o: capture.update(theta=o.detach().cpu().numpy()))
    geo = extractor._roi_extractor
    refs = {r["sample"]: r for r in json.loads((args.benchmark/"reference-roi-20261026/records.json").read_text())}
    inputs = json.loads((args.benchmark/"extraction_manifest.json").read_text())
    rows, panels = [], []
    pixels = {method: [] for method in ("mean", "sharpen", "peak")}
    for count, source in enumerate(inputs, 1):
        path = args.benchmark/"originals"/source["sample"]/"full.jpg"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["original_sha256"]
        image = Image.open(path).convert("RGB")
        tensor, osize, rsize, scale = extractor._prepare(image)
        with torch.inference_mode():
            extractor._model(torch.from_numpy(tensor))
        logits = capture["hm"][0]
        theta = capture["theta"].reshape(2, 3)
        np.savez_compressed(args.output/(source["sample"]+"-heatmaps.npz"), logits=logits, theta=theta)
        row = dict(sample=source["sample"], identity=source["subject"]+":"+source["hand"],
                   index=source["sample_index"], fused_valid=source["roi_geometry_valid"], branches={})
        panel = Image.new("RGB", (1200, 350), "white")
        for column, method in enumerate(pixels):
            local = decode(logits, method)
            standardized = (np.c_[local, np.ones(3)] @ theta.T + 1) * [150, 200]
            kp = extractor._unrotate_keypoints(standardized.reshape(-1), osize, rsize, scale)
            quad = np.asarray(geo.getROIckp(kp[:2], kp[2:4], geo.isAntiClock(kp)), np.float32)
            raw = geo.getROIimg(cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR), quad)
            ref = np.asarray(refs[row["sample"]]["quad"], np.float32)
            area = max(0, cv2.intersectConvexConvex(quad, ref)[0])
            iou = area / max(cv2.contourArea(quad)+cv2.contourArea(ref)-area, 1e-9)
            valid = bool((quad >= 0).all() and (quad[:, 0] < image.width).all() and (quad[:, 1] < image.height).all()
                         and np.linalg.norm(kp[:2]-kp[2:4])/min(image.size) >= .1)
            row["branches"][method] = dict(keypoints=kp.tolist(), quad=quad.tolist(), reference_iou=iou, geometry_valid=valid)
            pixels[method].append(raw)
            view = image.copy()
            draw = ImageDraw.Draw(view)
            for polygon, color in ((quad, "lime"), (ref, "cyan")):
                points = [tuple(map(float, pt)) for pt in polygon]
                draw.line(points+points[:1], fill=color, width=7)
            view.thumbnail((390, 220))
            panel.paste(view, (column*400, 25))
            panel.paste(Image.fromarray(raw).resize((96, 96)), (column*400, 250))
            ImageDraw.Draw(panel).text((column*400+2, 3), f"{method} #{count} IoU={iou:.2f} valid={valid}", fill="black")
        panel.save(args.output/(row["sample"]+".jpg"), quality=92)
        rows.append(row)
        print(f"{count}/40 "+str({k:round(v['reference_iou'], 3) for k,v in row['branches'].items()}), flush=True)
    summary = {method: dict(median_iou=float(np.median([r["branches"][method]["reference_iou"] for r in rows])),
                           below_half=sum(r["branches"][method]["reference_iou"] < .5 for r in rows),
                           geometry_pass=sum(r["branches"][method]["geometry_valid"] for r in rows)) for method in pixels}
    (args.output/"records.json").write_text(json.dumps(rows, indent=2))
    (args.output/"geometry.json").write_text(json.dumps(summary, indent=2))
    np.savez_compressed(args.output/"pixels.npz", **{k:np.stack(v) for k,v in pixels.items()})
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
