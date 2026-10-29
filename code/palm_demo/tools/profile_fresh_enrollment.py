"""Measure empty-gallery enrollment and immediate first queries, without camera IO.

Instrumentation wraps existing operations; no query answers/features are reused.
Nested stage timers overlap and must not be summed.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,debug_ui,http_app,save_json
from replay_demo_manifest import correct_identification
from replay_ready_queries import power_sample,power_fault
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration
from gallery import Gallery
from indexed_demo_matcher import IndexedDemoMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from union_matcher import FastCCWindowUnionMatcher
from templates import TemplateStore
from quality_evidence_matcher import QualityEvidenceMatcher


def restart_check(args,rows):
    report=json.loads((args.output/'result.json').read_text())
    result=dict(power_before=power_sample())
    if power_fault(result['power_before']):raise RuntimeError('Power/throttle fault')
    cv2.setNumThreads(1)
    begin=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    result['generic_model_startup_ms']=(time.perf_counter()-begin)*1000
    camera=ReplayCamera(False,engine);debug_ui.common.RUNTIME=args.output/'demo_runtime'
    begin=time.perf_counter();app=debug_ui.App(camera,demo_matcher='FastCCQualityEvidence-v24-experimental')
    result['app_and_gallery_rebuild_ms']=(time.perf_counter()-begin)*1000
    enable_native_registration(app.demo_algorithm,args.native_registration,1)
    row=sorted((r for r in rows if r['index']==6),key=lambda r:r['identity'])[0]
    camera.select([row]);transactions=app.demo.payments.transaction_count()
    try:
        with http_app(app) as (request,trace):
            status,response=request('/api/demo/identify',{},None);response.pop('roi_image',None)
            result['first_query']=dict(sample=row['sample'],ms=trace[-1]['ms'],result=response,
                correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])))
            if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
        result['transactions_unchanged']=app.demo.payments.transaction_count()==transactions
        result['power_after']=power_sample()
        report['fresh_process_restart']=result;save_json(args.output/'result.json',report)
        assert result['first_query']['correct'] and result['transactions_unchanged']
        assert not power_fault(result['power_after'])
        print(json.dumps(result),flush=True)
    finally:app.demo_algorithm.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--restart-only',action='store_true',help='Use saved enrollment in a fresh process; never reenroll or prime on a query')
    args=p.parse_args()
    rows=json.loads(args.manifest.read_text())
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
    if args.restart_only:
        restart_check(args,rows)
        return
    args.output.mkdir(parents=True,exist_ok=False)
    cv2.setNumThreads(1)
    report=dict(camera_tested=False,query_warmup=False,records=[],
        scope='Saved raw frames at camera boundary, fresh empty gallery, immediate query after each identity is enrolled.',
        timing_warning='Nested stage durations overlap; camera read is file decode, not live capture.')
    app_root=Path(__file__).resolve().parents[1]
    report['source_sha256']={name:hashlib.sha256((app_root/name).read_bytes()).hexdigest()
        for name in ('linked_enrollment_matcher.py','indexed_demo_matcher.py','quality_evidence_matcher.py',
                     'templates.py','tools/profile_fresh_enrollment.py')}
    state={'events':None,'start':None};originals=[]
    def check_power():
        sample=power_sample()
        if power_fault(sample):
            report['power_fault']=sample;save_json(args.output/'result.json',report)
            raise RuntimeError('Power/throttle fault')
        return sample
    report['power_before']=check_power()
    def wrap(owner,name,label):
        original=getattr(owner,name);originals.append((owner,name,original))
        def call(*a,**kw):
            begin=time.perf_counter()
            try:return original(*a,**kw)
            finally:
                end=time.perf_counter()
                if state['events'] is not None:
                    state['events'].append(dict(stage=label,start_ms=(begin-state['start'])*1000,
                        end_ms=(end-state['start'])*1000,ms=(end-begin)*1000))
        setattr(owner,name,call)
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
        (LinkedEnrollmentMatcher,'prepare_gallery','index_and_enrollment_links')]:wrap(owner,name,label)
    debug_ui.common.RUNTIME=args.output/'demo_runtime'
    engine=PKLNetROI(threads=3)
    begin=time.perf_counter();engine._ensure_loaded()
    engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    report['generic_model_startup_ms']=(time.perf_counter()-begin)*1000
    camera=ReplayCamera(False,engine)
    app=debug_ui.App(camera,demo_matcher='FastCCQualityEvidence-v24-experimental')
    enable_native_registration(app.demo_algorithm,args.native_registration,1)
    try:
        with http_app(app) as (request,trace):
            for identity in sorted({r['identity'] for r in rows}):
                group=sorted((r for r in rows if r['identity']==identity),key=lambda r:r['index'])
                assert [r['index'] for r in group]==list(range(1,11))
                camera.select(group[:5]);state.update(events=[],start=time.perf_counter())
                _,response=request('/api/demo/enroll',dict(user_id=identity.replace(':','-'),display_name='PROFILE '+identity),200)
                end=time.perf_counter();events=state['events'];state['events']=None
                frames=[e for e in events if e['stage']=='frame_file_read'];assert len(frames)==5
                record=dict(identity=identity,enrollment_http_ms=trace[-1]['ms'],events=events,
                    last_frame_read_to_ready_ms=(end-state['start'])*1000-frames[-1]['end_ms'],
                    response=response,power=check_power())
                assert response.get('recognition_ready') is True
                camera.select([group[5]])
                status,result=request('/api/demo/identify',{},None);result.pop('roi_image',None)
                record['first_query']=dict(sample=group[5]['sample'],ms=trace[-1]['ms'],result=result,
                    correct=correct_identification(dict(http_status=status,result=result,identity=identity)))
                if result.get('token'):request('/api/demo/cancel',dict(token=result['token']),200)
                record['power_after_query']=check_power();report['records'].append(record)
                save_json(args.output/'result.json',report)
                print(identity,record['enrollment_http_ms'],record['last_frame_read_to_ready_ms'],record['first_query']['ms'],flush=True)
            assert app.demo.payments.transaction_count()==0
        # Recreate the app with persisted templates and an empty in-memory gallery.
        # Keep model startup separate; no query sample primes either cache.
        app.demo_algorithm.close()
        state.update(events=[],start=time.perf_counter())
        restarted=debug_ui.App(camera,demo_matcher='FastCCQualityEvidence-v24-experimental')
        report['app_recreation_ms']=(time.perf_counter()-state['start'])*1000
        report['app_recreation_events']=state['events'];state['events']=None
        restarted.demo_algorithm.close()
        report['power_after']=check_power()
        report['all_first_queries_correct']=all(r['first_query']['correct'] for r in report['records'])
        save_json(args.output/'result.json',report)
        assert report['all_first_queries_correct']
    finally:
        for owner,name,original in reversed(originals):setattr(owner,name,original)


if __name__=='__main__':main()
