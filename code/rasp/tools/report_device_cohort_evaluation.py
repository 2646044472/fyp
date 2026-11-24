"""Render all frozen device cohorts and preserve every error/latency denominator."""
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from report_six_person_evaluation import esc,seconds,table,summarize


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();data=json.loads(args.evidence.read_text());protocol=data['protocol']
    feature_path=args.evidence.parent/'feature-diagnostics.json'
    diagnostic_rows={}
    if feature_path.is_file():
        feature_data=json.loads(feature_path.read_text(encoding='utf-8'))
        assert feature_data.get('complete') and feature_data.get('all_reference_equal')
        diagnostic_rows={(q['case'],q['sample']):q for q in feature_data['queries']}
    cases={c['name']:c for c in protocol['cases']}
    device_counts=protocol.get('device_images',{'old-camera':110,'new-camera':60})
    query_counts={device:sorted({len(c['queries']) for c in protocol['cases'] if c['device']==device}) for device in device_counts}
    expected_queries=sum(len(c['queries']) for c in protocol['cases'])
    status='Complete' if data.get('complete') else 'In progress: some groups are incomplete'
    chunks=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Seven-person within-device end-to-end experiment</title>',
      '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:1450px;margin:32px auto;padding:0 22px;color:#182637}h1{font-size:29px}h2{margin-top:32px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border:1px solid #cdd6e1;text-align:left;vertical-align:top}th{background:#edf2f8;white-space:nowrap}.notice{padding:12px 16px;border-left:4px solid #ac6914;background:#fff6e7}.failure{border:1px solid #d0d8e1;border-radius:8px;margin:16px 0;padding:16px}.failure img{max-width:100%;height:auto}code{overflow-wrap:anywhere}small{color:#526276}</style>',
      '<h1>Frozen end-to-end pipeline: seven people, separate device galleries and error analysis</h1>',
      '<p>2026-10-29 · Raspberry Pi 5 only · Wi-Fi management · '+status+'</p>',
      '<p class="notice">Frozen originals: '+str(protocol['images'])+'; old camera: '+str(device_counts['old-camera'])+'; new camera: '+str(device_counts['new-camera'])+'. Two people appear on both devices; counting unique people gives '+str(protocol['people'])+'. Matching galleries were always built separately by device.</p>',
      '<p>Frozen recognition version: <code>'+esc(protocol['matcher'])+'</code>; algorithm snapshot commit: <code>'+esc(protocol['frozen_commit'])+'</code>. The protocol fixes hashes for all recognition source and test tools. These results were not used for tuning.</p>',
      '<p>Each device enrolled either the earliest or latest five images per identity and queried all remaining images. Queries per old-camera group: '+esc(query_counts['old-camera'])+'; per new-camera group: '+esc(query_counts['new-camera'])+'; total: '+str(expected_queries)+' main queries. Each group started with an empty gallery, with no cross-device enrollment/query matching. Originals removed by the user were excluded under the protocol. Historical results are not rewritten as algorithm improvements: the earlier 120-image experiment remains 62/65.</p>',
      '<h2>Full main-query results</h2><p>Correct requires a successful MATCH for the true palm identity. Correct within 2.5 s additionally requires the full HTTP request to finish within 2500 ms. All failures, misidentifications, localization errors and timeouts are retained.</p>']
    summaries=[]
    for run in data['runs']:
        q=run['queries'];s=run.get('summary',{})
        summaries.append([run['case'],f"{len(q)}/{len(cases[run['case']]['queries'])}"]+summarize(q)+[
            seconds(s.get('p95_ms')),sum(e['result'].get('recognition_ready') is True for e in run['enrollments'])])
    chunks.append(table(['Group','Progress','Correct','Correct within 2.5 s','P50 including errors (s)','Maximum (s)','P95 (s)','Ready identities'],summaries))
    chunks.append('<p>Each query rereads and recomputes the original. Timing includes preprocessing, ROI extraction, features, retrieval/registration, scoring and local Pi HTTP response. Wi-Fi was used for management. Capture, hand placement, external upload, enrollment and startup waits are separate.</p>')
    for run in data['runs']:
        case=cases[run['case']]
        chunks.append('<h2>'+esc(run['case'])+': results by identity</h2>')
        groups=defaultdict(list)
        for q in run['queries']:groups[q['identity']].append(q)
        chunks.append(table(['Identity','Correct','Correct within 2.5 s','P50 (s)','Maximum (s)'],[[u]+summarize(groups[u]) for u in case['enrollment']]))
        chunks.append('<h2>'+esc(run['case'])+': enrollment → ready → immediate first query</h2>')
        immediate={q['identity']:q for q in run['immediate_queries']};registration=[]
        for e in run['enrollments']:
            q=immediate.get(e['identity']);stage=lambda label:sum(v['ms'] for v in e['events'] if v['stage']==label)
            registration.append([e['identity'],e['http_status'],e['result'].get('recognition_ready'),seconds(e['ms']),
              seconds(e.get('last_frame_read_to_response_ms')),seconds(stage('primary_roi')),seconds(stage('alternate_roi')),
              seconds(stage('complete_features')),seconds(stage('template_save')),seconds(stage('prepare_enrollment')),
              seconds(stage('descriptor_index')),seconds(stage('index_and_enrollment_links')),
              seconds(q['ms']) if q else '—',q['correct'] if q else '—'])
        chunks.append(table(['Identity','HTTP','ready','Total enrollment (s)','After final frame read (s)','Primary ROI (s)','Backup ROI (s)','Full features (s)','Save (s)','Template preparation (s)','Full index (s)','Index + alignment (s)','Immediate first query (s)','First query correct'],registration))
        chunks.append('<p>Nested or parallel stages are not additive. Time after reading the last frame is from file replay, not camera capture latency. The immediate first query is outside the main denominator; the same original is recomputed when queried in the main run.</p>')
        startup=run['startup'];chunks.append('<p>Generic model startup: '+seconds(startup['generic_model_startup_ms'])+' s; empty-gallery app initialization: '+seconds(startup['app_and_gallery_ms'])+' s. Only zero-valued inputs were used for model warm-up.</p>')
        restart=run.get('restart')
        if restart:chunks.append('<p>Independent fresh process: model startup '+seconds(restart['startup']['generic_model_startup_ms'])+' s; app/gallery rebuild '+seconds(restart['startup']['app_and_gallery_ms'])+' s; first query '+seconds(restart['first_query']['ms'])+' s; correct = '+esc(restart['first_query']['correct'])+'. This was a process restart, not a Pi reboot.</p>')
        if run.get('summary'):chunks.append('<p>Simulated transactions: '+str(run['summary']['payment_transactions'])+'; all identities passed confirmation, duplicate blocking, cancellation and post-cancellation confirmation checks: '+esc(run['summary']['payment_checks_complete'])+'.</p>')
        chunks.append('<h2>'+esc(run['case'])+': per-query error records</h2>')
        failures=[q for q in run['queries'] if not q['correct']]
        if not failures:chunks.append('<p>No errors in completed queries so far; incomplete groups cannot yet be called all-correct.</p>')
        for q in failures:
            result=q['result'];scores=q.get('diagnostics',{}).get('scores',{})
            ranked=sorted(scores.items(),key=lambda item:item[1]);truth=q['identity'].replace(':','-')
            rank=next((i+1 for i,(u,_) in enumerate(ranked) if u==truth),None)
            margin=(result['second_score']-result['score']) if result.get('second_score') is not None and result.get('score') is not None else None
            chunks.append('<div class="failure"><p><b>'+esc(q['sample'])+'</b><br>True: '+esc(q['identity'])+'; predicted: '+esc(result.get('user_id'))+'; '+seconds(q['ms'])+' s; route: '+esc(result.get('recognition_route'))+'.</p>')
            chunks.append('<p>True-identity rank: '+esc(rank)+'; best/runner-up score gap: '+esc(None if margin is None else round(margin,6))+'. Labels retain the active source records and were not changed to match recognition results.</p>')
            overlay=args.output.parent/'failure-images'/(run['case']+'-'+q['sample']+'.jpg')
            if overlay.is_file():chunks.append('<img src="'+esc(str(overlay.relative_to(args.output.parent)).replace('\\','/'))+'" alt="Original image and actual Pi ROI">')
            elif q.get('roi_artifact') and (args.output.parent/q['roi_artifact']).is_file():chunks.append('<img width="256" src="'+esc(q['roi_artifact'])+'" alt="Actual primary Pi ROI">')
            chunks.append(table(['Candidate identity','Score (lower is better)'],[[u,f'{value:.6f}'+(' ← true identity' if u==truth else '')] for u,value in ranked]))
            detail=diagnostic_rows.get((run['case'],q['sample']))
            if detail:
                assert detail['reference_equal'] and detail.get('roi_byte_equal')
                attempts=[r for r in detail['registrations'] if r['kind']=='registration']
                counts=Counter(r['reason'] for r in attempts)
                true_attempts=[r for r in attempts if (r.get('target') or {}).get('identity')==truth]
                true_counts=Counter(r['reason'] for r in true_attempts)
                labels={'accepted':'Registration passed','too_few_descriptors':'Fewer than four descriptors',
                    'too_few_mutual_pairs':'Fewer than four mutual matches','ransac_or_geometric_guard':'RANSAC or geometry constraints failed'}
                chunks.append('<p>Diagnostic reruns matched baseline identities, scores, routes and actual ROI PNGs exactly. Their timings do not replace baseline timings. Primary/backup keypoints: '+esc(detail['query_feature_counts']['primary'])+'/'+esc(detail['query_feature_counts']['secondary'])+'.</p>')
                chunks.append(table(['Registration result','Attempts across gallery','Attempts for true identity'],
                    [[label,counts[key],true_counts[key]] for key,label in labels.items()]))
                chunks.append('<p>Counts include repeated attempts across regions, scales and enrollment frames, not independent images. More keypoints do not imply usable texture. RANSAC/geometry failures were not separated by inliers, coverage, scale or angle. All generated base ROI candidates were retained; no evidence shows that overlap protection removed a correct candidate.</p>')
            chunks.append('</div>')
        chunks.append('<details><summary>All main queries by descending duration, including failures</summary>')
        chunks.append(table(['Sample','True identity','Returned identity','Correct','Correct within 2.5 s','Seconds','HTTP','Status','Best score','Runner-up score','Route'],[
          [q['sample'],q['identity'],q['result'].get('user_id','—'),q['correct'],q['correct'] and q['ms']<=2500,seconds(q['ms']),q['http_status'],q['result'].get('status',q['result'].get('message','—')),q['result'].get('score','—'),q['result'].get('second_score','—'),q['result'].get('recognition_route','—')]
          for q in sorted(run['queries'],key=lambda q:q['ms'],reverse=True)]))
        chunks.append('</details>')
    flags=sorted({s['get_throttled'] for s in data['power_samples']})
    chunks.append('<h2>Interpretation and integrity limits</h2><p>Early return requires a best score ≤0.32 and runner-up gap ≥0.08. Full fallback in the simulated demo uses closed-set ranking without calibrated stranger rejection; weak evidence can still be assigned an identity. Evaluate this separately from ROI/alignment issues. Removing failures or changing only the threshold does not establish a fix.</p>')
    if diagnostic_rows:
        chunks.append('<p>All five errors followed full search; none was an incorrect confident early return. Two ROIs shifted toward the palm base or wrist rather than the enrolled palm center. A third remained centered but had weak texture and unstable registration. The last two, from opposite hands of one person, stayed inside the palm but had weak fine texture and large lighting/viewpoint differences; crop position alone is not an established cause. Full registration found no stable true-identity correspondences meeting the constraints.</p>')
    slowest=max((q for run in data['runs'] for q in run['queries']),key=lambda q:q['ms'])
    chunks.append('<p>Slowest sample: '+esc(slowest['sample'])+', '+esc(slowest['identity'])+', '+seconds(slowest['ms'])+' s. More early returns require better ROI/alignment evidence; relaxing confidence gates risks misidentification. The algorithm stayed frozen and was not tuned for new participants.</p>')
    chunks.append('<p>Observed power/throttling flags: '+esc(', '.join(flags))+'; final original-image check unchanged: '+esc(data.get('originals_unchanged','Awaiting completion'))+'. Galleries of 11 and six within-device palm identities cannot establish capacity for 40 people. Inspected data are no longer independent unseen validation. Forward and reverse groups query different images, so enrollment choice alone cannot explain differences.</p></html>')
    args.output.write_text(''.join(chunks),encoding='utf-8')
    print(json.dumps(dict(complete=data.get('complete',False),summary=summaries),ensure_ascii=False))


if __name__=='__main__':main()
