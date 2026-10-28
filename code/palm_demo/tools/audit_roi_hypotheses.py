"""Keep both already-computed original/gamma localization hypotheses for queries.

Each hypothesis must pass the existing geometry guard. Labels never select it;
appearance and correspondence checks are uniform for all gallery templates.
"""
import argparse
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from registered_matcher import local_features
from pklnet_roi import normalize_roi
from palm_app.biometric import load_algorithm
from audit_expanded_query import fit


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    p.add_argument('--output-name',default='roi-hypotheses');p.add_argument('--sigmas',nargs='+',type=float,default=[0,2])
    p.add_argument('--base-distance',type=Path);p.add_argument('--fields',nargs='+',type=int,default=[384,768])
    p.add_argument('--candidate-file',type=Path,help='Additional frozen geometry hypotheses; retain every valid candidate')
    args=p.parse_args();root=args.root;out=root/'single-device'/args.output_name;out.mkdir(exist_ok=False)
    def save(name,v):(out/name).write_text(json.dumps(v,indent=2))
    save('plan.json',dict(hypotheses=['v4','gamma'],selection='both existing valid predictions, no true identity or annotations used',
        gallery='unchanged automatic v5 ROI descriptors and base FastCC',descriptor_fields=args.fields,descriptor_sigmas=args.sigmas,
        baseline_distance=str(args.base_distance) if args.base_distance else 'wide-context/expanded_strict',
        alignment='same mutual RootSIFT/RANSAC thresholds as v2, scale .5-2, angle±40, area .02, four inliers',
        appearance='one warp from original grayscale, min with expanded-query strict baseline; same best2 aggregation',
        caveat='Retrospective development test; old/new evaluated separately; neither samples nor failures removed'))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    hypotheses={r['sample']:r for cohort in ['new','old'] for r in json.loads((root/f'consistency-{cohort}/records.json').read_text())}
    additional={r['sample']:r['candidates'] for r in json.loads(args.candidate_file.read_text())} if args.candidate_file else {}
    save('additional-candidates.json',dict(source=str(args.candidate_file),selection='all valid candidates without identity-based selection'))
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCRegisteredBest2-v2');parts=[]
    for r in records:
        with np.load(root/'single-device/runtime-v2'/(r['sample']+'.npz'),allow_pickle=False) as a:f=a['feature']
        parts.append(matcher._views(f))
    gallery_views=[]
    for primary,secondary in parts:
        pixels=normalize_roi(primary[1][192:576,192:576])[0];views=[]
        for sigma in args.sigmas:
            if sigma==0:views.append((primary[4],primary[5]))
            elif sigma==2:views.append(secondary)
            else:views.append(local_features(cv2.GaussianBlur(pixels,(0,0),sigma)))
        gallery_views.append(views)
    matrix=(np.load(args.base_distance) if args.base_distance else np.load(root/'single-device/wide-context/distances.npz')['expanded_strict']).copy();details=[];started=time.perf_counter()
    for i,r in enumerate(records):
        gray=cv2.cvtColor(np.asarray(Image.open(r['original']).convert('RGB')),cv2.COLOR_RGB2GRAY);views=[]
        candidates=[(name,hypotheses[r['sample']]['variants'][name]) for name in ['v4','gamma']]
        candidates.extend((f'window-{n}',h) for n,h in enumerate(additional.get(r['sample'],[])))
        for name,h in candidates:
            if not h['valid']:continue
            q=np.asarray(h['quad'],np.float32)
            dst=np.asarray([[384,0],[0,0],[0,384],[384,384]] if matcher.geometry.isAntiClock(q[:3].reshape(-1)) else [[0,0],[384,0],[384,384],[0,384]],np.float32)
            source=cv2.getPerspectiveTransform(q,dst)
            for size in args.fields:
                offset=(size-384)/2
                shift=np.asarray([[1,0,offset],[0,1,offset],[0,0,1.]])
                pixels=normalize_roi(cv2.warpPerspective(gray,shift@source,(size,size)))[0]
                for v,sigma in enumerate(args.sigmas):
                    points,desc=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
                    views.append((name,size,v,source,(points-offset,desc)))
        for j,target in enumerate(records):
            if i==j or r['cohort']!=target['cohort']:continue
            gallery=gallery_views[j]
            for name,size,v,source,query in views:
                result=fit(query,gallery[v])
                if result is None:continue
                transform,info=result
                if not .5<=info['scale']<=2:continue
                warp=np.diag([1/3,1/3,1])@transform@source
                corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])@np.linalg.inv(warp).T;corners=corners[:,:2]/corners[:,2:]
                if (corners<1).any() or (corners[:,0]>=gray.shape[1]-1).any() or (corners[:,1]>=gray.shape[0]-1).any():continue
                pixels=normalize_roi(cv2.warpPerspective(gray,warp,(128,128)))[0]
                score=float(matcher.base.match(matcher.base.extract(pixels),parts[j][0][0][0].astype(bool)))
                matrix[i,j]=min(matrix[i,j],score)
                details.append(dict(query=i,gallery=j,hypothesis=name,field=size,view=v,sigma=args.sigmas[v],score=score,**info))
        if (i+1)%10==0:print(i+1,round(time.perf_counter()-started,1),flush=True)
    np.save(out/'distances.npy',matrix);save('alignments.json',details)
    cases=[r for r in json.loads((root/'single-device/runtime-v2/results.json').read_text()) if r['method']=='registered_best2'];results=[];summary=[]
    for c in cases:
        gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
        for t in c['trials']:
            i=lookup[t['sample']];scores={k:float(np.sort(matrix[i,ids])[:2].mean()) for k,ids in gallery.items()}
            trials.append(dict(sample=t['sample'],identity=t['identity'],correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity']),scores=scores))
        results.append(dict(case=c['case'],correct=sum(t['correct'] for t in trials),total=20,trials=trials))
    for cohort in ['new','old']:
        for split in ['original','reverse','random','extra']:
            values=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)];row=dict(cohort=cohort,split=split,min=min(values),max=max(values),mean=float(np.mean(values)),total=20);summary.append(row);print(row,flush=True)
    save('results.json',results);save('summary.json',summary);save('timing.json',dict(seconds=time.perf_counter()-started))


if __name__=='__main__':main()
