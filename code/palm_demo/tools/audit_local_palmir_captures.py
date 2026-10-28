"""Audit source overlays and original DoN matcher without selecting good results."""
import csv
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP / "vendor/palmprint-recognition-python"))
from pklnet_roi import PKLNetROI, normalize_roi
from palmprint.algorithms.don import DoNAlgorithm


def run(root):
    output = root / "audit"
    output.mkdir(exist_ok=False)
    extractor = PKLNetROI(threads=2)
    matcher = DoNAlgorithm()
    records, groups = [], {}
    for path in sorted((root / "originals").rglob("full.jpg")):
        meta = json.loads((path.parent / "metadata.json").read_text())
        subject, hand, index = meta["subject"], meta["hand"], int(meta["sample_index"])
        identity = subject + ":" + hand
        image = Image.open(path).convert("RGB")
        raw, quad, diagnostic = extractor.extract(image)
        folder = root / "rois" / f"{subject}_{hand}" / f"{index:02d}"
        saved = np.asarray(Image.open(folder / "original_roi.png").convert("L"))
        if not np.array_equal(raw, saved):
            raise RuntimeError("ROI replay differs from the reported input")
        restored = np.asarray(Image.open(folder / "restored_roi.png").convert("L"))
        raw_normalized, _ = normalize_roi(raw)
        restored_normalized, _ = normalize_roi(restored)
        record = dict(identity=identity, index=index, source=str(path),
                      roi_geometry=diagnostic, std=float(raw.std()),
                      sharpness=float(cv2.Laplacian(raw, cv2.CV_64F).var()),
                      mean=float(raw.mean()), clipped_fraction=float(np.mean((raw<5)|(raw>250))),
                      restored_mean_abs_change=float(np.abs(raw.astype(float)-restored).mean()),
                      raw_feature=matcher.extract(raw_normalized),
                      restored_feature=matcher.extract(restored_normalized))
        records.append(record)
        preview = image.copy()
        draw = ImageDraw.Draw(preview)
        points = [tuple(map(float, p)) for p in quad]
        draw.line(points + points[:1], fill="#00ff65", width=12)
        for x, y in np.asarray(diagnostic["pklnet_keypoints"]).reshape(-1,2):
            draw.ellipse((x-15,y-15,x+15,y+15), fill="red")
        preview.thumbnail((300,225))
        panel = Image.new("RGB", (320,440), "white")
        panel.paste(preview, ((320-preview.width)//2, 30))
        panel.paste(Image.fromarray(raw).resize((144,144)), (8,270))
        panel.paste(Image.fromarray(restored).resize((144,144)), (168,270))
        draw = ImageDraw.Draw(panel)
        draw.text((8,8), f"{identity} #{index}", fill="black")
        draw.text((8,250), "RAW                            RESTORED", fill="black")
        draw.text((8,421), f"std={record['std']:.1f} sharp={record['sharpness']:.1f}", fill="black")
        groups.setdefault(identity, []).append(panel)
        print(f"AUDIT {len(records)}/40 {identity} #{index}", flush=True)
    for identity, panels in groups.items():
        sheet = Image.new("RGB", (1600,880), "#e8eeec")
        for n, panel in enumerate(panels):
            sheet.paste(panel, ((n%5)*320, (n//5)*440))
        sheet.save(output / (identity.replace(":","_") + ".jpg"), quality=94)
    diagnostics = [{k:v for k,v in r.items() if not k.endswith("feature")} for r in records]
    (output / "roi_audit.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    results = {}
    for count in (1,5):
        gallery = {key:[r for r in records if r["identity"]==key and r["index"]<=count] for key in groups}
        scores=[]
        for query in records:
            if query["index"]==1:
                continue
            for key, refs in gallery.items():
                row=dict(probe=query["source"], identity=query["identity"], index=query["index"], target=key,
                         genuine=query["identity"]==key,
                         split="calibration" if query["index"]<=5 else "evaluation")
                for branch in ("raw","restored"):
                    row[branch]=float(np.median([matcher.match(query[branch+"_feature"],r["raw_feature"]) for r in refs]))
                scores.append(row)
        # Smaller DoN distance accepts. Freeze only from raw calibration impostors.
        negatives=[r["raw"] for r in scores if r["split"]=="calibration" and not r["genuine"]]
        operating=float(np.nextafter(min(negatives), -np.inf))
        result=dict(gallery_count=count, threshold=operating, distance_rule="accept iff median DoN distance <= threshold",
                    preprocessing="raw ROI -> optional RIA -> grayscale -> per-image 1/99 percentile normalization -> DoN",
                    warning="same-burst exploratory audit; 5-reference calibration genuine scores reuse enrolled images; threshold uses only other-palm comparisons")
        for branch in ("raw","restored"):
            rr=[r for r in scores if r["split"]=="evaluation"]
            g=[r for r in rr if r["genuine"]];im=[r for r in rr if not r["genuine"]]
            result[branch]=dict(true_accepts=sum(r[branch]<=operating for r in g),n_genuine=len(g),
                                false_accepts=sum(r[branch]<=operating for r in im),n_impostor=len(im),
                                max_genuine_distance=max(r[branch] for r in g),
                                min_impostor_distance=min(r[branch] for r in im))
        results[str(count)]=result
        with (output / f"don_gallery{count}_scores.csv").open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(scores[0]));writer.writeheader();writer.writerows(scores)
        print(json.dumps(result,indent=2),flush=True)
    (output / "don_summary.json").write_text(json.dumps(results,indent=2),encoding="utf-8")


if __name__=="__main__":
    run(Path(sys.argv[1]))
