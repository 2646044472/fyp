"""Audit candidate guard and winning regions on every unchanged single-device split."""
import json
from pathlib import Path
import sys,time,hashlib
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm

root=Path(sys.argv[1]);base=root/'single-device';out=base/'runtime-v5';out.mkdir(exist_ok=False)
def read(p):return json.loads(p.read_text())
def save(name,value):(out/name).write_text(json.dumps(value,indent=2))
records=read(root/'stability/records.json');lookup={r['sample']:i for i,r in enumerate(records)}
algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCAnchoredUnion-v5')
original=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCWindowUnion-v4')
fresh=read(base/'fresh-v4/results.json');changed={r['sample'] for r in fresh if not r['identical']}
features=[];stats=[];started=time.perf_counter()
save('plan.json',dict(source='fresh-v4 changed templates plus byte-identical runtime-v4 others',
    guard='candidate quad and aligned scoring quad must intersect automatic v5 anchor by >1 square pixel',
    purpose='spatial consistency, not semantic hand segmentation; primary ROI unchanged',
    protocol='unchanged original/reverse/ten random/100 extra; all images retained; no labels in matching'))
for i,r in enumerate(records):
    assert hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256']
    path=base/('fresh-v4' if r['sample'] in changed else 'runtime-v4')/(r['sample']+'.npz')
    with np.load(path,allow_pickle=False) as z:old=z['feature']
    feature=algorithm.upgrade_v4_template(old)
    np.savez_compressed(out/(r['sample']+'.npz'),feature=feature)
    with np.load(out/(r['sample']+'.npz'),allow_pickle=False) as z:
        np.testing.assert_array_equal(feature,z['feature']);features.append(z['feature'])
    before=original._unpack(old,decode_native=False);after=algorithm._unpack(feature,decode_native=False)
    stats.append(dict(sample=r['sample'],views_before=len(before[-1]),views_after=len(after[-1])))
    if (i+1)%10==0:print('templates',i+1,flush=True)
save('candidate-counts.json',stats)
matrix=np.full((80,80),np.nan);traces=[];timings=[]
for i,r in enumerate(records):
    query=algorithm._unpack(features[i])
    for j,g in enumerate(records):
        if r['cohort']!=g['cohort']:continue
        if i==j:matrix[i,j]=0;continue
        tick=time.perf_counter();details=[]
        matrix[i,j]=algorithm._match_unpacked(query,algorithm._unpack(features[j],decode_native=False),details)
        timings.append((time.perf_counter()-tick)*1000)
        winner=min((d for d in details if 'score' in d),key=lambda d:d['score'])
        traces.append(dict(query=r['sample'],gallery=g['sample'],winner=winner,
                           aligned_rejected=sum(d.get('rejected')=='disjoint_aligned_region' for d in details)))
    if (i+1)%10==0:print('pairs',i+1,round(time.perf_counter()-started,1),flush=True)
np.save(out/'distances.npy',matrix);save('pair-winners.json',traces)
results=[]
for c in read(base/'runtime-v4-fresh/results.json'):
    gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
    for t in c['trials']:
        idx=lookup[t['sample']];assert all(idx not in ids for ids in gallery.values())
        scores={k:float(np.sort(matrix[idx,ids])[:2].mean()) for k,ids in gallery.items()}
        trials.append(dict(sample=t['sample'],identity=t['identity'],scores=scores,correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity'])))
    results.append(dict(case=c['case'],gallery=c['gallery'],trials=trials,total=20,correct=sum(t['correct'] for t in trials)))
summary=[]
for cohort in ['new','old']:
    for split in ['original','reverse','random','extra']:
        values=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)]
        summary.append(dict(cohort=cohort,split=split,count=len(values),min=min(values),max=max(values),mean=float(np.mean(values))))
save('results.json',results);save('summary.json',summary)
save('timing.json',dict(pair_median_ms=float(np.median(timings)),pair_p95_ms=float(np.percentile(timings,95)),seconds=time.perf_counter()-started,host='local Windows; not Pi'))
print(json.dumps(summary,indent=2),flush=True)
