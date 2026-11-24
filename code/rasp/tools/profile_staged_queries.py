"""Instrument recorded over-budget development requests without changing scoring.

Stage timers overlap and must not be added. No input hashes/caches are inside
kernel timings. The original first/warm HTTP file remains the latency evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import threading
import time
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,http_app,debug_ui,save_json
from replay_demo_manifest import correct_identification
from replay_ready_queries import power_sample,power_fault
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration
from indexed_demo_matcher import IndexedDemoMatcher
from staged_index_matcher import StagedIndexMatcher
from affine_enrollment_matcher import AffineEnrollmentMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from pooled_enrollment_matcher import PooledEnrollmentMatcher
import pooled_enrollment_matcher
from union_matcher import FastCCWindowUnionMatcher
from demo_matcher import FastCCDemoMatcher
from compnet_evidence_matcher import CompNetEvidenceMatcher
from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay',type=Path)
    parser.add_argument('previous',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--native-registration',type=Path,required=True)
    parser.add_argument('--retain-reference-errors',action='store_true',help='Retain incorrect reference decisions and require their correctness/status to remain unchanged')
    parser.add_argument('--warm-model',action='store_true',help='Load/prime PKLNet before query timing; record initialization/ready wait separately')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    summary=json.loads((args.replay/'summary.json').read_text())
    assert summary['live_camera_tested'] is False
    if args.previous.is_dir():
        previous=json.loads((args.previous/'demo.json').read_text())
        traces=[t for t in previous['http_trace'] if t['route']=='/api/demo/identify']
        assert len(traces)==len(previous['probes'])
        selected={p['sample']:dict(p,ms=t['ms']) for p,t in zip(previous['probes'],traces) if t['ms']>2500}
        selection='all fresh-enrollment queries over 2500ms in supplied previous run'
    else:
        previous=json.loads(args.previous.read_text())
        selected={t['sample']:t for t in previous['passes'][-1]['trials'] if t['ms']>2500}
        selection='all warm-pass queries over 2500ms in supplied previous run'
    rows=[r for r in json.loads((args.replay/'input-manifest.json').read_text()) if r['sample'] in selected]
    assert rows and len(rows)==len(selected)
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
    cv2.setNumThreads(1)
    current=[None];lock=threading.Lock();originals=[]
    def event(label,start,extra=None):
        if current[0] is not None:
            with lock:current[0]['events'].append(dict(label=label,start_ms=(start-current[0]['start'])*1000,ms=(time.perf_counter()-start)*1000,**(extra or {})))
    def wrap(owner,name,label):
        old=getattr(owner,name);originals.append((owner,name,old))
        def call(*a,**kw):
            start=time.perf_counter()
            try:return old(*a,**kw)
            finally:event(label,start)
        setattr(owner,name,call)
    for owner,name,label in [
        (PKLNetROI,'_extract_once','localizer_once'),
        (IndexedDemoMatcher,'_legacy_probe','legacy_features'),
        (PooledEnrollmentMatcher,'_legacy_probe','pooled_legacy_features'),
        (StagedIndexMatcher,'_stage_views','context_features'),
        (LinkedEnrollmentMatcher,'_enrollment_link_stage','enrollment_links'),
        (AffineEnrollmentMatcher,'_enrollment_link_stage','links_and_affine'),
        (PooledEnrollmentMatcher,'_pool_stage','pooled_rescue'),
        (pooled_enrollment_matcher,'pool_correspondences','pool_transfer_and_median'),
        (pooled_enrollment_matcher,'estimate_pairs','pool_similarity_estimation'),
        (pooled_enrollment_matcher,'affine_registration','pool_affine_estimation'),
        (FastCCWindowUnionMatcher,'complete_hypotheses','complete_hypotheses'),
        (FastCCWindowUnionMatcher,'extract_with_hypotheses','complete_features'),
        (FastCCWindowUnionMatcher,'_hypothesis_views','hypothesis_features'),
        (FastCCDemoMatcher,'score_prepared','complete_identity_match')]:wrap(owner,name,label)
    wrap(CompNetEvidenceMatcher,'_auxiliary_scores','primary_embedding_evidence')
    wrap(CompNetAlternateROIMatcher,'_auxiliary_scores','base_roi_embedding_evidence')
    confident=StagedIndexMatcher.confident
    def gate(scores):
        answer=confident(scores)
        if current[0] is not None:
            with lock:current[0]['gates'].append(dict(ms=(time.perf_counter()-current[0]['start'])*1000,scores=dict(scores),confident=answer))
        return answer
    StagedIndexMatcher.confident=staticmethod(gate)
    report=dict(selection=selection,
        previous=str(args.previous),timing_warning='instrumented stage times overlap; use original HTTP run for latency acceptance',queries=[])
    def power():
        sample=power_sample()
        if power_fault(sample):
            report['aborted_power_fault']=sample;save_json(args.output,report)
            raise RuntimeError('Pi power/throttle fault')
        return sample
    report['preflight']=power()
    startup=time.perf_counter();engine=PKLNetROI(threads=3)
    if args.warm_model:
        engine._ensure_loaded()
        engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    camera=ReplayCamera(False,engine);debug_ui.common.RUNTIME=args.replay/'demo_runtime'
    app=debug_ui.App(camera,demo_matcher=summary['matcher'])
    native=enable_native_registration(app.demo_algorithm,args.native_registration,1)
    report.update(initialization_ready_ms=(time.perf_counter()-startup)*1000,model_primed=args.warm_model,
        retained_reference_errors=args.retain_reference_errors)
    class TimedNative:
        def pairs(self,*a):
            start=time.perf_counter()
            try:return native.pairs(*a)
            finally:event('native_correspondences',start)
        def __call__(self,*a):
            start=time.perf_counter()
            try:return native(*a)
            finally:event('native_registration',start)
    app.demo_algorithm.registration=app.demo_algorithm.legacy.registration=TimedNative()
    transactions=app.demo.payments.transaction_count()
    try:
        with http_app(app) as (request,trace):
            for repeat in range(2):
                for row in rows:
                    power();camera.select([row]);current[0]=dict(start=time.perf_counter(),events=[],gates=[])
                    status,response=request('/api/demo/identify',{})
                    record=current[0];current[0]=None;record.pop('start')
                    response.pop('roi_image',None)
                    reference=selected[row['sample']]['result']
                    trial=dict(sample=row['sample'],repeat=repeat,http_ms=trace[-1]['ms'],result=response,
                        correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])),
                        reference_correct=selected[row['sample']].get('correct'),
                        reference_equal=all(response.get(k)==reference.get(k) for k in ('user_id','score','second_score','status','recognition_route')),
                        **record,power_after=power())
                    report['queries'].append(trial);save_json(args.output,report)
                    if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                    print(row['sample'],repeat,round(trial['http_ms']),trial['reference_equal'],flush=True)
        report['transactions_unchanged']=transactions==app.demo.payments.transaction_count()
        assert report['transactions_unchanged'] and all(q['reference_equal'] and
            (q['correct']==q['reference_correct'] if args.retain_reference_errors else q['correct']) for q in report['queries'])
        report['complete']=True;save_json(args.output,report)
    finally:
        app.demo_algorithm.close()
        for owner,name,old in reversed(originals):setattr(owner,name,old)
        StagedIndexMatcher.confident=staticmethod(confident)


if __name__=='__main__':main()
