"""Fixed-development pseudo-unregistered HTTP diagnostic; no threshold tuning.

New isolated runtime and matcher per removal group, so no full-gallery search
cache survives. Same-hand-only removal is reported separately from whole-person.
This is not independent stranger FAR. Source images/templates are unchanged.
"""
import argparse,hashlib,json,os,shutil,time
from pathlib import Path
from collections import defaultdict
import cv2
from evaluate_six_person_frozen import initialize,sanitized
from replay_pi_pipeline import http_app,save_json
from replay_ready_queries import power_sample,power_fault
from replay_demo_manifest import correct_identification
from templates import TemplateStore


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('selection','manifest','protocol','baseline','output'):p.add_argument(name,type=Path)
 p.add_argument('--model-root',type=Path,required=True);p.add_argument('--native-registration',type=Path,required=True)
 a=p.parse_args();selection=json.loads(a.selection.read_text());rows={r['sample']:r for r in json.loads(a.manifest.read_text())};protocol=json.loads(a.protocol.read_text());b=json.loads((a.baseline/'results.json').read_text());assert b['complete']
 root=Path(__file__).resolve().parents[1];assert all(sha(root/n)==h for n,h in b['code_sha256'].items())
 assert not a.output.exists();a.output.mkdir();os.environ['PALM_COMPNET_MODEL_ROOT']=str(a.model_root.resolve());cv2.setNumThreads(1)
 refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']};cases={c['name']:c for c in protocol['cases']};aliases=protocol['subject_aliases_for_reporting_only']
 def person(identity):return aliases.get(identity.split(':')[1],identity.split(':')[1])
 groups=defaultdict(list)
 for q in selection['selected']:
  identity=rows[q['sample']]['identity']
  for mode in ('whole_person','same_hand_only'):
   key=(q['case'],mode,person(identity)if mode=='whole_person'else identity);groups[key].append(q)
 source_hashes={str(p):sha(p) for p in a.baseline.glob('*/runtime/demo_templates/*')if p.is_file()}
 report=dict(protocol='Fixed six selected queries, each with whole-person and same-hand-only gallery removal; new matcher and runtime per group',selection_sha256=sha(a.selection),baseline_sha256=sha(a.baseline/'results.json'),warning=__doc__,groups=[],normal=[],power_samples=[],complete=False)
 for q in selection['selected']:
  ref=refs[q['case'],q['sample']];report['normal'].append(dict(case=q['case'],sample=q['sample'],identity=ref['identity'],result=ref['result'],http_ms=ref['ms'],correct=ref['correct'],source='Frozen v26 normal-gallery baseline; not rerun'))
 def checkpoint():
  power=power_sample();report['power_samples'].append(power);save_json(a.output/'results.json',report)
  if power_fault(power):raise RuntimeError('Power fault')
 checkpoint()
 for number,((case,mode,key),queries)in enumerate(groups.items()):
  checkpoint();runtime=a.output/f'group-{number:02d}'/'runtime';runtime.parent.mkdir();shutil.copytree(a.baseline/case/'runtime',runtime);store=TemplateStore(runtime/'demo_templates')
  identity_map={u.replace(':','-'):u for u in cases[case]['enrollment']}
  removed=[u for u in store.list_users()if(person(identity_map[u])==key if mode=='whole_person'else identity_map[u]==key)]
  assert removed
  for user in removed:
   for path in store.paths(user):assert path.resolve().is_relative_to(runtime.resolve())
   store.delete(user)
  retained=store.list_users();assert set(retained).isdisjoint(removed)
  start=time.perf_counter();app,camera,startup=initialize(runtime,b['matcher'],a.native_registration);ready_ms=(time.perf_counter()-start)*1000
  assert app.demo.gallery.threshold==1.0 and app.demo.gallery.min_margin==0.0
  item=dict(case=case,mode=mode,key=key,removed=removed,retained=retained,startup=startup,initialization_and_ready_ms=ready_ms,fresh_matcher=True,threshold=1.0,min_margin=0.0,queries=[]);report['groups'].append(item)
  active={};old_score=app.demo_algorithm.score_gallery
  def scores(probe,groups):
   assert set(groups)==set(retained)
   value=old_score(probe,groups);active.update(scores=dict(value),route=probe.route);return value
  app.demo_algorithm.score_gallery=scores
  before=app.demo.payments.transaction_count()
  try:
   with http_app(app)as(request,trace):
    for q in queries:
     checkpoint();row=rows[q['sample']];assert sha(Path(row['original']))==row['sha256'];camera.select([row]);active.clear()
     status,response=request('/api/demo/identify',{},None);value=sanitized(response)
     trial=dict(sample=q['sample'],true_identity=row['identity'],http_status=status,result=value,http_ms=trace[-1]['ms'],scores=active.get('scores'),correct_identification=correct_identification(dict(identity=row['identity'],http_status=status,result=value)),accepted=response.get('status')=='MATCH',gap=None if response.get('score')is None or response.get('second_score')is None else response['second_score']-response['score'])
     item['queries'].append(trial)
     if response.get('token'):request('/api/demo/cancel',dict(token=response['token']),200)
     checkpoint();print(case,mode,row['sample'],value.get('status'),value.get('user_id'),round(trial['http_ms']),flush=True)
   assert app.demo.payments.transaction_count()==before;item['transactions_unchanged']=True
  finally:app.demo_algorithm.close()
  checkpoint()
 report['source_templates_unchanged']=all(sha(Path(p))==h for p,h in source_hashes.items());assert report['source_templates_unchanged'];report['complete']=True;checkpoint()


if __name__=='__main__':main()
