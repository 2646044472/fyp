"""Uniform union of previously computed geometry/descriptor candidates, no label routing."""
import json
from pathlib import Path
import sys
import numpy as np

root=Path(sys.argv[1]); out=root/'single-device/window-coarse-union';out.mkdir(exist_ok=False)
def read(p):return json.loads(p.read_text())
sources=['window-hypotheses','coarse-structure']
matrix=np.minimum.reduce([np.load(root/'single-device'/s/'distances.npy') for s in sources])
records=read(root/'stability/records.json');lookup={r['sample']:i for i,r in enumerate(records)}
cases=[r for r in read(root/'single-device/runtime-v3/results.json') if r['method']=='registered_best2'];results=[]
for c in cases:
    gallery={k:[lookup[s] for s in v] for k,v in c['gallery'].items()};trials=[]
    for t in c['trials']:
        scores={k:float(np.sort(matrix[lookup[t['sample']],ids])[:2].mean()) for k,ids in gallery.items()}
        trials.append(dict(sample=t['sample'],identity=t['identity'],scores=scores,correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity'])))
    results.append(dict(case=c['case'],total=20,correct=sum(t['correct'] for t in trials),trials=trials))
summary=[]
for cohort in ['new','old']:
    for split in ['original','reverse','random','extra']:
        values=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)]
        summary.append(dict(cohort=cohort,split=split,min=min(values),max=max(values),mean=float(np.mean(values)),total=20))
for name,value in [('plan',dict(sources=sources,selection='uniform minimum across all previously geometry-verified candidates',aggregation='unchanged best2',caveat='development data; not runtime integrated')),('results',results),('summary',summary)]:
    (out/(name+'.json')).write_text(json.dumps(value,indent=2))
np.save(out/'distances.npy',matrix)
print(json.dumps(summary,indent=2))
