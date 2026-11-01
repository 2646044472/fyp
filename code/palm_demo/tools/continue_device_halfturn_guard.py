"""Reviewed resource-only continuation of the missing device candidate case.

No public inference or automatic retry. The original stopped run is read-only;
only a whole, never-started candidate case can be continued in a new sibling.
"""
import argparse
import collections
import gc
import json
import os
from pathlib import Path
import random
import sys
import time

import pilot_device_halfturn_guard as base


def remaining_case(plan, report):
    if report.get('complete') or not report.get('failure','').startswith('MemoryError:'):
        raise ValueError('Expected preserved resource stop')
    expected = {c['name']:c for c in plan['protocol']['cases']}
    runs = {(r['variant'],r['case']):r for r in report['runs']}
    if len(runs) != len(report['runs']):
        raise ValueError('Duplicate case records')
    missing = []
    for name, case in expected.items():
        for variant in ['baseline','candidate']:
            r = runs.get((variant,name))
            if r is None:
                if variant != 'candidate':
                    raise ValueError('Baseline is incomplete')
                missing.append(case); continue
            if (not r.get('complete') or collections.Counter(q['sample'] for q in r['queries']) != collections.Counter(case['queries'])
                    or collections.Counter(e['identity'] for e in r['enrollments']) != collections.Counter(case['enrollment'].keys())):
                raise ValueError('Only a wholly unstarted case may continue')
    if len(missing) != 1:
        raise ValueError('Expected one missing candidate case')
    return missing[0]


def prepare(previous, output):
    import psutil
    plan = base.load(previous/'plan.json'); base.verify(plan)
    report = base.load(previous/'regression-results.json')
    case = remaining_case(plan, report)
    assert len(case['queries'])==55 and len(case['enrollment'])==11
    assert report['public_bytes_unchanged'] and report['original_images_unchanged']
    assert psutil.virtual_memory().available >= 8*1024**3
    before = {str(p.relative_to(previous)):base.sha(p) for p in previous.rglob('*') if p.is_file()}
    value = dict(parent_root=str(previous),parent_plan_sha256=base.sha(previous/'plan.json'),
        parent_result_sha256=base.sha(previous/'regression-results.json'),parent_files=before,
        source_sha256={str(Path(__file__).resolve()):base.sha(__file__)},
        case=case,expected_new_queries=55,expected_new_enrollments=11,
        algorithm_plan_fingerprint=plan['fingerprint'],recognition_changes=False,
        startup_free_GiB=8,boundary_free_GiB=2,max_RSS_GiB=14,
        reason='Reviewed operational headroom revision before continuation: observed worker peak counter 1.785GiB, host available about10.6GiB; prior12GiB stop retained. No recognition threshold/input/scoring change.',
        no_completed_query_retries=True,no_template_reuse=True,no_automatic_resume=True)
    value['fingerprint']=base.digest(value)
    output.mkdir(exist_ok=False)
    base.save(output/'plan.json',value,True)
    print(json.dumps(dict(prepared=True,fingerprint=value['fingerprint'],queries=55,enrollments=11,startup_free_GiB=8)))


def run(output):
    import cv2
    import numpy as np
    import psutil
    from retained_evidence_pilot import install_retained_evidence_pilot
    from smpd_continuation import ReadOnlyTree
    from lossless_template_store import LosslessTemplateStore
    cp=base.load(output/'plan.json')
    assert base.digest({k:v for k,v in cp.items() if k!='fingerprint'})==cp['fingerprint']
    previous=Path(cp['parent_root']);plan=base.load(previous/'plan.json');old=base.load(previous/'regression-results.json')
    assert base.sha(previous/'plan.json')==cp['parent_plan_sha256'] and base.sha(previous/'regression-results.json')==cp['parent_result_sha256']
    assert remaining_case(plan,old)==cp['case']
    assert all(base.sha(p)==h for p,h in cp['source_sha256'].items())
    base.verify(plan)
    original_boundary=base.boundary
    def boundary(root,startup=False):
        value=original_boundary(root,False)
        own=psutil.Process()
        for proc in psutil.process_iter(['cmdline']):
            try:
                argv=proc.info['cmdline'] or []
                if (proc.pid not in [own.pid,own.ppid()] and 'run' in argv
                        and any('continue_device_halfturn_guard.py' in s for s in argv)):
                    raise RuntimeError('Another continuation worker is active')
            except (psutil.AccessDenied,psutil.NoSuchProcess):pass
        if startup and value['available']<cp['startup_free_GiB']*1024**3:
            raise MemoryError('Reviewed continuation startup headroom unavailable')
        return value
    base.boundary=boundary
    boundary(output,True)
    if psutil.cpu_percent(interval=1)>35:
        raise RuntimeError('Host already busy; no continuation launched')
    base.save(output/'RUN_STARTED.json',dict(pid=os.getpid(),started=time.time(),fingerprint=cp['fingerprint']),True)
    before_public=base.original_inventory()
    result=dict(complete=False,pass_=False,parent_result_sha256=cp['parent_result_sha256'],
                continuation_fingerprint=cp['fingerprint'],resource_plan=cp['reason'],runs=[])
    os.environ['PALM_COMPNET_MODEL_ROOT']=plan['model_root'];cv2.setNumThreads(1);install_retained_evidence_pilot()
    try:
        with ReadOnlyTree(previous):
            assert {str(p.relative_to(previous)):base.sha(p) for p in previous.rglob('*') if p.is_file()}==cp['parent_files']
            samples=list(cp['case']['queries']);random.Random(cp['case']['query_seed']).shuffle(samples)
            with base.Telemetry(output/'telemetry.jsonl'):
                value=base.case_run(output/'execution',plan,cp['case'],samples,'candidate')
            result['runs'].append(value);gc.collect()
            ref=next(r for r in old['runs'] if r['variant']=='baseline' and r['case']==cp['case']['name'])
            lookup={q['sample']:q for q in ref['queries']}
            assert len(value['queries'])==55 and len(value['enrollments'])==11
            exact=all(base.exact_decision(q,lookup[q['sample']]) and base.exact_roi(q,lookup[q['sample']]) for q in value['queries'])
            stores=[LosslessTemplateStore(Path(r['runtime'])/'demo_templates') for r in [ref,value]]
            assert stores[0].list_users()==stores[1].list_users()
            equal=True
            for user in stores[0].list_users():
                arrays=[s.load(user)[0] for s in stores]
                equal &= len(arrays[0])==len(arrays[1])==5 and all(np.array_equal(a,b) for a,b in zip(*arrays))
                del arrays
            result.update(complete=True,pass_=bool(exact and equal and value['enrollments_all_verbatim'] and value['zero_transactions']),
                          paired_55_exact=exact,all_11_five_frame_arrays_exact=bool(equal))
    except Exception as e:
        result['failure']=type(e).__name__+': '+str(e)
        print(result['failure'],flush=True)
    finally:
        base.verify(plan)
        assert all(base.sha(p)==h for p,h in cp['source_sha256'].items())
        result['parent_files_unchanged']={str(p.relative_to(previous)):base.sha(p) for p in previous.rglob('*') if p.is_file()}==cp['parent_files']
        result['public_bytes_unchanged']=base.original_inventory()==before_public
        result['original_images_unchanged']=all(base.sha(r['original'])==r['sha256'] for r in plan['rows'])
        if not all(result[k] for k in ['parent_files_unchanged','public_bytes_unchanged','original_images_unchanged']):result['pass_']=False
        result['pass']=result.pop('pass_');result['ended']=time.time()
        result['peak_RSS_bytes']=psutil.Process().memory_info().peak_wset
        base.save(output/'results.json',result,True)
        print(json.dumps({k:v for k,v in result.items() if k!='runs'}),flush=True)
    return 0 if result['pass'] else 2


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run'])
    p.add_argument('previous',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    previous,output=a.previous.resolve(),a.output.resolve()
    if not output.is_relative_to(base.APP/'runtime') or output.is_relative_to(previous) or previous.is_relative_to(output):
        p.error('New isolated runtime sibling required')
    if a.mode=='prepare':prepare(previous,output)
    else:
        assert Path(base.load(output/'plan.json')['parent_root'])==previous
        sys.exit(run(output))
