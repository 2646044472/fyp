"""Summarize actual unchanged-result Pi profiles without summing nested timers."""
import argparse,hashlib,html,json
from collections import Counter
from pathlib import Path
import numpy as np


def covered_ms(events,labels):
    intervals=sorted((e['start_ms'],e['start_ms']+e['ms']) for e in events if e['label'] in labels)
    total=0.;end=-float('inf')
    for left,right in intervals:
        if right>end:total+=right-max(left,end);end=right
    return total


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('diagnosis',type=Path);p.add_argument('reference',type=Path);args=p.parse_args()
    root=args.diagnosis;protocol=json.loads((root/'protocol.json').read_text());assert protocol['complete'] and protocol['source_files_unchanged']
    assert hashlib.sha256(args.reference.read_bytes()).hexdigest()==protocol['source_results_sha256']
    data=json.loads(args.reference.read_text());assert data['complete']
    reference={(r['case'],q['sample']):q for r in data['runs'] for q in r['queries']}
    profiles=[(r['case'],json.loads((root/r['case']/'profile.json').read_text())) for r in protocol['runs']]
    assert all(p['complete'] and p['transactions_unchanged'] and p['model_primed'] for c,p in profiles)
    rows=[];power=[];ready=[]
    for case,profile in profiles:
        power.append(profile['preflight']['get_throttled']);ready.append([case,profile['initialization_ready_ms']/1000])
        for q in profile['queries']:
            assert q['reference_equal'] and q['correct']==reference[case,q['sample']]['correct']
            power.append(q['power_after']['get_throttled']);events=q['events']
            complete=[e for e in events if e['label']=='complete_hypotheses'];assert len(complete)==1
            gates=[g for g in q['gates'] if g['ms']<=2500];last=gates[-1] if gates else None
            latest=min(last['scores'],key=last['scores'].get) if last else None
            rows.append(dict(case=case,sample=q['sample'],repeat=q['repeat'],correct=q['correct'],http_ms=q['http_ms'],
                capture_ms=q['result']['timing_ms']['capture_and_extract'],early_elapsed_ms=complete[0]['start_ms'],
                additional_localization_ms=covered_ms(events,{'complete_hypotheses'}),
                complete_features_ms=covered_ms(events,{'complete_features'}),
                full_matching_ms=covered_ms(events,{'complete_identity_match'}),
                native_active_ms=covered_ms(events,{'native_correspondences','native_registration'}),
                confident_gate_before_2500=any(g['confident'] for g in gates),
                latest_gate_before_2500_identity=latest,
                latest_gate_before_2500_correct=latest==reference[case,q['sample']]['identity'].replace(':','-'),
                latest_gate_before_2500_ms=last['ms'] if last else None))
    assert set(power)=={'throttled=0x0'}
    values=list(reference.values());times=[q['ms'] for q in values]
    summary=dict(reference_correct=sum(q['correct'] for q in values),reference_total=len(values),
        reference_timely=sum(q['correct'] and q['ms']<=2500 for q in values),
        reference_p95_ms=float(np.percentile(times,95)),reference_max_ms=max(times),
        statuses=dict(Counter(q['result']['status'] for q in values)),
        wrong_identity_matches=sum(not q['correct'] and q['result']['status']=='MATCH' for q in values),
        explicit_rejects=sum(q['result']['status']=='REJECT' for q in values),
        unknown_person_far=None,verification_frr=None,ready_seconds=ready,profiles=rows,
        diagnosis_does_not_change_algorithm=True,full_reference_unchanged=True,power_flags=sorted(set(power)))
    (root/'summary.json').write_text(json.dumps(summary,indent=2))
    def table(headers,records):
        return '<div class="scroll"><table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>' for v in headers)+'</tr>'+''.join(
            '<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in row)+'</tr>' for row in records)+'</table></div>'
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><title>What blocks v26 on its slowest query and misidentifications</title>
<style>body{font:16px/1.65 system-ui;max-width:1500px;margin:32px auto;padding:0 20px;color:#203044}h1{font-size:28px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px;border:1px solid #ccd5df;text-align:left}th{background:#edf2f8;white-space:nowrap}.scroll{overflow:auto}.notice{background:#fff3dd;border-left:4px solid #a86a16;padding:14px}code{overflow-wrap:anywhere}</style>
<h1>v26: diagnosing the longest tail and all four misidentifications</h1><p>2026-10-30 · Stage timings from actual Pi HTTP requests · No changes to algorithm, thresholds, labels or deployment</p>
<p class="notice">No new speedup qualified. The full v26 run remains 164/168 correct, 146/168 correct within 2.5 s, P95 6.019 s and maximum 15.225 s. Only the slowest query and all misidentifications were repeated twice here; this is not a new 168-query acceptance run.</p>'''
    text+='<h2>Query timing breakdown</h2><p>Time before fallback already includes initial localization and extraction. Supplemental localization, fallback features and fallback matching are measured as unions of event intervals. Native matching active time is also a union and overlaps the other stages; do not add it again. Instrumentation adds overhead, so use the full v26 replay for deadline compliance.</p>'
    text+=table(['Group','Sample','Repeat','Correct','Initial localization and extraction (s)','Elapsed before fallback (s)','Supplemental localization (s)','Fallback features (s)','Fallback matching (s)','Native matching active (overlapping, s)','Total HTTP time (s)'],[
        [q['case'],q['sample'],q['repeat'],q['correct'],*[f"{q[k]/1000:.3f}" for k in
         ('capture_ms','early_elapsed_ms','additional_localization_ms','complete_features_ms','full_matching_ms','native_active_ms','http_ms')]] for q in rows])
    text+='<h2>Initialization and readiness measured separately</h2><p>This measures loading an enrolled gallery, indexing, loading and warming the primary localization model until the app accepts queries. The supplemental window model is still loaded lazily on first use. No identities were re-enrolled: this is not on-site enrollment time and is excluded from the query timings above.</p>'
    text+=table(['Group','Initialization to ready (s)'],[[c,f'{s:.3f}'] for c,s in ready])
    text+='<p>For the hardest image, the first supplemental localization call took about 1.364 s on the first pass and 0.506 s on the second, a difference of about 0.86 s. Prewarming might address that part, but was not independently tested. The second request still took about 14.31 s, nowhere near 2.5 s.</p>'
    text+='<h2>Evidence available before 2.5 s</h2>'+table(['Group','Sample','Repeat','Met the reliable early-return criteria','Leading identity in final round before deadline','Leading identity correct'],[
        [q['case'],q['sample'],q['repeat'],q['confident_gate_before_2500'],q['latest_gate_before_2500_identity'],q['latest_gate_before_2500_correct']] for q in rows])
    failures=[q for q in values if not q['correct']]
    text+='<h2>Misidentification versus rejection</h2><p>All 168 inputs belonged to enrolled identities and all returned MATCH. Four identities were wrong and none returned an explicit REJECT. Zero explicit rejections do not establish a verification FRR of 0%, and 4/168 is not a stranger FAR. Neither was measured; there were no stranger trials. The final DemoFlow gallery fallback ranks a closed set with threshold 1.0 and no minimum gap, so weak evidence can still return the top identity. That policy was unchanged.</p>'
    text+=table(['Sample','Returned distance','Runner-up distance','Gap'],[[q['sample'],f"{q['result']['score']:.6f}",f"{q['result']['second_score']:.6f}",f"{q['result']['second_score']-q['result']['score']:.6f}"] for q in failures])
    text+='<h2>Remaining blockers and criteria for the next experiment</h2><p>The hardest query did not meet the original reliable early-return criteria within 2.5 s. Supplemental localization, feature construction and matching each took seconds in full fallback. Previously inspected registered crops also lacked sufficiently strong early evidence. Optimizing only the final distance calculation cannot recover the preceding seconds; returning the current leader at 2.5 s would change the decision rather than preserve accuracy. This does not rule out future methods, but no small change has been validated against both the tail and the four errors.</p>'
    text+='<p>A new experiment needs a distinct reproducible ROI or representation mechanism. Without relabeling, changing thresholds, removing failures or file-specific tuning, it must first pass regression checks on all exposed data, then correctly identify the hardest image within 2.5 s on the Pi with no new misidentifications. Report deadline compliance, P95 and maximum for the full set. Independent new sessions and unenrolled people are still needed; repeated splits cannot substitute. Do not repeat the rejected neighborhood, SIMD or relaxed-threshold approaches.</p>'
    text+='<p>Across ten diagnostic requests, identity, score, runner-up, status and route matched the original v26 results, including the four errors. Simulated transaction counts and source files were unchanged; all power flags were 0x0. <a href="../compnet-v26-pi-20261030/report.html">Full v26 replay and actual ROI comparison</a>.</p></html>'
    (root/'report.html').write_text(text,encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in ('profiles','ready_seconds')}))


if __name__=='__main__':main()
