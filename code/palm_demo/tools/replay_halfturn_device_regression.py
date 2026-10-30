"""Fresh four-case Windows standard/candidate HTTP regression; no camera.

Reuses the frozen original run_case's real enrollment, identify, payment and
cancel/duplicate-confirmation handlers. Each variant has fresh writable data.
Concurrent full-public evaluation makes these timing diagnostics nonexclusive.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np
import psutil

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
import evaluate_six_person_frozen as frozen
from replay_pi_pipeline import ReplayCamera,debug_ui
from pklnet_roi import PKLNetROI
from retained_evidence_pilot import install_retained_evidence_pilot
from halfturn_roi_recovery import HalfTurnROIRecovery
from audit_halfturn_recovery import verify_sources,save,sha,source_sha

MATCHER='FastCCCompNetAlternateROI-v26-experimental'


def query_map(variant):
    return {(r['case'],q['sample']):q for r in variant['runs'] for q in r['queries']}


def summarize(variant):
    rows=list(query_map(variant).values())
    result=frozen.timed_summary(rows)
    result.update(wrong=sum(q['http_status']==200 and q['result'].get('status')=='MATCH' and not q['correct'] for q in rows),
        rejected=sum(q['http_status']==200 and q['result'].get('status')!='MATCH' for q in rows),
        processing_failures=sum(q['http_status']!=200 for q in rows),
        correct_within_2000=sum(q['correct'] and q['ms']<=2000 for q in rows),
        enrollments=sum(len(r['enrollments']) for r in variant['runs']),
        failed_enrollments=sum(e['http_status']!=200 for r in variant['runs'] for e in r['enrollments']),
        payment_checks_complete=all(r['summary']['payment_checks_complete'] for r in variant['runs']))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('audit',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model',required=True,type=Path);p.add_argument('--smpd-root',required=True,type=Path);a=p.parse_args()
    audit=json.loads((a.audit/'results.json').read_text())
    assert audit['complete'] and audit['device_summary']['changed_valid']==0 and audit['originals_unchanged']
    assert source_sha(Path(__file__).with_name('halfturn_roi_recovery.py'))==audit['candidate_sha256']
    verify_sources();rows=json.loads((a.audit/'device-manifest-local.json').read_text());assert len(rows)==169
    assert all(sha(r['original'])==r['sha256'] for r in rows)
    source=json.loads((APP/'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json').read_text())
    assert sum(len(c['queries']) for c in source['cases'])==168
    a.output.mkdir(exist_ok=False);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model.resolve());cv2.setNumThreads(1)
    if os.name=='nt':psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    installed=install_retained_evidence_pilot()
    report=dict(complete=False,standard_tag='standard-device-20261030',matcher=MATCHER,
        scope=__doc__,audit_sha256=sha(a.audit/'results.json'),evaluator_sha256=source_sha(__file__),
        candidate_sha256=audit['candidate_sha256'],model_sha256=sha(a.model/'compnet-tongji.onnx'),
        variants={name:dict(runs=[],localizations=[]) for name in ('standard','candidate')},
        timing_limit='Windows OpenCV reference registration; concurrent full-public workload, no exclusive-CPU or Pi speed claim. Separate fresh variant runtimes and alternating per-case order.',
        active_variant=None)
    concurrency_path=a.smpd_root/'localization-diagnostic-concurrency.json'
    count=lambda:len(json.loads((a.smpd_root/'evaluation/results.json').read_text())['queries'])
    history=json.loads(concurrency_path.read_text());history=history if isinstance(history,list) else [history]
    interval=dict(start_unix=time.time(),queries_completed_before=count(),output=str(a.output),
        scope='Full original-device paired HTTP regression, fresh enrollment and queries. Below-normal priority CPU process. Public Windows timings may include this competing workload.')
    history.append(interval);save(concurrency_path,history)
    active=[None]
    def checkpoint():
        if psutil.virtual_memory().available<1024**3:raise MemoryError('Less than 1GiB available; no gallery reduction allowed')
        save(a.output/'results.json',report)
    def initialize(runtime,matcher,native):
        tick=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
        engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
        candidate=HalfTurnROIRecovery(engine) if active[0]=='candidate' else engine
        camera=ReplayCamera(False,candidate);debug_ui.common.RUNTIME=runtime
        app=debug_ui.App(camera,demo_matcher=matcher);app.demo_algorithm._retain_fastcc_evidence_pilot=True
        assert app.demo.gallery.acceptance_policy is None
        original=candidate.extract
        def observe(image,*,side=128):
            result=original(image,side=side)
            report['variants'][active[0]]['localizations'].append(dict(sample=camera.last['sample'],
                roi_geometry_valid=bool(result[2]['roi_geometry_valid']),roi_sha256=hashlib.sha256(result[0].tobytes()).hexdigest(),
                recovered=bool(getattr(candidate,'last_trace',{}).get('recovered',False)) if active[0]=='candidate' else False))
            return result
        # Object-local instrumentation; no class/source/production change.
        candidate.extract=observe
        return app,camera,dict(total_ms=(time.perf_counter()-tick)*1000,registration='Windows unchanged OpenCV BF reference')
    frozen.initialize=initialize
    try:
        for index,case in enumerate(source['cases']):
            order=('standard','candidate') if index%2==0 else ('candidate','standard')
            for name in order:
                active[0]=name;report['active_variant']=dict(variant=name,case=case['name'])
                folder=a.output/name;folder.mkdir(exist_ok=True)
                args=argparse.Namespace(output=folder,native_registration=None)
                frozen.run_case(args,source,rows,case,report['variants'][name],checkpoint)
                checkpoint();gc.collect()
        left,right=[query_map(report['variants'][name]) for name in ('standard','candidate')]
        assert left.keys()==right.keys() and len(left)==168
        fields=('status','user_id','score','second_score','recognition_route')
        transitions=[]
        for key,before in left.items():
            after=right[key]
            transitions.append(dict(case=key[0],sample=key[1],before_correct=before['correct'],after_correct=after['correct'],
                http_equal=before['http_status']==after['http_status'],decision_equal=all(before['result'].get(k)==after['result'].get(k) for k in fields),
                standard_ms=before['ms'],candidate_ms=after['ms']))
        for value in report['variants'].values():value['summary']=summarize(value)
        report.update(transitions=transitions,lost_correct=sum(t['before_correct'] and not t['after_correct'] for t in transitions),
            genuine_corrections=sum(not t['before_correct'] and t['after_correct'] for t in transitions),
            exact_decisions=sum(t['http_equal'] and t['decision_equal'] for t in transitions),
            originals_unchanged=all(sha(r['original'])==r['sha256'] for r in rows))
        verify_sources();report['complete']=True;report['active_variant']=None
        report['regression_pass']=(report['lost_correct']==0 and report['originals_unchanged'] and
            all(v['summary']['failed_enrollments']==0 and v['summary']['payment_checks_complete'] for v in report['variants'].values()))
        checkpoint();print(json.dumps({name:v['summary'] for name,v in report['variants'].items()}),flush=True)
    except Exception as error:
        report['failure']=type(error).__name__+': '+str(error);save(a.output/'results.json',report);raise
    finally:
        interval.update(end_unix=time.time(),queries_completed_after=count(),
            potentially_overlapping_query_indices=[interval['queries_completed_before']+1,count()+1]);save(concurrency_path,history)
    # The monkeypatch exists only in this terminating evaluation process.


if __name__=='__main__':main()
