"""Summarize single-device error concentration, geometry and actual runtime checks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from write_stability_report import table


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);args=parser.parse_args()
    root=args.root;out=root/'single-device'
    records=read(root/'stability/records.json');lookup={r['sample']:i for i,r in enumerate(records)}
    assert len(records)==80 and all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
    old_cases=[r for r in read(root/'stability/results.json') if r['algorithm']=='FastCCPoseNearest-v1' and r['case'].startswith('new_') and '_to_' not in r['case']]
    seen=Counter(t['sample'] for c in old_cases for t in c['trials'])
    failures=Counter(t['sample'] for c in old_cases for t in c['trials'] if not t['correct'])
    reference=Path(__file__).resolve().parents[1]/'runtime/pi5-new-camera-20261021/reference-roi-20261026'
    references={r['sample']:r for r in read(reference/'records.json')}
    error_rows=[];diagnostics=[]
    for sample,n in failures.most_common():
        r=records[lookup[sample]];a=np.asarray(r['illumination']['details']['roi_quad_full'],np.float32);b=np.asarray(references[sample]['quad'],np.float32)
        area=cv2.intersectConvexConvex(a,b)[0];iou=area/(cv2.contourArea(a)+cv2.contourArea(b)-area)
        ratio=float(np.linalg.norm(a[1]-a[0])/np.linalg.norm(b[1]-b[0]));shift=float(np.linalg.norm(a.mean(0)-b.mean(0))/np.linalg.norm(b[1]-b[0]))
        diagnostics.append(dict(sample=sample,identity=r['identity'],index=r['index'],failures=n,queries=seen[sample],reference_iou=iou,side_ratio=ratio,center_shift_sides=shift))
        error_rows.append([r['identity']+' #'+str(r['index']),f'{n}/{seen[sample]}',f'{iou:.2f}',f'{ratio:.2f}',f'{shift:.2f}'])
    (out/'error-diagnosis.json').write_text(json.dumps(diagnostics,indent=2),encoding='utf-8')
    summary=read(out/'runtime-v2/summary.json');runtime=read(out/'runtime-v2/results.json')
    metrics={(r['method'],r['cohort'],r['split']):r for r in summary}
    def format_score(r):
        spread=str(r['min']) if r['min']==r['max'] else f'{r["min"]}–{r["max"]}'
        return spread+'/20'+(f' (mean {r["mean"]:.2f})' if r['count']>1 else '')
    metric_rows=[]
    for split,label in [('original','New: enroll first five, query last five'),('reverse','New: enroll last five, query first five'),('random','New: original ten random splits'),('extra','New: additional 100 random splits')]:
        metric_rows.append([label,*[format_score(metrics[m,'new',split]) for m in ['pose_nearest','registered_best2']]])
    metric_rows.append(['Old: all splits above','20/20 on every split','20/20 on every split'])
    before={r['case']:r for r in runtime if r['method']=='pose_nearest'}
    extra=[r for r in runtime if r['method']=='registered_best2' and r['case'].startswith('new_extra_')]
    improvements=dict(better=sum(r['correct']>before[r['case']]['correct'] for r in extra),same=sum(r['correct']==before[r['case']]['correct'] for r in extra),worse=sum(r['correct']<before[r['case']]['correct'] for r in extra))
    (out/'split-comparison.json').write_text(json.dumps(improvements,indent=2))
    http_rows=[];http=[]
    for c,label in [('new','New images'),('old','Old images')]:
        replay=read(out/f'http-v2-{c}/summary.json');assert replay['demo_matcher']=='FastCCRegisteredBest2-v2' and replay['originals_unchanged']
        d=replay['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
        http.append(correct)
        http_rows.append([label,f'{correct}/{len(d["probes"])}',f'{sum(t["http_status"]==200 for t in d["enrollments"])}/4',d['payment']['transactions']])
    latency=read(out/'runtime-v2/latency.json')
    # Save all simple aggregation controls attempted before local registration.
    distances=np.load(root/'stability/distances.npz');pose=distances['FastCCPoseNearest-v1'];controls=[]
    for name,matrix in [('directed',pose),('symmetric_mean',(pose+pose.T)/2),('mutual_max',np.maximum(pose,pose.T)),('either_min',np.minimum(pose,pose.T))]:
        for count in [1,2,3]:
            values=[]
            for c in old_cases:
                gs={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};correct=0
                for t in c['trials']:
                    i=lookup[t['sample']];sc={k:float(np.sort(matrix[i,ids])[:count].mean()) for k,ids in gs.items()}
                    correct+=sc[t['identity']]<min(v for k,v in sc.items() if k!=t['identity'])
                values.append(int(correct))
            controls.append(dict(distance=name,best_templates=count,original=values[0],reverse=values[1],random=values[2:]))
    (out/'aggregation-controls.json').write_text(json.dumps(controls,indent=2))
    doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Improving within-device recognition stability</title><style>
body{margin:0;background:#f3f5f6;color:#19333c;font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:32px 24px 64px}h1{font-size:36px;line-height:1.4}h2{margin-top:36px}.card{background:white;padding:22px;border-radius:12px;margin:22px 0}.warning{border-left:5px solid #c78736}table{border-collapse:collapse;width:100%;background:white;font-size:15px}td,th{padding:11px;border-bottom:1px solid #d6e0e5;text-align:left}th{background:#e1edf0}.scroll{overflow:auto}img{max-width:100%;height:auto}a{color:#006c82}code{font-size:14px;overflow-wrap:anywhere}figcaption,.small{font-size:14px;color:#50656e}</style><main>
<p>2026-10-28 · Within-device evaluation only · New candidate integrated locally, not deployed to the Pi</p>
<h1>Variation concentrates in a few off-center crops; <br>automatic alignment improves within-device stability.</h1>
<div class="card"><a href="image-review/report.html">Update: original failures, normal controls and native pixels illustrate the ROI errors</a>. Extended alignment experiments continue; the tables below retain v2 results from completed HTTP acceptance testing.</div>
<div class="card"><strong>Scope: enrollment and queries on the same device only.</strong><p>Old and new cameras were tested separately. Cross-device matching is no longer a target for this fix. All 80 originals remain, and failures stay in the denominator.</p></div>
<h2>Before and after the fix on identical splits</h2>'''+table(['Within-device test','Nine-pose candidate (before)','Automatic alignment + dual views (after)'],metric_rows)
    doc+=f'<p>Across the additional 100 new-image splits, {improvements["better"]} improved, {improvements["same"]} were unchanged and {improvements["worse"]} regressed. These splits reuse the same 40 development images, not independent new captures; do not count them as 2,000 independent queries.</p>'
    doc+='''<h2>Why did results vary from 15 to 18 correct out of 20?</h2><p>This is not randomness when rerunning a fixed image. Across the ten original splits and both enrollment directions, errors cluster in the few photos below. They often fail as queries and change template coverage when enrolled. A few superficially similar wrong templates also attract nearest-template matches. Changing enrollment photos therefore changes recognition results.</p>'''+table(['Sample (original label + number)','Errors / appearances as query','Automatic/reference box IoU','Automatic/reference side length','Center offset / reference side length'],error_rows)
    doc+='''<p>For one example, the automatic box side was only about 45% of the reference, enlarging and shifting the palm texture in the crop. Other images also showed scale or palm-region offsets. Reference boxes are earlier visual development annotations by the assistant, not an independent human gold standard. Substituting only those fixed ROIs gave FastCC median matching 18–20/20 on the ten original splits. Localization/alignment is an important bottleneck, not necessarily the only one.</p>
<figure><img src="roi-grid.jpg" alt="Ten automatic ROIs for each of four new-camera palm classes"><figcaption>Each row shows one hand in original image order 1–10, using automatic v5 crops. Main palm lines differ noticeably in position or scale in some images. Contrast or sharpness alone does not justify excluding them.</figcaption></figure>
<h2>Implemented changes</h2><ol>
<li>Find local texture correspondences in the 384-pixel automatic ROI and align palm lines using consistent rotation, scale and translation. Localization still uses automatic v5; reference points and identity labels are not built into the algorithm.</li>
<li>Find correspondences in both original texture and a fixed lightly smoothed view to reduce interference from fine texture. Final FastCC recognition pixels always come from the original, without cosmetic or generative restoration.</li>
<li>Correspondences must meet count, spatial coverage and geometry constraints. The aligned sampling area must fit the original and saved context. Without reliable alignment, keep the original nine-pose result to avoid matching black padding.</li>
<li>Each identity uses the mean distance of its best two enrollment templates so a single accidentally close template cannot decide alone. All five enrollment samples remain and all identities use the same rule.</li></ol>
<p>Changing aggregation alone, bidirectional averaging, or counting local keypoints alone did not resolve the problem. Recomputing palmprint features after local alignment showed clearer gains. Existing PalmIR restoration still added no benefit and remains off.</p>
<h2>Actual application replay</h2>'''+table(['Local HTTP','Queries correct','Successful enrollments','Isolated simulated payments'],http_rows)
    doc+='''<p>Historical originals replaced camera input. ROI localization, feature extraction, compressed template storage and loading, HTTP recognition and simulated payment confirmation all used actual code. Original hashes, production accounts and balances remained unchanged; this is not live capture acceptance.</p>
<p>Optional parameter: <code>--demo-matcher FastCCRegisteredBest2-v2</code>; requires <code>--roi-mode pklnet</code>. A separate template version requires re-enrollment; old DoN, nine-pose and v1 templates cannot be mixed. Default DoN and the Pi capture-only service were unchanged. Pi connectivity had not recovered, so this round was not deployed.</p>'''
    doc+=f'<p>Local median feature extraction: about {latency["extraction_ms"]["median"]:.0f} ms (excludes ROI localization); median matching time per template pair: about {latency["pair_match_ms"]["median"]:.1f} ms; one uncompressed feature: about {latency["template_bytes"]/1e6:.2f} MB. Disk storage uses compressed NPZ. These are local development measurements, not Pi latency guarantees. All 27 relevant matcher, template, payment and capture-only tests passed.</p>'
    doc+='''<div class="card warning"><strong>Remaining limitations</strong><p>Stability is incomplete. The worst additional split was 16/20 and the reverse split 18/20. Some undersized crops or images lacking sufficient palm correspondences still fail. A fixed split at 20/20 cannot replace acceptance on fresh sessions excluded from tuning. Repeated inspection of two people supports only a development-stage within-device improvement.</p></div>
<h2>Evidence and reproduction</h2><ul>
<li><a href="runtime-v2/summary.json">Stability summary for final runtime code</a> · <a href="runtime-v2/results.json">All splits, templates and per-query scores</a> · <a href="runtime-v2/plan.json">Protocol</a></li>
<li><a href="error-diagnosis.json">Concentration of errors and box offsets</a> · <a href="reference-controls.json">Reference-box control</a> · <a href="aggregation-controls.json">Aggregation controls</a></li>
<li><a href="http-v2-new/summary.json">New-image HTTP replay</a> · <a href="http-v2-old/summary.json">Old-image HTTP replay</a> · <a href="runtime-v2/latency.json">Timing and template size</a></li>
<li><a href="local-alignment/results.json">Local-features-only failure control</a> · <a href="registered/results.json">Full-original alignment prototype</a> · <a href="descriptor-smoothing/results.json">Single-view smoothing control</a></li>
<li><a href="../stability/report.html">Previous full stability audit (includes cross-device control, no longer a target)</a></li></ul></main></html>'''
    (out/'report.html').write_text(doc,encoding='utf-8');print(out/'report.html')


if __name__=='__main__':main()
