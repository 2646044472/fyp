"""Report reference-ROI controls, geometry errors and unsuccessful prototypes."""
import argparse
import hashlib
import html
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('benchmark',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args()
    out=args.output
    read=lambda p:json.loads(p.read_text())
    refs=read(out/'records.json');runtime={r['sample']:r for r in read(args.benchmark/'heatmap-v3-20261025/records.json')}
    assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in read(out/'scored-input-hashes.json').items())
    errors=[];groups={}
    for r in refs:
        a=runtime[r['sample']];q=np.array(a['diagnostics']['roi_quad_full'],np.float32);ref=np.array(r['quad'],np.float32)
        inter=max(0,float(cv2.intersectConvexConvex(q,ref)[0]));iou=inter/max(abs(cv2.contourArea(q))+abs(cv2.contourArea(ref))-inter,1e-9)
        side=float(np.linalg.norm(q[1]-q[0]));refside=float(np.linalg.norm(ref[1]-ref[0]))
        e=dict(sample=r['sample'],identity=r['identity'],index=r['index'],iou=iou,auto_side_px=side,reference_side_px=refside,
               side_ratio=side/refside,center_shift_in_reference_sides=float(np.linalg.norm(q.mean(0)-ref.mean(0))/refside))
        errors.append(e)
        image=Image.open(args.benchmark/'originals'/r['sample']/'full.jpg').convert('RGB')
        draw=ImageDraw.Draw(image)
        for quad,color in ((q,'lime'),(ref,'cyan')):
            pts=[tuple(map(float,p)) for p in quad];draw.line(pts+pts[:1],fill=color,width=7)
        image.thumbnail((480,270));panel=Image.new('RGB',(620,300),'white');panel.paste(image,(0,25))
        draw=ImageDraw.Draw(panel);draw.text((4,4),f"{r['identity']} #{r['index']} green=auto cyan=reference",fill='black')
        draw.text((486,40),f"IoU {iou:.2f}\nside ratio\n{side/refside:.2f}\ncenter shift\n{e['center_shift_in_reference_sides']:.2f}",fill='black')
        groups.setdefault(r['identity'],[]).append((r['index'],panel))
    sheets=[]
    for identity,panels in groups.items():
        sheet=Image.new('RGB',(1240,1500),'white')
        for j,(_,panel) in enumerate(sorted(panels)):sheet.paste(panel,((j%2)*620,(j//2)*300))
        name=identity.replace(':','-')+'-geometry.jpg';sheet.save(out/name,quality=95);sheets.append((identity,name))
    results=read(out/'classical.json')+read(out/'neural.json')['results']
    table=''
    for alg,variants in [('DoN',['fused_normalized','heatmap_normalized','reference_normalized']),('FastCC',['fused_normalized','heatmap_normalized','reference_normalized']),('local_training_matcher',['fused_raw','heatmap_raw','reference_raw'])]:
        values=[next(r['correct'] for r in results if r['algorithm']==alg and r['variant']==v and r['subset']=='all') for v in variants]
        table+=f'<tr><td>{alg}</td>'+''.join(f'<td>{n}/20</td>' for n in values)+'</tr>'
    summary=dict(images=40,probes=20,annotations_sha256=read(out/'scored-input-hashes.json')['annotations.json'],
        runtime_median_iou=float(np.median([e['iou'] for e in errors])),runtime_iou_below_half=sum(e['iou']<.5 for e in errors),geometry_errors=errors,
        annotation_scope='Single assistant visual estimates before recognition scoring; no independent human adjudication. Exploratory developer dataset.',
        runtime='Default heatmap-v3 unchanged; reference coordinates never loaded by the app; no Pi deployment.')
    (out/'geometry-summary.json').write_text(json.dumps(summary,indent=2))
    worst=''.join(f"<tr><td>{html.escape(r['identity'])} #{r['index']}</td><td>{r['iou']:.2f}</td><td>{r['auto_side_px']:.0f}</td><td>{r['reference_side_px']:.0f}</td><td>{r['side_ratio']:.2f}</td></tr>" for r in sorted(errors,key=lambda r:r['iou'])[:9])
    text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>ROI comparison · 2026-10-26</title>
<style>body{{max-width:1120px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{border:1px solid #cbd5e1;padding:10px;text-align:left}}img{{max-width:100%}}.note{{padding:18px;background:#dcfce7;border-radius:10px}}details{{margin:20px 0}}a{{color:#0369a1}}</style><body>
<h1>Reference crops identify localization as the main current bottleneck</h1><p class="note">No images were removed and the matchers did not change. Substituting crops based on a consistent finger-valley rule raised FastCC from 11 to 19/20 and DoN from 11 to 17/20.
This is a reference-coordinate experiment, not an automatic system achieving 19/20.</p>
<h2>All 40 images / fixed 20 queries</h2><table><tr><th>Matcher</th><th>Legacy fusion</th><th>Current automatic heatmap</th><th>Reference finger-valley ROI</th></tr>{table}</table>
<p>Enroll the first five images per hand and query the last five, scoring each identity by the median of five distances. All images remain, including failed localizations. Conventional matchers retain percentile normalization; the main neural comparison uses raw grayscale ROIs.
Brightness normalization of the reference crop yielded 16/20 for neural matching. Query-only or two-sided RIA restoration did not add correct matches (17/20 raw, 16/20 normalized).</p>
<h2>How reference coordinates were obtained</h2><p>The 40 originals were displayed under randomized identifiers without previous predictions or matching scores. The index–middle and ring–little finger valleys and a point on the palm side were marked by visual inspection. All crops used the original PalmKit alpha=0.15, beta=1.2 setting.
All crops were visually reviewed, then coordinates and pixel hashes frozen before scoring. A finger-valley point on S05 was corrected before scoring and the correction was logged.</p>
<p><strong>Limitations:</strong>The assistant's visual estimates were not independently reviewed and are not a manual gold standard. Previous access to the data and identities precludes calling this blinded. Two people and four hands do not establish an independent accuracy or false-match rate from 19/20.
All 40 reference boxes fall inside the frame. Variation in real pose and annotation error remain possible.</p>
<h2>Where the automatic boxes differ</h2><p>Median intersection-over-union (IoU) between automatic and reference boxes: {summary['runtime_median_iou']:.3f}; {summary['runtime_iou_below_half']} /40 have IoU below 0.5.
The problem extends beyond the four geometry failures. Some boxes pass boundary and span checks without covering a consistent palm region. Below are the 9 lowest-overlap cases; lengths are in original-image pixels.</p>
<table><tr><th>Sample</th><th>IoU</th><th>Automatic side length</th><th>Reference side length</th><th>Side-length ratio</th></tr>{worst}</table>
<h2>Automatic correction prototypes, including failed attempts</h2><ul>
<li>Enlarging the segmentation extent before localization gave DoN 6/20, FastCC 10/20 and neural matching 12/20; not enabled.</li>
<li>GrabCut contour refinement plus three finger-valley indentations used contours on 16/40 and retained the heatmap elsewhere. DoN 7/20, FastCC 4/20, neural 13/20; not enabled. Background and finger-gap boundary errors persisted.</li>
<li>Desaturating the input and trying four orientations returned 19/40 crops. No accuracy was reported on only the successful subset; not enabled. An OpenCV/ONNX comparison on identical input for one failed image showed little difference and did not implicate the inference backend.</li></ul>
<h2>Next repair target</h2><p>First stabilize the two finger valleys. Measure endpoint error, scale error and ROI overlap separately against the coordinates.
When calibrating or fine-tuning for this camera, use the 40 images only as development annotations and reserve fresh sessions for validation. Do not fit to these images and call their recognition scores a test.
The heatmap-v3 implementation remains. Neither visual reference points nor failed prototypes entered default recognition; no Pi deployment.</p>
<h2>Reproducibility</h2><p><a href="annotations.json">Reference coordinates</a> · <a href="plan.json">Rules and scope</a> · <a href="scored-input-hashes.json">Hashes frozen before scoring</a> ·
<a href="geometry-summary.json">Per-image geometry error</a> · <a href="classical.json">All conventional scores</a> · <a href="neural.json">All neural and RIA scores</a> ·
<a href="../heatmap-v3-20261025/report.html">Current automatic pipeline report</a></p>
<h2>All 40 images: automatic in green, reference in cyan</h2>'''
    for identity,name in sheets:text+=f'<details open><summary>{html.escape(identity)}</summary><img src="{name}"></details>'
    (out/'report.html').write_text(text+'</body></html>',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='geometry_errors'},indent=2))


if __name__=='__main__':main()
