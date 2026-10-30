"""Scalar v27 live report; uses exact journal prefixes, no inference."""
import argparse
from pathlib import Path
import time
import types

import report_terminal_smpd as original
from smpd_run_journal import load


def snapshot(root):
    summary,values=original.snapshot(root)
    p=load(root/'protocol.json')
    records=[load(path)['payload'] for path in sorted((root/'records/enrollment').glob('*.json'))]
    payloads=[r.get('capture',{}).get('feature_bytes',0) for r in records+values]
    summary.update(codec=p['codec'],template_storage_schema=p['storage'],reuse_audit=p['reuse_audit'],
        old70_prefix_imported=False,max_observed_payload_bytes=max(payloads,default=0),
        payload_scope='All fresh successful enrollments and actually invoked query exhaustive payloads; fast probes are transient objects.',
        supervisor_status=load(root/'supervisor-status.json') if (root/'supervisor-status.json').exists() else None)
    epochs={e['epoch']:e for e in summary['epoch_costs']}
    query_wall=0.
    for file in sorted((root/'query-phases').glob('*.json')):
        phase=load(file);epoch=epochs[phase['epoch']]
        end=epoch.get('ended_unix',summary['status'].get('updated_unix',phase['started_unix']))
        query_wall+=max(0,end-phase['started_unix'])
    rate=len(values)/query_wall if values and query_wall>0 else None
    overall=summary['overall'];p95=overall['all_timing']['p95_ms']
    eta=None
    if len(values)>=20 and rate:
        remaining=3217-len(values);mean=1/rate
        eta=dict(mean_cost_extrapolation_hours=remaining*mean/3600,
            p95_cost_extrapolation_hours=remaining*max(mean,p95/1000)/3600,
            warning='Only this new run; changing subjects/poses/routes can exceed either extrapolation. Not a confidence interval or completion promise.')
    summary['live_throughput']=dict(query_wall_after_gallery_ready_s=query_wall,
        completed_queries=len(values),wall_queries_per_hour=rate*3600 if rate else None,remaining_eta=eta,
        scope='Wall time after each full-gallery-ready event; includes lock checks, cancellation/checkpoint I/O, HTTP; excludes gallery rebuild and paused gaps.')
    if records and len(records)<460:
        first=min(e['started_unix'] for e in epochs.values());elapsed=max(1,summary['status'].get('updated_unix',first)-first)
        summary['enrollment_progress']=dict(completed=len(records),elapsed_s=elapsed,
            attempts_per_minute=len(records)/elapsed*60,remaining_minutes=(460-len(records))*elapsed/len(records)/60,
            warning='Measured new-run registration prefix only; query ETA remains unknown before queries.')
    return summary,values


def report(root,output):
    namespace=dict(vars(original),snapshot=snapshot)
    return types.FunctionType(original.report.__code__,namespace,original.report.__name__)(root,output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();summary=report(args.root,args.output)
    print(dict(complete=summary['complete'],enrollment=summary['fixed_registration_attempts_completed'],queries=summary['completed_queries'],throughput=summary['live_throughput']))
