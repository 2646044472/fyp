"""Publish final isolated HTTP timings alongside exact-equivalence evidence."""
import json,html
from pathlib import Path
import sys
import numpy as np
root=Path(sys.argv[1]);base=root/'single-device'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def table(rows):return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
parity=read(base/'speed-v5/prepared-parity-parallel.json');extraction=read(base/'speed-v5/parallel-extraction.json')
assert parity['pairs']==3120 and not parity['differences'] and len(extraction)==80 and all(r['identical'] for r in extraction)
metrics=[]
for cohort in ['new','old']:
    r=read(base/f'http-v6-final-{cohort}/summary.json');d=r['demo']
    assert r['originals_unchanged'] and r['demo_matcher']=='FastCCDemo-v6'
    correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    times={k:[t['ms'] for t in d['http_trace'] if t['route']==k and t['status']==200] for k in ['/api/demo/enroll','/api/demo/identify']}
    stages={k:dict(median=float(np.median([t['result']['timing_ms'][k] for t in d['probes']])),p95=float(np.percentile([t['result']['timing_ms'][k] for t in d['probes']],95))) for k in ['capture_and_extract','gallery','total']}
    disk=list((base/f'http-v6-final-{cohort}/demo_runtime/demo_templates').glob('*.npz'))
    metrics.append(dict(cohort=cohort,correct=correct,total=len(d['probes']),enrolled=sum(t['http_status']==200 for t in d['enrollments']),transactions=d['payment']['transactions'],
                        enroll_ms_median=float(np.median(times['/api/demo/enroll'])),identify_ms_median=float(np.median(times['/api/demo/identify'])),identify_ms_p95=float(np.percentile(times['/api/demo/identify'],95)),
                        identify_cold_ms=times['/api/demo/identify'][0],identify_warm_median_ms=float(np.median(times['/api/demo/identify'][1:])),
                        stages=stages,compressed_gallery_bytes=sum(p.stat().st_size for p in disk)))
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Demo v6: ROI checks and speed evaluation</title><style>body{max-width:1150px;margin:30px auto;padding:20px;background:#f5f7f8;font:17px/1.7 system-ui;color:#19333c}img{max-width:100%}table{width:100%;background:white}td{padding:10px;border-bottom:1px solid #ccc}pre{white-space:pre-wrap;font-size:14px}a{color:#006c82}</style><h1>Demo v6: removing redundant work without changing recognition scores</h1>
<p>2026-10-28 · Local Windows HTTP replay from historical originals. Final new- and old-camera runs were sequential, with no other heavy evaluation for this task. Not deployed to Pi.</p>
<h2>End-to-end outcomes and timing</h2>'''
doc+=table([['Device','Recognition','Enrollment','Simulated payment','Median five-image enrollment per person','Median query','Query p95']]+[[r['cohort'],f'{r["correct"]}/{r["total"]}',r['enrolled'],r['transactions'],f'{r["enroll_ms_median"]/1000:.2f}s',f'{r["identify_ms_median"]/1000:.2f}s',f'{r["identify_ms_p95"]/1000:.2f}s'] for r in metrics])
doc+='<p>The earlier v5 new-camera replay had a 26.98 s median enrollment and 7.09 s median query while other audits ran. Do not infer a controlled speedup ratio. The latest measurements include localization, extraction, template reads and HTTP recognition from historical originals, but not live capture, preview contention or Pi CPU cost.</p>'
doc+='<h2>Changes</h2><ol><li>Enrollment computes only gallery descriptors, omitting query candidates and native PNG storage.</li><li>Queries retain every spatially valid candidate and use at most two workers. Resolution and difficult images are retained.</li><li>Decode each query once. Enrollment caches only compact matching data (64 MiB limit); replacement, re-enrollment, metadata changes and deletion invalidate the cache.</li><li>Separate role checks prevent an enrollment-only template from being used as a query. Template versions stay isolated; re-enrolling an existing account does not reset its balance.</li></ol>'
doc+='<h2>Accuracy and determinism</h2><p>Parallel and serial extraction agreed byte for byte on all 80 query images except version fields. All 80 enrollment descriptors matched v5; all 3,120 non-self, same-device pair distances were identical. Both devices retained 20/20 on each of 112 fixed splits. Regression checks: 134 passed, 2 skipped; the pre-existing legacy import failure in test_existing_pipeline.py was excluded.</p>'
doc+='<h2>The small ROI in the illustration</h2><p>The spatial check excluded wall candidates 3 and 4. Across 9 images it removed 48 descriptor views without changing pair scores. The primary ROI may still be too small; this is not a replacement localizer. Purple marks the region actually scored, green the automatic primary box, and orange a candidate.</p><p><a href="report-v5.html">Actual aligned region and candidate checks for each contributing template</a></p>'
doc+='<h2>Enable the optional demo</h2><pre>python debug_ui.py --enable-recognition --roi-mode pklnet --demo-matcher FastCCDemo-v6</pre><p>Old templates require re-enrollment. The capture-only service, default DoN and network remain unchanged. Simulated payment still requires manual name confirmation. These two-person development data were repeatedly inspected; they establish neither independent-session accuracy, unknown-hand rejection nor live camera performance.</p><h2>Stage timings and evidence</h2><pre>'+html.escape(json.dumps(metrics,indent=2))+'</pre><ul>'
for p in ['speed-v5/prepared-parity-parallel.json','speed-v5/parallel-extraction.json','speed-v5/thread-profile.json','speed-v5/parallel-profile.json','runtime-v5/results.json','http-v6-final-new/summary.json','http-v6-final-old/summary.json']:
    doc+=f'<li><a href="{p}">{p}</a></li>'
doc+='</ul></html>'
(base/'speed-v5/final-metrics.json').write_text(json.dumps(metrics,indent=2));(base/'report-v6.html').write_text(doc,encoding='utf-8');print(json.dumps(metrics,indent=2));print(base/'report-v6.html')
