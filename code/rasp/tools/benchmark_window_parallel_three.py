"""Pi-only exact-output comparison of sequential and parallel ROI windows.

All windows and model weights are retained; independent sessions use one CPU
thread each. This is a component benchmark, not recognition latency evidence.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import threading
import time
import sys
import numpy as np
import cv2
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pklnet_roi import PKLNetROI
from window_roi import window_candidates
from replay_ready_queries import power_sample,power_fault


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('manifests',type=Path,nargs='+')
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    cv2.setNumThreads(1)
    rows=[r for f in args.manifests for r in json.loads(f.read_text())]
    report=dict(scope='ROI-window component only; all supplied original frames; no query-answer cache',records=[])
    def power():
        sample=power_sample()
        if power_fault(sample):
            report['power_fault']=sample;args.output.write_text(json.dumps(report,indent=2))
            raise RuntimeError('Power/throttle fault')
        return sample
    report['power_before']=power()
    sequential=PKLNetROI(threads=3,policy='heatmap')
    thread_state=threading.local();barrier=threading.Barrier(3)
    def prime(engine):
        engine._ensure_loaded()
        engine._session.run(['keypoints','heatmap_keypoints','fc_keypoints'],{'image':np.zeros((1,3,400,300),np.float32)})
    def worker_init(_):
        thread_state.engine=PKLNetROI(threads=1,policy='heatmap')
        prime(thread_state.engine);barrier.wait(timeout=90)
    class ParallelEngine:
        def extract(self,view):return thread_state.engine.extract(view)
    start=time.perf_counter();prime(sequential);report['sequential_startup_s']=time.perf_counter()-start
    with ThreadPoolExecutor(max_workers=3) as pool:
        start=time.perf_counter();list(pool.map(worker_init,range(3)));report['parallel_startup_s']=time.perf_counter()-start
        for index,row in enumerate(rows):
            path=Path(row['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
            with Image.open(path) as image:full=image.convert('RGB')
            methods={'sequential':lambda:window_candidates(full,sequential),
                     'parallel':lambda:window_candidates(full,ParallelEngine(),map_jobs=pool.map)}
            results={};timings={}
            for name in (('sequential','parallel') if index%2==0 else ('parallel','sequential')):
                start=time.perf_counter();results[name]=methods[name]();timings[name]=(time.perf_counter()-start)*1000
            report['records'].append(dict(sample=row['sample'],timings_ms=timings,
                windows=len(results['sequential']),exact=results['sequential']==results['parallel'],
                reference=results['sequential'],candidate=results['parallel'],power_after=power()))
            args.output.write_text(json.dumps(report,indent=2))
            print(index+1,row['sample'],timings,report['records'][-1]['exact'],flush=True)
    import resource
    report['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    report['all_exact']=all(r['exact'] for r in report['records'])
    args.output.write_text(json.dumps(report,indent=2))
    assert report['all_exact']


if __name__=='__main__':main()
