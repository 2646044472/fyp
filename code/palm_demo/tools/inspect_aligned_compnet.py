"""Observe existing accepted alignment crops; frozen embedding diagnostic only.

Replays an immutable v25 enrollment copy, records raw 128px warps already made
by alignment stages, and scores each crop against the entire original gallery.
No altered decisions, template updates, score gates, or production runtime.
Instrumented timing is not acceptance timing. Every saved crop is retained.
"""
import argparse,hashlib,inspect,json,os,shutil,threading,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from evaluate_six_person_frozen import initialize,sanitized
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from compnet_context_pilot import confident_identity
from templates import TemplateStore


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('candidate',type=Path);p.add_argument('manifest',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--model-root',type=Path,required=True);p.add_argument('--native-registration',type=Path,required=True)
    p.add_argument('--slowest-only',action='store_true',help='Mechanically select max-latency candidate query, diagnostic only')
    args=p.parse_args();data=json.loads((args.candidate/'results.json').read_text());assert data['complete']
    trials=[(r['case'],q) for r in data['runs'] for q in r['queries'] if q['result'].get('recognition_route')=='exhaustive_fallback']
    if args.slowest_only:trials=[max(trials,key=lambda t:t[1]['ms'])]
    rows={r['sample']:r for r in json.loads(args.manifest.read_text())}
    args.output.mkdir(exist_ok=False,parents=True);os.environ['PALM_COMPNET_MODEL_ROOT']=str(args.model_root.resolve())
    cv2.setNumThreads(1)
    report=dict(protocol='All existing exhaustive queries, or mechanical slowest-only diagnostic; accepted warps only, whole-gallery frozen embedding scores',
        decisions_changed=False,instrumented_timing=True,power_samples=[],queries=[])
    def checkpoint():
        sample=power_sample();report['power_samples'].append(sample);save_json(args.output/'results.json',report)
        if power_fault(sample):raise RuntimeError('Pi power/throttle fault')
    checkpoint()
    owners={'registered_matcher.py','union_matcher.py','staged_index_matcher.py',
        'linked_enrollment_matcher.py','affine_enrollment_matcher.py','pooled_enrollment_matcher.py'}
    for case in dict.fromkeys(c for c,q in trials):
        runtime=args.output/case/'runtime';shutil.copytree(args.candidate/case/'runtime',runtime)
        app,camera,startup=initialize(runtime,data['matcher'],args.native_registration)
        store=TemplateStore(runtime/'demo_templates');groups={}
        for user in store.list_users():
            f,_=store.load(user);groups[user]=app.demo_algorithm.prepare_enrollment(f)
        gallery=np.asarray([s[5] for ss in groups.values() for s in ss]);users=list(groups)
        offsets={};pos=0
        for u,ss in groups.items():offsets[u]=slice(pos,pos+len(ss));pos+=len(ss)
        original_warp=cv2.warpPerspective
        active={};lock=threading.Lock()
        def warp(src,matrix,size,*a,**kw):
            result=original_warp(src,matrix,size,*a,**kw)
            if size==(128,128) and np.asarray(src).ndim==2:
                frame=inspect.currentframe().f_back;filename=Path(frame.f_code.co_filename).name
                if filename in owners:
                    with lock:
                        active['crops'].append(result.copy())
                        active['metadata'].append(dict(owner=filename,function=frame.f_code.co_name,
                            line=frame.f_lineno,phase=active['phase'],matrix=np.asarray(matrix).tolist(),
                            source_shape=list(src.shape),elapsed_ms=(time.perf_counter()-active['start'])*1000))
            return result
        original_complete=app.demo_algorithm.complete_hypotheses
        def complete(*a,**kw):
            active['phase']='full';return original_complete(*a,**kw)
        app.demo_algorithm.complete_hypotheses=complete;cv2.warpPerspective=warp
        before=app.demo.payments.transaction_count()
        try:
            with http_app(app) as (request,trace):
                for _,reference in [(c,q) for c,q in trials if c==case]:
                    sample=reference['sample'];row=rows[sample]
                    assert hashlib.sha256(Path(row['original']).read_bytes()).hexdigest()==row['sha256']
                    active.clear();active.update(crops=[],metadata=[],phase='fast',start=time.perf_counter())
                    camera.select([row]);checkpoint();status,response=request('/api/demo/identify',{},None)
                    query_ms=trace[-1]['ms']
                    for field in ('status','user_id','score','second_score','recognition_route'):
                        assert response.get(field)==reference['result'].get(field),(field,response,reference)
                    if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
                    assert app.demo.payments.transaction_count()==before
                    checkpoint();folder=args.output/case/sample;folder.mkdir(parents=True)
                    crops=active['crops'];np.savez_compressed(folder/'crops.npz',pixels=np.asarray(crops))
                    evidence=[]
                    for pixels,metadata in zip(crops,active['metadata']):
                        query=app.demo_algorithm.encoder.extract(Image.fromarray(pixels))
                        distances=np.arccos(np.clip(gallery@query,-1,1))/np.pi
                        scores={u:float(np.sort(distances[offsets[u]])[:2].mean()) for u in users}
                        winner=confident_identity(scores)
                        evidence.append(dict(metadata,scores=scores,confident_identity=winner,
                            correct=winner==response.get('user_id') if reference['correct'] else winner==row['identity'].replace(':','-')))
                    record=dict(case=case,sample=sample,identity=row['identity'],reference_correct=reference['correct'],
                        unchanged_result=sanitized(response),http_status=status,instrumented_ms=query_ms,
                        crops=evidence,fast_confident=sum(e['phase']=='fast' and e['confident_identity'] is not None for e in evidence),
                        full_confident=sum(e['phase']=='full' and e['confident_identity'] is not None for e in evidence))
                    report['queries'].append(record);checkpoint()
                    print(case,sample,'crops',len(crops),'fast confident',record['fast_confident'],'full confident',record['full_confident'],flush=True)
        finally:
            cv2.warpPerspective=original_warp;app.demo_algorithm.close()
    report['complete']=True;checkpoint()


if __name__=='__main__':main()
