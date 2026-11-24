"""Test whether a too-small automatic query ROI loses matching palm context.

Expand the QUERY descriptor search only. Gallery descriptors remain inside the
automatic palm ROI. All parameters are shared; no reference annotations enter.
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
from registered_matcher import FastCCDualRegisteredMatcher,local_features,registration
from pklnet_roi import normalize_roi
from palm_app.biometric import load_algorithm


def fit(left,right):
    p,d=left;q,e=right
    if min(len(d),len(e))<4:return None
    bf=cv2.BFMatcher();matches=bf.knnMatch(d,e,k=2);reverse=bf.knnMatch(e,d,k=1)
    good=[a for a,b in matches if a.distance<.85*b.distance and reverse[a.trainIdx][0].trainIdx==a.queryIdx]
    if len(good)<4:return None
    a=np.asarray([p[m.queryIdx] for m in good],np.float32);b=np.asarray([q[m.trainIdx] for m in good],np.float32)
    cv2.setRNGSeed(20261028)
    transform,mask=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=3.,maxIters=2000,confidence=.99,refineIters=10)
    if transform is None:return None
    keep=mask.ravel().astype(bool);n=int(keep.sum())
    coverage=min(cv2.contourArea(cv2.convexHull(x[keep])) for x in [a,b])/(384*384)
    scale=float(np.hypot(transform[0,0],transform[1,0]));angle=float(np.rad2deg(np.arctan2(transform[1,0],transform[0,0])))
    if n<4 or coverage<.02 or not 1/3<=scale<=3 or abs(angle)>40:return None
    return np.vstack([transform,[0,0,1]]),dict(inliers=n,coverage=coverage,scale=scale,angle=angle,query_points=a[keep].tolist(),gallery_points=b[keep].tolist())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);args=parser.parse_args();root=args.root;out=root/'single-device/wide-context'
    out.mkdir(exist_ok=True)
    assert not (out/'plan.json').exists(),'Do not overwrite an evaluated plan'
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2))
    save('plan.json',dict(controls=['v2 frozen','base descriptors / full-original appearance','expanded query descriptors 2x, original scale bounds','expanded query descriptors 2x, scale bounds1/3-3'],
        descriptor='RootSIFT original/sigma2, gallery always base automaticROI, query expanded with fixed offset',
        geometry='4 inliers, area .02, angle±40, mutual ratio .85; same for all identities',
        appearance='normalized original gray warped to128, FastCC, min with v2 pair distance; best2 identity aggregation',
        caveat='Development experiment. Expanded query can include nonpalm pixels; gallery restricted to automatic palm; inspect matches and regression controls. No annotation-based routing.'))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    algorithm=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCRegisteredBest2-v2')
    parts=[];expanded=[]
    for r in records:
        with np.load(root/'single-device/runtime-v2'/(r['sample']+'.npz'),allow_pickle=False) as ar:f=ar['feature']
        primary,secondary=algorithm._views(f);parts.append((primary,secondary))
        pixels=normalize_roi(primary[1])[0];views=[]
        for sigma in [0,2]:
            p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels);views.append((p-192,d))
        expanded.append(views)
    frozen=np.load(root/'single-device/runtime-v2/distances.npy');matrices={name:frozen.copy() for name in ['base_full','expanded_strict','expanded_relaxed']};details=[];started=time.perf_counter()
    for i,r in enumerate(records):
        raw=cv2.cvtColor(np.asarray(Image.open(r['original']).convert('RGB')),cv2.COLOR_RGB2GRAY);source=parts[i][0][2]
        base_views=[(parts[i][0][4],parts[i][0][5]),parts[i][1]]
        for j,target in enumerate(records):
            if i==j or r['cohort']!=target['cohort']:continue
            gallery_views=[(parts[j][0][4],parts[j][0][5]),parts[j][1]]
            for mode,views in [('base',base_views),('expanded',expanded[i])]:
                for view,(a,b) in enumerate(zip(views,gallery_views)):
                    result=fit(a,b)
                    if result is None:continue
                    transform,info=result;strict=.5<=info['scale']<=2
                    if mode=='base' and not strict:continue
                    warp=np.diag([1/3,1/3,1])@transform@source
                    corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])@np.linalg.inv(warp).T;corners=corners[:,:2]/corners[:,2:]
                    if (corners<1).any() or (corners[:,0]>=raw.shape[1]-1).any() or (corners[:,1]>=raw.shape[0]-1).any():continue
                    pixels=normalize_roi(cv2.warpPerspective(raw,warp,(128,128)))[0]
                    score=float(algorithm.base.match(algorithm.base.extract(pixels),parts[j][0][0][0].astype(bool)))
                    keys=['base_full'] if mode=='base' else ['expanded_relaxed']+(['expanded_strict'] if strict else [])
                    for key in keys:matrices[key][i,j]=min(matrices[key][i,j],score)
                    details.append(dict(query=i,gallery=j,mode=mode,view=view,score=score,transform=transform.tolist(),**info))
        if (i+1)%10==0:print(i+1,round(time.perf_counter()-started,1),flush=True)
    np.savez_compressed(out/'distances.npz',**matrices);save('alignment-details.json',details)
    cases=[r for r in json.loads((root/'single-device/runtime-v2/results.json').read_text()) if r['method']=='registered_best2'];results=[];summary=[]
    for mode,distances in matrices.items():
        for c in cases:
            gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
            for t in c['trials']:
                i=lookup[t['sample']];scores={k:float(np.sort(distances[i,ids])[:2].mean()) for k,ids in gallery.items()}
                trials.append(dict(sample=t['sample'],identity=t['identity'],correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity']),scores=scores))
            results.append(dict(case=c['case'],mode=mode,correct=sum(t['correct'] for t in trials),total=20,trials=trials))
        for cohort in ['new','old']:
            for split in ['original','reverse','random','extra']:
                values=[r['correct'] for r in results if r['mode']==mode and r['case'].startswith(cohort+'_'+split)]
                row=dict(mode=mode,cohort=cohort,split=split,min=min(values),max=max(values),mean=float(np.mean(values)),total=20);summary.append(row);print(row,flush=True)
    save('results.json',results);save('summary.json',summary);save('timing.json',dict(seconds=time.perf_counter()-started))


if __name__=='__main__':main()
