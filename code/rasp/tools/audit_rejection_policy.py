"""Post-ranking development audit; no fitted thresholds or recognition fixes.

The fixed margin points are a risk/coverage comparison, not independent
calibration. Historical pseudo-unknown results belong to their original scorer.
"""
import argparse,hashlib,json
from pathlib import Path
from acceptance_policy import AcceptancePolicy


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def profile(margin):
    return dict(version=1, name=f'development-margin-{margin:g}-v1', profiles={
        'fastcc': dict(max_distance=1., min_margin=margin),
        'compnet': dict(max_distance=.32, min_margin=.08),
        'quality': dict(max_distance=.32, min_margin=.08)})


def assess(queries, policy):
    rows=[]
    for q in queries:
        result=q['result']; rejection=policy.rejection(result['score'],result.get('second_score'),result['recognition_route'])
        rows.append(dict(case=q['case'],sample_suffix=q['sample'][-8:],previously_correct=q['correct'],
            status=rejection[0] if rejection else result['status'],reason=rejection[1] if rejection else None,
            score=result['score'],second_score=result.get('second_score'),route=result['recognition_route']))
    return dict(correct_accept=sum(r['previously_correct']and r['status']=='MATCH'for r in rows),
        wrong_accept=sum(not r['previously_correct']and r['status']=='MATCH'for r in rows),
        correct_falsely_rejected=sum(r['previously_correct']and r['status']!='MATCH'for r in rows),
        wrong_blocked=sum(not r['previously_correct']and r['status']!='MATCH'for r in rows),
        rejected=sum(r['status']!='MATCH'for r in rows),rows=rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('recognition','historical_unknown','output','example_policy'):p.add_argument(name,type=Path)
    a=p.parse_args();full=json.loads(a.recognition.read_text());unknown=json.loads(a.historical_unknown.read_text());assert full['complete']and unknown['complete']
    report=dict(recognition_sha256=sha(a.recognition),historical_unknown_sha256=sha(a.historical_unknown),
        policy_code_sha256=sha(Path(__file__).resolve().parents[1]/'acceptance_policy.py'),
        warning=__doc__,fixed_margin_points=[.01,.02,.04,.08],profiles=[])
    for margin in report['fixed_margin_points']:
        document=profile(margin);policy=AcceptancePolicy(document);value=dict(policy=document,known=assess(full['queries'],policy),historical_unknown={})
        for mode in('whole_person','same_hand_only'):
            queries=[q for g in unknown['groups']if g['mode']==mode for q in g['queries']]
            rejections=[policy.rejection(q['result']['score'],q['result'].get('second_score'),q['result']['recognition_route'])for q in queries]
            value['historical_unknown'][mode]=dict(total=len(queries),accepted=sum(v is None for v in rejections),rejected=sum(v is not None for v in rejections),warning='Historical frozen v26 scores, not retained-evidence candidate or independent stranger FAR')
        report['profiles'].append(value)
    for path,value in ((a.output,report),(a.example_policy,profile(.02))):
        assert not path.exists();path.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps([dict(margin=v['policy']['profiles']['fastcc']['min_margin'],**{k:x for k,x in v['known'].items()if k!='rows'},historical_unknown=v['historical_unknown'])for v in report['profiles']],indent=2))


if __name__=='__main__':main()
