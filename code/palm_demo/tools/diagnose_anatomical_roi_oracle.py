"""Locked anatomical ROI 2x2 diagnostic using frozen v26 pair matcher.

Preregistered enrollment frames per true/competing identity; string selects
its original first frame, list selects protocol frames in their saved order. This is
not gallery accuracy or HTTP latency; manual ROI is an oracle diagnostic only.
No writes to templates, no live camera and no localizer/model retraining.
"""
import argparse,hashlib,json,os,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image
from biometric import load_algorithm
from native_registration import enable_native_registration
from pklnet_roi import normalize_roi_pixels
from replay_ready_queries import power_sample,power_fault
from replay_pi_pipeline import save_json
from pose_matcher import FastCCPoseMatcher


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('locked','manifest','baseline','diagnostics','geometry','output'):p.add_argument(name,type=Path)
 p.add_argument('--native-registration',type=Path,required=True);p.add_argument('--model-root',type=Path,required=True)
 a=p.parse_args();lock=json.loads(a.locked.read_text());manifest={r['sample']:r for r in json.loads(a.manifest.read_text())}
 baseline=json.loads((a.baseline/'results.json').read_text());diag=json.loads(a.diagnostics.read_text());geometry=json.loads(a.geometry.read_text())['records']
 assert baseline['complete']and diag['complete']and diag['all_reference_equal']
 assert diag['baseline_results_sha256']==sha(a.baseline/'results.json')
 app_root=Path(__file__).resolve().parents[1]
 assert all(sha(app_root/name)==value for name,value in baseline['code_sha256'].items())
 assert sha(a.native_registration)=='272857b624cad687b7d87a32eb79ac0124f3d782be3e3a2b0ca092c92d87e600'
 assert not a.output.exists();a.output.mkdir()
 os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve());cv2.setNumThreads(1)
 algorithm=load_algorithm(app_root/'vendor/palmprint-recognition-python',baseline['matcher']);enable_native_registration(algorithm,a.native_registration,1)
 refs={(r['case'],q['sample']):q for r in baseline['runs']for q in r['queries']};traces={(q['case'],q['sample']):q for q in diag['queries']}
 locked={r['sample']:r for r in lock['blind_rows']};stored={(r['case'],r['sample']):r for r in geometry}
 report=dict(protocol_sha256=sha(a.locked),warning=__doc__,selection=lock['selection'],rule=lock['rule'],orientation_rule=lock['orientation_rule'],queries=[],power_samples=[],complete=False)
 current=[None];original_pose=FastCCPoseMatcher.match;original_aligned=algorithm.legacy._aligned_score;original_cv=[]
 def pose(owner,probe,candidate):
  probe=owner._validate(probe);candidate=owner._validate(candidate);base=candidate[0].astype(bool)
  values=[dict(index=i,score=float(owner.base.match(v.astype(bool),base)))for i,v in enumerate(probe)if v[0,0]>=0]
  if current[0] is not None:current[0]['pose'].append(dict(views=values,winner=min(values,key=lambda v:v['score'])))
  return min(v['score']for v in values)
 def aligned(context,source,size,other,transform,fallback):
  value=original_aligned(context,source,size,other,transform,fallback)
  if current[0] is not None:current[0]['legacy_alignment'].append(dict(score=value,fallback=fallback,improved=value<fallback,matrix=transform.tolist()))
  return value
 FastCCPoseMatcher.match=pose;algorithm.legacy._aligned_score=aligned
 for name in ('estimateAffinePartial2D','estimateAffine2D'):
  old=getattr(cv2,name);original_cv.append((name,old))
  def observe(*args,_old=old,_name=name,**kw):
   value=_old(*args,**kw)
   if current[0] is not None:
    matrix,mask=value;keep=None if mask is None else mask.ravel().astype(bool);n=0 if keep is None else int(keep.sum())
    coverage=min(cv2.contourArea(cv2.convexHull(np.asarray(v,np.float32).reshape(-1,2)[keep]))for v in args[:2])/(384*384)if n>=3 else 0.
    current[0]['estimates'].append(dict(kind=_name,inliers=n,coverage=float(coverage),matrix=None if matrix is None else matrix.tolist()))
   return value
  setattr(cv2,name,observe)
 def checkpoint():
  sample=power_sample();report['power_samples'].append(sample);save_json(a.output/'results.json',report)
  if power_fault(sample):raise RuntimeError('Pi power fault')
 def full(sample):
  row=manifest[sample];path=Path(row['original']);assert sha(path)==row['sha256'];return Image.open(path).convert('RGB')
 def roi(image,quad):return normalize_roi_pixels(algorithm.geometry.getROIimg(cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR),np.asarray(quad,np.float32),side=128,ratio=1.0))
 gallery={};template_hashes={}
 try:
  checkpoint()
  for selection in lock['selected']:
   case=selection['case'];sample=selection['sample'];ref=refs[case,sample];image=full(sample);trace=traces.get((case,sample));entry=dict(**selection,cells=[],skipped=[],reference_pair_parity=[]);report['queries'].append(entry)
   original_quad=locked[sample]['original_quad'];hypotheses=([dict(valid=v['valid'],quad=v['quad'],kind=v['kind'])for v in trace['candidate_decisions'][0]['decisions']]if trace else[dict(valid=True,quad=original_quad,kind='base')])
   queries={}
   for qmode in ('original','oracle'):
    checkpoint()
    if qmode=='oracle'and not locked[sample]['available']:entry['skipped'].append(dict(query=qmode,reason=locked[sample]['reason']));continue
    quad=original_quad if qmode=='original'else locked[sample]['quad']
    pixels=np.asarray(Image.open(a.baseline/case/'query-rois'/(sample+'.png')).convert('L'))if qmode=='original'else roi(image,quad)
    features=algorithm.extract_with_hypotheses(image,np.asarray(quad,np.float32),pixels,hypotheses)
    queries[qmode]=algorithm._unpack(features)
   for identity,enrolled_samples in selection['enrollments'].items():
    for enrollment_index,enrolled_sample in enumerate(enrolled_samples if isinstance(enrolled_samples,list)else[enrolled_samples]):
     user=identity.replace(':','-');key=(case,user,enrollment_index);path=a.baseline/case/'runtime/demo_templates'/(user+'.npz');template_hashes[str(path)]=sha(path)
     if key not in gallery:
      with np.load(path,allow_pickle=False)as z:original=z['features'][enrollment_index].copy()
      gallery[key]={'original':algorithm._unpack(original,decode_native=False)}
      if locked[enrolled_sample]['available']:
       enrolled_image=full(enrolled_sample);quad=locked[enrolled_sample]['quad'];features=algorithm.extract_gallery_with_context(enrolled_image,np.asarray(quad,np.float32),roi(enrolled_image,quad));gallery[key]['oracle']=algorithm._unpack(features,decode_native=False)
     for qmode,query in queries.items():
      for emode in ('original','oracle'):
       if emode not in gallery[key]:entry['skipped'].append(dict(query=qmode,enrollment=emode,identity=identity,reason=locked[enrolled_sample]['reason']));continue
       checkpoint();details=dict(pose=[],legacy_alignment=[],estimates=[]);current[0]=details;attempts=[];start=time.perf_counter()
       score=algorithm._match_unpacked(query,gallery[key][emode],attempts);current[0]=None
       cell=dict(identity=identity,enrollment_index=enrollment_index,enrollment_sample=enrolled_sample,query_roi=qmode,enrollment_roi=emode,score=score,winner=min((v for v in attempts if 'score'in v),key=lambda v:v['score']),attempts=attempts,diagnostic_pair_ms=(time.perf_counter()-start)*1000,**details)
       entry['cells'].append(cell)
       if trace and qmode==emode=='original':
        expected=next(v['score']for v in trace['pairs']if v['target']==dict(identity=user,index=enrollment_index));entry['reference_pair_parity'].append(dict(identity=identity,expected=expected,actual=score,equal=score==expected))
       checkpoint()
   print(case,sample,'cells',len(entry['cells']),'parity',entry['reference_pair_parity'],flush=True)
  report['templates_unchanged']=all(sha(Path(path))==value for path,value in template_hashes.items());assert report['templates_unchanged']
  report['all_reference_pair_equal']=all(v['equal']for q in report['queries']for v in q['reference_pair_parity']);report['complete']=True;checkpoint()
 finally:
  FastCCPoseMatcher.match=original_pose
  for name,old in original_cv:setattr(cv2,name,old)
  algorithm.close()


if __name__=='__main__':main()
