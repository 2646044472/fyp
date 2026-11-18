"""Publish verified v3 development results without replacing historical v2 evidence."""
import hashlib
import html
import json
from pathlib import Path
import sys

root=Path(sys.argv[1]); out=root/'single-device'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
records=read(root/'stability/records.json')
assert len(records)==80 and all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
lookup={r['sample']:r for r in records}
cases=read(out/'runtime-v3/results.json')
for c in cases:
    gallery={s for samples in c['gallery'].values() for s in samples}
    assert len(c['trials'])==20
    for t in c['trials']:
        assert t['sample'] not in gallery
        assert all(lookup[s]['cohort']==lookup[t['sample']]['cohort'] for s in gallery)
summary=[r for r in read(out/'runtime-v3/summary.json') if r['method']=='registered_best2']
http=[]
for cohort in ['new','old']:
    r=read(out/f'http-v3-{cohort}/summary.json')
    assert r['demo_matcher']=='FastCCMultiROI-v3' and r['originals_unchanged']
    d=r['demo'];correct=sum(t['result'].get('user_id')==t['identity'].replace(':','-') for t in d['probes'])
    http.append(dict(cohort=cohort,correct=correct,total=len(d['probes']),enrollments=sum(t['http_status']==200 for t in d['enrollments']),transactions=d['payment']['transactions']))
def table(rows):
    return '<table>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r)+'</tr>' for r in rows)+'</table>'
doc='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Image-level failures and the multi-ROI fix</title><style>body{font:17px/1.7 system-ui;background:#f3f5f6;color:#19333c;margin:30px auto;max-width:1150px;padding:20px}img{max-width:100%}td{padding:10px;border-bottom:1px solid #ccc}table{background:white;width:100%}a{color:#006c82}</style>
<h1>Undersized crops near the finger bases caused different regions of the same palm to be compared</h1>
<p>Same-device data only. All 80 original image hashes were unchanged, and all queries were separated from enrollment. Green denotes the automatic box; orange is a development reference, not independent ground truth.</p>
<h2>Right hand, image 8: missing principal palm lines</h2><p>Principal lines are visible in the original, but the automatic crop covers only a small area near the finger bases. Expanding query alignment reduced errors for this image from 51/63 to 0/63 across 112 fixed splits, consistent with insufficient coverage.</p><img src="image-review/bankey-right.jpg">
<h2>Left hand, image 1: the most difficult remaining case</h2><p>The box shrank toward the finger bases. Local features matched reliably only against the second enrollment image, so changing the gallery could cause failure. Multi-ROI still failed on 10/51 appearances; these are repeated splits of one image.</p><img src="image-review/stephen-left.jpg">
<h2>Right hand, image 5: an enlarged crop does not establish camera defocus</h2><p>Principal lines remained in native pixels. Enlarging a small box made grain and blur more apparent. The earlier algorithm discarded a preferable gamma localization because its box did not overlap the other prediction. Retaining both valid candidates and checking texture eliminated 53/53 prior errors on this image. Backlighting and low contrast also occurred in successful images.</p><img src="image-review/stephen-right-native.jpg">
<h2>Runtime retest</h2><p>FastCCMultiROI-v3 keeps original and gamma candidates, uses geometry to verify texture correspondences, and samples once from native gray pixels. Default DoN was unchanged; not deployed to Pi.</p>'''
doc+=table([['Data','Split','Minimum','Maximum','Mean /20']]+[[r['cohort'],r['split'],r['min'],r['max'],r['mean']] for r in summary])
doc+='<h2>Local HTTP replay from historical originals</h2>'+table([['Data','Correct identifications','Queries','Successful enrollments','Simulated transactions']]+[list(r.values()) for r in http])
doc+='<p>Development data from the same two people: 100 splits are not 100 independent captures. No live-camera/Pi validation. Uncompressed templates used about 8.16 MB/image and local median matching time was 26.8 ms per pair, not Pi performance.</p><h2>Additional controls</h2>'
for folder in ['wide-context','dense-alignment','roi-hypotheses','coarse-structure','wider-field','palm-coverage','grid-alignment','window-hypotheses','window-coarse-union']:
    p=out/folder/'summary.json'
    if p.exists():
        doc+=f'<p><a href="{folder}/summary.json">{folder} All results</a></p>'
        if folder in ['window-hypotheses','window-coarse-union']:doc+=table([[r['cohort'],r['split'],r['min'],r['max'],r['mean']] for r in read(p)])
doc+='<p>Additional windows resolved the remaining errors on left-hand image 1. The sole remaining window error involved right-hand image 6 in seed 2026102984: same-hand distance 0.37354 vs 0.37061 for the other hand. Uniformly combining the computed coarse descriptor alignment candidates gave 20/20 in each of 112 fixed splits per device. All images used identical rules without identity-specific selection. Offline only; not integrated into v3 or deployed to Pi. Independent-session generalization is untested.</p>'
doc+='<p><a href="report.html">Historical v2 report</a> · <a href="runtime-v3/results.json">All v3 per-sample results</a> · <a href="http-v3-new/summary.json">New-camera HTTP replay</a> · <a href="http-v3-old/summary.json">Old-camera HTTP replay</a></p></html>'
(out/'report-v3.html').write_text(doc,encoding='utf-8')
(out/'verified-v3.json').write_text(json.dumps(dict(original_hashes_verified=80,split_integrity=True,http=http),indent=2))
print(json.dumps(http));print(out/'report-v3.html')
