"""Anonymize scalar operation/replay costs; never export recorded feature arrays."""
import argparse,collections,hashlib,json,statistics
from pathlib import Path


def union_ms(intervals):
 total=0.;end=None
 for lo,hi in sorted(intervals):
  if end is None or lo>end:total+=hi-lo;end=hi
  elif hi>end:total+=hi-end;end=hi
 return total


def arrays(value):
 if isinstance(value,dict):
  if value.get('type')=='ndarray':return [dict(shape=value['shape'],dtype=value['dtype'],bytes=value['bytes'],c_contiguous=value['c_contiguous'])]
  return [v for x in value.values()for v in arrays(x)]
 if isinstance(value,list):return [v for x in value for v in arrays(x)]
 return []


def operation_summary(profile):
 nodes=profile['nodes'];children=collections.defaultdict(list)
 for n in nodes:
  if n['parent']is not None:children[n['parent']].append((n['start_ms'],n['end_ms']))
 groups={}
 for n in nodes:
  group=groups.setdefault(n['label'],dict(category=n['category'],calls=0,exclusive_thread_cpu_ms=0.,summed_exclusive_thread_wall_ms=0.,intervals=[],inputs=collections.Counter(),outputs=collections.Counter()))
  group['calls']+=1;group['exclusive_thread_cpu_ms']+=n['exclusive_thread_cpu_ms'];group['summed_exclusive_thread_wall_ms']+=n['exclusive_wall_ms']
  cursor=n['start_ms']
  for lo,hi in sorted(children[n['id']]):
   if lo>cursor:group['intervals'].append((cursor,lo))
   cursor=max(cursor,hi)
  if cursor<n['end_ms']:group['intervals'].append((cursor,n['end_ms']))
  if n['category']!='framework':
   group['inputs'][json.dumps(arrays(n.get('input_spec')),sort_keys=True)]+=1
   group['outputs'][json.dumps(arrays(n.get('output_spec')),sort_keys=True)]+=1
 out={}
 for label,g in groups.items():
  g['exclusive_wall_union_ms']=union_ms(g.pop('intervals'))
  g['actual_array_input_specs']=[dict(arrays=json.loads(k),calls=v)for k,v in g.pop('inputs').items()]
  g['actual_array_output_specs']=[dict(arrays=json.loads(k),calls=v)for k,v in g.pop('outputs').items()]
  out[label]=g
 return out


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('inputs',type=Path,nargs='+');a=p.parse_args()
 data=[json.loads(path.read_text())for path in a.inputs];assert all(v['complete']and v['source_templates_unchanged']for v in data)
 qs=sorted((q for d in data for q in d['queries']),key=lambda q:(q['case'],q['sample']));assert len(qs)==8
 out=dict(complete=True,input_sha256=[hashlib.sha256(path.read_bytes()).hexdigest()for path in a.inputs],queries=[],all_40_response_fields_equal=True,full168_rerun=False,
  warning='SIFT oracle replay is a diagnostic using known outputs, not deployable speed or independent accuracy. CPU scope: issuing-thread exclusive CPU and whole-process HTTP CPU; native worker/background difference remains unattributed. Per-operation unions can overlap other operations; only global partition is additive.')
 for index,q in enumerate(qs,1):
  phases={v['phase']:v for v in q['phases']};assert len(phases)==5 and all(v['reference_equal']for v in phases.values())
  record=phases['record_profile'];ops=operation_summary(record['operation_profile']);wall=record['operation_profile']['global_wall_partition_ms'];assert sum(wall.values())<=record['http_ms']+.1
  row=dict(id=f'C{index:02d}',device_group='new'if q['case'].startswith('new')else'old',reference_correct=q['reference_correct'],role='fixed_fast_control'if q['reference_correct']and q['baseline_http_ms']<=2500 else'preselected_hard_query',
   original_baseline_http_ms=q['baseline_http_ms'],plain_before_ms=phases['plain_before']['http_ms'],plain_after_ms=phases['plain_after']['http_ms'],plain_bracketing_median_ms=statistics.median([phases[v]['http_ms']for v in('plain_before','plain_after')]),
   verified_replay_ms=phases['verify_replay']['http_ms'],timed_oracle_replay_ms=phases['timed_replay']['http_ms'],record_profile_http_ms=record['http_ms'],record_process_cpu_ms=record['process_cpu_ms'],
   record_issuing_threads_exclusive_cpu_ms=sum(n['exclusive_thread_cpu_ms']for n in record['operation_profile']['nodes']),global_nonoverlap_wall_ms=wall,operations=ops,phases=[])
  row['native_background_and_uninstrumented_cpu_ms']=row['record_process_cpu_ms']-row['record_issuing_threads_exclusive_cpu_ms']
  for phase in q['phases']:
   row['phases'].append(dict(phase=phase['phase'],http_ms=phase['http_ms'],process_cpu_ms=phase['process_cpu_ms'],reference_equal=phase['reference_equal'],roi_sha256=phase['roi_sha256'],status=phase['result']['status'],score=phase['result']['score'],second_score=phase['result']['second_score'],route=phase['result']['recognition_route'],oracle=phase['oracle']))
  row['all_40_response_fields_equal']=True;out['queries'].append(row)
 out['formal_reference']=dict(total=168,correct=164,wrong_accept=4,rejected=0,correct_within_2500=146,p50_ms=1540.17,p95_ms=6019.3185,max_ms=15225.)
 out['initialization_ready']=[dict(device_group='new'if x['case'].startswith('new')else'old',startup=x['startup'])for d in data for x in d['initializations']]
 with a.output.open('x')as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps([dict(id=q['id'],plain_ms=q['plain_bracketing_median_ms'],oracle_ms=q['timed_oracle_replay_ms'],correct=q['reference_correct'])for q in out['queries']],indent=2))


if __name__=='__main__':main()
