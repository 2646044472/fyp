"""Read sealed scalar records; write only this new diagnosis directory, once."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

OUT=Path(__file__).resolve().parent
APP=OUT.parents[2]
PARENT=APP/'runtime/smpd-lossless-v27-20261031'
CHILD=APP/'runtime/smpd-v27-continuation-20261031-r1'
sys.path.insert(0,str(APP/'tools'))
from report_smpd_continuation import snapshot


def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=True,sort_keys=True,indent=2);f.write('\n')
def table(name,rows):
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def percentile(values,p):
    values=sorted(values);pos=(len(values)-1)*p;i=int(pos)
    return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(pos-i)


def main():
    state=snapshot(CHILD)
    assert state['completed_queries']==1239 and state['status']['state']=='paused_STOP'
    query_paths=[p for root in [PARENT,CHILD] for p in sorted((root/'records/query').glob('*.json'))]
    enrollment_paths=sorted((PARENT/'records/enrollment').glob('*.json'))
    queries=[load(p) for p in query_paths];enrollments=[load(p) for p in enrollment_paths]
    protocol=load(CHILD/'protocol.json');gallery=load(PARENT/'gallery.json')
    ledger=[];ties=[];transitions=collections.Counter();dev_transitions=collections.Counter()
    for path,r in zip(query_paths,queries):
        x=r['payload'];s=x['scores'];truth=x['identity'].replace(':','-');t=x.get('terminal_rf') or {}
        d=x['capture']['localizations'][0]['details'];partition='development' if int(x['subject'])%5 else 'protected'
        stage=(d['roi_geometry_reason'] if x['outcome']=='processing_failure' else
               'correct' if x['outcome']=='correct' else 'truth_missing_from_gallery' if not x['truth_enrolled'] else 'truth_present_rank_wrong')
        best=min(s.values()) if s else None;winners=[u for u,v in s.items() if v==best]
        old=t.get('original_scores',{});old_winner=min(old,key=old.get) if old else None
        row=dict(sample=r['sample'],sequence=r['sequence'],partition=partition,subject=x['subject'],pose=x['condition'],
            outcome=x['outcome'],diagnostic_stage=stage,http_status=x['http_status'],truth_enrolled=x['truth_enrolled'],
            roi_geometry_valid=d['roi_geometry_valid'],roi_geometry_reason=d['roi_geometry_reason'],
            route=x['result'].get('recognition_route'),winner=x['result'].get('user_id'),best_score=x['result'].get('score'),
            second_score=x['result'].get('second_score'),true_score=s.get(truth),
            true_rank=1+sum(v<s[truth] for v in s.values()) if truth in s else None,
            gallery_score_count=len(s),exact_min_tie_count=len(winners),
            ordinary_winner=old_winner,ordinary_true_score=old.get(truth),rf_applied=t.get('rf_applied',False),
            http_ms=x['ms'],original_scoring_ms=t.get('original_scoring_ms'),rf_ms=t.get('rf_ms'),
            record_path=str(path.relative_to(APP)),record_sha256=r['record_sha256'],record_file_sha256=sha(path))
        ledger.append(row)
        if t.get('rf_applied'):
            key=('correct' if old_winner==truth else 'wrong')+'_to_'+('correct' if x['outcome']=='correct' else 'wrong')
            transitions[key]+=1
            if partition=='development':dev_transitions[key]+=1
        # No protected-query tie/parameter selection output.
        if partition=='development' and len(winners)>1:
            ties.append(dict(sample=r['sample'],sequence=r['sequence'],outcome=x['outcome'],best=best,
                             tied_identities=winners,truth_in_tie=truth in winners,true_score=s.get(truth),
                             truth_enrolled=x['truth_enrolled'],returned=x['result'].get('user_id')))
    table('query-diagnosis.csv',ledger)
    outcomes=['correct','wrong_identity_accepted','processing_failure','rejected','true_identity_nonunique']
    def group(key):
        result=[]
        for value in sorted({r[key] for r in ledger}):
            rows=[r for r in ledger if r[key]==value];counts=collections.Counter(r['outcome'] for r in rows)
            result.append({key:value,'total':len(rows),**{k:counts[k] for k in outcomes},
                'span_too_small':sum(r['diagnostic_stage']=='pklnet_keypoint_span_too_small' for r in rows),
                'out_of_bounds':sum(r['diagnostic_stage']=='roi_out_of_bounds' for r in rows),
                'wrong_truth_missing':sum(r['diagnostic_stage']=='truth_missing_from_gallery' for r in rows),
                'wrong_truth_present':sum(r['diagnostic_stage']=='truth_present_rank_wrong' for r in rows)})
        return result
    identities=group('subject');poses=group('pose');partitions=group('partition')
    table('by-identity.csv',identities);table('by-pose.csv',poses);table('by-partition.csv',partitions)
    failures=[]
    for path,r in zip(enrollment_paths,enrollments):
        x=r['payload']
        if x['ok']:continue
        d=x['capture']['localizations'][0]['details']
        failures.append(dict(sample=r['sample'],sequence=r['sequence'],subject=r['sample'].split('-')[1],
            reason=d['roi_geometry_reason'],aspect_retry=d['pklnet_aspect_retry'],retry_reason=d.get('pklnet_retry_reason'),
            span=d.get('pklnet_keypoint_span_ratio'),error=x.get('error'),record_sha256=r['record_sha256'],record_file_sha256=sha(path)))
    table('enrollment-failures.csv',failures)
    def timing(rows):
        return dict(n=len(rows),http_ms=sum(r['payload']['ms'] for r in rows),
            capture_and_extract_ms=sum(r['payload']['result'].get('timing_ms',{}).get('capture_and_extract',0) for r in rows),
            gallery_ms=sum(r['payload']['result'].get('timing_ms',{}).get('gallery',0) for r in rows),
            original_scoring_ms=sum((r['payload'].get('terminal_rf') or {}).get('original_scoring_ms',0) for r in rows),
            rf_ms=sum((r['payload'].get('terminal_rf') or {}).get('rf_ms',0) for r in rows),
            localization_ms=sum(l['ms'] for r in rows for l in r['payload']['capture']['localizations']),
            p50_http_ms=percentile([r['payload']['ms'] for r in rows],.5),
            p95_http_ms=percentile([r['payload']['ms'] for r in rows],.95))
    timings={label:timing(rows) for label,rows in [
        ('all',queries),('http200',[r for r in queries if r['payload']['http_status']==200]),
        ('terminal',[r for r in queries if (r['payload'].get('terminal_rf') or {}).get('rf_applied')]),
        ('nonterminal',[r for r in queries if r['payload'].get('terminal_rf') and not r['payload']['terminal_rf']['rf_applied']]),
        ('failure',[r for r in queries if r['payload']['outcome']=='processing_failure'])]}
    ordinary_calls=sum((r['payload'].get('terminal_rf') or {}).get('ordinary_calls',0) for r in queries)
    captured_pairs=sum((r['payload'].get('terminal_rf') or {}).get('captured_pairs',0) for r in queries)
    summary=dict(schema=1,created_unix=time.time(),scope='Read-only scalar diagnosis of sealed parent216 + continuation1023; fixed, incomplete, seen public Windows prefix',
        builder_sha256=sha(Path(__file__)),snapshot=state,
        protocol_files_sha256={str(p.relative_to(APP)):sha(p) for p in [PARENT/'protocol.json',CHILD/'protocol.json']},
        original_thresholds=protocol['thresholds'],failure_stages=dict(collections.Counter(r['diagnostic_stage'] for r in ledger)),
        by_identity=identities,by_pose=poses,by_partition=partitions,
        missing_gallery=[e['identity'] for e in gallery['enrollments'] if not e['registered']],
        enrollment_failures=failures,rf_internal_transitions_all=dict(transitions),rf_internal_transitions_development=dict(dev_transitions),
        exact_min_ties_development=ties,
        exact_min_tie_counterfactual=dict(development_queries=994,old_correct=286,new_correct=286,old_wrong=542,new_wrong=540,
            old_rejected=0,new_rejected=2,processing_failure_unchanged=166,
            scope='Offline decision accounting only; no policy implemented, no recognition improvement, protected outcomes not used to choose rule'),
        timing_sums_ms=timings,timing_note='Nested scopes overlap; original_scoring includes lazy exhaustive extraction/registration/matching; these are saved scalar sums, not a new profile or causal attribution',
        request_cache_hypothesis=dict(ordinary_calls=ordinary_calls,captured_pairs_per_frame=captured_pairs,
            duplicate_lower_bound_fraction=1-captured_pairs/ordinary_calls,
            status='Not implemented or benchmarked; pure 32x32 AcceleratedFastCC.match branch may permit exact ordered-code-byte request-scoped cache; packing/locking/memory and trace preservation must be measured'),
        cache_inventory=dict(enrollment_feature_npz=447,registered_gallery_npz=86,registered_frames=430,successful_unregistered_frames=17,
            query_feature_npz=0,query_scores_available=True,query_code_pairs_persisted=False),
        model_receipt_limit='Parent requested gpt-6-astra; visible spawn receipt contains canonical task ID only, without independent actual execution model field.',
        hardware_parent_readonly_observation=dict(cpu='Intel Core Ultra 5 338H',physical_cores=12,logical_cores=12,
            physical_memory_bytes=33873752064,gpu='NVIDIA GeForce RTX 4070 SUPER',gpu_memory_mib=12282,
            nvidia_driver='610.88',cuda_umd='13.3 (driver capability only)',
            original_environment=dict(torch='2.15.0+cpu',torch_cuda=None,torch_cuda_available=False,onnxruntime='1.31.1',providers=['AzureExecutionProvider','CPUExecutionProvider']),
            scope='Reported by parent agent from read-only host/environment checks; this diagnostic script did not rerun hardware probes. No GPU dependencies installed. Base environment metadata also lacked torch/ORT-gpu/cupy; not a machine-wide proof of no CUDA environment.'),
        geometry_pilot_reference='runtime/smpd-roi-oob-pilot-20261101/results.json',
        no_accuracy_edit_qualified=True,no_full_evaluation_started=True,no_deployment=True,
        limitations=['ROI geometry validity is not anatomical correctness.',
            'Registration failure can prevent true identification; recovering registration does not guarantee query corrections.',
            'The completed-record failure categories do not classify prior uncommitted attempts or historical capacity failures.',
            'Previously seen development-only mechanism selection; protected split is prospective, not independent blind data.',
            'Windows timing is not Pi timing; closed-set scores do not establish stranger FAR.'])
    assert summary['failure_stages']=={'correct':354,'pklnet_keypoint_span_too_small':183,'roi_out_of_bounds':26,'truth_missing_from_gallery':118,'truth_present_rank_wrong':558}
    assert len(failures)==13 and len(ties)==2 and all(t['outcome']=='wrong_identity_accepted' and not t['truth_in_tie'] for t in ties)
    save('summary.json',summary)
    save('artifact-manifest.json',{'files':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-manifest.json'},
         'scope':'Hashes of new diagnosis artifacts; no original runtime file written'})
    print(json.dumps(dict(completed_queries=1239,classification=summary['failure_stages'],ordinary_calls=ordinary_calls,
          captured_pairs=captured_pairs,exact_min_ties_development=len(ties),outputs=str(OUT))),flush=True)


if __name__=='__main__':main()
