"""Package the locally verified heatmap repair and its full-denominator report."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import zipfile

APP=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();out=args.output
    read=lambda name:json.loads((out/name).read_text())
    records=read('records.json')
    results=read('classical.json')+read('neural.json')['results']
    rows=''
    for alg,old,new in [('DoN','original','heatmap_runtime'),('FastCC','original','heatmap_runtime'),
                        ('local_training_matcher','original_raw','heatmap_runtime_raw')]:
        values=[next(r['correct'] for r in results if r['algorithm']==alg and r['variant']==v and r['subset']=='all') for v in (old,new)]
        rows+=f'<tr><td>{alg}</td><td>{values[0]}/20</td><td>{values[1]}/20</td></tr>'
    failures=''.join(f"<li>{html.escape(r['identity'])} #{r['index']}: {html.escape(r['diagnostics']['roi_geometry_reason'])}</li>" for r in records if not r['runtime_valid'])
    live=''.join(f"<li>{r['algorithm']}: {r['correct']}/{r['total']}; geometry rejected {r['geometry_rejected_probes']}  queries, retained in the denominator.</li>" for r in read('runtime-guard.json'))
    images=''.join(f'<details><summary>All sample comparisons {i+1}–{i+10}</summary><img src="comparison-{i}.jpg"></details>' for i in range(0,40,10))
    text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>ROI pipeline fix v3</title>
<style>body{{max-width:1100px;margin:40px auto;padding:0 24px;font:17px/1.65 system-ui;color:#213547;background:#f8fafc}}h1,h2{{line-height:1.3}}table{{border-collapse:collapse;background:white;width:100%}}td,th{{padding:12px;border:1px solid #cbd5e1;text-align:left}}.note{{padding:18px;background:#e0f2fe;border-radius:10px}}img{{max-width:100%}}details{{margin:18px 0}}a{{color:#0369a1}}</style>
<h1>ROI pipeline fix v3: locally verified</h1><p class="note">The default now uses the PKLNet heatmap branch rather than averaging branches.
Contrast and sharpness are recorded, not used for rejection. Not deployed to Pi. This supersedes consensus-v2 rejection.</p>
<h2>All 40 originals: fixed 20 enrollments and 20 queries</h2>
<p>For each hand, enroll the first five and query the last five; use the median of five distances per identity. All images, including geometric failures, remain in the comparison. No selection was used to raise scores.
This is a rank-one diagnostic on the development set, not independent validation, transaction acceptance or a false-match rate.</p>
<table><tr><th>Matcher</th><th>Legacy fused ROI</th><th>ROI from the new runtime</th></tr>{rows}</table>
<p>ONNX inference covered all 40 images. Maximum coordinate difference from independently cached PyTorch heatmaps: {max(r['keypoint_parity_max_px'] for r in records):.5f} px。
Geometry passed on 36/40 rather than 31/40. 92 relevant tests passed; the legacy test_existing_pipeline.py still referenced a pre-migration module and was excluded.</p>
<h2>Runtime geometry checks reported separately</h2><p>The application still prevents out-of-bounds and collapsed crops from reaching matching. Counts below include geometry rejections and are separate from the unfiltered experiment above.</p><ul>{live}</ul>
<h2>Why the fix was needed and what remains</h2><p>On 8/40 images the endpoints ran in opposite directions across the two branches; averaging by array index shrank or collapsed the ROI.
One consistent spatial branch is used without selecting per image by identity or match score. This removes faulty fusion, not all heatmap errors.</p><ul>{failures}</ul>
<p>Aligning endpoints before averaging gave DoN 5/20, FastCC 7/20 and neural matching 13/20, so it was not adopted.
The separate OpenCV detector plus four-direction search returned only 22/40 crops and included visible background detections. No success-only accuracy was reported and no automatic fallback enabled.</p>
<h2>PalmIR</h2><p>The local model is CompactRestorer PalmIR-style RIA, not the official PalmIR weights. With new ROIs, neural matching scored 14/20 using original inputs, query-only restoration or restoration on both sides.
There is no evidence for enabling restoration by default. No complete deployment-ready pretrained release was found during the review; that does not invalidate the official method.</p>
<p>Subsequent tests covered normalization, half-strength restoration, pixel-only weights and PyTorch controls. See <a href="../restoration-adaptation-20261025/report.html">Local restoration audit and possible improvements</a>。</p>
<h2>Deployment and reproducibility</h2><p>Re-enroll five images under each existing identifier. Account names, balances and transactions are retained. Updating code does not change the service mode.
The patch depends on the existing app, PKLNet weights and geometry code; it is not a fresh installer. Compare and back up remote files, run offline inference checks, and restart in the original mode.
The user manages Pi networking. No deployment in this round.</p><p><a href="heatmap-v3-patch.zip">Latest patch</a> · <a href="patch-manifest.json">File SHA-256</a> ·
<a href="classical.json">All conventional matcher scores</a> · <a href="neural.json">Neural / RIA scores</a> · <a href="runtime-guard.json">Actual runtime geometry rejections</a> ·
<a href="records.json">Per-image coordinates and diagnostics</a></p><p>Replay: python tools/evaluate_heatmap_policy.py &lt;benchmark&gt; &lt;new-output-directory&gt;</p>
<h2>Per-image crop boxes and original ROIs</h2>{images}</html>'''
    (out/'report.html').write_text(text,encoding='utf-8')
    files=['pklnet_roi.py','pklnet_policy.py','demo_flow.py','demo_page.py','gallery.py','palm_app/debug_ui.py',
        'README.md','docs/SETUP.md','deploy/make_deploy_bundle.ps1','tools/expose_pklnet_branches.py',
        'tools/export_pklnet_onnx.py','tools/audit_roi_branches.py','tools/evaluate_pklnet_policy.py',
        'tools/evaluate_heatmap_policy.py','tools/audit_endpoint_fusion.py','tools/audit_landmark_roi.py',
        'tools/write_heatmap_report.py','tools/audit_restoration_adaptation.py','tools/check_restoration_checkpoint.py',
        'tools/write_restoration_adaptation_report.py','tests/test_pklnet_consensus.py']
    entries={name:APP/name for name in files}
    for suffix in ('onnx','json'):
        name='pklnet-keypoints-diagnostics.'+suffix
        entries['pklnet/'+name]=APP.parent/'pklnet'/name
    manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in entries.items()}
    (out/'patch-manifest.json').write_text(json.dumps(manifest,indent=2))
    with zipfile.ZipFile(out/'heatmap-v3-patch.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name,path in entries.items():archive.write(path,name)
        archive.write(out/'patch-manifest.json','patch-manifest.json')
    with zipfile.ZipFile(out/'heatmap-v3-patch.zip') as archive:
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==digest for name,digest in manifest.items())
    print(out/'report.html')


if __name__=='__main__':main()
