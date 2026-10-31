"""Scalar reports for a linked parent216 + continuation suffix, never inference."""
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import time

from smpd_run_journal import atomic, digest, file_sha, load
from smpd_continuation import read_chain


def summarize(records):
    values=[r['payload'] for r in records]; counts=Counter(v['outcome'] for v in values)
    times=sorted(v['ms'] for v in values)
    def percentile(p):
        if not times:return None
        x=(len(times)-1)*p;a=int(x);b=min(a+1,len(times)-1)
        return times[a]+(times[b]-times[a])*(x-a)
    return dict(total=len(values),outcomes={k:counts[k] for k in ('correct','wrong_identity_accepted',
        'true_identity_nonunique','rejected','processing_failure')},
        correct_within_2500=sum(v['outcome']=='correct' and v['ms']<=2500 for v in values),
        http=dict(n=len(times),p50_ms=percentile(.5),p95_ms=percentile(.95),max_ms=max(times,default=None)))


def query_wall(root,now):
    epochs={p.stem:load(p) for p in (root/'epochs').glob('*.json')}
    elapsed=0.
    for path in (root/'query-phases').glob('*.json'):
        phase=load(path);epoch=epochs[phase['epoch']]
        elapsed+=max(0,epoch.get('ended_unix',now)-phase['started_unix'])
    return elapsed


def live_fields(root,p,journal):
    if journal is None:return {}
    records=journal.records;boundary=p['lineage']['parent_chains']['query']['count']
    prefix=records[:boundary];suffix=records[boundary:];now=time.time()
    old_wall=query_wall(Path(p['lineage']['parent_root']),now);new_wall=query_wall(root,now)
    overall=summarize(records);new=summarize(suffix)
    overall_rate=len(records)*3600/(old_wall+new_wall) if old_wall+new_wall>0 else None
    new_rate=len(suffix)*3600/new_wall if suffix and new_wall>0 else None
    eta=None
    if len(suffix)>=20 and new_rate:
        mean=new_wall/len(suffix);remaining=3217-len(records)
        eta=dict(mean_cost_hours=remaining*mean/3600,
            p95_cost_hours=remaining*max(mean,new['http']['p95_ms']/1000)/3600,
            warning='Observed continuation prefix only; later poses can be slower; not a confidence interval')
    return dict(parent_completed_queries=boundary,continuation_completed_queries=len(suffix),
        version_boundary=dict(parent_run_fingerprint=p['lineage']['parent_run_fingerprint'],
                              continuation_run_fingerprint=p['run_fingerprint'],first_new_global_sequence=boundary),
        live_metrics=dict(overall=overall,parent=summarize(prefix),continuation=new,
            query_wall_s=old_wall+new_wall,continuation_query_wall_s=new_wall,
            overall_wall_queries_per_hour=overall_rate,continuation_wall_queries_per_hour=new_rate,
            remaining_eta=eta),
        scope='Seen public SMPD Windows evaluation; same3217 denominator; not Pi timing, independent generalization or stranger FAR')


def snapshot(root):
    p=load(root/'protocol.json')
    if digest({k:v for k,v in p.items() if k!='run_fingerprint'})!=p['run_fingerprint']:
        raise ValueError('Report protocol fingerprint mismatch')
    parent=Path(p['lineage']['parent_root']);old=load(parent/'protocol.json')
    if file_sha(parent/'protocol.json')!=p['lineage']['parent_protocol_sha256']:
        raise ValueError('Report parent protocol changed')
    rows=lambda stage:sorted((r for r in old['rows'] if r['enrollment']==(stage=='enrollment')),
                             key=lambda r:(r['subject'],r['index']))
    enrollment=read_chain(parent/'records/enrollment','enrollment',old['run_fingerprint'],rows('enrollment'))
    prefix=read_chain(parent/'records/query','query',old['run_fingerprint'],rows('query'))
    if len(enrollment)!=460 or len(prefix)!=216:raise ValueError('Report inherited counts changed')
    suffix=read_chain(root/'records/query','query',p['run_fingerprint'],rows('query'),start=216,
                      previous=prefix[-1]['record_sha256'])
    from types import SimpleNamespace
    fields=live_fields(root,p,SimpleNamespace(records=prefix+suffix))
    return dict(status=load(root/'status.json'),expected_queries=3217,completed_queries=216+len(suffix),
        registration_attempts=460,registration_success=sum(r['payload']['ok'] for r in enrollment),
        registration_failure=sum(not r['payload']['ok'] for r in enrollment),
        registered_identities=load(parent/'gallery.json')['registered'],
        journal_tip=(suffix or prefix)[-1]['record_sha256'],parent_tip=prefix[-1]['record_sha256'],
        **fields)


def write_report(root):
    value=snapshot(root);out=root/'report';out.mkdir(exist_ok=True)
    atomic(out/'summary.json',value)
    body=html.escape(json.dumps(value,ensure_ascii=False,indent=2))
    text='<!doctype html><meta charset="utf-8"><title>SMPD v27 continuation</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;padding:20px}</style><h1>SMPD v27: explicit continuation</h1><p>Parent216 + new suffix /3217. Windows, seen public data.</p><pre>'+body+'</pre>'
    # JSON status is authoritative; HTML is a view only.
    (out/'report.html').write_text(text,encoding='utf-8')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path)
    args=parser.parse_args();print(json.dumps(write_report(args.root.resolve()),ensure_ascii=False))
