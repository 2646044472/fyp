"""Summarize saved Pi v24 development runs without selecting or dropping queries."""
import argparse
import html
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    rows=[];details=[]
    for path in sorted(args.evidence.glob('ready-quality-v24-*.json')):
        value=json.loads(path.read_text())
        for run in value['passes']:
            rows.append([path.stem,run['label'],f"{run['correct']}/{run['n']}",
                f"{run['correct_within_2_5s']}/{run['n']}",f"{run['median_ms']/1000:.3f}",f"{run['max_ms']/1000:.3f}"])
        details.append(dict(run=path.stem,startup_s=value['startup_s'],
            queue_correct=value['queue_correct'],queue_seconds=[q['ms']/1000 for q in value['concurrent_requests']]))
    for path in sorted(args.evidence.glob('quality-v24-fresh-*/summary.json')):
        value=json.loads(path.read_text());run=value['identify']
        rows.append([path.parent.name,'Re-enrollment',f"{value['correct']}/{value['total']}",
            f"{value['correct_within_2_5s']}/{value['total']}",f"{run['median_ms']/1000:.3f}",f"{run['max_ms']/1000:.3f}"])
        details.append(dict(run=path.parent.name,enrollment_timing=value['enroll'],
            simulated_transactions=value['payment']['transactions'],
            originals_unchanged=value['originals_unchanged'],slow_queries=value['over_2s']))
    for path in sorted(args.evidence.glob('quality-v24-on-site-*/result.json')):
        value=json.loads(path.read_text())
        details.append(dict(run=path.parent.name,generic_model_startup_ms=value['generic_model_startup_ms'],
            app_recreation_ms=value.get('app_recreation_ms'),
            fresh_process_restart=value.get('fresh_process_restart'),
            camera_tested=value['camera_tested'],query_warmup=value['query_warmup'],
            records=[dict(identity=r['identity'],enrollment_http_ms=r['enrollment_http_ms'],
                last_frame_read_to_ready_ms=r['last_frame_read_to_ready_ms'],
                first_query_ms=r['first_query']['ms'],correct=r['first_query']['correct'],
                per_frame_ms=[e['ms'] for e in r['events'] if e['stage']=='frame_and_features'],
                nested_stage_totals_ms={stage:sum(e['ms'] for e in r['events'] if e['stage']==stage)
                    for stage in sorted({e['stage'] for e in r['events']})}) for r in value['records']]))
    table='<table><tr>'+''.join(f'<th>{s}</th>' for s in ['Experiment','Round','Correct','Correct within 2.5 s','Median (s)','Maximum (s)'])+'</tr>'
    table+=''.join('<tr>'+''.join(f'<td>{html.escape(str(s))}</td>' for s in row)+'</tr>' for row in rows)+'</table>'
    content='''<!doctype html><html lang="zh"><meta charset="utf-8"><title>v24 measurements on local captures</title>
<style>body{font:16px/1.65 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#182534}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border:1px solid #ccd5df;text-align:left}th{background:#eaf0f6}pre{white-space:pre-wrap;overflow-wrap:anywhere}h1{font-size:28px}</style>
<h1>v24 checkpoint: data captured on the Raspberry Pi</h1><p>2026-10-29 · Pi 5 only · Isolated test environment · Production v6 unchanged</p>
<p>Timing includes loading the original image, preprocessing, ROI extraction, features, retrieval/registration, scoring and the local HTTP response. Camera capture and external upload are excluded. Each query was recomputed without caching recognition results.</p>
<h2>Full results, including timeouts</h2>'''+table+'''
<h2>Findings</h2><p>All 80 queries across four fresh enrollments were correct; 77 finished within 2.5 s. The reverse enrollment split on the new camera exposed a 13.886 s tail. Early search was still uncertain at about 2.59 s; full fallback took another 11.30 s. Localization alone took about 2 s for the other two late queries. Lowering confidence requirements is unsafe: weighted fast scoring ranked the wrong identity first for the slowest query, and the original gate correctly rejected that shortcut.</p>
<p>Incremental enrollment reused alignments for unchanged identities and used lossless compression level 1. Fourth-identity enrollment fell from 51.338 to 47.434 s; time from reading the last image to ready fell from 20.193 to 16.235 s. All scores and routes matched across 224 splits and 4,480 queries. The full index is still rebuilt; first-query latency for a single identity and the difficult reverse split remain unresolved.</p>
<h2>Changes and limitations</h2><p>Parallel execution of two independent SIFT paths and batched group medians for correspondences preserve the original mathematics. New quality-weighted scoring reduces the influence of weak filter responses and convolution boundaries. It runs only if the existing early path is uncertain, then falls back to full search if necessary. This defines a new distance, not an equivalent speedup of ordinary Hamming distance. Scores are replaced as a group, never mixed across metrics.</p>
<p>All 224 fixed development splits scored 20/20, but reuse the same 80 images and do not provide independent generalization evidence. Numeric thresholds were not relaxed; rejecting unknown identities with the new distance still needs independent calibration. Public datasets were not used for this optimization; previously inspected holdout data were not used to select parameters.</p>
<p>Swapping enrollment and query photos is still a same-device test. Capacity for 40 people, independent capture sessions and live capture have not been validated. Development-set gains do not resolve the earlier holdout cohort’s 10.681 s tail. Queuing and startup are reported separately.</p>
<p>On-site enrollment processes each image before reading or capturing the next, then prepares the gallery index after all five. Re-enrollment timing includes this computation, not actual camera capture or hand positioning. New identities cannot have templates prepared in advance: a two-second query does not mean two-second enrollment. The on-site run below enrolled each identity into an initially empty gallery and immediately issued its first query. Generic model warm-up used only zero-valued inputs.</p>
<h2>Startup, queuing, re-enrollment and slow-query details</h2><p>All *_ms values are in milliseconds.</p><pre>'''+html.escape(json.dumps(details,ensure_ascii=False,indent=2))+'</pre></html>'
    args.output.write_text(content,encoding='utf-8')
    print(json.dumps(rows,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
