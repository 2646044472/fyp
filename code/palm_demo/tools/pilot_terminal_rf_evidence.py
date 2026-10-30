"""Fixed terminal-only RF pilot; original confident paths must stay verbatim."""
import argparse
import gc
import json
import os
from pathlib import Path
import shutil
import time

import numpy as np

from audit_device_error_evidence import initialize_windows,MATCHER
from audit_halfturn_recovery import verify_sources,sha,source_sha,save
from terminal_rf_evidence import install,POLICY,ORIGINAL_TERMINAL
from retained_evidence_pilot import install_retained_evidence_pilot
from replay_pi_pipeline import http_app
from replay_demo_manifest import correct_identification
from report_raw_smpd import summarize


from pilot_device_rf_distance import validate_audit


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','audit','output'):p.add_argument(name,type=Path)
    p.add_argument('--model-root',required=True,type=Path);a=p.parse_args();verify_sources()
    audit=json.loads(a.audit.read_text());validate_audit(audit)
    assert audit['baseline_sha256']==sha(a.baseline/'results.json')
    assert audit['helper_sha256']==source_sha(Path(__file__).with_name('fastcc_valid_support.py'))
    baseline=json.loads((a.baseline/'results.json').read_text());assert baseline['complete'] and baseline['executed_matcher']==MATCHER
    refs={(r['case'],q['sample']):q for r in baseline['runs'] for q in r['queries']}
    app_root=Path(__file__).resolve().parents[1]
    previous=json.loads((app_root/'runtime/device-rf-full168-20261030/evaluation/results.json').read_text())
    assert previous['complete'] and previous['candidate_accuracy_pass']
    prev={(run['case'],q['sample']):q for run in previous['runs'] for q in run['queries']}
    selection=set(map(tuple,audit['selection']))
    speed_controls={key for key,q in prev.items() if q['result'].get('recognition_route')==ORIGINAL_TERMINAL and refs[key]['result'].get('recognition_route')!=ORIGINAL_TERMINAL}
    selection.update(speed_controls);assert len(selection)==9 and len(speed_controls)==2
    selection=sorted(selection)
    rows={r['sample']:r for r in json.loads((app_root/'runtime/halfturn-recovery-20261030/device-manifest-local.json').read_text())}
    assert all(sha(r['original'])==r['sha256'] for r in rows.values())
    a.output.mkdir(exist_ok=False);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    install_retained_evidence_pilot()
    report=dict(complete=False,scope=__doc__,matcher=MATCHER,policy=POLICY,selection=selection,queries=[],initializations=[],
        speed_controls=sorted(speed_controls),previous_full_rf_sha256=sha(app_root/'runtime/device-rf-full168-20261030/evaluation/results.json'),
        candidate_sha256=source_sha(Path(__file__).with_name('terminal_rf_evidence.py')),
        baseline_sha256=sha(a.baseline/'results.json'),audit_sha256=sha(a.audit),
        evaluator_sha256=source_sha(__file__),kernel_sha256=source_sha(Path(__file__).with_name('fastcc_valid_support.py')),
        thresholds=baseline['thresholds'],host='Windows PC. Instrumented audit times are not a timing control.',
        fresh_enrollment=False,diagnostic_protocol='TERMINAL_RF_PROTOCOL_20261030.md')
    files={str(p):sha(p) for p in a.baseline.glob('*/runtime/demo_templates/*') if p.is_file()}
    save(a.output/'results.json',report)
    try:
        for case in dict.fromkeys(c for c,s in selection):
            source=a.baseline/case/'runtime';runtime=a.output/case/'runtime';runtime.parent.mkdir()
            shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'))
            destination=runtime/'demo_templates';destination.mkdir()
            for path in (source/'demo_templates').iterdir():
                if path.is_file():(destination/path.name).symlink_to(path.resolve())
            app,camera,startup=initialize_windows(runtime);algorithm=app.demo_algorithm
            assert app.demo.gallery.acceptance_policy is None and app.demo.gallery.threshold==1 and app.demo.gallery.min_margin==0
            assert len(app.demo.gallery._prepared_cache)==app.demo.gallery.size
            algorithm._retain_fastcc_evidence_pilot=True;install(algorithm)
            report['initializations'].append(dict(case=case,startup=startup,gallery_size=app.demo.gallery.size))
            scoring=algorithm.score_gallery;values={}
            def score(probe,groups):
                result=scoring(probe,groups);values.clear();values.update(result);return result
            algorithm.score_gallery=score;before=app.demo.payments.transaction_count()
            try:
                with http_app(app) as (request,trace):
                    for c,sample in selection:
                        if c!=case:continue
                        ref=refs[case,sample];row=rows[sample];camera.select([row]);values.clear()
                        status,response=request('/api/demo/identify',{},None)
                        diagnostic=dict(algorithm._terminal_rf_trace)
                        record=dict(case=case,sample=sample,identity=row['identity'],http_status=status,
                            result={k:v for k,v in response.items() if k not in ('token','expires_at','roi_image')},
                            ms=trace[-1]['ms'],scores=dict(values),reference_correct=ref['correct'],
                            reference_result={k:v for k,v in ref['result'].items() if k not in ('token','expires_at','roi_image')},
                            terminal_rf=diagnostic)
                        record['original_scores_equal']=diagnostic['original_scores']==ref['diagnostics']['scores']
                        record['original_route_equal']=diagnostic['original_route']==ref['result'].get('recognition_route')
                        assert record['original_scores_equal'] and record['original_route_equal']
                        assert diagnostic['unknown_calls']==0
                        if ref['result'].get('recognition_route')!=ORIGINAL_TERMINAL:
                            record['fast_decision_equal']=all(response.get(k)==ref['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route')) and values==ref['diagnostics']['scores']
                            assert record['fast_decision_equal'] and not diagnostic['rf_applied'] and diagnostic['exhaustive_callback_calls']==0
                        record['correct']=correct_identification(record);report['queries'].append(record)
                        if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                        save(a.output/'results.json',report)
                        print(case,sample,ref['correct'],'->',record['correct'],response.get('user_id'),round(record['ms']),flush=True)
                assert app.demo.payments.transaction_count()==before
            finally:algorithm.close()
            gc.collect()
        assert len(report['queries'])==9
        report['summary']=summarize(report['queries'])
        report['genuine_corrections']=sum(not q['reference_correct'] and q['correct'] for q in report['queries'])
        report['lost_correct']=sum(q['reference_correct'] and not q['correct'] for q in report['queries'])
        report['templates_unchanged']=all(sha(p)==digest for p,digest in files.items())
        report['originals_unchanged']=all(sha(r['original'])==r['sha256'] for r in rows.values())
        assert report['templates_unchanged'] and report['originals_unchanged'];verify_sources()
        results={(q['case'],q['sample']):q for q in report['queries']}
        prior_corrections={key for key,q in prev.items() if q['correct'] and not refs[key]['correct']}
        assert prior_corrections<=set(results)
        report['retained_prior_corrections']=all(results[key]['correct'] for key in prior_corrections)
        report['speed_controls_pass']=all(results[key]['correct'] and results[key]['ms']<=2500 and results[key].get('fast_decision_equal') for key in speed_controls)
        report['pilot_pass']=report['retained_prior_corrections'] and report['genuine_corrections']>0 and report['lost_correct']==0 and report['summary']['processing_failure']==0 and report['speed_controls_pass']
        report['complete']=True;save(a.output/'results.json',report);print(json.dumps(report['summary']),flush=True)
    except Exception as e:
        report['failure']=type(e).__name__+': '+str(e);save(a.output/'results.json',report);raise


if __name__=='__main__':main()
