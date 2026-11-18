"""Render the completed fixed-cohort Pi speed audit without hiding slow queries."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args();root=args.root
    def read(path):return json.loads((root/path).read_text(encoding='utf-8'))
    runs={c:read(f'pi-staged-{c}-summary.json') for c in ('new','old')}
    ready={c:read(f'ready-staged-{c}.json') for c in runs}
    cases=read('staged-final-all-splits/results.json')
    assert len(cases)==224, 'Do not present an incomplete audit as complete'
    integrity=read('final-data-integrity.json')
    baseline=json.loads((root.parent/'pi5-v6-20261028/comparison.json').read_text())['runs']
    labels={'new':'New camera','old':'Old camera'}
    escape=lambda value:html.escape(str(value))
    def table(headers,rows):
        return '<table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
    seconds=lambda ms:f'{ms/1000:.3f} s'
    rows=[]
    for c,r in runs.items():
        rows.append([labels[c],f"{r['correct']}/{r['total']}",f"{r['correct_within_2s']}/{r['total']}",
            seconds(baseline['final-'+c]['identify']['median_ms'])+' → '+seconds(r['identify']['median_ms']),
            seconds(r['identify']['p95_ms']),seconds(r['identify']['max_ms'])])
    body='<h1>Raspberry Pi 5: recognition speed and accuracy</h1><p>2026-10-29 · v10 staged retrieval plus native ARM registration · Live service remains v6</p>'
    passed=all(c['correct']==c['total'] for c in cases) and all(r['correct_within_2s']==r['total'] for r in runs.values())
    body+='<div class="notice">'+('Historical-data speed checks passed; independent validation remains outstanding.' if passed else 'The goal of every query within 2 seconds with no recognition loss is still unmet. A better median does not eliminate the difficult tail.')+'</div>'
    body+='<h2>Full HTTP workflow</h2>'+table(['Data','Correct','Correct within 2 s','Median recognition time: v6 → experimental','P95','Maximum'],rows)
    body+='<p>Includes localization, extraction, matching and the HTTP round trip from originals. Isolated simulated accounts were used; file replay replaced capture, so live-preview contention remains untested.</p>'
    body+='<h2>Fixed-split regression and overfitting checks</h2>'+table(['Data','Completed splits','Range of correct counts per split'],[[labels[c],sum(x['case'].startswith(c+'_') for x in cases),str(min(x['correct'] for x in cases if x['case'].startswith(c+'_')))+'–'+str(max(x['correct'] for x in cases if x['case'].startswith(c+'_')))+'/20'] for c in runs])
    body+='<p>These splits reuse the same 80 development images and do not measure independent accuracy. Reserved old-camera data from 4 people (80 images) remained unused for matching or tuning. No identity exceptions, discarded images or relaxed criteria.</p>'
    body+='<p>Original development-image check:'+escape(integrity['development_unchanged'])+'; reserved archive check:'+escape(integrity['reserved_unchanged'])+'。</p>'
    cold=[]
    for c,r in ready.items():
        for p in r['passes']:
            cold.append([labels[c],p['label'],f"{p['correct']}/{p['n']}",f"{p['correct_within_2s']}/{p['n']}",seconds(p['median_ms']),seconds(p['p95_ms']),seconds(p['first_ms'])])
    body+='<h2>After restart and on repeated queries</h2>'+table(['Data','Round','Correct','Correct within 2 s','Median','P95','First in this round'],cold)
    body+='<p>Startup index loading is separate: new-camera data '+f"{ready['new']['startup_s']:.3f}"+'  s, old-camera data '+f"{ready['old']['startup_s']:.3f}"+'  s. No query identity was precomputed; each round processed originals again.</p>'
    body+='<h2>All full-workflow queries exceeding 2 seconds</h2>'+table(['Data','Sample','Elapsed time','Route'],[[labels[c],q['sample'],seconds(q['ms']),q['route']] for c,r in runs.items() for q in r['over_2s']])
    body+='<h2>Enrollment, resources and interaction</h2>'+table(['Data','Median five-image enrollment','Peak RSS','Two concurrent requests'],[[labels[c],seconds(r['enroll']['median_ms']),f"{r['peak_rss_bytes']/1024**3:.2f} GiB",' / '.join(seconds(q['ms']) for q in ready[c]['concurrent_requests'])] for c,r in runs.items()])
    body+='<p>Eight simulated payments across new and old data, cancellation and duplicate-confirmation checks passed. Concurrent queries returned the correct identities without increasing the transaction count. Python: 151 passed; 2 PalmIR/ONNX tests skipped for missing dependencies; 5 legacy API tests explicitly excluded. Frontend interaction checks passed.</p>'
    body+='<h2>Why a long tail remains</h2><p>Easy images are resolved by pose or local registration; ambiguous ones expand search and retain the original exhaustive fallback. Exhaustive search still requires repeated localization and substantial registration. Those costs cannot be removed from timing or confidence reduced to meet 2 seconds.</p>'
    body+='<p>All 4,760 ARM registrations matched the reference. Faster v7/v8 results with missed matches were retained. Heatmap pruning saved only about 10 ms and was not integrated. Reserved data were not used for repeated parameter selection.</p>'
    if (root/'center-summary.json').exists():
        center=read('center-summary.json')
        body+='<h2>Aspect-ratio preprocessing control: not adopted</h2><p>Centered padding passed geometry checks on new images, but average correct counts over all 112 new-camera splits at the same matching stage fell from '+f"{center['new_legacy_baseline']['mean_correct']:.3f}"+' /20 to '+f"{center['new_centered_legacy']['mean_correct']:.3f}"+' /20. Both had a minimum of 16/20. The existing preprocessing was not replaced for isolated gains. This is not accuracy for a complete centered-padding pipeline.</p>'
    body+='<p><a href="pi-staged-new-summary.json">New-camera raw statistics</a> · <a href="pi-staged-old-summary.json">Old-camera raw statistics</a> · <a href="staged-final-all-splits/summary.json">All split summaries</a></p>'
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pi 5 recognition acceleration checks</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f4f6fa;color:#182331;margin:0}main{max-width:1150px;margin:30px auto;background:white;padding:32px;border-radius:16px}h1{font-size:30px}h2{font-size:21px;margin-top:30px}p{color:#465568}.notice{background:#fff1d4;border-left:5px solid #c98418;padding:16px;font-weight:600}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #e2e7ef;text-align:left;overflow-wrap:anywhere}th{background:#eef3f9}a{color:#1764a1}@media(max-width:800px){main{margin:0;padding:16px}table{font-size:12px}th,td{padding:5px}}</style><main>'+body+'</main></html>'
    output=root/'report.html';output.write_text(page,encoding='utf-8');print(output.resolve())


if __name__=='__main__':main()
