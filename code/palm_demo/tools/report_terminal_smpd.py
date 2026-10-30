"""Scalar-only snapshot of the new SMPD journal. Never imports inference code."""
import argparse
from collections import Counter, defaultdict
import csv
import html
from pathlib import Path
import statistics

from smpd_run_journal import Journal, atomic, file_sha, load


def summarize(rows):
    counts = Counter(r['outcome'] for r in rows)
    def times(values):
        values=sorted(values)
        if not values: return dict(n=0,p50_ms=None,p95_ms=None,max_ms=None)
        position=(len(values)-1)*.95;index=int(position);fraction=position-index
        p95=values[index]+fraction*(values[min(index+1,len(values)-1)]-values[index])
        return dict(n=len(values),p50_ms=statistics.median(values),p95_ms=p95,max_ms=values[-1])
    return dict(total=len(rows),outcomes={k:counts[k] for k in ('correct','wrong_identity_accepted',
        'true_identity_nonunique','rejected','processing_failure')},
        correct_within_2500=sum(r['outcome']=='correct' and r['ms']<=2500 for r in rows),
        accuracy=counts['correct']/len(rows) if rows else None,
        all_timing=times([r['ms'] for r in rows]),correct_timing=times([r['ms'] for r in rows if r['outcome']=='correct']),
        routes=dict(Counter(r['result'].get('recognition_route','none') for r in rows)))


def snapshot(root):
    p=load(root/'protocol.json');fingerprint=p['run_fingerprint']
    order=lambda flag:sorted((r for r in p['rows'] if r['enrollment']==flag),key=lambda r:(r['subject'],r['index']))
    enroll=Journal(root,'enrollment',fingerprint,[r['sample'] for r in order(True)])
    queries=Journal(root,'query',fingerprint,[r['sample'] for r in order(False)])
    values=[dict(record['payload'],sample=record['sample']) for record in queries.records]
    full=len(values)==3217
    state=load(root/'status.json')
    complete=full and state['complete']
    groups=defaultdict(list);enrollment_hashes={r['sha256'] for r in p['rows'] if r['enrollment']}
    for row in values: groups[row['source_sha256']].append(row)
    unique=[min(rows,key=lambda r:r['sample']) for rows in groups.values()]
    enroll_values=[r['payload'] for r in enroll.records]
    gallery=load(root/'gallery.json') if (root/'gallery.json').exists() else None
    localizations=[r['capture'].get('localizations',[]) for r in enroll_values+values]
    geometry=[v[0]['details'] for v in localizations if v]
    epochs=[load(path) for path in sorted((root/'epochs').glob('*.json'))]
    summary=dict(complete=complete,expected_queries=3217,completed_queries=len(values),
        scope='Seen public data evaluation; Windows HTTP replay; not independent generalization, stranger FAR or Pi timing.',
        run_fingerprint=fingerprint,protocol_sha256=file_sha(root/'protocol.json'),
        candidate=p['candidate'],matcher=p['matcher'],thresholds=p['thresholds'],
        fixed_registration_attempts_completed=len(enroll_values),fixed_registration_attempts_expected=460,
        enrollment_feature_success=sum(r['ok'] for r in enroll_values),
        enrollment_feature_failure=sum(not r['ok'] for r in enroll_values),
        registered_identities=gallery['registered'] if gallery else None,
        registration_failures=92-gallery['registered'] if gallery else None,
        queries_truth_enrolled=sum(r['truth_enrolled'] for r in values),
        queries_truth_unregistered=sum(not r['truth_enrolled'] for r in values),
        overall=summarize(values),per_view={view:summarize([r for r in values if r['condition']==view]) for view in ('F','RF','P','RP')},
        development=summarize([r for r in values if r['subject'] in p['split']['development_subjects']]),
        protected=summarize([r for r in values if r['subject'] in p['split']['reserved_subjects']]),
        protected_expected=629,development_expected=2588,
        truth_enrolled=summarize([r for r in values if r['truth_enrolled']]),
        truth_unregistered_diagnostic=summarize([r for r in values if not r['truth_enrolled']]),
        observed_roi_geometry=dict(observed=len(geometry),valid=sum(r['roi_geometry_valid'] for r in geometry),
            invalid=sum(not r['roi_geometry_valid'] for r in geometry),
            reasons=dict(Counter(r.get('roi_geometry_reason') for r in geometry if not r['roi_geometry_valid']))),
        unique_content_diagnostic=summarize(unique),
        unique_content_without_enrollment_overlap=summarize([r for r in unique if r['source_sha256'] not in enrollment_hashes]),
        query_files_overlapping_enrollment=sum(r['source_sha256'] in enrollment_hashes for r in values),
        completed_query_unique_contents=len(unique),
        whole_release_duplicates=dict(files=3677,unique_contents=3591,redundant_files=86,groups=62,
            query_unique_contents=3137,enrollment_query_byte_overlap_files=2,source='Frozen audited source-byte hashes; no perceptual duplicate claim.'),
        epoch_costs=epochs,interruptions=[load(path) for path in sorted((root/'interruptions').glob('*.json'))],
        journal_tip=queries.previous,status=state,
        limitations=['Failed registration queries remain in primary denominator.',
            'Geometry validity is not annotated anatomical correctness; no complete finger-valley visibility annotation.',
            'No old query scores/features imported; no outcome-selected replacement or threshold scan.',
            'Public reserve is prospective protection, not unseen independent validation.',
            'One complete gallery with increased Windows memory guards; no Pi capacity/speed claim.',
            'Old241 prefix does not provide a complete paired baseline.'])
    if sum(summary['overall']['outcomes'].values())!=len(values): raise ValueError('Outcome accounting mismatch')
    return summary,values


def report(root,output):
    summary,values=snapshot(root);output.mkdir(parents=True,exist_ok=True)
    atomic(output/'summary.json',summary)
    with (output/'query-ledger.csv').open('w',newline='',encoding='utf-8') as stream:
        fields=['sample','identity','condition','source_sha256','truth_enrolled','http_status','outcome','ms','user_id','score','second_score','recognition_route']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for q in values:
            value={k:q.get(k) for k in fields};value.update({k:q['result'].get(k) for k in ('user_id','score','second_score','recognition_route')});writer.writerow(value)
    title='COMPLETE' if summary['complete'] else 'INCOMPLETE — checkpoint snapshot'
    body=html.escape(__import__('json').dumps(summary,indent=2))
    (output/'report.html').write_text('<!doctype html><meta charset="utf-8"><title>SMPD terminal RF</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:0 20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f7;padding:20px}</style><h1>SMPD terminal RF: '+title+'</h1><p>Seen public data; Windows full HTTP replay. Not Pi timing or independent generalization.</p><pre>'+body+'</pre>',encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();result=report(args.root,args.output)
    print(dict(complete=result['complete'],completed_queries=result['completed_queries'],overall=result['overall']))
