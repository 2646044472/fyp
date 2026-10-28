"""Cold/warm and queued HTTP queries against an existing isolated replay runtime.

Every query re-reads its original image and recomputes its ROI/features. No query
features or identity answers are cached. Existing simulated accounts are never
charged; generated tokens are cancelled. Live acquisition remains unmeasured.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import time
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,http_app,debug_ui,save_json
from pklnet_roi import PKLNetROI
from replay_demo_manifest import peak_rss_bytes,correct_identification


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--native-registration',type=Path)
    parser.add_argument('--native-threads',type=int,choices=(1,2,4),default=4)
    parser.add_argument('--warm-model',action='store_true',help='Prime the model at startup on zeros, counted in startup time')
    args=parser.parse_args()
    # Only the documented replay layout is supported, never a bare production runtime.
    summary=json.loads((args.replay/'summary.json').read_text())
    rows=json.loads((args.replay/'input-manifest.json').read_text())
    assert summary['live_camera_tested'] is False
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
    if args.output.exists():raise FileExistsError(args.output)
    queries=[r for r in sorted(rows,key=lambda r:(r['identity'],r['index'])) if r['index']>5]
    cv2.setNumThreads(4)
    start=time.perf_counter()
    engine=PKLNetROI(threads=4)
    if args.warm_model:
        engine._ensure_loaded()
        engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    debug_ui.common.RUNTIME=args.replay/'demo_runtime'
    camera=ReplayCamera(False,engine)
    app=debug_ui.App(camera,demo_matcher=summary['matcher'])
    if args.native_registration:
        from native_registration import enable_native_registration
        enable_native_registration(app.demo_algorithm,args.native_registration,args.native_threads)
    result=dict(host=platform.node(),matcher=summary['matcher'],startup_s=time.perf_counter()-start,
                model_primed=args.warm_model,live_camera_tested=False,passes=[])
    result['native_registration']=None if args.native_registration is None else dict(
        path=str(args.native_registration),sha256=hashlib.sha256(args.native_registration.read_bytes()).hexdigest(),threads=args.native_threads)
    result['input_manifest_sha256']=hashlib.sha256((args.replay/'input-manifest.json').read_bytes()).hexdigest()
    transactions=app.demo.payments.transaction_count()
    with http_app(app) as (request,trace):
        for label in ('first_pass','warm_pass'):
            trials=[]
            for row in queries:
                camera.select([row]);status,response=request('/api/demo/identify',{})
                elapsed=trace[-1]['ms'];response.pop('roi_image',None)
                correct=correct_identification(dict(http_status=status,result=response,identity=row['identity']))
                trials.append(dict(sample=row['sample'],status=status,correct=correct,ms=elapsed,result=response))
                if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
            times=[t['ms'] for t in trials]
            result['passes'].append(dict(label=label,n=len(trials),correct=sum(t['correct'] for t in trials),
                correct_within_2s=sum(t['correct'] and t['ms']<=2000 for t in trials),median_ms=float(np.median(times)),
                p95_ms=float(np.percentile(times,95)),max_ms=max(times),first_ms=times[0],trials=trials))
            save_json(args.output,result)
            print(label,result['passes'][-1]['median_ms'],flush=True)
        camera.select(queries[:2])
        def queued(_):
            begin=time.perf_counter();status,response=request('/api/demo/identify',{})
            response.pop('roi_image',None)
            return dict(status=status,ms=(time.perf_counter()-begin)*1000,result=response)
        with ThreadPoolExecutor(max_workers=2) as executor:queue=list(executor.map(queued,range(2)))
        for item in queue:
            if item['result'].get('token'):request('/api/demo/cancel',dict(token=item['result']['token']),200)
        result['concurrent_requests']=queue
        result['queue_expected_users']=sorted(r['identity'].replace(':','-') for r in queries[:2])
        result['queue_correct']=all(q['status']==200 for q in queue) and sorted(q['result'].get('user_id','') for q in queue)==result['queue_expected_users']
        result['transactions_unchanged']=app.demo.payments.transaction_count()==transactions
        result['peak_rss_bytes']=peak_rss_bytes()
        save_json(args.output,result)
    assert result['transactions_unchanged'] and result['queue_correct']
    assert all(p['correct']==p['n'] for p in result['passes'])


if __name__=='__main__':main()
