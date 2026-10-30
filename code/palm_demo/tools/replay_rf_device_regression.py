"""Fresh RF-distance candidate regression on Windows, all four v26 cases.

Real five-frame enrollment, original-image HTTP identification, isolated payment
guards and ready costs. Explicit matcher provenance; no candidate optimization.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import sys
import time

import cv2
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
import evaluate_six_person_frozen as frozen
from replay_pi_pipeline import ReplayCamera,debug_ui
from pklnet_roi import PKLNetROI
from retained_evidence_pilot import install_retained_evidence_pilot
from audit_halfturn_recovery import verify_sources,sha,source_sha,save
from pilot_device_rf_distance import install as install_rf
from templates import TemplateStore
import hashlib

MATCHER='FastCCCompNetAlternateROI-v26-experimental'


def summarize(rows):
    return dict(frozen.timed_summary(rows),
        wrong=sum(q['http_status']==200 and q['result'].get('status')=='MATCH' and not q['correct'] for q in rows),
        rejected=sum(q['http_status']==200 and q['result'].get('status')!='MATCH' for q in rows),
        processing_failures=sum(q['http_status']!=200 for q in rows),
        correct_within_2000=sum(q['correct'] and q['ms']<=2000 for q in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--model',required=True,type=Path);p.add_argument('--pilot',required=True,type=Path)
    a=p.parse_args();verify_sources()
    pilot=json.loads(a.pilot.read_text());assert pilot['complete'] and pilot['pilot_pass'] and pilot['lost_correct']==0
    assert pilot['evaluator_sha256']==source_sha(Path(__file__).with_name('pilot_device_rf_distance.py'))
    assert pilot['kernel_sha256']==source_sha(Path(__file__).with_name('fastcc_valid_support.py'))
    baseline_path=APP/'runtime/v26-device-reference-20261030/evaluation'
    baseline=json.loads((baseline_path/'results.json').read_text());assert baseline['complete']
    assert pilot['baseline_sha256']==sha(baseline_path/'results.json')
    requirements=json.loads((APP/'docs/protocols/CANDIDATE_DEVICE_REGRESSION_REQUIREMENTS_20261030.json').read_text())
    manifest=APP.parents[1]/requirements['original_manifest'];assert sha(manifest)==requirements['manifest_sha256']
    protocol_path=APP/'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json'
    original_protocol=json.loads(protocol_path.read_text());protocol=dict(original_protocol,matcher=MATCHER)
    rows=json.loads((APP/'runtime/halfturn-recovery-20261030/device-manifest-local.json').read_text())
    assert len(rows)==169 and sum(len(c['queries']) for c in protocol['cases'])==168
    assert sorted((r['sample'],r['sha256']) for r in rows)==sorted((r['sample'],r['sha256']) for r in json.loads(manifest.read_text()))
    assert all(sha(r['original'])==r['sha256'] for r in rows)
    model=a.model/'compnet-tongji.onnx'
    assert sha(model)=='b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea'
    a.output.mkdir(exist_ok=False);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model.resolve());cv2.setNumThreads(1)
    patch=install_retained_evidence_pilot()
    report=dict(complete=False,full=True,scope=__doc__,matcher=MATCHER,executed_matcher=MATCHER,
        distance_policy='uniform-fully-supported-FastCC-responses-v1',pilot_sha256=sha(a.pilot),
        kernel_sha256=pilot['kernel_sha256'],baseline_sha256=sha(baseline_path/'results.json'),
        enrollment_feature_parity=[],
        standard_tag='standard-device-20261030',manifest_sha256=sha(manifest),protocol_sha256=sha(protocol_path),
        split_protocol_matcher=original_protocol['matcher'],explicit_matcher_override=True,
        helper_sha256=source_sha(Path(__file__).with_name('retained_evidence_pilot.py')),
        evaluator_sha256=source_sha(__file__),model_sha256=sha(model),runs=[],active_case=None,
        host='Windows PC; OpenCV BF reference; camera acquisition excluded. Not Pi latency.',
        thresholds=dict(early_distance=.32,early_margin=.08,final_distance=1.,final_margin=0.,rejection=False),
        started_unix=time.time())
    def checkpoint():save(a.output/'results.json',report)
    def initialize(runtime,matcher,native):
        assert matcher==MATCHER and native is None
        tick=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
        engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
        camera=ReplayCamera(False,engine);debug_ui.common.RUNTIME=runtime
        app=debug_ui.App(camera,demo_matcher=matcher);app.demo_algorithm._retain_fastcc_evidence_pilot=True
        install_rf(app.demo_algorithm)
        assert app.demo_algorithm.name==MATCHER and type(app.demo_algorithm).__name__=='CompNetAlternateROIMatcher'
        assert app.demo_algorithm.magic==2801066
        assert app.demo.gallery.threshold==1 and app.demo.gallery.min_margin==0 and app.demo.gallery.acceptance_policy is None
        return app,camera,dict(total_ms=(time.perf_counter()-tick)*1000,actual_matcher=app.demo_algorithm.name,
            actual_matcher_type=type(app.demo_algorithm).__name__,feature_magic=app.demo_algorithm.magic,
            distance_policy=report['distance_policy'],
            registration='Windows unchanged OpenCV BF reference')
    frozen.initialize=initialize;checkpoint()
    try:
        for case in protocol['cases']:
            report['active_case']=case['name'];checkpoint()
            frozen.run_case(argparse.Namespace(output=a.output,native_registration=None),protocol,rows,case,report,checkpoint)
            # Fresh extraction is unchanged. Verify every stored five-frame array,
            # not NPZ ZIP timestamps/compression bytes, against the frozen reference.
            stores=[TemplateStore(root/case['name']/'runtime/demo_templates') for root in (baseline_path,a.output)]
            for user in stores[0].list_users():
                arrays=[store.load(user)[0] for store in stores]
                equal=np.array_equal(*arrays)
                report['enrollment_feature_parity'].append(dict(case=case['name'],user=user,equal=equal,
                    source_sha256=hashlib.sha256(memoryview(np.ascontiguousarray(arrays[0]))).hexdigest()))
                assert equal,'Feature extraction unexpectedly changed'
                del arrays
            gc.collect()
        queries=[dict(q,case=run['case']) for run in report['runs'] for q in run['queries']]
        assert len(queries)==168 and sum(len(r['enrollments']) for r in report['runs'])==34
        report['payment_guards_complete']=all(r['summary']['payment_checks_complete'] for r in report['runs'])
        report['enrollment_ready_complete']=all(e['http_status']==200 and e['result'].get('recognition_ready') for r in report['runs'] for e in r['enrollments'])
        report['summary']=summarize(queries)
        refs={(run['case'],q['sample']):q for run in baseline['runs'] for q in run['queries']}
        report['transitions']=[dict(case=q['case'],sample=q['sample'],before_correct=refs[q['case'],q['sample']]['correct'],after_correct=q['correct']) for q in queries]
        report['lost_correct']=sum(t['before_correct'] and not t['after_correct'] for t in report['transitions'])
        report['genuine_corrections']=sum(not t['before_correct'] and t['after_correct'] for t in report['transitions'])
        report['candidate_accuracy_pass']=report['lost_correct']==0 and report['genuine_corrections']>0 and report['payment_guards_complete'] and report['enrollment_ready_complete']
        for run in report['runs']:run['accounting']=summarize(run['queries'])
        reference=json.loads((APP/'runtime/pi5-under2-20261028/retained-evidence-full168-results-20261030.json').read_text())
        refs={(q['case'],q['sample']):q for q in reference['queries']}
        assert len(refs)==168
        report['historical_pi_comparison']=dict(
            scope='Identity coverage diagnostic only. Separate host, registration implementation and execution epoch; never compare these durations as acceleration.',
            transitions=[dict(case=q['case'],sample=q['sample'],pi_correct=refs[q['case'],q['sample']]['correct'],windows_correct=q['correct']) for q in queries])
        report['originals_unchanged']=all(sha(r['original'])==r['sha256'] for r in rows)
        assert report['originals_unchanged'];verify_sources()
        report.update(complete=True,active_case=None,ended_unix=time.time());checkpoint()
        print(json.dumps(report['summary']),flush=True)
    except Exception as e:
        report['failure']=type(e).__name__+': '+str(e);checkpoint();raise


if __name__=='__main__':main()
