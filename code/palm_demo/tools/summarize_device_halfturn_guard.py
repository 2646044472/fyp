"""Validate fixed device coverage and export aggregate-only local pilot results."""
import argparse
import collections
import json
from pathlib import Path


def merge_preserved_case(parent, child):
    """Create a new in-memory view; never mutate stopped-run artifacts."""
    import copy
    if parent.get('complete') or not parent.get('failure','').startswith('MemoryError:'):
        raise ValueError('Parent must be the preserved resource stop')
    if not child.get('complete') or not child.get('pass') or len(child['runs'])!=1 or child['runs'][0]['variant']!='candidate':
        raise ValueError('Continuation must complete exactly one candidate case')
    existing={(r['case'],r['variant']) for r in parent['runs']}
    if (child['runs'][0]['case'],'candidate') in existing:
        raise ValueError('Completed/partial candidate case would be duplicated')
    merged=copy.deepcopy(parent)
    merged['runs']+=copy.deepcopy(child['runs'])
    merged.update(complete=True,**{'pass':True})
    merged.pop('failure',None)
    return merged


def audit_coverage(report, plan):
    expected = {c['name']:c for c in plan['protocol']['cases']}
    runs = report['runs']
    keys = [(r['variant'],r['case']) for r in runs]
    wanted = {(v,c) for v in ['baseline','candidate'] for c in expected}
    flags = dict(exact_case_variant_set=len(keys)==len(wanted) and set(keys)==wanted,
                 fixed_query_keys=True, fixed_five_frame_enrollments=True,
                 ready_all=True, zero_transactions=True)
    for r in runs:
        case = expected.get(r['case'])
        if case is None:
            flags['fixed_query_keys']=False; flags['fixed_five_frame_enrollments']=False
            continue
        flags['fixed_query_keys'] &= collections.Counter(q['sample'] for q in r['queries']) == collections.Counter(case['queries'])
        flags['fixed_five_frame_enrollments'] &= collections.Counter(e['identity'] for e in r['enrollments']) == collections.Counter(case['enrollment'].keys())
        for e in r['enrollments']:
            selected = case['enrollment'].get(e['identity'], [])
            flags['fixed_five_frame_enrollments'] &= (len(selected)==5 and
                collections.Counter(l['sample'] for l in e['localizations'])==collections.Counter(selected))
            flags['ready_all'] &= e['http_status']==200 and e['result'].get('recognition_ready') is True
        flags['zero_transactions'] &= r.get('zero_transactions') is True
    return flags


def export(root, continuation=None):
    from pilot_device_halfturn_guard import digest, exact_decision, exact_roi, summarize
    plan = json.loads((root/'plan.json').read_text())
    report = json.loads((root/'regression-results.json').read_text())
    panel = json.loads((root/'panel-results.json').read_text())
    if digest({k:v for k,v in plan.items() if k!='fingerprint'}) != plan['fingerprint']:
        raise ValueError('Plan changed')
    continuation_receipt = None
    if continuation is not None:
        from pilot_device_halfturn_guard import sha
        cp=json.loads((continuation/'plan.json').read_text())
        child=json.loads((continuation/'results.json').read_text())
        assert digest({k:v for k,v in cp.items() if k!='fingerprint'})==cp['fingerprint']
        assert Path(cp['parent_root']).resolve()==root.resolve()
        assert cp['parent_plan_sha256']==sha(root/'plan.json') and cp['parent_result_sha256']==sha(root/'regression-results.json')
        assert child['parent_result_sha256']==cp['parent_result_sha256'] and child['continuation_fingerprint']==cp['fingerprint']
        assert child['complete'] and child['pass'] and child['parent_files_unchanged'] and child['public_bytes_unchanged'] and child['original_images_unchanged']
        report=merge_preserved_case(report,child)
        continuation_receipt=dict(original_run_complete=False,resource_stop_preserved=True,
            reviewed_continuation_complete=True,new_candidate_queries=cp['expected_new_queries'],
            new_candidate_enrollments=cp['expected_new_enrollments'],startup_free_GiB=cp['startup_free_GiB'],
            recognition_changes=cp['recognition_changes'],no_completed_query_retries=cp['no_completed_query_retries'],
            parent_files_unchanged=child['parent_files_unchanged'],peak_RSS_GiB=child['peak_RSS_bytes']/1024**3)
    flags = audit_coverage(report, plan)
    flags['expected_168_each'] = sum(len(c['queries']) for c in plan['protocol']['cases'])==168
    flags['expected_34_enrollments_each'] = sum(len(c['enrollment']) for c in plan['protocol']['cases'])==34
    paired = {}
    for r in report['runs']:
        for q in r['queries']:
            paired.setdefault((r['case'],q['sample']), {})[r['variant']]=q
    complete_pairs = [v for v in paired.values() if set(v)=={'baseline','candidate'}]
    flags['168_complete_pairs'] = len(complete_pairs)==168
    flags['all_decisions_scores_exact'] = bool(complete_pairs) and all(exact_decision(v['baseline'],v['candidate']) for v in complete_pairs)
    flags['all_roi_exact'] = bool(complete_pairs) and all(exact_roi(v['baseline'],v['candidate']) for v in complete_pairs)
    stored = {(r['case'],q['sample']):q for r in plan['stored_terminal']['runs'] for q in r['queries']}
    correct_keys = {k for k,v in stored.items() if v['correct']}
    decision_fields=['status','user_id','score','second_score','recognition_route']
    flags['historical_terminal_decisions_exact'] = all(
        q['scores']==stored[r['case'],q['sample']]['diagnostics']['scores']
        and all(q['result'].get(f)==stored[r['case'],q['sample']]['result'].get(f) for f in decision_fields)
        for r in report['runs'] for q in r['queries'])
    checked_correct = {k for k in correct_keys if k in paired and 'candidate' in paired[k]}
    checked_lost = sum(paired[k]['candidate']['outcome']!='correct' for k in checked_correct)
    flags['all_166_old_correct_retained'] = len(correct_keys)==166 and all(
        k in paired and paired[k].get('candidate',{}).get('outcome')=='correct' for k in correct_keys)
    expected_features = {(c['name'],u.replace(':','-')) for c in plan['protocol']['cases'] for u in c['enrollment']}
    feature_rows = report.get('feature_parity',[])
    flags['all_34_five_frame_arrays_exact'] = (len(feature_rows)==34 and
        {(f['case'],f['user']) for f in feature_rows}==expected_features and all(f['all_five_exact'] for f in feature_rows))
    # Independently read paired completed templates after an interrupted run;
    # never infer images or rewrite the original run's sealed result.
    from lossless_template_store import LosslessTemplateStore
    import numpy as np
    compared = 0; exact_arrays = True
    for case in plan['protocol']['cases']:
        found = {r['variant']:r for r in report['runs'] if r['case']==case['name']}
        if set(found) != {'baseline','candidate'}:
            continue
        stores = [LosslessTemplateStore(Path(found[v]['runtime'])/'demo_templates') for v in ['baseline','candidate']]
        assert stores[0].list_users() == stores[1].list_users()
        assert set(stores[0].list_users()) == {u.replace(':','-') for u in case['enrollment']}
        for user in stores[0].list_users():
            arrays = [s.load(user)[0] for s in stores]
            exact_arrays &= len(arrays[0])==len(arrays[1])==5 and all(np.array_equal(a,b) for a,b in zip(*arrays))
            compared += 1
            del arrays
    flags['all_34_five_frame_arrays_exact'] = compared==34 and bool(exact_arrays) and flags['fixed_five_frame_enrollments'] and flags['exact_case_variant_set']
    flags['public_pause_preserved'] = (report.get('public_bytes_unchanged') is True and
        report.get('public_boundary')==panel['public_boundary'] and report['public_boundary']['state']=='paused_STOP'
        and report['public_boundary']['completed']==1239)
    flags['original_images_preserved'] = report.get('original_images_unchanged') is True
    flags['logical_execution_pass'] = report.get('pass') is True and report.get('complete') is True
    variants = {}
    for name in ['baseline','candidate']:
        runs = [r for r in report['runs'] if r['variant']==name]
        queries = [q for r in runs for q in r['queries']]
        nested = collections.Counter()
        for r in runs:
            for q in r['queries']:
                for event in q['events']:
                    nested[event['stage']] += event['ms']
        variants[name] = dict(summary=summarize(queries) if queries else None,
            cases={r['case']:r['summary'] for r in runs},
            fresh_enrollments=sum(len(r['enrollments']) for r in runs),
            enrollment_request_s=sum(e['ms'] for r in runs for e in r['enrollments'])/1000,
            enrollment_ready_count=sum(e['http_status']==200 and e['result'].get('recognition_ready') is True for r in runs for e in r['enrollments']),
            enrollment_gallery_ready_nested_s=sum(event['ms'] for r in runs for e in r['enrollments'] for event in e['events'] if event['stage']=='gallery_prepare')/1000,
            startup_ready_s=sum(r['startup_ready_ms'] for r in runs)/1000,
            query_http_s=sum(q['ms'] for q in queries)/1000,
            capture_extract_s=sum(q['result'].get('timing_ms',{}).get('capture_and_extract',0) for q in queries)/1000,
            gallery_s=sum(q['result'].get('timing_ms',{}).get('gallery',0) for q in queries)/1000,
            original_scoring_s=sum((q.get('terminal_rf') or {}).get('original_scoring_ms',0) for q in queries)/1000,
            appended_rf_s=sum((q.get('terminal_rf') or {}).get('rf_ms',0) for q in queries)/1000,
            query_stage_nested_s={k:v/1000 for k,v in nested.items()})
    telemetry = [json.loads(l) for l in (root/'regression/telemetry.jsonl').read_text().splitlines()]
    stats = {}
    if telemetry:
        cores = len(telemetry[0]['cpu_per_core'])
        stats = dict(samples=len(telemetry),peak_sampled_RSS_GiB=max(t['rss'] for t in telemetry)/1024**3,
            min_available_GiB=min(t['available'] for t in telemetry)/1024**3,
            cpu_mean_percent_per_core=[sum(t['cpu_per_core'][i] for t in telemetry)/len(telemetry) for i in range(cores)],
            process_cpu_s_delta=telemetry[-1]['cpu_s']-telemetry[0]['cpu_s'],
            sampled_wall_s=telemetry[-1]['time']-telemetry[0]['time'],
            host_disk_read_bytes_delta=telemetry[-1]['disk_read_bytes']-telemetry[0]['disk_read_bytes'],
            host_disk_write_bytes_delta=telemetry[-1]['disk_write_bytes']-telemetry[0]['disk_write_bytes'])
        stats['last_sample_available_GiB'] = telemetry[-1]['available']/1024**3
        stats['last_sample_RSS_GiB'] = telemetry[-1]['rss']/1024**3
        stats['last_sample_time'] = telemetry[-1]['time']
    observed = root/'regression/peak-observations.jsonl'
    if observed.exists():
        counters=[json.loads(l) for l in observed.read_text().splitlines()]
        stats['observed_peak_counter_GiB'] = max(v['peak_rss_bytes'] for v in counters)/1024**3
        stats['peak_counter_scope'] = 'Live Windows peak-working-set observations; last observation before final baseline finished, not a post-exit final counter'
    if continuation is not None:
        extra=[json.loads(l) for l in (continuation/'telemetry.jsonl').read_text().splitlines()]
        if extra:
            stats['continuation']=dict(samples=len(extra),sampled_wall_s=extra[-1]['time']-extra[0]['time'],
                peak_sampled_RSS_GiB=max(x['rss'] for x in extra)/1024**3,min_available_GiB=min(x['available'] for x in extra)/1024**3,
                process_cpu_s_delta=extra[-1]['cpu_s']-extra[0]['cpu_s'],
                host_disk_read_bytes_delta=extra[-1]['disk_read_bytes']-extra[0]['disk_read_bytes'],
                host_disk_write_bytes_delta=extra[-1]['disk_write_bytes']-extra[0]['disk_write_bytes'])
        stats['epoch_note']='Original stopped run and reviewed continuation are separate epochs/processes; original resource counters are retained separately'
    timely = lambda q: q['outcome']=='correct' and q['ms']<=2500
    time_transitions = dict(
        timely_correct_to_late_or_incorrect=sum(timely(p['baseline']) and not timely(p['candidate']) for p in complete_pairs),
        late_or_incorrect_to_timely_correct=sum(not timely(p['baseline']) and timely(p['candidate']) for p in complete_pairs))
    return dict(complete=report.get('complete',False), all_guards_pass=all(flags.values()), guards=flags,
        variants=variants, resources=stats,
        paired_subset_summaries={v:summarize([p[v] for p in complete_pairs]) for v in ['baseline','candidate']} if complete_pairs else {},
        completed_template_array_audit=dict(paired_groups=compared,all_five_exact=bool(exact_arrays)),
        continuation=continuation_receipt,
        paired_timely_transitions=time_transitions,
        partial_coverage=dict(paired_queries=len(complete_pairs),stored_correct_checked=len(checked_correct),
                              stored_correct_lost=checked_lost,stored_correct_untested=len(correct_keys-checked_correct)),
        scope='Previously seen Windows device regression. No Pi timing, independent generalization, GPU or speedup claim.',
        timing_note='Sequential fresh variants; enrollment/ready separate. Stage timers are nested, do not add. CPU/disk counters include host activity.',
        public_state='paused_STOP 1239/3217, unchanged' if flags['public_pause_preserved'] else 'Preservation check failed',
        harness_note='Prior observer attribute-forwarding failure retained; zero identify requests in that invalid run.',
        payment_scope='All tokens canceled, zero transactions; positive payment-confirmation tests not executed.',
        model_evidence='Current session system identifier gpt-6.1-sol; no additional tool-returned runtime-model receipt.',
        failure=report.get('failure'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--continuation',type=Path);a=p.parse_args()
    result=export(a.root,a.continuation)
    with a.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(dict(complete=result['complete'],all_guards_pass=result['all_guards_pass'],guards=result['guards'])))
