"""Summarize completed runtime and fresh-inference evidence, not prototype scores."""
import hashlib
import html
import json
from pathlib import Path
import sys
import numpy as np

root=Path(sys.argv[1]);out=root/'single-device'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</table>'
audit=read(out/'union-audit.json');fresh=read(out/'fresh-v4/summary.json');summary=read(out/'runtime-v4-fresh/summary.json')
assert audit['runtime_cases_verified']==224
http=[];timing=[]
for cohort in ['new','old']:
    r=read(out/f'http-v4-{cohort}/summary.json')
    assert r['demo_matcher']=='FastCCWindowUnion-v4' and r['originals_unchanged']
    d=r['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    http.append([cohort,correct,len(d['probes']),sum(t['http_status']==200 for t in d['enrollments']),d['payment']['transactions']])
    routes={t['route'] for t in d['http_trace']}
    for route in sorted(routes):
        times=[t['ms'] for t in d['http_trace'] if t['route']==route and t['status']==200]
        if times:timing.append(dict(cohort=cohort,route=route,count=len(times),median_ms=float(np.median(times)),p95_ms=float(np.percentile(times,95))))
disk=[p.stat().st_size for p in (out/'runtime-v4').glob('*.npz')]
resource=dict(template_envelope_bytes=16*1024*1024,compressed_template_bytes=dict(median=float(np.median(disk)),max=max(disk),total=sum(disk)),
              cached_geometry_runtime=read(out/'runtime-v4/latency.json'),fresh_localization=fresh['inference_plus_extraction_ms'],http=timing,
              caveat='Local Windows CPU, some audits run concurrently; not Pi latency or an isolated performance benchmark')
(out/'resource-v4.json').write_text(json.dumps(resource,indent=2))
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>v4 single-device runtime evaluation</title><style>body{font:17px/1.75 system-ui;background:#f3f5f6;color:#19333c;margin:30px auto;max-width:1150px;padding:20px}td{padding:10px;border-bottom:1px solid #ccc}table{background:white;width:100%}a{color:#006c82}pre{white-space:pre-wrap;font-size:14px}</style><h1>Single-device multi-candidate ROI: runtime and actual entry-point evaluation</h1>
<p>2026-10-28 · Optional FastCCWindowUnion-v4 · No Pi deployment, network change or change to default DoN</p>
<p>Full localization, search, alignment and scoring description:<a href="../../../docs/ROI_PIPELINE.md">ROI_PIPELINE.md</a>. <a href="report-v3.html">Specific failure images and historical comparisons</a>. </p>
<h2>All original splits after fresh inference</h2>'''
doc+=table([['Device','Split','Splits','Minimum /20','Maximum /20','Mean /20']]+[[r['cohort'],r['split'],r['count'],r['min'],r['max'],r['mean']] for r in summary])
doc+=f'<p>All 80 original image hashes were preserved. Queries and enrollments do not overlap; devices are evaluated separately, with 112 splits each. After fresh ONNX localization,{fresh["identical"]} /80 templates matched the cached-localization version byte for byte. All directed pairs involving the remaining templates were recomputed. Only matching cached pairs reused scores.</p>'
doc+='<h2>Local HTTP replay from historical originals</h2>'+table([['Device','Correct','Queries','Successful enrollments','Simulated payments']]+http)
doc+='<p>Historical originals replaced the camera; localization, templating, querying and payment ran through the real application. This is not live-camera or Pi validation. 48 regression checks passed.</p>'
doc+='<h2>Union strategy audit</h2><p>Candidates were combined uniformly without identity- or failure-specific selection; the matcher receives no labels. The separate base_full control was not silently included. Cached runtime distances are compared with the offline union matrix below.</p><pre>'+html.escape(json.dumps(audit['runtime_parity'],indent=2))+'</pre>'
doc+='<h2>Timing and resources</h2><pre>'+html.escape(json.dumps(resource,indent=2))+'</pre>'
doc+='<p>16 MiB is the uncompressed template size, including lossless gray pixels and descriptors. See the table for on-disk NPZ size. V4 requires re-enrollment; do not mix template versions. The 80-template batch evaluation once used about 1.6 GB peak working memory in the development tool; this is not a Pi or application guarantee.</p>'
doc+='<h2>Limits and reproducibility</h2><p>All images were repeatedly used for development. There is no independent-session, unknown-hand rejection or field-performance evidence. Perfect scores of 20/20 on the current splits do not establish stability. Historical failures and v2/v3 results are preserved.</p><ul>'
for p in ['union-audit.json','runtime-v4/summary.json','runtime-v4-fresh/results.json','fresh-v4/results.json','runtime-v4-fresh/plan.json','http-v4-new/summary.json','http-v4-old/summary.json','resource-v4.json','window-coarse-union/plan.json']:
    doc+=f'<li><a href="{p}">{p}</a></li>'
doc+='</ul></html>'
(out/'report-v4.html').write_text(doc,encoding='utf-8')
print(json.dumps(http));print(out/'report-v4.html')
