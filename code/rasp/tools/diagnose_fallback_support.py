"""Shadow audit of evidence support for every frozen exhaustive decision.

No HTTP result/policy is changed. Existing accepted warps and per-frame minima
are observed once. Candidate RETRY rule is assessed separately from correctness.
"""
import argparse,hashlib,json,os,shutil,threading
from pathlib import Path
import cv2,numpy as np
from evaluate_six_person_frozen import initialize
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from pose_matcher import FastCCPoseMatcher
from anchored_matcher import source_quad,overlaps_anchor


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in('baseline','manifest','output'):p.add_argument(name,type=Path)
 p.add_argument('--native-registration',type=Path,required=True);p.add_argument('--model-root',type=Path,required=True)
 a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());assert b['complete'];rows={r['sample']:r for r in json.loads(a.manifest.read_text())};root=Path(__file__).resolve().parents[1]
 assert all(sha(root/n)==value for n,value in b['code_sha256'].items());assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
 report=dict(complete=False,baseline_sha256=sha(a.baseline/'results.json'),evaluator_sha256=sha(Path(__file__)),selection='All 13 exhaustive queries plus lexicographically first fast correct control per case',queries=[],initializations=[],power_samples=[],policy='Shadow only: weak exhaustive MATCH requires both best-two frames to have a strictly improving accepted geometric winner, whose source quads overlap one another under existing >1 pixel anchor rule; otherwise RETRY. Numerical thresholds unchanged.')
 source_hashes={str(path):sha(path)for path in a.baseline.glob('*/runtime/demo_templates/*')if path.is_file()}
 def checkpoint():
  value=power_sample();report['power_samples'].append(value);save_json(a.output/'results.json',report)
  if power_fault(value):raise RuntimeError('Power fault')
 checkpoint()
 for run in b['runs']:
  selected=[q for q in run['queries']if q['result']['recognition_route']=='exhaustive_fallback']
  selected.append(min((q for q in run['queries']if q['correct']and q['ms']<=2500),key=lambda q:q['sample']))
  source=a.baseline/run['case']/'runtime';runtime=a.output/run['case']/'runtime';runtime.parent.mkdir();shutil.copytree(source,runtime,ignore=shutil.ignore_patterns('demo_templates'));store=runtime/'demo_templates';store.mkdir()
  for path in(source/'demo_templates').iterdir():
   if path.is_file():(store/path.name).symlink_to(path.resolve())
  app,camera,startup=initialize(runtime,b['matcher'],a.native_registration);report['initializations'].append(dict(case=run['case'],startup=startup));active=[None];target_ids={};local=threading.local()
  old_pose=FastCCPoseMatcher.match;old_align=app.demo_algorithm.legacy._aligned_score;old_pair=app.demo_algorithm._match_unpacked;old_scores=app.demo_algorithm.score_gallery
  def pose(owner,probe,candidate):
   value=old_pose(owner,probe,candidate)
   if getattr(local,'pair',None)is not None:local.pair['pose_score']=value
   return value
  def align(context,source,size,other,transform,fallback):
   value=old_align(context,source,size,other,transform,fallback)
   if getattr(local,'pair',None)is not None and value<fallback:
    warp=np.diag([1/3,1/3,1])@transform@source;corners=np.array([[0,0,1],[128,0,1],[128,128,1],[0,128,1.]])@np.linalg.inv(warp).T;quad=corners[:,:2]/corners[:,2:]
    local.pair['legacy_improvements'].append(dict(score=value,quad=quad.tolist(),transform=transform.tolist(),source=source.tolist()))
   return value
  def pair(query,target,details=None):
   item=dict(target=target_ids.get(id(target)),legacy_improvements=[]);previous=getattr(local,'pair',None);local.pair=item;attempts=[]
   try:value=old_pair(query,target,attempts)
   finally:local.pair=previous
   assert item['target']is not None;pose_score=item['pose_score'];quads=[]
   if value<pose_score:
    quads.extend(v['quad']for v in item['legacy_improvements']if v['score']==value)
    quads.extend(v['aligned_quad']for v in attempts if v.get('score')==value and v.get('branch')=='union')
   item.update(score=value,winning_quads=quads,attempts=attempts,anchor_quad=source_quad(query[1][2]).tolist())
   if active[0]is not None:active[0]['pairs'].append(item)
   if details is not None:details.extend(attempts)
   return value
  def scores(probe,groups):
   target_ids.clear();target_ids.update({id(s[3]):dict(identity=user,index=i)for user,ss in groups.items()for i,s in enumerate(ss)})
   values=old_scores(probe,groups)
   if active[0]is not None:active[0]['scores']=dict(values)
   return values
  FastCCPoseMatcher.match=pose;app.demo_algorithm.legacy._aligned_score=align;app.demo_algorithm._match_unpacked=pair;app.demo_algorithm.score_gallery=scores
  before=app.demo.payments.transaction_count()
  try:
   with http_app(app)as(request,trace):
    for ref in selected:
     checkpoint();row=rows[ref['sample']];assert sha(Path(row['original']))==row['sha256'];camera.select([row]);active[0]=dict(pairs=[])
     status,response=request('/api/demo/identify',{},None);data=active[0];active[0]=None
     equal=status==ref['http_status']and all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'));assert equal
     assert data['scores']==ref['diagnostics']['scores']
     selected_pairs=sorted([v for v in data['pairs']if v['target']['identity']==response.get('user_id')],key=lambda v:v['score'])[:2]
     support=bool(len(selected_pairs)==2 and all(v['winning_quads']for v in selected_pairs)and any(overlaps_anchor(x,y)for x in selected_pairs[0]['winning_quads']for y in selected_pairs[1]['winning_quads']))
     weak=response.get('recognition_route')=='exhaustive_fallback'and not app.demo_algorithm.confident(data['scores'])
     trial=dict(case=run['case'],sample=ref['sample'],reference_correct=ref['correct'],reference_equal=equal,http_ms=trace[-1]['ms'],result={k:v for k,v in response.items()if k not in('roi_image','token','expires_at')},supported_best_two=support,shadow_status='RETRY'if weak and not support else response.get('status'),selected_pairs=selected_pairs,**data)
     report['queries'].append(trial)
     if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
     checkpoint();print(run['case'],ref['sample'],ref['correct'],support,trial['shadow_status'],flush=True)
   assert app.demo.payments.transaction_count()==before
  finally:FastCCPoseMatcher.match=old_pose;app.demo_algorithm.close()
 report['source_templates_unchanged']=all(sha(Path(path))==value for path,value in source_hashes.items());assert report['source_templates_unchanged'];report['complete']=True;checkpoint()


if __name__=='__main__':main()
