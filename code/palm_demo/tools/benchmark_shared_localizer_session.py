"""ABBA fresh-process HTTP pilot for sharing PKLNet's loaded ONNX session.

Every inference still runs, unchanged. This is not SIFT/registration memoization,
not parallel localization, not query caching and not production configuration.
"""
import argparse,base64,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
import numpy as np,cv2
from evaluate_six_person_frozen import initialize
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification
from pklnet_roi import PKLNetROI
from union_matcher import FastCCWindowUnionMatcher
from shared_localizer_session_pilot import shared_heatmap_view


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('suite','run'))
 for name in ('baseline','manifest','output'):p.add_argument(name,type=Path)
 p.add_argument('--native-registration',type=Path,required=True);p.add_argument('--model-root',type=Path,required=True)
 p.add_argument('--runtime',type=Path);p.add_argument('--case');p.add_argument('--samples',nargs='+');p.add_argument('--mode',choices=('baseline','shared'))
 a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());assert b['complete']
 app_root=Path(__file__).resolve().parents[1];assert all(sha(app_root/n)==value for n,value in b['code_sha256'].items())
 assert sha(a.native_registration)=='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600'
 rows={r['sample']:r for r in json.loads(a.manifest.read_text())};refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']}
 if a.action=='suite':
  assert not a.output.exists();a.output.mkdir();case,hard=max(refs,key=lambda k:refs[k]['ms'])
  other=min(sample for (c,sample),q in refs.items()if c==case and sample!=hard and q['result'].get('recognition_route')=='exhaustive_fallback')
  control=min(sample for (c,sample),q in refs.items()if c==case and q['correct']and q['ms']<=2500)
  samples=[hard,other,control];runtime=a.output/'runtime';shutil.copytree(a.baseline/case/'runtime',runtime)
  source_hashes={str(path):sha(path)for path in(a.baseline/case/'runtime/demo_templates').iterdir()if path.is_file()}
  report=dict(complete=False,case=case,samples=samples,baseline_sha256=sha(a.baseline/'results.json'),manifest_sha256=sha(a.manifest),
   evaluator_sha256=sha(Path(__file__)),mechanism_sha256=sha(Path(__file__).with_name('shared_localizer_session_pilot.py')),
   design='Four fresh processes ABBA, same full gallery, three fixed queries repeated twice per process; no query outputs reused',runs=[])
  for index,mode in enumerate(('baseline','shared','shared','baseline')):
   power=power_sample();assert not power_fault(power),power
   out=a.output/f'run-{index:02d}';cmd=[sys.executable,str(Path(__file__)), 'run',str(a.baseline),str(a.manifest),str(out),
    '--native-registration',str(a.native_registration),'--model-root',str(a.model_root),'--runtime',str(runtime),'--case',case,'--samples',*samples,'--mode',mode]
   with(a.output/f'run-{index:02d}.log').open('x')as log:
    result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_WAIT_POLICY='PASSIVE'))
   if result.returncode:raise RuntimeError(f'Child {index} failed: {result.returncode}; inspect retained log')
   run=json.loads((out/'results.json').read_text());assert run['complete']and run['all_reference_equal'];report['runs'].append(run)
   if index:
    expected={(q['sample'],q['repeat']):q for q in report['runs'][0]['queries']}
    for q in run['queries']:
     ref=expected[q['sample'],q['repeat']]
     assert q['localizer_signatures']==ref['localizer_signatures'],('localizer parity',mode,q['sample'])
     assert q['roi_sha256']==ref['roi_sha256'],('ROI parity',mode,q['sample'])
   save_json(a.output/'summary.json',report);print(index,mode,'reference and geometry parity',flush=True)
  hard_times={mode:{repeat:[q['http_ms']for run in report['runs']if run['mode']==mode for q in run['queries']if q['sample']==hard and q['repeat']==repeat]for repeat in (0,1)}for mode in('baseline','shared')}
  aw=hard_times['baseline'][1];bw=hard_times['shared'][1];ac=hard_times['baseline'][0];bc=hard_times['shared'][0]
  gain=float(np.median(aw)-np.median(bw));required=max(100.,.05*float(np.median(aw)))
  report.update(hard_times=hard_times,warm_median_gain_ms=gain,required_warm_gain_ms=required,
   passes_sustained_gate=bool(gain>=required and min(aw)>=max(bw)+100 and max(bc)<=max(ac)),
   source_templates_unchanged=all(sha(Path(path))==value for path,value in source_hashes.items()),complete=True)
  assert report['source_templates_unchanged'];save_json(a.output/'summary.json',report)
  print(json.dumps({k:report[k]for k in('hard_times','warm_median_gain_ms','required_warm_gain_ms','passes_sustained_gate')}),flush=True);return
 assert a.runtime and a.case and a.samples and a.mode
 a.output.mkdir(exist_ok=False);cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
 report=dict(mode=a.mode,case=a.case,fresh_process=True,pid=os.getpid(),queries=[],power_samples=[],complete=False)
 def checkpoint():
  value=power_sample();report['power_samples'].append(value);save_json(a.output/'results.json',report)
  if power_fault(value):raise RuntimeError('Power fault')
 checkpoint();old_complete=FastCCWindowUnionMatcher.complete_hypotheses;old_extract=PKLNetROI._extract_once;active=[None]
 if a.mode=='shared':
  def complete(owner,full,candidates,localizer):
   if owner._window_engine is None:owner._window_engine=shared_heatmap_view(localizer)
   return old_complete(owner,full,candidates,localizer)
  FastCCWindowUnionMatcher.complete_hypotheses=complete
 def extract(owner,image,**kw):
  value=old_extract(owner,image,**kw)
  if active[0] is not None:
   pixels,quad,details=value
   active[0].append(dict(policy=owner.policy,image_size=list(image.size),roi_sha256=hashlib.sha256(np.asarray(pixels).tobytes()).hexdigest(),
    quad_sha256=hashlib.sha256(np.asarray(quad).tobytes()).hexdigest(),diagnostic_sha256=hashlib.sha256(json.dumps(details,sort_keys=True,allow_nan=False).encode()).hexdigest()))
  return value
 PKLNetROI._extract_once=extract
 try:
  app,camera,startup=initialize(a.runtime,b['matcher'],a.native_registration);report['initialization_ready']=startup
  assert app.demo.gallery.threshold==1.0 and app.demo.gallery.min_margin==0.0
  before=app.demo.payments.transaction_count()
  with http_app(app)as(request,trace):
   for repeat in range(2):
    for sample in a.samples:
     checkpoint();row=rows[sample];assert sha(Path(row['original']))==row['sha256'];camera.select([row]);active[0]=[]
     status,response=request('/api/demo/identify',{},None);signatures=active[0];active[0]=None;ref=refs[a.case,sample]
     equal=status==ref['http_status']and all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'))
     pixels=base64.b64decode(response['roi_image'].split(',')[-1]);baseline_roi=a.baseline/a.case/'query-rois'/(sample+'.png');assert pixels==baseline_roi.read_bytes()
     window=app.demo_algorithm._window_engine;parent=camera.tracker.extractor
     trial=dict(sample=sample,repeat=repeat,http_ms=trace[-1]['ms'],http_status=status,result={k:v for k,v in response.items()if k not in('roi_image','token','expires_at')},
      reference_equal=equal,correct=correct_identification(dict(http_status=status,result=response,identity=row['identity'])),
      roi_sha256=hashlib.sha256(pixels).hexdigest(),localizer_signatures=signatures,
      window_session_loaded=bool(window is not None and window._session is not None),
      window_session_is_parent=bool(window is not None and window._session is not None and window._session is parent._session))
     report['queries'].append(trial)
     if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
     checkpoint();assert equal,(sample,response);assert app.demo.payments.transaction_count()==before
     print(a.mode,sample,repeat,round(trial['http_ms']),equal,len(signatures),trial['window_session_is_parent'],flush=True)
  report.update(all_reference_equal=all(q['reference_equal']for q in report['queries']),transactions_unchanged=True,complete=True);checkpoint()
 finally:
  PKLNetROI._extract_once=old_extract;FastCCWindowUnionMatcher.complete_hypotheses=old_complete
  if 'app'in locals():app.demo_algorithm.close()


if __name__=='__main__':main()
