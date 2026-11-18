"""Render the saved v5/PalmIR development evidence without rerunning inference."""
import argparse
import html
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pklnet_roi import normalize_roi


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path);args=parser.parse_args();root=args.output
    original=read(root/'new-camera/recognition.json');guarded=read(root/'consistency-new/recognition.json')
    baseline=next(x for x in original if x['variant']=='v4' and x['algorithm']=='DoN')
    current=next(x for x in guarded if x['algorithm']=='DoN')
    old={x['sample']:x for x in baseline['trials']}
    fixed=[x for x in current['trials'] if x['correct'] and not old[x['sample']]['correct']]
    worse=[x for x in current['trials'] if not x['correct'] and old[x['sample']]['correct']]
    rows=read(root/'consistency-new/records.json');by_id={r['sample']:(i,r) for i,r in enumerate(rows)}
    pixels={'v4':np.load(root/'new-camera/pixels.npz')['v4'],
            'v5':np.load(root/'consistency-new/pixels.npz')['consistent_gamma']}
    figures=[]
    for count,(label,t) in enumerate([('Corrected mismatch',x) for x in fixed]+[('New mismatch, retained for disclosure',x) for x in worse],1):
        i,r=by_id[t['sample']];im=Image.open(r['original']).convert('RGB');panel=Image.new('RGB',(1200,510),'white')
        for col,(p,k) in enumerate([('v4','v4'),('v5','consistent_gamma')]):
            view=im.copy();d=ImageDraw.Draw(view);q=[tuple(v) for v in r['variants'][k]['quad']];d.line(q+q[:1],fill='lime',width=7)
            view.thumbnail((590,330));panel.paste(view,(col*600,25));panel.paste(Image.fromarray(normalize_roi(pixels[p][i])[0]),(col*600,365))
            ImageDraw.Draw(panel).text((col*600,5),f'{p} {r["identity"]} #{r["index"]}',fill='black')
        panel.save(root/f'comparison-{count}.jpg',quality=94)
        figures.append(f'<figure><img src="comparison-{count}.jpg"><figcaption>{label} · {html.escape(r["identity"])} · image {r["index"]}. Left: v4; right: v5. Normalized ROIs below.</figcaption></figure>')
    stress=read(root/'stress/results.json') if (root/'stress/results.json').exists() else []
    conditions={'dark_065':'Brightness × 0.65','blur_sigma3':'Gaussian blur, σ=3 original-image pixels','shift_3pct':'Horizontal/vertical shift of 3%'}
    stress_rows=''.join(f'<tr><td>{conditions[c]}</td>'+''.join(f'<td>{next(x["correct"] for x in stress if x["condition"]==c and x["policy"]==p and x["algorithm"]==a)}/20</td>' for p,a in [('v4','DoN'),('v5','DoN'),('v4','FastCC'),('v5','FastCC')])+'</tr>' for c in conditions if any(x['condition']==c for x in stress))
    classical=read(root/'palmir-consistent/classical.json');neural=read(root/'palmir-consistent/neural.json')
    restoration_rows=''
    for name,data in [('DoN',classical),('FastCC',classical),('Companion neural matcher',neural)]:
        alg='local_training_matcher' if name=='Companion neural matcher' else name
        values=[next(x['correct'] for x in data if x['subset']=='all' and x['algorithm']==alg and x['variant']==v) for v in ['raw_both','raw_ria_both','raw_ria_probe']]
        restoration_rows+=f'<tr><td>{name}</td>'+''.join(f'<td>{v}/20</td>' for v in values)+'</tr>'
    stats=read(root/'palmir-consistent/stats.json')['stats']
    deployment=read(root/'deployment.json') if (root/'deployment.json').exists() else None
    pi=read(root/'pi-consistent/summary.json') if (root/'pi-consistent/summary.json').exists() else None
    state='Deployed; file hashes and service status verified' if deployment else 'Candidate; deployment not confirmed'
    pi_text='Final-version Pi replay is incomplete.'
    if pi:
        d=pi['demo'];n=sum(p['result'].get('user_id')==p['identity'].replace(':','-') for p in d['probes']);lat=pi['latency_ms']['illumination']
        pi_text=f'Final Pi version: 40/40 passed geometry; {sum(x["http_status"]==200 for x in d["enrollments"])}/4 groups enrolled; actual HTTP DoN: {n}/20, {d["payment"]["transactions"]} isolated simulated debits. Duplicate confirmation and confirmation after cancellation checks passed. Single-core ROI median: {lat["median"]/1000:.2f} s; P95: {lat["p95"]/1000:.2f} s.'
    candidates=''.join(f'<tr><td>{html.escape(x["variant"])}</td><td>{x["algorithm"]}</td><td>{x["correct"]}/20</td><td>{x["valid"]}/40</td></tr>' for x in original)
    doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ROI v5 and PalmIR evaluation</title><style>body{margin:0;background:#f2f5f4;color:#17352e;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1120px;margin:auto;padding:38px 24px}h1{font-size:38px;line-height:1.35}h2{margin-top:35px}.card,figure{background:white;padding:22px;border-radius:14px;margin:22px 0}img{width:100%;height:auto}figcaption,.small{font-size:14px;color:#4b635b}table{border-collapse:collapse;width:100%;background:white;font-size:16px}td,th{padding:12px;border-bottom:1px solid #d3dfd8;text-align:left}th{background:#dfebe3}a{color:#007263}code{overflow-wrap:anywhere;font-size:14px}.note{border-left:5px solid #d59b37;padding-left:18px}summary{cursor:pointer}</style><main>'''
    doc+=f'<p>2026-10-28 · {state}</p><div class="card"><a href="stability/report.html">Update: complete stability and nine-pose candidate evaluation across old and new cameras</a>. New-camera results still vary with enrollment composition; cross-camera matching is unreliable. The candidate is not deployed.</div><h1>DoN improved to 14/20 on the Pi; <br>PalmIR added no recognition gain in this round.</h1>'
    doc+='''<p>The final candidate <code>pklnet-illumination-consistent-v5</code> checks localization on both the original and moderately brightened input. It accepts the brightened localization only when the boxes have at least 0.5 intersection over union; otherwise it retains v4. The final ROI is always cropped from the original photo. Model weights, matching and existing geometry gates are unchanged.</p>
<table><tr><th>Development-set metric</th><th>v4</th><th>Local v5</th><th>v5 Pi</th></tr><tr><td>New-camera DoN correct</td><td>13/20</td><td>15/20</td><td>14/20</td></tr><tr><td>New-camera FastCC correct</td><td>12/20</td><td>15/20</td><td>15/20</td></tr><tr><td>New-camera ROI geometry passes</td><td>40/40</td><td>40/40</td><td>40/40</td></tr><tr><td>Old-camera DoN / FastCC</td><td>20/20</td><td>20/20</td><td>Not rerun this round</td></tr></table>
<p class="note">Not every image improved: local DoN corrected three errors and introduced one, a net gain of two. An additional borderline query failed on the Pi, leaving 6/20 wrong. Valid geometry does not guarantee correct palm alignment. Both hands of just two people were repeatedly used for development; neither 75% locally nor 70% on the Pi establishes field reliability.</p>
<p>Maximum workstation/Pi coordinate difference was about 0.00193 pixels; mean absolute normalized ROI pixel difference was about 0.2503/255. Workstation matching on the 40 Pi ROIs also gave 14/20, narrowing the discrepancy to ROI pixel generation rather than HTTP or matcher flow. Decoding versus perspective interpolation remains unresolved. The differing query had nearly tied scores for the true and incorrect identities, exposing instability. <a href="backend-parity.json">Cross-platform pixel comparison</a></p>
<h2>Why check localization consistency?</h2><p>Brightening alone also achieved 15/20 but substantially changed seven ROIs. Retaining original localization under a fixed 0.5 IoU rule kept DoN/FastCC at 15/20 and reduced the count below 0.5 IoU with the assistant’s reference boxes from eight to six. The rule uses predicted geometry only, not labels or scores. The boxes are development annotations, not an independent gold standard. The rule was compared on the same data and needs new-session validation.</p>
<h2>Simulated changes in capture quality</h2><p>Images 1–5 in each group remained enrolled; only query images 6–10 changed. All 20 queries were retained per condition, including localization failures as errors. This is synthetic development-set stress testing, not new captures. Occasional gains from blur indicate instability, not a reason to blur the camera.</p>
<table><tr><th>Query change</th><th>v4 DoN</th><th>v5 DoN</th><th>v4 FastCC</th><th>v5 FastCC</th></tr>'''+stress_rows+'</table>'
    doc+='''<h2>PalmIR evaluation</h2><p>We used the project’s existing <strong>Local PalmIR-style RIA / CompactRestorer</strong>, trained on PolyU-II palm ROIs; this is not official PalmIR. All 40 final v5 ROIs were tested with raw/normalized input, restoration on both sides or only queries, and 50% blending. All queries remained in the denominator.</p><table><tr><th>Matcher</th><th>Unrestored</th><th>Enrollment and queries restored</th><th>Queries only restored</th></tr>'''+restoration_rows+'</table>'
    doc+=f'<p>Mean absolute change on raw ROIs was only {stats["raw"]["mean_abs_change_8bit"]:.4f}/255; on normalized inputs it was {stats["normalized"]["mean_abs_change_8bit"]:.4f}/255. No restoration setting increased the number correct. The local model behaves nearly as an identity transform here. Together with normal responses to blur in earlier training-domain controls, this suggests a degradation/domain mismatch, not proof of blur in field images. Restoration stays off by default.</p>'
    doc+='<h2>Local corrections and regressions</h2><p>These per-image local comparisons do not replace the measured Pi results above.</p>'+''.join(figures)
    doc+='<h2>End-to-end flow, costs and rollback</h2><p>'+pi_text+'</p><p>Final runtime code on the 40 old-camera originals locally gave 40 valid images, four groups enrolled, 20/20 correct over actual HTTP and four simulated debits. Production accounts and originals were preserved; the service stayed capture-only. The camera was disconnected, so live acceptance is not claimed. v5 needs two localization passes or more with retries, making it slower than v4. Old templates require re-enrollment; account balances are retained.</p>'
    doc+='<p>At v5 deployment, 43 relevant unit tests passed. Further work is needed on geometrically valid but inconsistent palm regions, more real sessions and restoration degradations representative of field images. The hourly automation was removed. Subsequent experiments are in the stability report above.</p>'
    doc+='<details><summary>All localization experiments, including unsuccessful configurations</summary><table><tr><th>Configuration</th><th>Algorithm</th><th>Correct</th><th>Geometry passed</th></tr>'+candidates+'</table></details>'
    doc+='''<div class="card"><strong>Evidence</strong><ul><li><a href="consistency-new/recognition.json">Per-image final candidate scores</a> · <a href="stress/results.json">Fixed stress test</a></li><li><a href="palmir-consistent/classical.json">PalmIR DoN/FastCC</a> · <a href="palmir-consistent/neural.json">Neural matcher</a> · <a href="palmir-consistent/stats.json">Model hashes and changes</a></li><li><a href="old-runtime-consistent/summary.json">Actual old-data flow</a> · <a href="pi-consistent/summary.json">Actual Pi flow</a> · <a href="deployment.json">Deployment and backup</a></li><li><a href="../pi5-roi-v4-20261027/report.html">Previous report</a></li></ul><p class="small">Some historical score files also include an original_geometry_pass subset. This report always uses the all result covering all 20 queries, never a filtered score.</p></div></main></html>'''
    (root/'report.html').write_text(doc,encoding='utf-8')
    print(root/'report.html')


if __name__=='__main__':main()
