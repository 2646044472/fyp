"""Opt-in v25 HTTP replay on immutable copies of a completed v24 enrollment.

Reuses enrollment images/features only, never query features/answers. Does not
claim fresh on-site enrollment latency. Production runtime is never selected.
"""
import argparse,base64,gc,hashlib,json,os,random,shutil,sys
from pathlib import Path
import cv2,numpy as np
from evaluate_six_person_frozen import initialize,sanitized,timed_summary
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification,peak_rss_bytes
from templates import TemplateStore


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('baseline',type=Path);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model-root',type=Path,required=True);p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--matcher',choices=('FastCCQualityEvidence-v24-experimental','FastCCCompNetEvidence-v25-experimental'),default='FastCCCompNetEvidence-v25-experimental',help='v24 creates a matched fresh-process control with the same copied enrollment protocol')
    args=p.parse_args();data=json.loads((args.baseline/'results.json').read_text());assert data['complete']
    rows={r['sample']:r for r in json.loads(args.manifest.read_text())};assert len(rows)==data['protocol']['images']
    assert all(digest(Path(r['original']))==r['sha256'] for r in rows.values())
    args.output.mkdir(exist_ok=False,parents=True);os.environ['PALM_COMPNET_MODEL_ROOT']=str(args.model_root.resolve())
    app_root=Path(__file__).resolve().parents[1]
    report=dict(matcher=args.matcher,baseline=args.baseline.as_posix(),
        baseline_results_sha256=digest(args.baseline/'results.json'),live_camera_tested=False,
        enrollment='Immutable copy of completed baseline enrollment; only envelope magic/algorithm metadata versioned; no fresh-enrollment latency claim',
        timing_scope=data['timing_scope'],metric_warning='Auxiliary angular embedding distance differs from FastCC; nominal .32/.08 gates, unknown-person rejection uncalibrated',
        code_sha256={p.name:digest(p) for p in [app_root/n for n in ('compnet_evidence_matcher.py','compnet_pilot.py','staged_index_matcher.py','biometric.py')]},
        model_metadata=json.loads((args.model_root/'metadata.json').read_text()),runs=[],power_samples=[])
    source_hashes={str(p):digest(p) for p in args.baseline.glob('*/runtime/demo_templates/*') if p.is_file()}
    def checkpoint():
        sample=power_sample();report['power_samples'].append(sample);save_json(args.output/'results.json',report)
        if power_fault(sample):raise RuntimeError('Pi power fault; partial candidate evidence saved')
    cv2.setNumThreads(1);checkpoint()
    for source_run in data['runs']:
        case=next(c for c in data['protocol']['cases'] if c['name']==source_run['case'])
        directory=args.output/case['name'];directory.mkdir();runtime=directory/'runtime'
        shutil.copytree(args.baseline/case['name']/'runtime',runtime)
        store=TemplateStore(runtime/'demo_templates',compression_level=1)
        for user in store.list_users():
            features,metadata=store.load(user);assert features.shape[0]==5 and features.dtype==np.uint8
            assert all(int(row[:4].view('<i4')[0])==2801064 for row in features)
            payload=hashlib.sha256(features[:,4:].tobytes()).hexdigest()
            if args.matcher=='FastCCQualityEvidence-v24-experimental':continue
            features[:,:4]=np.asarray([2801065],'<i4').view(np.uint8)
            assert hashlib.sha256(features[:,4:].tobytes()).hexdigest()==payload
            metadata['algorithm']=report['matcher'];store.save(user,features,metadata)
        app,camera,startup=initialize(runtime,report['matcher'],args.native_registration)
        run=dict(case=case['name'],startup=startup,enrollment_reused=True,queries=[],payment_checks={})
        report['runs'].append(run);source_scores=app.demo_algorithm.score_gallery;active={}
        def traced_score(probe,groups):
            values=source_scores(probe,groups);active.update(scores=dict(values),source_matrix=probe.source.tolist())
            return values
        app.demo_algorithm.score_gallery=traced_score
        try:
            before=app.demo.payments.transaction_count();order=list(case['queries']);random.Random(case['query_seed']).shuffle(order)
            with http_app(app) as (request,trace):
                for sample in order:
                    row=rows[sample];camera.select([row]);active.clear();checkpoint()
                    status,response=request('/api/demo/identify',{},None)
                    trial=dict(sample=sample,identity=row['identity'],http_status=status,result=sanitized(response),
                        ms=trace[-1]['ms'],diagnostics=dict(active))
                    trial['correct']=correct_identification(trial)
                    if response.get('roi_image'):
                        folder=directory/'query-rois';folder.mkdir(exist_ok=True)
                        path=folder/(sample+'.png');path.write_bytes(base64.b64decode(response['roi_image'].split(',')[-1]))
                        trial['roi_artifact']=path.relative_to(args.output).as_posix()
                        baseline_roi=args.baseline/case['name']/'query-rois'/(sample+'.png')
                        trial['roi_byte_equal']=path.read_bytes()==baseline_roi.read_bytes()
                    run['queries'].append(trial)
                    if response.get('token'):
                        user=row['identity'];checks=run['payment_checks'].setdefault(user,{})
                        payload=dict(token=response['token'],user_id=response['user_id'])
                        if trial['correct'] and not checks.get('confirmed'):
                            old=app.demo.payments.balance_for(response['user_id'])
                            confirmed,value=request('/api/demo/confirm',payload,None);duplicate,_=request('/api/demo/confirm',payload,None)
                            checks.update(confirmed=confirmed==200 and value.get('balance_cents')==old-2000,
                                duplicate_blocked=duplicate==400 and app.demo.payments.balance_for(response['user_id'])==old-2000)
                        else:
                            cancelled,_=request('/api/demo/cancel',dict(token=response['token']),None)
                            expired,_=request('/api/demo/confirm',payload,None)
                            if trial['correct']:checks.update(cancelled=cancelled==200,cancelled_confirmation_blocked=expired==400)
                    checkpoint();print(case['name'],len(run['queries']),trial['correct'],round(trial['ms']),response.get('recognition_route'),flush=True)
            run['summary']=timed_summary(run['queries'])
            run['payment_checks_complete']=all(all(run['payment_checks'].get(u,{}).get(k) for k in
                ('confirmed','duplicate_blocked','cancelled','cancelled_confirmation_blocked')) for u in case['enrollment'])
            run['payment_transactions']=app.demo.payments.transaction_count()-before
            run['peak_rss_bytes']=peak_rss_bytes();run['complete']=True;checkpoint()
        finally:app.demo_algorithm.close()
        gc.collect()
    report['source_templates_unchanged']=all(digest(Path(p))==v for p,v in source_hashes.items())
    report['originals_unchanged']=all(digest(Path(r['original']))==r['sha256'] for r in rows.values())
    report['complete']=True;checkpoint();print(json.dumps([r['summary'] for r in report['runs']]),flush=True)


if __name__=='__main__':main()
