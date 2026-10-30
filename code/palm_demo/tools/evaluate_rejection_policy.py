"""Actual Pi HTTP policy pilot and all-person gallery-removal diagnostic.

Known: all 13 exhaustive queries plus four fixed fast controls. Unknown: each
person removed completely from each original-split gallery, then lexicographic
first query per palm label. New matcher/runtime per removal; no threshold fit.
"""
import argparse,hashlib,inspect,json,os,shutil
from pathlib import Path
import cv2
# Import these before replay_pi_pipeline inserts its frozen APP path. An isolated
# PYTHONPATH override can test changed gateway files without changing frozen APP.
import gallery,demo_flow
from acceptance_policy import AcceptancePolicy
from retained_evidence_pilot import install_retained_evidence_pilot
from evaluate_six_person_frozen import initialize
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification
import staged_index_matcher


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('baseline','reference','manifest','protocol','policy','output'):p.add_argument(name,type=Path)
    p.add_argument('--model-root',type=Path,required=True);p.add_argument('--native-registration',type=Path,required=True)
    a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());f=json.loads(a.reference.read_text());assert b['complete']and f['complete']
    rows={r['sample']:r for r in json.loads(a.manifest.read_text())};protocol=json.loads(a.protocol.read_text())
    config=json.loads(a.policy.read_text());policy=AcceptancePolicy(config);root=Path(staged_index_matcher.__file__).parent
    assert all(sha(root/n)==v for n,v in b['code_sha256'].items())
    assert sha(a.native_registration)=='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600'
    refs={(q['case'],q['sample']):q for q in f['queries']};aliases=protocol['subject_aliases_for_reporting_only']
    def person(identity):return aliases.get(identity.split(':')[1],identity.split(':')[1])
    plan=[]
    for run in b['runs']:
        selected=[q['sample']for q in run['queries']if q['result']['recognition_route']=='exhaustive_fallback']
        selected.append(min((q for q in run['queries']if q['correct']and q['ms']<=2500),key=lambda q:q['sample'])['sample'])
        plan.append(dict(case=run['case'],mode='known',samples=selected,removed=[]))
    cases={c['name']:c for c in protocol['cases']}
    for run in b['runs']:
        if not run['case'].endswith('-original'):continue
        enrollment=cases[run['case']]['enrollment']
        for who in sorted({person(identity)for identity in enrollment}):
            identities=sorted(identity for identity in enrollment if person(identity)==who)
            samples=[min(q['sample']for q in run['queries']if q['identity']==identity)for identity in identities]
            plan.append(dict(case=run['case'],mode='whole_person_removed',samples=samples,
                removed=[identity.replace(':','-')for identity in identities]))
    assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
    installed=install_retained_evidence_pilot()
    report=dict(complete=False,warning=__doc__,policy=config,policy_sha256=sha(a.policy),
        reference_sha256=sha(a.reference),baseline_sha256=sha(a.baseline/'results.json'),plan=plan,
        gateway_code_sha256={Path(module.__file__).name:sha(Path(module.__file__))for module in(gallery,demo_flow)},
        policy_code_sha256=sha(Path(inspect.getfile(AcceptancePolicy))),evaluator_sha256=sha(Path(__file__)),
        patch={k:v for k,v in installed.items()if k!='original'},groups=[],power_samples=[])
    source_hashes={str(path):sha(path)for path in a.baseline.glob('*/runtime/demo_templates/*')if path.is_file()}
    def checkpoint():
        value=power_sample();report['power_samples'].append(value);save_json(a.output/'results.json',report)
        if power_fault(value):raise RuntimeError('Power fault')
    checkpoint()
    try:
        for number,group in enumerate(plan):
            source=a.baseline/group['case']/'runtime';runtime=a.output/f'group-{number:02d}'/'runtime';runtime.parent.mkdir()
            shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'));store=runtime/'demo_templates';store.mkdir()
            for path in(source/'demo_templates').iterdir():
                # Filenames are exact user_id.npz/user_id.json from TemplateStore.
                if path.is_file()and path.stem not in group['removed']:(store/path.name).symlink_to(path.resolve())
            (runtime/'demo_acceptance_policy.json').write_text(json.dumps(config))
            app,camera,startup=initialize(runtime,b['matcher'],a.native_registration)
            assert app.demo.gallery.acceptance_policy.name==config['name']
            assert set(app.demo.store.list_users()).isdisjoint(group['removed'])
            app.demo_algorithm._retain_fastcc_evidence_pilot=True
            item=dict(**group,startup=startup,queries=[],retained=app.demo.store.list_users());report['groups'].append(item)
            numeric={};old=app.demo_algorithm.score_gallery
            def scores(probe,groups):
                assert set(groups)==set(item['retained'])
                value=old(probe,groups);numeric.update(value);return value
            app.demo_algorithm.score_gallery=scores;before=app.demo.payments.transaction_count()
            try:
                with http_app(app)as(request,trace):
                    for sample in group['samples']:
                        checkpoint();row=rows[sample];assert sha(Path(row['original']))==row['sha256']
                        camera.select([row]);numeric.clear();status,response=request('/api/demo/identify',{},None);elapsed=trace[-1]['ms']
                        expected=policy.rejection(response.get('score'),response.get('second_score'),response.get('recognition_route'))
                        if group['mode']=='known':
                            ref=refs[group['case'],sample];assert numeric==ref['scores'],'Policy changed recognition scores'
                            expected=policy.rejection(ref['result']['score'],ref['result']['second_score'],ref['result']['recognition_route'])
                            assert response['recognition_route']==ref['result']['recognition_route']
                            assert response['score']==ref['result']['score']and response['second_score']==ref['result']['second_score']
                        assert status==200 and response['status']==(expected[0]if expected else'MATCH')
                        if expected:
                            assert response['reason']==expected[1]and 'token'not in response and 'user_id'not in response and not app.demo.pending
                            request('/api/demo/confirm',dict(token='rejected-no-token',user_id='none'),400)
                        else:
                            assert response['user_id']==min(numeric,key=numeric.get)
                            request('/api/demo/cancel',dict(token=response['token']),200)
                        trial=dict(sample=sample,identity=row['identity'],http_status=status,http_ms=elapsed,
                            result={k:v for k,v in response.items()if k not in('token','roi_image','expires_at')},scores=dict(numeric),
                            no_payment_token=expected is not None,reference_correct=refs[group['case'],sample]['correct']if group['mode']=='known'else None)
                        trial['correct']=correct_identification(dict(trial,result=response));item['queries'].append(trial)
                        checkpoint();print(group['mode'],group['case'],sample,response['status'],round(elapsed),flush=True)
                item['transactions_unchanged']=app.demo.payments.transaction_count()==before;assert item['transactions_unchanged']
            finally:app.demo_algorithm.close()
        known=[q for g in report['groups']if g['mode']=='known'for q in g['queries']]
        unknown=[q for g in report['groups']if g['mode']=='whole_person_removed'for q in g['queries']]
        report['summary']=dict(known=dict(total=len(known),correct_accept=sum(q['correct']for q in known),
            wrong_accept=sum(not q['correct']and q['result']['status']=='MATCH'for q in known),
            correct_falsely_rejected=sum(q['reference_correct']and q['result']['status']!='MATCH'for q in known),
            rejected=sum(q['result']['status']!='MATCH'for q in known)),
            unknown=dict(total=len(unknown),accepted=sum(q['result']['status']=='MATCH'for q in unknown),rejected=sum(q['result']['status']!='MATCH'for q in unknown)))
        report['source_templates_unchanged']=all(sha(Path(path))==v for path,v in source_hashes.items());assert report['source_templates_unchanged']
        report['complete']=True;checkpoint();print(json.dumps(report['summary']),flush=True)
    finally:staged_index_matcher.StagedIndexMatcher.score_gallery=installed['original']


if __name__=='__main__':main()
