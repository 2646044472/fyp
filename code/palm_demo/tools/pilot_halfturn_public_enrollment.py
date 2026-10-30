"""One predeclared development registration recovery in the full eligible gallery.

Wait for complete original-device paired regression; run only if its gate
passes. This is a single-person mechanism pilot, never full-cohort accuracy.
"""
import argparse
from contextlib import contextmanager
import hashlib
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import threading
import time

import cv2
import numpy as np
import psutil

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from audit_halfturn_recovery import verify_sources,save,sha,source_sha
from evaluate_raw_smpd import ExifReplay,install_windows_capacity,MATCHER
from replay_pi_pipeline import debug_ui
from replay_demo_manifest import correct_identification
from pklnet_roi import PKLNetROI
from halfturn_roi_recovery import HalfTurnROIRecovery
from retained_evidence_pilot import install_retained_evidence_pilot


@contextmanager
def http(app,trace):
    base=debug_ui.make_handler(app)
    class Handler(base):
        def log_message(self,*a):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(route,payload):
        tick=time.perf_counter();connection=HTTPConnection(*server.server_address,timeout=1800)
        connection.request('POST',route,json.dumps(payload),{'Content-Type':'application/json'})
        response=connection.getresponse();result=json.loads(response.read());status=response.status;connection.close()
        trace.append(dict(route=route,http_status=status,ms=(time.perf_counter()-tick)*1000))
        return status,result
    try:yield request
    finally:server.shutdown();server.server_close();thread.join();app.demo_algorithm.close()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('smpd_root',type=Path);p.add_argument('regression',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--regression-pid',required=True,type=int);p.add_argument('--model',required=True,type=Path);a=p.parse_args()
    verify_sources();a.output.mkdir(exist_ok=False)
    protocol=dict(selection='Fixed development 008 F0..F4 enrollment, F5..F9 queries. Both required valleys manually reviewed on the five query originals before scores.',
        scope=__doc__,standard_tag='standard-device-20261030',enrollment_count=5,query_count=5,
        evaluator_sha256=source_sha(__file__),
        gallery='All 76 successfully registered public-baseline identities, plus recovered 008 if its unchanged five enrollment images succeed. No gallery subsets.',
        candidate_sha256=source_sha(Path(__file__).with_name('halfturn_roi_recovery.py')),
        threshold_changes=False,model_training=False,source_selection_uses_identity_scores=False,
        limits='Development-only single-person pilot, not full generalization accuracy, unseen-person FAR, Pi timing or proof of 40-person device capacity. Missing-valley captures are not recovery targets.')
    save(a.output/'protocol.json',protocol)
    process=None;created=None
    while True:
        regression=json.loads((a.regression/'results.json').read_text())
        if regression.get('failure'):raise RuntimeError('Original-device regression failed: '+regression['failure'])
        if regression['complete']:break
        if process is None:
            process=psutil.Process(a.regression_pid);created=process.create_time()
        if not process.is_running() or process.create_time()!=created:raise RuntimeError('Original-device regression process exited incomplete')
        save(a.output/'progress.json',dict(complete=False,state='waiting_for_original_device_regression'))
        time.sleep(20)
    assert regression['regression_pass'] and regression['candidate_sha256']==protocol['candidate_sha256']
    assert psutil.virtual_memory().available>6*1024**3,'Insufficient host memory for complete gallery; do not reduce identities'
    if os.name=='nt':psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model.resolve());cv2.setNumThreads(1)
    capacity=install_windows_capacity();install_retained_evidence_pilot()
    rows=json.loads((a.smpd_root/'prepared/manifest.json').read_text())
    selected=sorted((r for r in rows if r['subject']=='008' and r['condition']=='F'),key=lambda r:r['index'])
    assert [r['index'] for r in selected]==list(range(10))
    source=a.smpd_root/'evaluation/runtime/demo_templates'
    files=[f for f in source.iterdir() if f.is_file()];before={f.name:sha(f) for f in files}
    enrolled=json.loads((a.smpd_root/'evaluation/enrollments.json').read_text())
    users=[e['identity'].replace(':','-') for e in enrolled if e['registered']]
    assert len(users)==76 and 'smpd-008-right' not in users
    count=lambda:len(json.loads((a.smpd_root/'evaluation/results.json').read_text())['queries'])
    path=a.smpd_root/'localization-diagnostic-concurrency.json';history=json.loads(path.read_text())
    interval=dict(start_unix=time.time(),queries_completed_before=count(),output=str(a.output),
        scope='Single-development-person recovery enrollment and five original-image queries; full 76/77 gallery. Below-normal priority; overlapping public Windows timings include competing inference/index load.')
    history.append(interval);save(path,history)
    report=dict(complete=False,protocol=protocol,resources=capacity,regression_sha256=sha(a.regression/'results.json'),
        variants={},query_results=[],model_sha256=sha(a.model/'compnet-tongji.onnx'))
    try:
        for variant in ('standard','candidate'):
            runtime=a.output/variant/'runtime';engine=PKLNetROI(threads=3);engine._ensure_loaded()
            engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
            extractor=HalfTurnROIRecovery(engine) if variant=='candidate' else engine
            camera=ExifReplay(False,extractor);debug_ui.common.RUNTIME=runtime
            app=debug_ui.App(camera,demo_matcher=MATCHER);app.demo_algorithm._retain_fastcc_evidence_pilot=True
            assert app.demo.gallery.acceptance_policy is None
            # Read-only hard links to frozen template bytes; independent accounts.
            (runtime/'demo_templates').mkdir(parents=True,exist_ok=True)
            for f in files:os.link(f,(runtime/'demo_templates')/f.name)
            for user in users:app.demo.payments.create_account(user,'EVAL '+user,10000)
            trace=[];item=dict(http_trace=trace);report['variants'][variant]=item
            with http(app,trace) as request:
                camera.select(selected[:5]);status,response=request('/api/demo/enroll',dict(user_id='smpd-008-right',display_name='EVAL smpd:008:right'))
                item['enrollment']=dict(http_status=status,result={k:v for k,v in response.items() if k not in ('roi_image','token')})
                item['registered']=app.demo.store.exists('smpd-008-right') and app.demo.payments.user_exists('smpd-008-right')
                save(a.output/'results.json',report)
                if variant=='standard':
                    assert status==400 and not item['registered'],'Standard enrollment outcome differs from frozen preparation'
                    continue
                assert status==200 and item['registered'] and response.get('recognition_ready') is True
                assert len(app.demo.gallery._prepared_cache)==77
                assert set(app.demo.store.list_users())==set(users)|{'smpd-008-right'}
                checks=dict(confirmed=False,duplicate_blocked=False,cancelled=False,cancelled_confirmation_blocked=False)
                for row in selected[5:]:
                    camera.select([row]);status,response=request('/api/demo/identify',{})
                    result={k:v for k,v in response.items() if k not in ('roi_image','token','expires_at')}
                    q=dict(sample=row['sample'],identity=row['identity'],http_status=status,result=result,ms=trace[-1]['ms'])
                    q['correct']=correct_identification(q);report['query_results'].append(q)
                    token=response.get('token')
                    if token and q['correct'] and not checks['confirmed']:
                        balance=app.demo.payments.balance_for('smpd-008-right');payload=dict(token=token,user_id='smpd-008-right')
                        s,r=request('/api/demo/confirm',payload);d,_=request('/api/demo/confirm',payload)
                        checks.update(confirmed=s==200 and r.get('balance_cents')==balance-2000,duplicate_blocked=d==400)
                    elif token:
                        s,_=request('/api/demo/cancel',dict(token=token));d,_=request('/api/demo/confirm',dict(token=token,user_id=response['user_id']))
                        if q['correct']:checks.update(cancelled=s==200,cancelled_confirmation_blocked=d==400)
                    save(a.output/'results.json',report);print(row['sample'],q['correct'],round(q['ms']),flush=True)
                item.update(payment_checks=checks,payment_transactions=app.demo.payments.transaction_count())
        report.update(complete=True,correct=sum(q['correct'] for q in report['query_results']),query_count=len(report['query_results']),
            source_templates_unchanged=all(sha(source/name)==h for name,h in before.items()),
            originals_unchanged=all(sha(r['original'])==r['sha256'] for r in selected),
            query_enrollment_byte_overlap=sum(r['sha256'] in {e['sha256'] for e in selected[:5]} for r in selected[5:]))
        report['pilot_pass']=(report['correct']==5 and all(report['variants']['candidate']['payment_checks'].values())
            and report['variants']['candidate']['payment_transactions']==1)
        assert report['query_count']==5 and report['source_templates_unchanged'] and report['originals_unchanged'];verify_sources()
        save(a.output/'results.json',report);print('pilot-complete',report['correct'],'/5',flush=True)
    except Exception as error:
        report['failure']=type(error).__name__+': '+str(error);save(a.output/'results.json',report);raise
    finally:
        interval.update(end_unix=time.time(),queries_completed_after=count(),
            potentially_overlapping_query_indices=[interval['queries_completed_before']+1,count()+1]);save(path,history)


if __name__=='__main__':main()
