"""Render the frozen six-person evaluation, keeping every main query visible."""
import argparse
from collections import defaultdict
import html
import json
from pathlib import Path
import numpy as np


def esc(value):return html.escape(str(value))
def seconds(value):return '—' if value is None else f'{value/1000:.3f}'
def table(headers,rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join(
        '<tr>'+''.join('<td>'+esc(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def summarize(trials):
    values=[t['ms'] for t in trials]
    return [f"{sum(t['correct'] for t in trials)}/{len(trials)}",
        f"{sum(t['correct'] and t['ms']<=2500 for t in trials)}/{len(trials)}",
        seconds(float(np.median(values))) if values else '—',seconds(max(values)) if values else '—']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();data=json.loads(args.evidence.read_text());protocol=data['protocol']
    complete=data.get('complete',False)
    state='Complete' if complete else ('Paused; incomplete groups included below' if data.get('paused_by_user') else 'Running; partial results below')
    chunks=['<!doctype html><html lang="en"><meta charset="utf-8"><title>Six-person end-to-end local-data experiment</title>',
        '<style>body{font:16px/1.65 system-ui,sans-serif;max-width:1400px;margin:36px auto;padding:0 22px;color:#182637}h1{font-size:29px}h2{margin-top:32px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #d0d8e2;padding:8px;text-align:left;vertical-align:top}th{background:#edf2f8;white-space:nowrap}.scroll{overflow:auto}.notice{border-left:4px solid #b97216;padding:10px 16px;background:#fff7e8}code{overflow-wrap:anywhere}details{margin:18px 0}small{color:#526276}</style>',
        '<h1>Frozen end-to-end pipeline and speed on six-person local data</h1>',
        '<p>2026-10-29 · Raspberry Pi 5 only · Isolated test environment · '+state+'</p>',
        '<p class="notice">This experiment did not tune the algorithm. It includes 120 originals, six participant labels and 11 palm identities. The earlier 80/80 development result is not the result for these six people; this page reports the full denominator for this run.</p>',
        '<p>Frozen algorithm version: <code>'+esc(protocol['frozen_commit'])+'</code>; matcher: <code>'+esc(protocol['matcher'])+'</code>. The protocol records checksums for recognition code, models and originals. Participants had been inspected or tested previously, so this is not unseen-identity validation.</p>',
        '<h2>Data and splits</h2>']
    chunks.append(table(['Participant label','Original images'],protocol['subject_images'].items()))
    chunks.append('<p>Two capture sessions for one participant share a single confirmed right-hand identity. Original ZIP labels and the correction record were retained. Forward groups enrolled the earliest five images per identity, reverse groups the latest five, and all other images were queried. Each group had 55 enrollment and 65 query images: 15 queries for that participant and ten for each other person. Both groups re-enrolled from empty galleries.</p>')
    chunks.append('<h2>Main query results</h2><p>Correct requires HTTP success, MATCH status and the correct identity. Correct within 2.5 s also requires the entire request to finish within 2500 ms. Errors, localization failures, queries affected by failed enrollment and timeouts remain in the denominator.</p>')
    main_rows=[]
    for run in data['runs']:
        main_rows.append([run['case'],f"{len(run['queries'])}/65"]+summarize(run['queries'])+[
            sum(e['http_status']==200 for e in run['enrollments']),
            sum(e['result'].get('recognition_ready') is True for e in run['enrollments'])])
    chunks.append(table(['Group','Query progress','Correct','Correct within 2.5 s','Median including errors (s)','Maximum (s)','Successfully enrolled identities','Prepared identities'],main_rows))
    chunks.append('<p>Timing includes reading the original, preprocessing, ROI extraction, features, retrieval/registration, scoring and local HTTP response. Live capture, hand placement and external upload are excluded. Each query rereads the original and recomputes without caching answers. Query time excludes prior enrollment computation, service startup and queuing.</p>')
    for run in data['runs']:
        chunks.append('<h2>'+esc(run['case'])+': results by person</h2>')
        people=defaultdict(list)
        for trial in run['queries']:people[trial['identity'].rsplit(':',1)[0]].append(trial)
        chunks.append(table(['Participant label','Correct','Correct within 2.5 s','Median (s)','Maximum (s)'],[[person]+summarize(trials) for person,trials in sorted(people.items())]))
        chunks.append('<h2>'+esc(run['case'])+': on-site-equivalent enrollment and immediate first query</h2>')
        immediate={r['identity']:r for r in run['immediate_queries']};enrollment_rows=[]
        for entry in run['enrollments']:
            query=immediate.get(entry['identity']);events=entry['events']
            stage=lambda label:sum(e['ms'] for e in events if e['stage']==label)
            enrollment_rows.append([entry['identity'],entry['http_status'],entry['result'].get('recognition_ready'),
                seconds(entry['ms']),seconds(entry.get('last_frame_read_to_response_ms')),
                seconds(stage('primary_roi')),seconds(stage('alternate_roi')),seconds(stage('complete_features')),
                seconds(stage('template_save')),seconds(stage('prepare_enrollment')),seconds(stage('descriptor_index')),
                seconds(stage('index_and_enrollment_links')),seconds(query['ms']) if query else '—',query['correct'] if query else '—'])
        chunks.append(table(['Identity','Enrollment HTTP','ready','Total enrollment (s)','After final frame read (s)','Primary ROI (s)','Backup ROI (s)','Full features (s)','Save (s)','Template preparation (s)','Full-gallery indexing (s)','Index + alignment (s)','Immediate first query (s)','First query correct'],enrollment_rows))
        chunks.append('<p>Nested and parallel stages are not additive. Time after the final frame read measures file replay from completion of that read to the HTTP response, not camera-to-ready latency. Total enrollment includes per-frame processing; live capture was not timed. The extra immediate first query is reported separately from the 65 main queries.</p>')
        startup=run['startup'];restart=run.get('restart')
        chunks.append('<p>Generic model startup for this group: '+seconds(startup['generic_model_startup_ms'])+' s; empty-gallery app initialization: '+seconds(startup['app_and_gallery_ms'])+' s. Model warm-up used zero-valued inputs only.</p>')
        if restart:
            chunks.append('<p>Fresh process reloading the enrolled gallery: model startup '+seconds(restart['startup']['generic_model_startup_ms'])+' s; app/gallery rebuild '+seconds(restart['startup']['app_and_gallery_ms'])+' s; first query '+seconds(restart['first_query']['ms'])+' s; correct = '+esc(restart['first_query']['correct'])+'. This was a process restart, not a Pi reboot.</p>')
        if run.get('summary'):
            chunks.append('<p>New simulated payment transactions: '+esc(run['summary']['payment_transactions'])+'; all identities passed confirmation, duplicate blocking, cancellation and post-cancellation confirmation checks: '+esc(run['summary']['payment_checks_complete'])+'.</p>')
        checks=run['payment_checks']
        if checks:chunks.append(table(['Identity','Confirmation','Duplicate confirmation blocked','Cancellation','Confirmation after cancellation blocked'],[[u]+[checks[u].get(k,'Not covered') for k in ('confirmed','duplicate_blocked','cancelled','cancelled_confirmation_blocked')] for u in sorted(checks)]))
        chunks.append('<h2>'+esc(run['case'])+': all main queries by descending duration</h2>')
        chunks.append(table(['Sample','True identity','Returned identity','Correct','Correct within 2.5 s','Seconds','HTTP','Status','Best score','Runner-up score','Route'],[
            [r['sample'],r['identity'],r['result'].get('user_id','—'),r['correct'],r['correct'] and r['ms']<=2500,
             seconds(r['ms']),r['http_status'],r['result'].get('status',r['result'].get('message','—')),
             r['result'].get('score','—'),r['result'].get('second_score','—'),r['result'].get('recognition_route','—')]
            for r in sorted(run['queries'],key=lambda r:r['ms'],reverse=True)]))
    samples=data['power_samples'];flags=sorted({s.get('get_throttled','unknown') for s in samples})
    chunks.append('<h2>Integrity and limitations</h2><p>Power/temperature samples: '+str(len(samples))+'; observed power/throttling flags: '+esc(', '.join(flags))+'. Originals verified unchanged: '+esc(data.get('originals_unchanged','Awaiting final verification'))+'.</p>')
    chunks.append('<p>This closed-set test on previously exposed local old-camera data does not establish 40-person capacity, cross-device performance, independent new-session generalization or stranger rejection. The simulated demo ultimately uses closed-set ranking. Early gates select the computational route; they do not calibrate rejection. Algorithm parameters were not changed in response to this run.</p>')
    chunks.append('<p><small>Raw results: '+esc(args.evidence.name)+'. Original images and templates remain in isolated local directories, outside the code commit.</small></p></html>')
    args.output.write_text(''.join(chunks),encoding='utf-8')
    print(json.dumps(dict(complete=complete,runs=main_rows),ensure_ascii=False))


if __name__=='__main__':main()
