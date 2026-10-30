"""Isolated HTTP regression for retaining same-metric per-frame FastCC evidence."""
import argparse,hashlib,json,os,shutil
from pathlib import Path
import cv2,numpy as np
from evaluate_six_person_frozen import initialize,timed_summary
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification
from retained_evidence_pilot import install_retained_evidence_pilot
from staged_index_matcher import StagedIndexMatcher


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_records(values):
    return [dict(identity=u,index=j,score=v)for(u,j),v in sorted(values.items())]


def aggregate(values):
    return {u:float(np.mean(sorted(v for (owner,j),v in values.items()if owner==u)[:2]))for u,j in values}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('baseline','manifest','output'):p.add_argument(name,type=Path)
    p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--model-root',type=Path,required=True)
    p.add_argument('--full',action='store_true')
    a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());assert b['complete']
    rows={r['sample']:r for r in json.loads(a.manifest.read_text())};root=Path(__file__).resolve().parents[1]
    assert all(sha(root/n)==value for n,value in b['code_sha256'].items())
    assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1)
    os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    installed=install_retained_evidence_pilot()
    report=dict(complete=False,full=a.full,baseline_sha256=sha(a.baseline/'results.json'),
        manifest_sha256=sha(a.manifest),evaluator_sha256=sha(Path(__file__)),
        helper_sha256=sha(Path(__file__).with_name('retained_evidence_pilot.py')),
        patch={k:v for k,v in installed.items()if k!='original'},
        queries=[],initializations=[],power_samples=[],
        selection='All frozen queries'if a.full else'All 13 exhaustive queries plus first fast correct control per case')
    source_hashes={str(path):sha(path)for path in a.baseline.glob('*/runtime/demo_templates/*')if path.is_file()}
    def checkpoint():
        value=power_sample();report['power_samples'].append(value);save_json(a.output/'results.json',report)
        if power_fault(value):raise RuntimeError('Power fault')
    try:
        checkpoint()
        for run in b['runs']:
            selected=list(run['queries'])if a.full else[q for q in run['queries']if q['result']['recognition_route']=='exhaustive_fallback']
            if not a.full:selected.append(min((q for q in run['queries']if q['correct']and q['ms']<=2500),key=lambda q:q['sample']))
            source=a.baseline/run['case']/'runtime';runtime=a.output/run['case']/'runtime';runtime.parent.mkdir()
            shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'));store=runtime/'demo_templates';store.mkdir()
            for path in(source/'demo_templates').iterdir():
                if path.is_file():(store/path.name).symlink_to(path.resolve())
            app,camera,startup=initialize(runtime,b['matcher'],a.native_registration)
            report['initializations'].append(dict(case=run['case'],startup=startup))
            assert app.demo.gallery.threshold==1.0 and app.demo.gallery.min_margin==0.0
            app.demo_algorithm._retain_fastcc_evidence_pilot=True
            scores={};original_score=app.demo_algorithm.score_gallery
            def traced(probe,groups):
                value=original_score(probe,groups);scores.update(value);return value
            app.demo_algorithm.score_gallery=traced;before=app.demo.payments.transaction_count()
            try:
                with http_app(app)as(request,http_trace):
                    for ref in selected:
                        checkpoint();row=rows[ref['sample']];assert sha(Path(row['original']))==row['sha256']
                        camera.select([row]);scores.clear();app.demo_algorithm._retained_evidence_trace=None
                        status,response=request('/api/demo/identify',{},None)
                        trace=app.demo_algorithm._retained_evidence_trace
                        if trace is not None:
                            assert aggregate(trace['after'])==ref['diagnostics']['scores'],'Exhaustive baseline scores changed'
                            assert aggregate(trace['merged'])==scores,'Candidate scores do not equal frame minima'
                        else:
                            assert scores==ref['diagnostics']['scores']
                            assert status==ref['http_status']and all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'))
                        trial=dict(case=run['case'],sample=ref['sample'],identity=row['identity'],
                            reference_correct=ref['correct'],reference_ms=ref['ms'],reference_result={k:v for k,v in ref['result'].items()if k not in('roi_image','token','expires_at')},
                            http_status=status,result={k:v for k,v in response.items()if k not in('roi_image','token','expires_at')},
                            ms=http_trace[-1]['ms'],scores=dict(scores),
                            baseline_scores_reconstructed=True,frames={k:frame_records(v)for k,v in trace.items()}if trace else None)
                        trial['correct']=correct_identification(trial);report['queries'].append(trial)
                        if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                        checkpoint();print(run['case'],ref['sample'],ref['correct'],'->',trial['correct'],response.get('user_id'),round(trial['ms']),flush=True)
                assert app.demo.payments.transaction_count()==before
            finally:app.demo_algorithm.close()
        q=report['queries'];report['summary']=dict(timed_summary(q),
            corrections=sum(not r['reference_correct']and r['correct']for r in q),
            regressions=sum(r['reference_correct']and not r['correct']for r in q),
            wrong_matches=sum(r['result'].get('status')=='MATCH'and not r['correct']for r in q),
            retries_or_rejections=sum(r['result'].get('status')!='MATCH'for r in q))
        report['pilot_pass']=report['summary']['corrections']>0 and report['summary']['regressions']==0
        report['source_templates_unchanged']=all(sha(Path(path))==value for path,value in source_hashes.items())
        assert report['source_templates_unchanged'];report['complete']=True;checkpoint()
        print(json.dumps(report['summary']),flush=True)
    finally:StagedIndexMatcher.score_gallery=installed['original']


if __name__=='__main__':main()
