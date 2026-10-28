"""Dense interior-grid correspondence control inspired by contactless palm alignment.

This is not a reproduction of the cited paper. No reference points or labels are
used for tracking, forward/backward consistency, or affine verification.
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


def track(template,query,scale):
    grid=np.asarray([(x,y) for y in range(92,165,6) for x in range(92,165,6)],np.float32).reshape(-1,1,2)
    initial=(grid-128)*scale+128
    flags=cv2.OPTFLOW_USE_INITIAL_FLOW;criteria=(cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,30,.01)
    forward,ok,_=cv2.calcOpticalFlowPyrLK(template,query,grid,initial.copy(),winSize=(21,21),maxLevel=3,criteria=criteria,flags=flags)
    backward,back_ok,_=cv2.calcOpticalFlowPyrLK(query,template,forward,grid.copy(),winSize=(21,21),maxLevel=3,criteria=criteria,flags=flags)
    p=grid.reshape(-1,2);q=forward.reshape(-1,2)
    keep=(ok.ravel()>0)&(back_ok.ravel()>0)&(np.linalg.norm(backward.reshape(-1,2)-p,axis=1)<1.5)&(q>=1).all(1)&(q<255).all(1)
    if keep.sum()<12:return None
    cv2.setRNGSeed(20261028);m,inliers=cv2.estimateAffine2D(p[keep],q[keep],method=cv2.RANSAC,ransacReprojThreshold=2.,maxIters=2000,confidence=.99,refineIters=10)
    if m is None or not np.isfinite(m).all():return None
    good=inliers.ravel().astype(bool)
    area=min(cv2.contourArea(cv2.convexHull(a[keep][good])) for a in [p,q])/(128*128)
    singular=np.linalg.svd(m[:,:2],compute_uv=False);angle=float(np.rad2deg(np.arctan2(m[1,0],m[0,0])))
    if (good.sum()<12 or area<.08 or np.linalg.det(m[:,:2])<=0 or singular.min()<.5 or singular.max()>2 or singular.max()/singular.min()>1.5 or abs(angle)>40):return None
    return np.vstack([m,[0,0,1]]),dict(inliers=int(good.sum()),coverage=area,scale=singular.tolist(),angle=angle)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);args=p.parse_args();root=args.root;out=root/'single-device/grid-alignment';out.mkdir(exist_ok=False)
    def save(n,v):(out/n).write_text(json.dumps(v,indent=2))
    save('plan.json',dict(grid='13x13 interior palm, spacing6 at28..100 inside base128',image='same fixed 2xcontext256, normalized gray, Gaussian sigma1',
        tracker='pyramidal LK, 21x21 window, levels3, 30 iterations, starts .67/1/1.5, forward-backward1.5px',
        verification='affine RANSAC2px, >=12 inliers, area .08, scale.5-2, anisotropy<=1.5, angle±40, original bounds',
        score='single warp original pixels, FastCC, min with roi-hypotheses pair distances, unchanged best2 identity aggregation',
        source='https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/TIFS2019_Palm.pdf',caveat='Mechanism-inspired development control; not a reproduction or independent validation'))
    rows=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(rows)}
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCRegisteredBest2-v2');parts=[];pixels=[]
    for r in rows:
        with np.load(root/'single-device/runtime-v2'/(r['sample']+'.npz'),allow_pickle=False) as a:f=a['feature']
        part,_=matcher._views(f);parts.append(part);im=normalize_roi(cv2.resize(part[1],(256,256),interpolation=cv2.INTER_AREA))[0];pixels.append(cv2.GaussianBlur(im,(0,0),1))
    matrix=np.load(root/'single-device/roi-hypotheses/distances.npy').copy();details=[];started=time.perf_counter()
    for i,r in enumerate(rows):
        raw=cv2.cvtColor(np.asarray(Image.open(r['original']).convert('RGB')),cv2.COLOR_RGB2GRAY);source=np.asarray([[1/3,0,64],[0,1/3,64],[0,0,1.]])@parts[i][2]
        for j,target in enumerate(rows):
            if i==j or r['cohort']!=target['cohort']:continue
            for scale in [.67,1,1.5]:
                result=track(pixels[j],pixels[i],scale)
                if result is None:continue
                transform,info=result;warp=np.asarray([[1.,0,-64],[0,1,-64],[0,0,1]])@np.linalg.inv(transform)@source
                corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])@np.linalg.inv(warp).T;corners=corners[:,:2]/corners[:,2:]
                if (corners<1).any() or (corners[:,0]>=raw.shape[1]-1).any() or (corners[:,1]>=raw.shape[0]-1).any():continue
                roi=normalize_roi(cv2.warpPerspective(raw,warp,(128,128)))[0];score=float(matcher.base.match(matcher.base.extract(roi),parts[j][0][0].astype(bool)));matrix[i,j]=min(matrix[i,j],score)
                details.append(dict(query=i,gallery=j,initial_scale=scale,score=score,transform=transform.tolist(),**info))
        if (i+1)%10==0:print(i+1,round(time.perf_counter()-started,1),len(details),flush=True)
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
            v=[r['correct'] for r in results if r['case'].startswith(cohort+'_'+split)];row=dict(cohort=cohort,split=split,min=min(v),max=max(v),mean=float(np.mean(v)),total=20);summary.append(row);print(row,flush=True)
    save('results.json',results);save('summary.json',summary);save('timing.json',dict(seconds=time.perf_counter()-started))


if __name__=='__main__':main()
