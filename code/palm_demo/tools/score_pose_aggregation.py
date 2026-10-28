"""Exploratory uniform template aggregation on cached pairwise distances."""
import argparse
import json
from pathlib import Path
import numpy as np


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);args=parser.parse_args()
    trials=json.loads((args.source/'trials.json').read_text());results=[]
    for algorithm in ['DoN','FastCC']:
        for pose in ['baseline','rotation_scale']:
            for rule in ['median','best3','nearest']:
                rows=[]
                for trial in trials:
                    allowed=[p for p in trial['poses'] if pose=='rotation_scale' or p['angle']==0 and p['scale']==1]
                    if not allowed:
                        rows.append(dict(sample=trial['sample'],identity=trial['identity'],correct=False,scores={}))
                        continue
                    scores={}
                    for identity in allowed[0]['template_scores'][algorithm]:
                        values=[]
                        for item in allowed:
                            v=sorted(item['template_scores'][algorithm][identity])
                            values.append(float(np.median(v)) if rule=='median' else float(np.mean(v[:3])) if rule=='best3' else v[0])
                        scores[identity]=min(values)
                    correct=scores[trial['identity']]<min(v for k,v in scores.items() if k!=trial['identity'])
                    rows.append(dict(sample=trial['sample'],identity=trial['identity'],correct=correct,scores=scores))
                result=dict(algorithm=algorithm,pose=pose,rule=rule,correct=sum(t['correct'] for t in rows),total=len(rows),trials=rows)
                results.append(result);print({k:v for k,v in result.items() if k!='trials'},flush=True)
    (args.source/'aggregation-controls.json').write_text(json.dumps(results,indent=2))
    (args.source/'aggregation-plan.json').write_text(json.dumps(dict(
        rules=['median_all5','mean_best3','nearest_template'],
        status='Exploratory comparison after inspection of median-pose results; not preregistered or independent validation',
        choice='Each rule uniformly applied across all identities, no true label used for selection'),indent=2))


if __name__=='__main__':main()
