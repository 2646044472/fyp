"""Isolated cold-model and warm HTTP runs with peak working-set measurement."""
import time
PROCESS_START=time.perf_counter()
import argparse,json,os,platform,shutil,sqlite3,sys,hashlib,cProfile,pstats
from pathlib import Path
import numpy as np
APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from replay_pi_pipeline import ReplayCamera,http_app
from palm_app import debug_ui
from pklnet_roi import PKLNetROI


def memory():
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage']]
        kernel=ctypes.WinDLL('kernel32');api=ctypes.WinDLL('psapi')
        kernel.GetCurrentProcess.restype=wintypes.HANDLE
        api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        counters=Counters();counters.cb=ctypes.sizeof(counters)
        if not api.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counters),counters.cb):raise ctypes.WinError()
        return dict(rss_bytes=counters.WorkingSetSize,peak_rss_bytes=counters.PeakWorkingSetSize)
    import resource
    return dict(peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    out=a.output;out.mkdir(exist_ok=False);runtime=out/'runtime';runtime.mkdir()
    shutil.copytree(a.source/'demo_runtime/demo_templates',runtime/'demo_templates')
    with sqlite3.connect(a.source/'demo_runtime/demo_payment.sqlite3') as src,sqlite3.connect(runtime/'demo_payment.sqlite3') as dst:src.backup(dst)
    records=json.loads((a.source/'input-manifest.json').read_text())
    # The saved manifest may wrap records; never infer a filtered cohort.
    if isinstance(records,dict):records=records['records']
    probes=sorted((r for r in records if r['index']>5),key=lambda r:(r['identity'],r['index']))
    assert len(records)==40 and len(probes)==20
    assert all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in records)
    debug_ui.common.RUNTIME=runtime;engine=PKLNetROI(threads=2)
    app=debug_ui.App(ReplayCamera(False,engine),demo_matcher='FastCCDemo-v6')
    unloaded=engine._session is None and engine._model is None
    start=dict(process_to_app_ready_ms=(time.perf_counter()-PROCESS_START)*1000,model_unloaded=unloaded,memory=memory())
    results=[]
    with http_app(app) as (request,trace):
        for kind,rows in [('cold',[probes[0]]),('warm',probes)]:
            for r in rows:
                app.camera.select([r]);prof=cProfile.Profile() if kind=='warm' and not any(x['kind']=='warm' for x in results) else None
                # Profiling the main HTTP client would miss the server thread.
                # Stage timings are recorded by the actual server response.
                status,result=request('/api/demo/identify',{},200)
                elapsed=trace[-1]['ms'];correct=result.get('user_id')==r['identity'].replace(':','-')
                results.append(dict(kind=kind,sample=r['sample'],correct=correct,http_ms=elapsed,stages=result['timing_ms'],memory=memory()))
                request('/api/demo/cancel',dict(token=result['token']),200)
                print(kind,r['index'],round(elapsed),correct,flush=True)
        cache_bytes=app.demo.gallery._prepared_cache_bytes
    warm=[r for r in results if r['kind']=='warm'];cold=[r for r in results if r['kind']=='cold']
    summary=dict(host=dict(platform=platform.platform(),logical_cpu_count=os.cpu_count()),startup=start,cold=cold,
        warm=dict(n=len(warm),correct=sum(r['correct'] for r in warm),median_ms=float(np.median([r['http_ms'] for r in warm])),p95_ms=float(np.percentile([r['http_ms'] for r in warm],95)),
                  stages={k:dict(median_ms=float(np.median([r['stages'][k] for r in warm])),p95_ms=float(np.percentile([r['stages'][k] for r in warm],95))) for k in warm[0]['stages']}),
        memory=memory(),prepared_cache_bytes=cache_bytes,notes='Local HTTP, file replay at camera boundary, copied simulated accounts, cancel only; no Pi/live camera/browser/render/network timing. Cold=one initially unloaded model and cache; warm=all 20 unchanged probes.')
    (out/'results.json').write_text(json.dumps(results,indent=2));(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
    assert all(r['correct'] for r in results)

if __name__=='__main__':main()
