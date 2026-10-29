"""Paired HTTP timing: same loaded v25 gallery, auxiliary enabled/disabled.

Selects the three slowest v24-control queries and the largest v25 early-return
gain mechanically. Recomputes each original on every request, alternates order,
and only cancels simulated tokens. This is a timing diagnostic, not validation.
"""
import argparse,hashlib,json,os,shutil,time
from pathlib import Path
import cv2
from evaluate_six_person_frozen import initialize,sanitized
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('control',type=Path);p.add_argument('candidate',type=Path)
    p.add_argument('manifest',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model-root',type=Path,required=True)
    p.add_argument('--native-registration',type=Path,required=True)
    args=p.parse_args()
    control=json.loads(args.control.read_text());candidate=json.loads((args.candidate/'results.json').read_text())
    assert control['complete'] and candidate['complete']
    refs={(r['case'],q['sample']):q for r in control['runs'] for q in r['queries']}
    options=[(r['case'],q) for r in candidate['runs'] for q in r['queries']
             if q['result'].get('recognition_route')=='compnet_evidence_confident']
    selected=sorted(refs,key=lambda k:refs[k]['ms'],reverse=True)[:3]
    gain=max(options,key=lambda t:refs[t[0],t[1]['sample']]['ms']-t[1]['ms'])
    key=(gain[0],gain[1]['sample'])
    if key not in selected:selected.append(key)
    rows={r['sample']:r for r in json.loads(args.manifest.read_text())}
    args.output.mkdir(exist_ok=False,parents=True)
    os.environ['PALM_COMPNET_MODEL_ROOT']=str(args.model_root.resolve());cv2.setNumThreads(1)
    report=dict(protocol='Top 3 control latency plus largest auxiliary gain; ABBA paired; same loaded v25 gallery; no query cache',
                selected=selected,power_samples=[],trials=[],live_camera_tested=False)
    def checkpoint():
        sample=power_sample();report['power_samples'].append(sample);save_json(args.output/'results.json',report)
        if power_fault(sample):raise RuntimeError('Pi power/throttle fault')
    checkpoint()
    for index,(case,sample) in enumerate(selected):
        row=rows[sample]
        assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest()==row['sha256']
        runtime=args.output/str(index)/'runtime'
        shutil.copytree(args.candidate/case/'runtime',runtime)
        app,camera,startup=initialize(runtime,candidate['matcher'],args.native_registration)
        original=app.demo_algorithm._auxiliary_scores;active={};mode={'enabled':False}
        def auxiliary(*a):
            if not mode['enabled']:return None
            begin=time.perf_counter()
            try:return original(*a)
            finally:active['auxiliary_ms']=(time.perf_counter()-begin)*1000
        app.demo_algorithm._auxiliary_scores=auxiliary
        transactions=app.demo.payments.transaction_count()
        try:
            with http_app(app) as (request,trace):
                for enabled in (False,True,True,False):
                    mode['enabled']=enabled;active.clear();checkpoint();camera.select([row])
                    status,response=request('/api/demo/identify',{},None)
                    trial=dict(case=case,sample=sample,identity=row['identity'],enabled=enabled,
                               ms=trace[-1]['ms'],http_status=status,result=sanitized(response),**active)
                    trial['correct']=correct_identification(trial);report['trials'].append(trial)
                    if response.get('token'):
                        cancelled,_=request('/api/demo/cancel',dict(token=response['token']),None)
                        assert cancelled==200
                    assert app.demo.payments.transaction_count()==transactions
                    checkpoint();print(case,sample,enabled,round(trial['ms']),active,flush=True)
        finally:app.demo_algorithm.close()
    report['complete']=True;checkpoint()


if __name__=='__main__':main()
