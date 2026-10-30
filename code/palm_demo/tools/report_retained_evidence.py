"""Export scalar correctness, regression and timing evidence for isolated pilot."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from evaluate_six_person_frozen import timed_summary


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows):
    return dict(timed_summary(rows),
        wrong_match=sum(q['result'].get('status')=='MATCH'and not q['correct']for q in rows),
        retry_or_reject=sum(q['result'].get('status')!='MATCH'for q in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('baseline','pilot','full','output'):p.add_argument(name,type=Path)
    a=p.parse_args();b,pilot,full=[json.loads(path.read_text())for path in(a.baseline,a.pilot,a.full)]
    assert b['complete']and pilot['complete']and full['complete']and not pilot['full']and full['full']
    assert pilot['baseline_sha256']==full['baseline_sha256']==sha(a.baseline)
    assert pilot['pilot_pass']and full['pilot_pass']and pilot['source_templates_unchanged']and full['source_templates_unchanged']
    assert pilot['patch']==full['patch']and pilot['helper_sha256']==full['helper_sha256']
    refs={(r['case'],q['sample']):q for r in b['runs']for q in r['queries']}
    qs={(q['case'],q['sample']):q for q in full['queries']};assert set(refs)==set(qs)and len(qs)==168
    assert all(q['baseline_scores_reconstructed']for q in full['queries'])
    powers=pilot['power_samples']+full['power_samples'];assert all(p['get_throttled']=='throttled=0x0'for p in powers)
    out=dict(input_sha256={k:sha(getattr(a,k))for k in('baseline','pilot','full')},
        patch=full['patch'],pilot_summary=pilot['summary'],baseline=summarize(list(refs.values())),candidate=summarize(full['queries']),
        corrections=sum(not refs[k]['correct']and q['correct']for k,q in qs.items()),
        regressions=sum(refs[k]['correct']and not q['correct']for k,q in qs.items()),
        cases=[],exhaustive_queries=[],unchanged_early_routes=0,power_samples=len(powers),
        source_templates_unchanged=True,
        limits='Development cohort replay, no independent generalization or live camera claim; unknown-person rejection remains uncalibrated; not production deployed. RETRY never counts as correct. Timings include read/ROI/features/matching/HTTP, exclude camera acquisition and external upload.')
    for case in dict.fromkeys(q['case']for q in full['queries']):
        selected=[q for q in full['queries']if q['case']==case]
        out['cases'].append(dict(case=case,baseline=summarize([refs[case,q['sample']]for q in selected]),candidate=summarize(selected)))
    for key,q in qs.items():
        ref=refs[key]
        if q['frames']is None:
            assert q['scores']==ref['diagnostics']['scores']
            assert all(q['result'].get(k)==ref['result'].get(k)for k in('status','user_id','score','second_score','recognition_route'))
            out['unchanged_early_routes']+=1;continue
        user=q['identity'].replace(':','-');record=dict(case=q['case'],sample_suffix=q['sample'][-8:],reference_correct=ref['correct'],correct=q['correct'],
            baseline_ms=ref['ms'],candidate_ms=q['ms'],baseline_winner_score=ref['result']['score'],candidate_winner_score=q['result']['score'],
            candidate_second_score=q['result']['second_score'],frames={},identity_scores={})
        for stage,rows in q['frames'].items():
            values={}
            for row in rows:values.setdefault(row['identity'],[]).append(dict(index=row['index'],score=row['score']))
            score={u:float(np.mean(sorted(v['score']for v in vs)[:2]))for u,vs in values.items()}
            if stage in('after','merged'):
                assert score==(ref['diagnostics']['scores']if stage=='after'else q['scores'])
            record['identity_scores'][stage]=dict(true=score[user],baseline_winner=score[ref['result']['user_id']],candidate_winner=score[q['result']['user_id']])
            record['frames'][stage]={role:values[u]for role,u in dict(true=user,baseline_winner=ref['result']['user_id'],candidate_winner=q['result']['user_id']).items()}
        out['exhaustive_queries'].append(record)
    assert out['unchanged_early_routes']==155 and len(out['exhaustive_queries'])==13
    assert not a.output.exists();a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in('baseline','candidate','corrections','regressions','unchanged_early_routes','cases')},indent=2))


if __name__=='__main__':main()
