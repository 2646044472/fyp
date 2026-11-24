"""Assess exact lazy/shared fallback feasibility from saved complete evidence.

No inference, new benchmark, candidate filtering or policy change. The
certificate applies ONLY to subsets/reorderings of the identical exhaustive
FastCC hypotheses, not to changed descriptors or independent metric branches.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('reference',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    data=json.loads(args.reference.read_text());assert data['complete']
    assert data['matcher']=='FastCCCompNetAlternateROI-v26-experimental'
    args.output.mkdir(exist_ok=False,parents=True)
    app=Path(__file__).resolve().parents[1]
    assert hashlib.sha256((app/'staged_index_matcher.py').read_bytes()).hexdigest()==data['code_sha256']['staged_index_matcher.py'], 'Gate source differs from the recorded v26 run'
    gate=.32;records=[];queries=[q for r in data['runs'] for q in r['queries']]
    for run in data['runs']:
        for q in run['queries']:
            if q['result']['recognition_route']!='exhaustive_fallback':continue
            scores=q['diagnostics']['scores'];ranking=sorted(scores.values());assert len(ranking)>=2
            assert ranking[0]==q['result']['score'] and ranking[1]==q['result']['second_score']
            records.append(dict(case=run['case'],sample=q['sample'],correct=q['correct'],
                full_best=ranking[0],full_second=ranking[1],full_margin=ranking[1]-ranking[0],
                same_hypothesis_subset_distance_gate_impossible=ranking[0]>gate))
    blocked=[r for r in records if r['same_hypothesis_subset_distance_gate_impossible']]
    slow=[q for q in queries if q['correct'] and q['ms']>2500]
    result=dict(protocol='Offline architecture assessment of exact same-score shared/lazy fallback; no recognition or timing rerun',
        source_results_sha256=hashlib.sha256(args.reference.read_bytes()).hexdigest(),
        code_sha256={name:hashlib.sha256((app/name).read_bytes()).hexdigest() for name in
            ('union_matcher.py','demo_matcher.py','indexed_demo_matcher.py','staged_index_matcher.py')},
        proof='A subset minimum cannot be smaller than its full-set minimum; mean of the best two is componentwise monotone. If the full best identity score exceeds .32, every identical-hypothesis subset also fails that distance gate.',
        scope='Only same exhaustive FastCC candidates/descriptors/distances, not alternative embeddings, newly generated geometry or a faster complete computation',
        threshold_audited_not_changed=gate,gate_source_matches_recorded_run=True,records=records,
        fallback_count=len(records),distance_certificate_count=len(blocked),
        wrong_identity_count=sum(not q['correct'] for q in queries),
        wrong_identities_covered_by_certificate=sum(not r['correct'] for r in blocked),
        no_distance_certificate_count=len(records)-len(blocked),
        correct_over_budget_count=len(slow),correct_over_budget_routes=dict(Counter(q['result']['recognition_route'] for q in slow)),
        reference=dict(total=len(queries),correct=sum(q['correct'] for q in queries),
            timely_correct=sum(q['correct'] and q['ms']<=2500 for q in queries),
            wrong_identity_matches=sum(not q['correct'] and q['result']['status']=='MATCH' for q in queries),
            explicit_rejects=sum(q['result']['status']=='REJECT' for q in queries)),
        algorithm_changed=False,inference_run=False,new_pi_latency_claim=False,complete=True)
    (args.output/'assessment.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','code_sha256','proof','scope')}))


if __name__=='__main__':main()
