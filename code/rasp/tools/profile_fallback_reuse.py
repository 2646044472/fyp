"""Profile every recorded full-search slow case, without changing computations.

Hashing is outside kernel timers but inside HTTP time. Duplicate-duration sums
overestimate recoverable wall time because workers overlap. Caching is disabled
unless --cache explicitly selects the isolated within-query memoization pilot.
Output contains private sample identifiers; keep it with the isolated replay.
"""
import argparse
import hashlib
import json
from pathlib import Path
import threading
import time
import cv2
import numpy as np
from replay_pi_pipeline import ReplayCamera,http_app,debug_ui,save_json
from replay_demo_manifest import correct_identification
from pklnet_roi import PKLNetROI
from native_registration import enable_native_registration
import registered_matcher,union_matcher,indexed_demo_matcher,staged_index_matcher,demo_matcher


class Recorder:
    def __init__(self,cache=False):self.current=None;self.lock=threading.Lock();self.originals=[];self.cache=cache
    @staticmethod
    def clone(value):
        if isinstance(value,np.ndarray):return value.copy()
        if isinstance(value,tuple):return tuple(Recorder.clone(v) for v in value)
        return value
    @staticmethod
    def digest(arrays):
        digest=hashlib.sha256()
        for array in arrays:
            a=np.asarray(array);digest.update(str((a.shape,a.dtype.str)).encode());digest.update(a.tobytes())
        return digest.hexdigest()
    def call(self,fn,label,args,kwargs,key=None):
        current=self.current
        if current is None:return fn(*args,**kwargs)
        signature=key(args,kwargs) if key else None
        inputs=([args[0]] if label=='sift' else [*args[0],*args[1]]) if label in ('sift','registration') else []
        cache_key=(label,signature)
        with self.lock:
            seen=current['seen'].setdefault(label,set())
            duplicate=signature is not None and signature in seen
            if signature is not None:seen.add(signature)
            cached=current['cache'].get(cache_key) if self.cache and inputs else None
        start=time.perf_counter();cpu=time.process_time()
        hit=False
        try:
            if cached is not None and len(inputs)==len(cached[0]) and all(a.dtype==b.dtype and np.array_equal(a,b) for a,b in zip(inputs,cached[0])):
                hit=True
                return self.clone(cached[1])
            result=fn(*args,**kwargs)
            if self.cache and inputs:
                # Snapshot inputs so caller mutation cannot corrupt validation.
                # The budget accounts for input snapshots and result arrays.
                size=sum(np.asarray(a).nbytes for a in inputs)
                size+=sum(a.nbytes for a in result if isinstance(a,np.ndarray)) if isinstance(result,tuple) else (result.nbytes if isinstance(result,np.ndarray) else 0)
                with self.lock:
                    if cache_key not in current['cache'] and current['cache_bytes']+size<=256*1024*1024:
                        current['cache'][cache_key]=(tuple(a.copy() for a in inputs),self.clone(result))
                        current['cache_bytes']+=size
            return result
        finally:
            end=time.perf_counter()
            event=dict(label=label,start_ms=(start-current['start'])*1000,ms=(end-start)*1000,
                       process_cpu_ms=(time.process_time()-cpu)*1000,duplicate=duplicate,signature=signature,cache_hit=hit)
            with self.lock:current['events'].append(event)
    def wrap(self,owner,name,label,key=None):
        fn=getattr(owner,name);self.originals.append((owner,name,fn))
        def wrapped(*args,**kwargs):return self.call(fn,label,args,kwargs,key)
        setattr(owner,name,wrapped)
    def install(self):
        for module in (registered_matcher,union_matcher,indexed_demo_matcher,staged_index_matcher,demo_matcher):
            if hasattr(module,'local_features'):
                self.wrap(module,'local_features','sift',lambda a,k:self.digest([a[0]]))
        self.wrap(PKLNetROI,'_extract_once','localizer_once',lambda a,k:
            str(a[0].policy)+self.digest([np.asarray(a[1])]))
        for owner,name,label in [
            (union_matcher.FastCCWindowUnionMatcher,'complete_hypotheses','window_localization'),
            (union_matcher.FastCCWindowUnionMatcher,'extract_with_hypotheses','full_feature_extraction'),
            (union_matcher.FastCCWindowUnionMatcher,'_hypothesis_views','candidate_features'),
            (union_matcher.FastCCWindowUnionMatcher,'_pack','template_pack'),
            (union_matcher.FastCCWindowUnionMatcher,'_unpack','template_unpack'),
            (demo_matcher.FastCCDemoMatcher,'score_prepared','full_gallery_user'),
            (indexed_demo_matcher.IndexedDemoMatcher,'_legacy_probe','initial_legacy_features'),
            (staged_index_matcher.StagedIndexMatcher,'_stage_views','initial_context_features')]:
            self.wrap(owner,name,label)
        self.wrap(cv2,'imencode','image_encode');self.wrap(cv2,'imdecode','image_decode')
    def registration(self,native):
        def wrapped(*args,**kwargs):
            return self.call(native,'registration',args,kwargs,lambda a,k:self.digest([*a[0],*a[1]]))
        return wrapped
    def finish(self):
        data=self.current;self.current=None
        events=data['events'];labels=sorted({e['label'] for e in events})
        totals={label:dict(calls=sum(e['label']==label for e in events),
            summed_ms=sum(e['ms'] for e in events if e['label']==label),
            duplicate_calls=sum(e['label']==label and e['duplicate'] for e in events),
            duplicate_summed_ms=sum(e['ms'] for e in events if e['label']==label and e['duplicate'])) for label in labels}
        return dict(totals=totals,events=events,cache_bytes_accounted=data['cache_bytes'],cache_hits=sum(e['cache_hit'] for e in events))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('replays',type=Path,nargs='+')
    parser.add_argument('--native-registration',type=Path,required=True)
    parser.add_argument('--cache',action='store_true',help='Isolated per-query exact-input memoization pilot; never enabled in the app')
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    cv2.setNumThreads(4);recorder=Recorder(cache=args.cache);recorder.install()
    report=dict(method='All previously recorded exhaustive-fallback queries, first and warm passes; no reuse between queries',
                cache_pilot=args.cache,warning='Instrumented HTTP time includes hashing. Nested/parallel durations must not be added as exclusive time.',queries=[])
    for replay in args.replays:
        summary=json.loads((replay/'summary.json').read_text())
        manifest=json.loads((replay/'input-manifest.json').read_text())
        previous=json.loads((replay/'demo.json').read_text())
        expected={p['sample']:p for p in previous['probes'] if p['result'].get('recognition_route')=='exhaustive_fallback'}
        records=[r for r in manifest if r['sample'] in expected]
        assert len(records)==len(expected)>0
        assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
        camera=ReplayCamera(False,PKLNetROI(threads=4));debug_ui.common.RUNTIME=replay/'demo_runtime'
        app=debug_ui.App(camera,demo_matcher=summary['matcher'])
        native=enable_native_registration(app.demo_algorithm,args.native_registration,4)
        app.demo_algorithm.registration=app.demo_algorithm.legacy.registration=recorder.registration(native)
        transactions=app.demo.payments.transaction_count()
        with http_app(app) as (request,trace):
            for repeat in range(2):
                for row in records:
                    camera.select([row]);recorder.current=dict(start=time.perf_counter(),seen={},events=[],cache={},cache_bytes=0)
                    status,response=request('/api/demo/identify',{});elapsed=trace[-1]['ms']
                    profile=recorder.finish();response.pop('roi_image',None)
                    reference=expected[row['sample']]['result']
                    entry=dict(replay=str(replay),sample=row['sample'],repeat=repeat,http_ms=elapsed,
                        correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])),
                        reference_equal=all(response.get(k)==reference.get(k) for k in ('user_id','score','second_score','status','recognition_route')),
                        result=response,**profile)
                    report['queries'].append(entry);save_json(args.output,report)
                    print(row['sample'],repeat,elapsed,entry['reference_equal'],flush=True)
                    if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
            assert app.demo.payments.transaction_count()==transactions
    assert all(q['correct'] and q['reference_equal'] for q in report['queries'])


if __name__=='__main__':main()
