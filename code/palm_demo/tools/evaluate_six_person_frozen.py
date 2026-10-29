"""Frozen Pi HTTP evaluation of all six local subjects, with all failures retained."""
import argparse
from collections import Counter
import gc
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,debug_ui,http_app,save_json
from replay_demo_manifest import correct_identification,peak_rss_bytes
from replay_ready_queries import power_sample,power_fault
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration
from templates import TemplateStore
from gallery import Gallery
from indexed_demo_matcher import IndexedDemoMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from quality_evidence_matcher import QualityEvidenceMatcher
from union_matcher import FastCCWindowUnionMatcher


def sanitized(value):
    return {k:v for k,v in value.items() if k!='roi_image'} if isinstance(value,dict) else value


def timed_summary(trials):
    values=[r['ms'] for r in trials]
    return dict(total=len(trials),correct=sum(r['correct'] for r in trials),
        correct_within_2_5s=sum(r['correct'] and r['ms']<=2500 for r in trials),
        median_ms=float(np.median(values)),p95_ms=float(np.percentile(values,95)),max_ms=max(values),
        routes=dict(Counter(r['result'].get('recognition_route','unspecified') for r in trials)))


class EnrollmentStages:
    def __init__(self):self.events=None;self.start=None;self.originals=[]
    def install(self):
        for owner,name,label in [
            (ReplayCamera,'capture_highres','frame_file_read'),
            (debug_ui.App,'detect_full_still','primary_roi'),
            (debug_ui.App,'capture_demo_feature','frame_and_features'),
            (FastCCWindowUnionMatcher,'complete_hypotheses','alternate_roi'),
            (FastCCWindowUnionMatcher,'extract_with_hypotheses','complete_features'),
            (TemplateStore,'save','template_save'),
            (QualityEvidenceMatcher,'prepare_enrollment','prepare_enrollment'),
            (Gallery,'warm_up','gallery_prepare'),
            (IndexedDemoMatcher,'prepare_gallery','descriptor_index'),
            (LinkedEnrollmentMatcher,'prepare_gallery','index_and_enrollment_links')]:
            original=getattr(owner,name);self.originals.append((owner,name,original))
            def wrapper(*a,_original=original,_label=label,**kw):
                begin=time.perf_counter()
                try:return _original(*a,**kw)
                finally:
                    end=time.perf_counter()
                    if self.events is not None:self.events.append(dict(stage=_label,
                        start_ms=(begin-self.start)*1000,end_ms=(end-self.start)*1000,ms=(end-begin)*1000))
            setattr(owner,name,wrapper)
    def restore(self):
        for owner,name,original in reversed(self.originals):setattr(owner,name,original)


def initialize(runtime,matcher,native):
    start=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    model_ms=(time.perf_counter()-start)*1000
    debug_ui.common.RUNTIME=runtime;camera=ReplayCamera(False,engine)
    begin=time.perf_counter();app=debug_ui.App(camera,demo_matcher=matcher)
    enable_native_registration(app.demo_algorithm,native,1)
    return app,camera,dict(generic_model_startup_ms=model_ms,app_and_gallery_ms=(time.perf_counter()-begin)*1000,
        total_ms=(time.perf_counter()-start)*1000,
        localizer_sha256=hashlib.sha256((engine.root/'pklnet-keypoints-diagnostics.onnx').read_bytes()).hexdigest())


def restart_case(args,protocol,rows,case):
    destination=args.output/('restart-'+case['name']+'.json')
    if destination.exists():raise FileExistsError(destination)
    power=power_sample()
    if power_fault(power):raise RuntimeError('Power fault before restart')
    app,camera,startup=initialize(args.output/case['name']/'runtime',protocol['matcher'],args.native_registration)
    result=dict(case=case['name'],fresh_python_process=True,startup=startup,power_before=power)
    row=min((r for r in rows if r['sample'] in case['queries']),key=lambda r:r['sample'])
    try:
        camera.select([row]);before=app.demo.payments.transaction_count()
        with http_app(app) as (request,trace):
            status,response=request('/api/demo/identify',{},None)
            result['first_query']=dict(sample=row['sample'],identity=row['identity'],http_status=status,
                result=sanitized(response),ms=trace[-1]['ms'],
                correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])))
            if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
        result['transactions_unchanged']=before==app.demo.payments.transaction_count()
        result['power_after']=power_sample();result['peak_rss_bytes']=peak_rss_bytes()
        save_json(destination,result)
        if power_fault(result['power_after']):raise RuntimeError('Power fault after restart')
        assert result['transactions_unchanged']
    finally:app.demo_algorithm.close()


def run_case(args,protocol,rows,case,report,checkpoint):
    directory=args.output/case['name'];directory.mkdir(exist_ok=False)
    app,camera,startup=initialize(directory/'runtime',protocol['matcher'],args.native_registration)
    run=dict(case=case['name'],startup=startup,enrollment_reused=False,enrollments=[],immediate_queries=[],
        queries=[],payment_checks={},requests=[])
    report['runs'].append(run)
    lookup={r['sample']:r for r in rows}
    stages=EnrollmentStages();stages.install()
    def after_request(trace,response):
        completed=time.perf_counter()
        record=dict(trace,result=sanitized(response))
        if stages.events is not None:record['relative_response_end_ms']=(completed-stages.start)*1000
        run['requests'].append(record);checkpoint()
    try:
        with http_app(app,after_request=after_request) as (request,trace):
            for identity,samples in sorted(case['enrollment'].items()):
                selected=[lookup[s] for s in samples];assert len(selected)==5
                camera.select(selected);stages.start=time.perf_counter();stages.events=[]
                status,response=request('/api/demo/enroll',dict(user_id=identity.replace(':','-'),display_name='EVAL '+identity),None)
                events=stages.events;stages.events=None
                frames=[e for e in events if e['stage']=='frame_file_read']
                entry=dict(identity=identity,samples=samples,http_status=status,result=sanitized(response),
                    ms=trace[-1]['ms'],events=events)
                if frames:entry['last_frame_read_to_response_ms']=run['requests'][-1]['relative_response_end_ms']-frames[-1]['end_ms']
                run['enrollments'].append(entry);checkpoint()
                print(case['name'],'enroll',len(run['enrollments']),identity,status,round(entry['ms']),flush=True)
                # A new query is recomputed immediately; no prebuilt identity template or query warmup.
                row=min((r for r in rows if r['identity']==identity and r['sample'] in case['queries']),key=lambda r:r['sample'])
                camera.select([row]);status,response=request('/api/demo/identify',{},None)
                trial=dict(sample=row['sample'],identity=identity,http_status=status,result=sanitized(response),ms=trace[-1]['ms'])
                trial['correct']=correct_identification(trial);run['immediate_queries'].append(trial)
                if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                checkpoint()
            query_samples=list(case['queries']);random.Random(case['query_seed']).shuffle(query_samples)
            before=app.demo.payments.transaction_count()
            for sample in query_samples:
                row=lookup[sample];camera.select([row]);status,response=request('/api/demo/identify',{},None)
                trial=dict(sample=sample,identity=row['identity'],session=row['session'],http_status=status,
                    result=sanitized(response),ms=trace[-1]['ms'])
                trial['correct']=correct_identification(trial);run['queries'].append(trial)
                token=response.get('token')
                if token:
                    identity=row['identity'];checks=run['payment_checks'].setdefault(identity,{})
                    confirmation=dict(token=token,user_id=response['user_id'])
                    if trial['correct'] and not checks.get('confirmed'):
                        old_balance=app.demo.payments.balance_for(response['user_id'])
                        confirmed_status,confirmed=request('/api/demo/confirm',confirmation,None)
                        duplicate_status,_=request('/api/demo/confirm',confirmation,None)
                        checks.update(confirmed=confirmed_status==200 and confirmed.get('balance_cents')==old_balance-2000,
                            duplicate_blocked=duplicate_status==400 and app.demo.payments.balance_for(response['user_id'])==old_balance-2000)
                    else:
                        cancelled_status,_=request('/api/demo/cancel',dict(token=token),None)
                        expired_status,_=request('/api/demo/confirm',confirmation,None)
                        if trial['correct']:checks.update(cancelled=cancelled_status==200,cancelled_confirmation_blocked=expired_status==400)
                checkpoint()
                print(case['name'],'query',len(run['queries']),trial['correct'],round(trial['ms']),flush=True)
            assert len(run['queries'])==65 and len(run['enrollments'])==11
            run['summary']=timed_summary(run['queries'])
            run['summary']['immediate_queries']=timed_summary(run['immediate_queries'])
            run['summary']['successful_enrollments']=sum(e['http_status']==200 for e in run['enrollments'])
            run['summary']['recognition_ready_enrollments']=sum(e['result'].get('recognition_ready') is True for e in run['enrollments'])
            run['summary']['payment_transactions']=app.demo.payments.transaction_count()-before
            run['summary']['payment_checks_complete']=all(all(run['payment_checks'].get(u,{}).get(k) for k in
                ('confirmed','duplicate_blocked','cancelled','cancelled_confirmation_blocked')) for u in case['enrollment'])
            run['summary']['per_identity']={u:timed_summary([t for t in run['queries'] if t['identity']==u]) for u in case['enrollment']}
            run['failures']=[t for t in run['queries'] if not t['correct']]
            run['over_budget']=[t for t in run['queries'] if t['ms']>2500]
            run['peak_rss_bytes']=peak_rss_bytes();run['complete']=True;checkpoint()
    finally:
        stages.restore();app.demo_algorithm.close();checkpoint()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path);p.add_argument('protocol',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--restart-only',choices=('original','reverse'))
    args=p.parse_args();protocol=json.loads(args.protocol.read_text());rows=json.loads(args.manifest.read_text())
    app_root=Path(__file__).resolve().parents[1]
    for name,digest in protocol['code_hashes'].items():
        assert hashlib.sha256((app_root/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256(args.native_registration.read_bytes()).hexdigest()==protocol['native_sha256']
    assert len(rows)==120 and len({r['identity'] for r in rows})==11
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
    cv2.setNumThreads(1)
    if args.restart_only:
        restart_case(args,protocol,rows,next(c for c in protocol['cases'] if c['name']==args.restart_only));return
    args.output.mkdir(exist_ok=False)
    report=dict(protocol=protocol,live_camera_tested=False,runs=[],power_samples=[],
        cpu_affinity=sorted(os.sched_getaffinity(0)),thread_settings=dict(opencv=1,onnx=3,native=1),
        timing_scope='Original frame read, ROI, features, retrieval/alignment, scoring and loopback HTTP; capture and external upload excluded.',
        stage_warning='Nested/parallel stage timers overlap and must not be added.')
    destination=args.output/'results.json'
    def checkpoint():
        sample=power_sample();report['power_samples'].append(sample);save_json(destination,report)
        if power_fault(sample):raise RuntimeError('Pi power fault; partial evidence saved')
    checkpoint()
    for case in protocol['cases']:
        run_case(args,protocol,rows,case,report,checkpoint);gc.collect()
        command=[sys.executable,str(Path(__file__).resolve()),str(args.manifest),str(args.protocol),str(args.output),
            '--native-registration',str(args.native_registration),'--restart-only',case['name']]
        subprocess.run(command,check=True)
        report['runs'][-1]['restart']=json.loads((args.output/('restart-'+case['name']+'.json')).read_text());checkpoint()
    report['originals_unchanged']=all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
    report['complete']=True;checkpoint()
    print(json.dumps([r['summary'] for r in report['runs']]),flush=True)


if __name__=='__main__':main()
