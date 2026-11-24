"""Scalar operation costs and private-memory SIFT-output oracle on frozen Pi queries.

Oracle replay uses pre-recorded outputs for the identical request/call graph.
It is a cost counterfactual, never a production speedup or new recognition result.
"""
import argparse,base64,hashlib,importlib,json,os,shutil,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import cv2,numpy as np,onnxruntime as ort
from operation_cost_oracle import OperationTrace,FeatureOracle
from evaluate_six_person_frozen import initialize
from replay_pi_pipeline import http_app,save_json,ReplayCamera,debug_ui
from replay_ready_queries import power_sample,power_fault
from demo_flow import DemoFlow
from gallery import Gallery
from registered_matcher import FastCCRegisteredMatcher
from union_matcher import FastCCWindowUnionMatcher
from demo_matcher import FastCCDemoMatcher
from fastcc_accelerated import AcceleratedFastCC
from native_registration import NativeRegistration
from pklnet_roi import PKLNetROI


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in('baseline','manifest','output'):p.add_argument(name,type=Path)
 p.add_argument('--model-root',type=Path,required=True);p.add_argument('--native-registration',type=Path,required=True)
 p.add_argument('--part',choices=('pilot','remaining','audit'),required=True)
 a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());assert b['complete'];rows={v['sample']:v for v in json.loads(a.manifest.read_text())}
 app_root=Path(__file__).resolve().parents[1];assert all(sha(app_root/n)==h for n,h in b['code_sha256'].items())
 refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']};hard=max(refs,key=lambda k:refs[k]['ms'])
 selected={k for k,q in refs.items()if not q['correct']};selected.add(hard)
 for case in {c for c,s in selected}:
  selected.add(min((k for k,q in refs.items()if k[0]==case and q['correct']and q['ms']<=2500),key=lambda k:k[1]))
 pilot={hard,min((k for k,q in refs.items()if k[0]==hard[0]and q['correct']and q['ms']<=2500),key=lambda k:k[1])}
 selected=pilot if a.part=='pilot'else selected-pilot if a.part=='remaining'else{k for k in selected if not refs[k]['correct']or k==hard}
 assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
 report=dict(complete=False,part=a.part,selection=sorted(selected),baseline_sha256=sha(a.baseline/'results.json'),evaluator_sha256=sha(Path(__file__)),helper_sha256=sha(Path(__file__).with_name('operation_cost_oracle.py')),warning=__doc__,initializations=[],queries=[],power_samples=[])
 source_hashes={str(p):sha(p)for p in a.baseline.glob('*/runtime/demo_templates/*')if p.is_file()}
 trace=OperationTrace();oracle=FeatureOracle(trace);oracle.install_submit(ThreadPoolExecutor)
 for name in('registered_matcher','union_matcher','indexed_demo_matcher','staged_index_matcher','pooled_enrollment_matcher','demo_matcher'):
  module=importlib.import_module(name)
  if hasattr(module,'local_features'):oracle.wrap(module,'local_features',name+'.local_features')
 oracle.wrap(FastCCRegisteredMatcher,'local_features','registered.static.local_features',static=True)
 oracle.wrap(FastCCWindowUnionMatcher,'local_features','union.static.local_features',static=True)
 for owner,name,label,cat,static in[
  (DemoFlow,'identify','demo.identify','framework',False),(Gallery,'identify','gallery.identify','framework',False),
  (ReplayCamera,'capture_highres','read_original','input_io',False),
  (PKLNetROI,'_prepare','model.prepare','model_preprocess',True),
  (ort.InferenceSession,'run','onnx.run','model_inference',False),
  (AcceleratedFastCC,'extract','fastcc.extract','binary_descriptor',False),
  (AcceleratedFastCC,'match','fastcc.match','distance_matching',False),
  (NativeRegistration,'pairs','native.descriptor_pairs','distance_matching',False),
  (NativeRegistration,'__call__','native.registration','geometry_control',False),
  (FastCCWindowUnionMatcher,'_pack','feature.pack','pack_copy',False),
  (FastCCWindowUnionMatcher,'_unpack','feature.unpack','decode_parse',False),
  (FastCCWindowUnionMatcher,'_match_unpacked','fallback.frame','framework',False),
  (FastCCDemoMatcher,'score_prepared','fallback.identity_five_frames','framework',False)]:trace.wrap(owner,name,label,cat,static=static)
 for name in('warpPerspective','getPerspectiveTransform','GaussianBlur','cvtColor','rotate','resize','estimateAffinePartial2D','estimateAffine2D'):
  trace.wrap(cv2,name,'cv2.'+name,'geometry'if name.startswith('estimate')else'image_transform')
 for name in('matchTemplate','gemm','integral'):trace.wrap(cv2,name,'cv2.'+name,'distance_matching')
 trace.wrap(cv2,'filter2D','cv2.filter2D','binary_descriptor')
 for name in('imencode','imdecode'):trace.wrap(cv2,name,'cv2.'+name,'codec_copy')
 for name in('ascontiguousarray','concatenate','stack','pad','zeros'):trace.wrap(np,name,'np.'+name,'array_conversion_allocation')
 trace.wrap(np.linalg,'inv','np.linalg.inv','geometry')
 def checkpoint():
  power=power_sample();report['power_samples'].append(power);save_json(a.output/'results.json',report)
  if power_fault(power):raise RuntimeError('Power fault')
 try:
  checkpoint()
  for run in b['runs']:
   samples=sorted(s for c,s in selected if c==run['case'])
   if not samples:continue
   source=a.baseline/run['case']/'runtime';runtime=a.output/run['case']/'runtime';runtime.parent.mkdir()
   shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'));store=runtime/'demo_templates';store.mkdir()
   for original in(source/'demo_templates').iterdir():
    if original.is_file():(store/original.name).symlink_to(original.resolve())
   app,camera,startup=initialize(runtime,b['matcher'],a.native_registration);report['initializations'].append(dict(case=run['case'],startup=startup,templates='Read-only identification operations through links to frozen experimental templates; writable DBs copied separately'))
   assert app.demo.gallery.threshold==1.0 and app.demo.gallery.min_margin==0.0
   before=app.demo.payments.transaction_count()
   numeric={};target_ids={};original_score=app.demo_algorithm.score_gallery;original_pair=app.demo_algorithm._match_unpacked
   def scores(probe,groups):
    target_ids.clear();target_ids.update({id(sample[3]):dict(identity=user,index=i)for user,samples in groups.items()for i,sample in enumerate(samples)})
    value=original_score(probe,groups);numeric['scores']=dict(value);return value
   def pair(query,target,details=None):
    value=original_pair(query,target,details)
    numeric.setdefault('pairs',[]).append(dict(target=target_ids.get(id(target)),score=value));return value
   app.demo_algorithm.score_gallery=scores;app.demo_algorithm._match_unpacked=pair
   try:
    with http_app(app)as(request,http_trace):
     for sample in samples:
      row=rows[sample];assert sha(Path(row['original']))==row['sha256'];ref=refs[run['case'],sample];query=dict(case=run['case'],sample=sample,reference_correct=ref['correct'],baseline_http_ms=ref['ms'],phases=[]);report['queries'].append(query);oracle.clear()
      phases=(('record_profile','record'),('verify_replay','verify'))if a.part=='audit'else(('record_profile','record'),('plain_before','plain'),('verify_replay','verify'),('timed_replay','timed'),('plain_after','plain'))
      for phase,mode in phases:
       checkpoint();camera.select([row]);numeric.clear();oracle.begin(mode)
       if mode=='record':trace.begin()
       cpu=time.process_time();status,response=request('/api/demo/identify',{},None);process_cpu_ms=(time.process_time()-cpu)*1000
       costs=trace.finish()if mode=='record'else None;memory=oracle.finish()
       equal=status==ref['http_status']and all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'))
       pixels=base64.b64decode(response['roi_image'].split(',')[-1]);assert pixels==(a.baseline/run['case']/'query-rois'/(sample+'.png')).read_bytes()
       pair_values=sorted(numeric.get('pairs',[]),key=lambda v:(v['target']['identity'],v['target']['index']))
       if a.part=='audit':
        assert numeric['scores']==ref['diagnostics']['scores'],'Whole-gallery numerical drift'
        if query['phases']:assert pair_values==query['phases'][0]['pair_scores'],'Per-frame numerical drift'
       trial=dict(candidate_scores=numeric.get('scores'),pair_scores=pair_values,phase=phase,http_ms=http_trace[-1]['ms'],process_cpu_ms=process_cpu_ms,http_status=status,result={k:v for k,v in response.items()if k not in('roi_image','token','expires_at')},reference_equal=equal,roi_sha256=hashlib.sha256(pixels).hexdigest(),oracle=memory)
       if costs is not None:trial['operation_profile']=costs
       query['phases'].append(trial)
       if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
       checkpoint();assert equal,(sample,phase);assert app.demo.payments.transaction_count()==before
       print(run['case'],sample,phase,round(trial['http_ms']),equal,memory['feature_calls'],flush=True)
      assert len({p['oracle']['feature_calls']for p in query['phases']})==1,'Feature call-count drift'
      oracle.clear()
   finally:app.demo_algorithm.close()
  report['source_templates_unchanged']=all(sha(Path(path))==value for path,value in source_hashes.items());assert report['source_templates_unchanged'];report['complete']=True;checkpoint()
 finally:oracle.close();trace.close()


if __name__=='__main__':main()
