"""Check the actual packed matcher on all within-device splits and fresh seeds."""
import argparse
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from palm_app.biometric import load_algorithm


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--matcher',choices=['FastCCRegisteredBest2-v1','FastCCRegisteredBest2-v2','FastCCMultiROI-v3','FastCCWindowUnion-v4'],default='FastCCRegisteredBest2-v1')
    p.add_argument('--output-name',default='runtime');args=p.parse_args()
    root=args.root;out=root/'single-device'/args.output_name;out.mkdir(exist_ok=False)
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2))
    save('plan.json',dict(matcher=args.matcher,scope='within each device only',
                         splits='existing original/reverse/ten random plus 100 additional fixed seeds 2026102900:2026103000',
                         caveat='New splits of same previously inspected images are not new independent data',
                         runtime='packed numeric templates reloaded with allow_pickle=False; bounded context with image boundary checks'))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python',args.matcher);features=[];timings=[]
    hypotheses={r['sample']:r for cohort in ['new','old'] for r in json.loads((root/f'consistency-{cohort}/records.json').read_text())} if hasattr(algorithm,'extract_with_hypotheses') else None
    windows={r['sample']:r['candidates'] for r in json.loads((root/'single-device/localizer-windows/candidates.json').read_text())} if args.matcher=='FastCCWindowUnion-v4' else {}
    for r in records:
        replay=root/('new-runtime-consistent' if r['cohort']=='new' else 'old-runtime-consistent')
        roi=np.asarray(Image.open(replay/'rois'/r['sample']/'illumination/roi_128.png').convert('L'))
        started=time.perf_counter();image=Image.open(r['original']).convert('RGB');quad=r['illumination']['details']['roi_quad_full']
        if hypotheses is not None:
            candidates=[hypotheses[r['sample']]['variants'][key] for key in ['v4','gamma']]
            candidates += [dict(h,kind='window') for h in windows.get(r['sample'],[])]
            f=algorithm.extract_with_hypotheses(image,quad,roi,candidates)
        else:f=algorithm.extract_with_context(image,quad,roi)
        timings.append((time.perf_counter()-started)*1000)
        np.savez_compressed(out/(r['sample']+'.npz'),feature=f)
        with np.load(out/(r['sample']+'.npz'),allow_pickle=False) as saved:
            np.testing.assert_array_equal(saved['feature'],f);features.append(saved['feature'])
    matrix=np.full((80,80),np.nan);matched=[];started=time.perf_counter()
    for i,a in enumerate(features):
        for j,b in enumerate(features):
            if records[i]['cohort']!=records[j]['cohort']:continue
            if i==j:matrix[i,j]=0;continue
            tick=time.perf_counter();matrix[i,j]=algorithm.match(a,b);matched.append((time.perf_counter()-tick)*1000)
        if (i+1)%10==0:print(f'{i+1}/80 {time.perf_counter()-started:.1f}s',flush=True)
    np.save(out/'distances.npy',matrix)
    cases=[r for r in json.loads((root/'stability/results.json').read_text()) if r['algorithm']=='FastCCPoseNearest-v1' and '_to_' not in r['case']]
    for cohort in ['new','old']:
        groups={k:[i for i,r in enumerate(records) if r['cohort']==cohort and r['canonical_identity']==k] for k in sorted({r['canonical_identity'] for r in records})}
        for seed in range(2026102900,2026103000):
            rng=np.random.default_rng(seed);gallery={k:sorted(map(int,rng.choice(ids,5,replace=False))) for k,ids in groups.items()}
            cases.append(dict(case=f'{cohort}_extra_{seed}',gallery={k:[records[i]['sample'] for i in ids] for k,ids in gallery.items()},
                              trials=[dict(sample=records[i]['sample'],identity=k) for k,ids in groups.items() for i in ids if i not in gallery[k]]))
    baseline=np.load(root/'stability/distances.npz')['FastCCPoseNearest-v1'];results=[]
    for method,dist,k in [('pose_nearest',baseline,1),('registered_best2',matrix,2)]:
        for c in cases:
            gallery={key:[lookup[s] for s in ids] for key,ids in c['gallery'].items()};trials=[]
            for t in c['trials']:
                i=lookup[t['sample']];assert all(i not in ids for ids in gallery.values())
                scores={key:float(np.sort(dist[i,ids])[:k].mean()) for key,ids in gallery.items()}
                trials.append(dict(sample=t['sample'],identity=t['identity'],correct=scores[t['identity']]<min(v for key,v in scores.items() if key!=t['identity']),scores=scores))
            results.append(dict(case=c['case'],method=method,correct=sum(t['correct'] for t in trials),total=20,trials=trials,gallery=c['gallery']))
    save('results.json',results);summary=[]
    for method in ['pose_nearest','registered_best2']:
        for cohort in ['new','old']:
            for part in ['original','reverse','random','extra']:
                rows=[r for r in results if r['method']==method and r['case'].startswith(cohort+'_'+part)]
                summary.append(dict(method=method,cohort=cohort,split=part,count=len(rows),min=min(r['correct'] for r in rows),max=max(r['correct'] for r in rows),mean=float(np.mean([r['correct'] for r in rows])),total=20))
    save('summary.json',summary);save('latency.json',dict(extraction_ms=dict(median=float(np.median(timings)),p95=float(np.percentile(timings,95))),pair_match_ms=dict(median=float(np.median(matched)),p95=float(np.percentile(matched,95))),template_bytes=features[0].nbytes,host='local Windows; not Pi'))
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__':main()
