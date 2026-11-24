"""Fixed larger-region query proposals to test missing anatomical coverage.

All ten proposals are applied to every sample. No manual/reference coordinates
enter extraction. Preserve a separate distance matrix for each proposal.
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
from palm_app.biometric import load_algorithm
from pklnet_roi import normalize_roi


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);args=p.parse_args();root=args.root;out=root/'single-device/palm-coverage';out.mkdir(exist_ok=False)
    def save(n,v):(out/n).write_text(json.dumps(v,indent=2))
    proposals=[(scale,x,y) for scale in [1.5,2.] for x,y in [(0,0),(-.25,0),(.25,0),(0,-.25),(0,.25)]]
    save('plan.json',dict(proposals=proposals,frame='chosen automatic v5 quad basis; no label/reference routing',
                         appearance='original BGR pixels, one warp128, same normalization and FastCC',
                         matching='query proposal against unchanged gallery base; minimum with existing hypotheses distance; best2 aggregation',
                         caveat='Expanded region may include nonpalm; assess all wrong-class distances and retain regressions. Exploratory development control.'))
    rows=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(rows)}
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCPoseNearest-v1');bank=np.load(root/'stability/features.npz')['pose'];features=[];valids=[]
    for r in rows:
        im=np.asarray(Image.open(r['original']).convert('RGB'));bgr=cv2.cvtColor(im,cv2.COLOR_RGB2BGR);q=np.asarray(r['illumination']['details']['roi_quad_full'],np.float32);c=q.mean(0);fs=[];ok=[]
        for scale,x,y in proposals:
            quad=((q-c)*scale+c+x*(q[1]-q[0])+y*(q[3]-q[0])).astype(np.float32)
            valid=bool((quad>=1).all() and (quad[:,0]<im.shape[1]-1).all() and (quad[:,1]<im.shape[0]-1).all());ok.append(valid)
            fs.append(matcher.base.extract(normalize_roi(matcher.geometry.getROIimg(bgr,quad))[0]) if valid else np.zeros((32,32),bool))
        features.append(fs);valids.append(ok)
    fs=np.asarray(features);valids=np.asarray(valids);np.savez_compressed(out/'features.npz',features=fs,valid=valids)
    distances=np.full((len(proposals),80,80),np.nan);baseline=np.load(root/'single-device/roi-hypotheses/distances.npy');combined=baseline.copy();started=time.perf_counter()
    for i,r in enumerate(rows):
        for j,other in enumerate(rows):
            if i==j or r['cohort']!=other['cohort']:continue
            for k in range(len(proposals)):
                if not valids[i,k]:continue
                distances[k,i,j]=matcher.base.match(fs[i,k],bank[j,0].astype(bool));combined[i,j]=min(combined[i,j],distances[k,i,j])
        if (i+1)%10==0:print(i+1,round(time.perf_counter()-started,1),flush=True)
    np.savez_compressed(out/'distances.npz',proposals=distances,combined=combined)
    cases=[r for r in json.loads((root/'single-device/runtime-v2/results.json').read_text()) if r['method']=='registered_best2'];results=[];summary=[]
    for c in cases:
        gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
        for t in c['trials']:
            i=lookup[t['sample']];scores={k:float(np.sort(combined[i,ids])[:2].mean()) for k,ids in gallery.items()}
            trials.append(dict(sample=t['sample'],identity=t['identity'],correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity']),scores=scores))
        results.append(dict(case=c['case'],correct=sum(t['correct'] for t in trials),total=20,trials=trials))
    for cohort in ['new','old']:
        for split in ['original','reverse','random','extra']:
            values=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)];row=dict(cohort=cohort,split=split,min=min(values),max=max(values),mean=float(np.mean(values)),total=20);summary.append(row);print(row,flush=True)
    save('results.json',results);save('summary.json',summary);save('timing.json',dict(seconds=time.perf_counter()-started))


if __name__=='__main__':main()
