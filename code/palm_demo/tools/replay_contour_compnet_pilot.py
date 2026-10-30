"""Fixed paired device pilot with immutable enrollment and real HTTP queries.

Development only. No public images, production service, thresholds or labels
are modified. Stored five-frame enrollments are reused, not freshly recorded.
"""
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

import cv2
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from replay_pi_pipeline import ReplayCamera,debug_ui,http_app
from replay_demo_manifest import correct_identification
from pklnet_roi import PKLNetROI
from retained_evidence_pilot import install_retained_evidence_pilot
from contour_compnet_pilot import install,POLICY
from audit_halfturn_recovery import sha,source_sha,save,verify_sources
from templates import TemplateStore

MATCHER='FastCCCompNetAlternateROI-v26-experimental'


def versioned_copy(features,metadata):
    """Same lossless v24-to-v26 envelope migration used by the Pi baseline.

    No feature recomputation, query input, label change or compatibility bypass.
    Only a fresh destination receives these arrays/metadata.
    """
    assert features.dtype==np.uint8 and len(features)==5
    assert metadata['algorithm']=='FastCCQualityEvidence-v24-experimental'
    assert all(int(row[:4].view('<i4')[0])==2801064 for row in features)
    payload=lambda array:hashlib.sha256(b''.join(hashlib.sha256(row[4:].tobytes()).digest() for row in array)).hexdigest()
    before=payload(features);converted=features.copy()
    converted[:,:4]=np.asarray([2801066],'<i4').view(np.uint8)
    assert payload(converted)==before
    return converted,dict(metadata,algorithm=MATCHER),before


def selection(reference):
    chosen=set()
    for run in reference['runs']:
        for query in run['queries']:
            if not query['correct'] or query['result'].get('recognition_route')=='exhaustive_retained_fastcc_pilot':
                chosen.add((run['case'],query['sample']))
        timely=[q for q in run['queries'] if q['correct'] and q['ms']<=2500]
        if timely:chosen.add((run['case'],min(timely,key=lambda q:q['sample'])['sample']))
    return sorted(chosen)


def summary(rows):
    times=[r['ms'] for r in rows]
    return dict(total=len(rows),correct=sum(r['correct'] for r in rows),
        wrong=sum(r['http_status']==200 and r['result'].get('status')=='MATCH' and not r['correct'] for r in rows),
        rejected=sum(r['http_status']==200 and r['result'].get('status')!='MATCH' for r in rows),
        processing_failures=sum(r['http_status']!=200 for r in rows),
        correct_within_2500=sum(r['correct'] and r['ms']<=2500 for r in rows),
        p50_ms=float(np.median(times)),p95_ms=float(np.percentile(times,95)),max_ms=max(times))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path);p.add_argument('--model',required=True,type=Path)
    a=p.parse_args();verify_sources()
    baseline=APP/'runtime/halfturn-device-regression-20261030'
    reference=json.loads((baseline/'results.json').read_text())
    assert reference['complete'] and reference['exact_decisions']==168
    ref=reference['variants']['standard'];chosen=selection(ref)
    rows=json.loads((APP/'runtime/halfturn-recovery-20261030/device-manifest-local.json').read_text())
    lookup={r['sample']:r for r in rows};assert len(rows)==169
    assert all(sha(r['original'])==r['sha256'] for r in rows)
    protocol=json.loads((APP/'runtime/pi5-under2-20261028/active169-baseline-20261029/protocol.json').read_text())
    cases={c['name']:c for c in protocol['cases']}
    expected={(r['case'],q['sample']):q for r in ref['runs'] for q in r['queries']}
    a.output.mkdir(exist_ok=False)
    cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model.resolve())
    install_retained_evidence_pilot()
    report=dict(complete=False,policy=POLICY,selection=chosen,
        selection_rule='Every saved Windows-standard exhaustive query and wrong query, plus first timely correct per case; frozen before candidate scoring.',
        scope=__doc__,selection_reference_sha256=sha(baseline/'results.json'),matcher=MATCHER,
        historical_reference_warning='Selection reference was mislabeled v26 but executed the v24 matcher from its nested protocol. Its scores are not a v26 baseline; compare only fresh paired v26 executions here.',
        helper_sha256=source_sha(Path(__file__).with_name('contour_compnet_pilot.py')),
        runner_sha256=source_sha(__file__),model_sha256=sha(a.model/'compnet-tongji.onnx'),
        variants={v:dict(queries=[],cases=[]) for v in ('standard','candidate')},
        host='Windows PC; no Pi timing claim',thresholds=dict(early_distance=.32,early_margin=.08,final_distance=1.,final_margin=0.,rejection=False))
    save(a.output/'results.json',report)
    sources={str(p):sha(p) for case in cases for p in (baseline/'standard'/case/'runtime/demo_templates').iterdir() if p.is_file()}
    report['template_files']=len(sources)
    try:
        for ci,case in enumerate(cases):
            selected=[s for c,s in chosen if c==case]
            if not selected:continue
            for variant in (('standard','candidate') if ci%2==0 else ('candidate','standard')):
                source=baseline/'standard'/case/'runtime';runtime=a.output/variant/case/'runtime'
                runtime.parent.mkdir(parents=True)
                shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'))
                source_store=TemplateStore(source/'demo_templates')
                store=TemplateStore(runtime/'demo_templates',compression_level=1)
                copying=time.perf_counter()
                converted=[]
                for user in source_store.list_users():
                    features,metadata=source_store.load(user)
                    features,metadata,payload=versioned_copy(features,metadata)
                    store.save(user,features,metadata)
                    converted.append(dict(user=user,source_magic=2801064,destination_magic=2801066,payload_sha256=payload))
                    del features
                copy_ms=(time.perf_counter()-copying)*1000
                start=time.perf_counter();engine=PKLNetROI(threads=3);engine._ensure_loaded()
                engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
                camera=ReplayCamera(False,engine);debug_ui.common.RUNTIME=runtime
                loader=debug_ui.load_algorithm
                def load(*args,**kwargs):
                    algorithm=loader(*args,**kwargs)
                    if getattr(algorithm,'name',None)==MATCHER:
                        algorithm._retain_fastcc_evidence_pilot=True
                        if variant=='candidate':install(algorithm)
                    return algorithm
                debug_ui.load_algorithm=load
                try:app=debug_ui.App(camera,demo_matcher=MATCHER)
                finally:debug_ui.load_algorithm=loader
                algorithm=app.demo_algorithm
                entry=dict(case=case,startup_and_gallery_ready_ms=(time.perf_counter()-start)*1000,
                    enrollments_reused=True,enrollment_requests_this_run=0,gallery_size=app.demo.gallery.size,
                    actual_matcher=algorithm.name,actual_matcher_type=type(algorithm).__name__,enrollment_payloads=converted)
                entry['offline_enrollment_copy_ms']=copy_ms
                report['variants'][variant]['cases'].append(entry)
                assert entry['gallery_size']==len(cases[case]['enrollment'])
                assert algorithm.name==MATCHER and type(algorithm).__name__=='CompNetAlternateROIMatcher'
                assert len(app.demo.gallery._prepared_cache)==entry['gallery_size'],'Entire gallery must pass metadata checks and be prepared'
                assert app.demo.gallery.threshold==1 and app.demo.gallery.min_margin==0 and app.demo.gallery.acceptance_policy is None
                before=app.demo.payments.transaction_count()
                try:
                    with http_app(app) as (request,trace):
                        for sample in selected:
                            row=lookup[sample];camera.select([row])
                            old=len(getattr(algorithm,'_contour_query_trace',[]))
                            status,response=request('/api/demo/identify',{},None)
                            record=dict(case=case,sample=sample,identity=row['identity'],http_status=status,
                                result={k:v for k,v in response.items() if k!='roi_image'},ms=trace[-1]['ms'])
                            record['correct']=correct_identification(record)
                            record['contour_trace']=getattr(algorithm,'_contour_query_trace',[])[old:]
                            report['variants'][variant]['queries'].append(record)
                            if variant=='standard':
                                previous=expected[case,sample]
                                record['saved_result']=previous['result']
                                record['matches_v24_selection_reference']=status==previous['http_status'] and all(response.get(k)==previous['result'].get(k) for k in ('status','user_id','score','second_score','recognition_route'))
                                save(a.output/'results.json',report)
                            if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                            save(a.output/'results.json',report)
                            print(variant,case,sample,record['correct'],round(record['ms']),response.get('recognition_route'),flush=True)
                    entry['transactions_unchanged']=before==app.demo.payments.transaction_count()
                    assert entry['transactions_unchanged']
                    entry['preparation_trace']=getattr(algorithm,'_contour_preparation_trace',[])
                    if variant=='candidate':assert len(entry['preparation_trace'])==5*entry['gallery_size']
                finally:algorithm.close()
                save(a.output/'results.json',report);gc.collect()
        maps={v:{(q['case'],q['sample']):q for q in data['queries']} for v,data in report['variants'].items()}
        assert all(set(m)==set(chosen) for m in maps.values())
        transitions=[dict(case=k[0],sample=k[1],before_correct=maps['standard'][k]['correct'],after_correct=maps['candidate'][k]['correct']) for k in chosen]
        report.update(transitions=transitions,
            lost_correct=sum(t['before_correct'] and not t['after_correct'] for t in transitions),
            genuine_corrections=sum(not t['before_correct'] and t['after_correct'] for t in transitions),
            templates_unchanged=all(sha(p)==h for p,h in sources.items()),
            originals_unchanged=all(sha(r['original'])==r['sha256'] for r in rows))
        for variant in report['variants'].values():variant['summary']=summary(variant['queries'])
        report['pilot_pass']=report['genuine_corrections']>0 and report['lost_correct']==0 and report['templates_unchanged'] and report['originals_unchanged']
        report['next_step']='Full168 fresh-enrollment paired regression required' if report['pilot_pass'] else 'Reject candidate without parameter scan'
        verify_sources();report['complete']=True;save(a.output/'results.json',report)
        print(json.dumps({v:d['summary'] for v,d in report['variants'].items()}),flush=True)
    except Exception as e:
        report['failure']=type(e).__name__+': '+str(e);save(a.output/'results.json',report);raise


if __name__=='__main__':main()
