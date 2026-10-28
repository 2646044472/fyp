"""Recompute every pair touching a freshly changed template; reuse only byte-identical pairs."""
import json
from pathlib import Path
import sys
import time
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm

root=Path(sys.argv[1]);base=root/'single-device';out=base/'runtime-v4-fresh';out.mkdir(exist_ok=False)
def read(p):return json.loads(p.read_text())
rows=read(base/'fresh-v4/results.json');records=read(root/'stability/records.json');lookup={r['sample']:i for i,r in enumerate(records)}
assert len(rows)==80 and {r['sample'] for r in rows}==set(lookup)
changed={lookup[r['sample']] for r in rows if not r['identical']}
features=[]
for i,r in enumerate(records):
    directory='fresh-v4' if i in changed else 'runtime-v4'
    with np.load(base/directory/(r['sample']+'.npz'),allow_pickle=False) as saved:features.append(saved['feature'])
algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCWindowUnion-v4')
matrix=np.load(base/'runtime-v4/distances.npy').copy();n=0;started=time.perf_counter()
for i in range(80):
    for j in range(80):
        if i==j or records[i]['cohort']!=records[j]['cohort'] or not ({i,j}&changed):continue
        matrix[i,j]=algorithm.match(features[i],features[j]);n+=1
    if (i+1)%10==0:print(i+1,n,round(time.perf_counter()-started,1),flush=True)
np.save(out/'distances.npy',matrix);results=[]
for c in read(base/'runtime-v4/results.json'):
    if c['method']!='registered_best2':continue
    gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
    for t in c['trials']:
        scores={k:float(np.sort(matrix[lookup[t['sample']],ids])[:2].mean()) for k,ids in gallery.items()}
        trials.append(dict(sample=t['sample'],identity=t['identity'],scores=scores,correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity'])))
    results.append(dict(case=c['case'],method=c['method'],gallery=c['gallery'],trials=trials,total=20,correct=sum(t['correct'] for t in trials)))
summary=[]
for cohort in ['new','old']:
    for split in ['original','reverse','random','extra']:
        values=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)]
        summary.append(dict(cohort=cohort,split=split,count=len(values),min=min(values),max=max(values),mean=float(np.mean(values)),total=20))
for name,value in [('results',results),('summary',summary),('plan',dict(changed_indices=sorted(changed),recomputed_pairs=n,seconds=time.perf_counter()-started,reuse='only pairs whose two fresh features are byte-identical to cached runtime templates'))]:
    (out/(name+'.json')).write_text(json.dumps(value,indent=2))
print(json.dumps(summary,indent=2),flush=True)
