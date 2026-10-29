"""Pi HTTP timing tree with exclusive same-thread times and separate worker telemetry.

Instrumented development diagnostics only. Worker intervals overlap the request
thread and MUST NOT be added to HTTP wall time. --oracle-candidate skips retrieval
using known truth but keeps the actual exhaustive feature and five-frame matcher;
its results are not identification accuracy or normal-gallery latency.
"""
import argparse,hashlib,json,os,shutil,threading,time
from pathlib import Path
from collections import Counter
import cv2
from evaluate_six_person_frozen import initialize,sanitized
from replay_pi_pipeline import http_app,save_json,ReplayCamera,debug_ui
from replay_ready_queries import power_sample,power_fault
from gallery import Gallery
from demo_flow import DemoFlow
from pklnet_roi import PKLNetROI
from demo_matcher import FastCCDemoMatcher
from union_matcher import FastCCWindowUnionMatcher
from pose_matcher import FastCCPoseMatcher
from staged_index_matcher import StagedIndexMatcher
from pooled_enrollment_matcher import PooledEnrollmentMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from affine_enrollment_matcher import AffineEnrollmentMatcher
from compnet_evidence_matcher import CompNetEvidenceMatcher
from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher


class TimingTree:
 def __init__(self):self.active=False;self.nodes=[];self.local=threading.local();self.lock=threading.Lock();self.originals=[]
 def wrap(self,owner,name,label):
  old=getattr(owner,name);self.originals.append((owner,name,old))
  def call(*args,**kw):
   if not self.active:return old(*args,**kw)
   parent=getattr(self.local,'node',None);start=time.perf_counter()
   with self.lock:
    node=dict(id=len(self.nodes),parent=None if parent is None else parent['id'],thread=threading.get_ident(),label=label,start_ms=(start-self.start)*1000,children_ms=0.)
    self.nodes.append(node)
   self.local.node=node
   try:return old(*args,**kw)
   finally:
    node['inclusive_ms']=(time.perf_counter()-start)*1000;node['exclusive_ms']=node['inclusive_ms']-node.pop('children_ms');self.local.node=parent
    if parent is not None:parent['children_ms']+=node['inclusive_ms']
  setattr(owner,name,call)
 def begin(self):self.nodes=[];self.start=time.perf_counter();self.active=True
 def end(self):self.active=False;return self.nodes
 def close(self):
  for owner,name,old in reversed(self.originals):setattr(owner,name,old)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('baseline','manifest','output'):p.add_argument(name,type=Path)
 p.add_argument('--native-registration',type=Path,required=True);p.add_argument('--model-root',type=Path,required=True);p.add_argument('--oracle-candidate',action='store_true')
 a=p.parse_args();b=json.loads((a.baseline/'results.json').read_text());rows={r['sample']:r for r in json.loads(a.manifest.read_text())};assert b['complete']
 root=Path(__file__).resolve().parents[1];assert all(sha(root/n)==h for n,h in b['code_sha256'].items());assert not a.output.exists();a.output.mkdir();cv2.setNumThreads(1);os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve())
 refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']};selected={k for k,q in refs.items()if q['ms']>2500}
 if a.oracle_candidate:
  selected={k for k,q in refs.items()if not q['correct']};selected.add(max(refs,key=lambda k:refs[k]['ms']))
 else:
  for run in b['runs']:
   q=min((q for q in run['queries']if q['correct']and q['ms']<=2500),key=lambda q:q['sample']);selected.add((run['case'],q['sample']))
 tree=TimingTree()
 for owner,name,label in [(DemoFlow,'identify','demo_identify'),(debug_ui.App,'capture_demo_feature','capture_extract'),(debug_ui.App,'detect_full_still','localization'),(ReplayCamera,'capture_highres','read_original'),(Gallery,'identify','gallery'),(PKLNetROI,'_extract_once','localizer_once'),(FastCCPoseMatcher,'extract_with_context','pose_features'),(StagedIndexMatcher,'score_gallery','staged_gallery'),(StagedIndexMatcher,'_stage_views','context_features'),(PooledEnrollmentMatcher,'_legacy_probe','legacy_features'),(LinkedEnrollmentMatcher,'_enrollment_link_stage','enrollment_links'),(AffineEnrollmentMatcher,'_enrollment_link_stage','links_affine'),(PooledEnrollmentMatcher,'_pool_stage','pool_stage'),(FastCCWindowUnionMatcher,'complete_hypotheses','extra_localization'),(FastCCWindowUnionMatcher,'extract_with_hypotheses','fallback_features'),(FastCCWindowUnionMatcher,'_hypothesis_views','hypothesis_features'),(FastCCWindowUnionMatcher,'_match_unpacked','fallback_pair'),(FastCCDemoMatcher,'score_prepared','fallback_identity'),(CompNetEvidenceMatcher,'_auxiliary_scores','primary_embedding'),(CompNetAlternateROIMatcher,'_auxiliary_scores','embedding_total')]:tree.wrap(owner,name,label)
 report=dict(evaluator_sha256=sha(Path(__file__)),warning=__doc__,oracle_candidate=a.oracle_candidate,selection=sorted(selected),baseline_sha256=sha(a.baseline/'results.json'),queries=[],initializations=[],power_samples=[],complete=False)
 source_hashes={str(p):sha(p) for p in a.baseline.glob('*/runtime/demo_templates/*')if p.is_file()}
 def checkpoint():
  power=power_sample();report['power_samples'].append(power);save_json(a.output/'results.json',report)
  if power_fault(power):raise RuntimeError('Power fault')
 try:
  checkpoint()
  for run in b['runs']:
   chosen=sorted(sample for case,sample in selected if case==run['case'])
   if not chosen:continue
   runtime=a.output/run['case']/'runtime';runtime.parent.mkdir()
   source_runtime=a.baseline/run['case']/'runtime'
   if a.oracle_candidate:
    # Only the preselected true identities are needed by this oracle. Copy DBs
    # normally; never hardlink a writable database or modify source templates.
    shutil.copytree(source_runtime,runtime,ignore=shutil.ignore_patterns('demo_templates'))
    target_store=runtime/'demo_templates';target_store.mkdir()
    truth_users={rows[s]['identity'].replace(':','-') for s in chosen}
    for user in truth_users:
     for suffix in ('.npz','.json'):shutil.copy2(source_runtime/'demo_templates'/(user+suffix),target_store/(user+suffix))
   else:shutil.copytree(source_runtime,runtime)
   app,camera,startup=initialize(runtime,b['matcher'],a.native_registration);report['initializations'].append(dict(case=run['case'],startup=startup));before=app.demo.payments.transaction_count();old=app.demo_algorithm.score_gallery;active={}
   def score(probe,groups):
    active['gallery_identities']=len(groups);active['gallery_template_frames']=sum(len(v)for v in groups.values())
    if a.oracle_candidate:
     user=active['truth'];assert user in groups
     complete=app.demo_algorithm._unpack(probe.exhaustive());probe.route='oracle_true_candidate_full_features'
     active['evaluated_identities']=1;active['evaluated_template_frames']=len(groups[user])
     value=FastCCDemoMatcher.score_prepared(app.demo_algorithm,complete,[s[3]for s in groups[user]])
     active['true_score_equal']=value==active['expected_true_score']
     return {user:value}
    return old(probe,groups)
   app.demo_algorithm.score_gallery=score
   try:
    with http_app(app)as(request,trace):
     for sample in chosen:
      checkpoint();row=rows[sample];assert sha(Path(row['original']))==row['sha256'];camera.select([row]);active.clear();active['truth']=row['identity'].replace(':','-')
      if a.oracle_candidate:active['expected_true_score']=refs[run['case'],sample]['diagnostics']['scores'][active['truth']]
      tree.begin()
      status,response=request('/api/demo/identify',{},None);nodes=tree.end();ref=refs[run['case'],sample]
      roots=[n for n in nodes if n['label']=='demo_identify'];assert len(roots)==1;main_thread=roots[0]['thread'];main=[n for n in nodes if n['thread']==main_thread]
      counts=Counter(n['label']for n in nodes);sums=Counter()
      for n in main:sums[n['label']]+=n['exclusive_ms']
      total=sum(sums.values());assert abs(total-roots[0]['inclusive_ms'])<.1
      trial=dict(case=run['case'],sample=sample,reference_correct=ref['correct'],baseline_http_ms=ref['ms'],http_ms=trace[-1]['ms'],http_status=status,result=sanitized(response),reference_equal=all(response.get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route')),
       request_thread=main_thread,request_tree_exclusive_ms=dict(sums),request_tree_total_ms=total,http_outside_tree_ms=trace[-1]['ms']-total,call_counts=dict(counts),nodes=nodes,**active)
      report['queries'].append(trial)
      if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
      checkpoint();print(run['case'],sample,round(trial['http_ms']),trial['reference_equal'],flush=True)
    assert app.demo.payments.transaction_count()==before
   finally:app.demo_algorithm.close()
  report['source_templates_unchanged']=all(sha(Path(p))==h for p,h in source_hashes.items());assert report['source_templates_unchanged'];report['complete']=True;checkpoint()
 finally:tree.close()


if __name__=='__main__':main()
