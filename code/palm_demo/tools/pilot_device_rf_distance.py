"""Single fixed all-stage RF-distance ablation after complete support observation."""
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
from fastcc_valid_support import ReceptiveFieldFastCC
from retained_evidence_pilot import install_retained_evidence_pilot
from replay_pi_pipeline import http_app
from replay_demo_manifest import correct_identification
from report_raw_smpd import summarize


def install(algorithm):
    """Replace the one ordinary distance shared by pose/legacy/all-stage scoring."""
    assert algorithm.base is algorithm.legacy.base and algorithm.base is algorithm._pose.base
    if getattr(algorithm,'_rf_distance_installed',False):raise ValueError('RF distance already installed')
    kernel=ReceptiveFieldFastCC();algorithm._rf_match_calls=0
    def matching(left,right):
        if np.asarray(left).shape!=(32,32) or np.asarray(right).shape!=(32,32):
            raise ValueError('RF distance requires the existing ordinary FastCC code geometry')
        algorithm._rf_match_calls+=1
        return kernel.match(left,right)
    algorithm.base.match=matching;algorithm._rf_distance_installed=True
    return algorithm


def validate_audit(audit):
    assert audit['complete'] and audit['matcher']==MATCHER and len(audit['queries'])==7
    assert audit['originals_unchanged'] and audit['source_templates_unchanged']
    for q in audit['queries']:
        c=q['matching_coverage']
        assert q['reference_equal'] and not q['missing']
        assert c['calls']==c['geometric_calls']+c['pose_calls'] and c['unknown_query']==c['unknown_target']==0
        assert all(x['full_rf_support'] for x in q['poses']+q['geometry_matches'])


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
    rows={r['sample']:r for r in json.loads((app_root/'runtime/halfturn-recovery-20261030/device-manifest-local.json').read_text())}
    assert all(sha(r['original'])==r['sha256'] for r in rows.values())
    a.output.mkdir(exist_ok=False);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    install_retained_evidence_pilot()
    report=dict(complete=False,scope=__doc__,matcher=MATCHER,selection=audit['selection'],queries=[],initializations=[],
        baseline_sha256=sha(a.baseline/'results.json'),audit_sha256=sha(a.audit),
        evaluator_sha256=source_sha(__file__),kernel_sha256=source_sha(Path(__file__).with_name('fastcc_valid_support.py')),
        thresholds=baseline['thresholds'],host='Windows PC. Instrumented audit times are not a timing control.',
        fresh_enrollment=False,diagnostic_protocol='DEVICE_RF_ABLATION_20261030.md')
    files={str(p):sha(p) for p in a.baseline.glob('*/runtime/demo_templates/*') if p.is_file()}
    save(a.output/'results.json',report)
    try:
        for case in dict.fromkeys(c for c,s in audit['selection']):
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
                    for c,sample in audit['selection']:
                        if c!=case:continue
                        ref=refs[case,sample];row=rows[sample];camera.select([row]);values.clear()
                        count=algorithm._rf_match_calls
                        status,response=request('/api/demo/identify',{},None)
                        record=dict(case=case,sample=sample,identity=row['identity'],http_status=status,
                            result={k:v for k,v in response.items() if k not in ('token','expires_at','roi_image')},
                            ms=trace[-1]['ms'],scores=dict(values),reference_correct=ref['correct'],
                            reference_result={k:v for k,v in ref['result'].items() if k not in ('token','expires_at','roi_image')},
                            rf_match_calls=algorithm._rf_match_calls-count)
                        record['correct']=correct_identification(record);report['queries'].append(record)
                        if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                        save(a.output/'results.json',report)
                        print(case,sample,ref['correct'],'->',record['correct'],response.get('user_id'),round(record['ms']),flush=True)
                assert app.demo.payments.transaction_count()==before
            finally:algorithm.close()
            gc.collect()
        assert len(report['queries'])==7
        report['summary']=summarize(report['queries'])
        report['genuine_corrections']=sum(not q['reference_correct'] and q['correct'] for q in report['queries'])
        report['lost_correct']=sum(q['reference_correct'] and not q['correct'] for q in report['queries'])
        report['templates_unchanged']=all(sha(p)==digest for p,digest in files.items())
        report['originals_unchanged']=all(sha(r['original'])==r['sha256'] for r in rows.values())
        assert report['templates_unchanged'] and report['originals_unchanged'];verify_sources()
        report['pilot_pass']=report['genuine_corrections']>0 and report['lost_correct']==0 and report['summary']['processing_failure']==0
        report['complete']=True;save(a.output/'results.json',report);print(json.dumps(report['summary']),flush=True)
    except Exception as e:
        report['failure']=type(e).__name__+': '+str(e);save(a.output/'results.json',report);raise


if __name__=='__main__':main()
