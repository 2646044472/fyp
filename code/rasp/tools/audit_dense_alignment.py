"""Fixed multiscale intensity alignment, independent of sparse keypoint availability."""
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


def structure(image):
    image=np.asarray(image,np.float32)/255
    return cv2.GaussianBlur(image,(0,0),1)-cv2.GaussianBlur(image,(0,0),9)


def align(template,image,scale):
    warp=np.asarray([[scale,0,128-64*scale],[0,scale,128-64*scale]],np.float32)
    warp[:,2]*=.5
    for side in [64,128]:
        if side==128:warp[:,2]*=2
        a=cv2.resize(template,(side,side),interpolation=cv2.INTER_AREA)
        b=cv2.resize(image,(side*2,side*2),interpolation=cv2.INTER_AREA)
        try:
            cc,warp=cv2.findTransformECC(a,b,warp,cv2.MOTION_AFFINE,
                                       (cv2.TERM_CRITERIA_COUNT|cv2.TERM_CRITERIA_EPS,40,1e-4),None,5)
        except cv2.error:return None
        if not np.isfinite(warp).all():return None
    singular=np.linalg.svd(warp[:,:2],compute_uv=False)
    angle=float(np.rad2deg(np.arctan2(warp[1,0],warp[0,0])))
    if (cc<.6 or np.linalg.det(warp[:,:2])<=0 or singular.min()<1/3
            or singular.max()>3 or singular.max()/singular.min()>1.5 or abs(angle)>40):return None
    return float(cc),np.vstack([warp,[0,0,1]])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);args=p.parse_args();root=args.root;out=root/'single-device/dense-alignment';out.mkdir(exist_ok=False)
    def save(name,v):(out/name).write_text(json.dumps(v,indent=2))
    save('plan.json',dict(method='ECC affine on fixed bandpass structure, 64/128 pyramid, starts .67/1/1.5, 40iter per level',
         geometry='cc>=.6, positive determinant, singular values1/3..3, ratio<=1.5, angle±40, original image and search context bounds',
         score='original pixels FastCC after warp; min with frozen expanded-query strict control; unchanged best2 aggregation',
         scope='all within-device pairs, all fixed original/reverse/10+100 splits, no labels during alignment',
         sources=['https://docs.opencv.org/4.x/dc/d6b/group__video__track.html','https://web.comp.polyu.edu.hk/csajaykr/myhome/papers/TIFS2019_Palm.pdf'],
         status='development control, not a reproduction of cited paper'))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCRegisteredBest2-v2');parts=[];large=[];small=[]
    for r in records:
        with np.load(root/'single-device/runtime-v2'/(r['sample']+'.npz'),allow_pickle=False) as ar:f=ar['feature']
        base,_=matcher._views(f);parts.append(base);im=cv2.resize(base[1],(256,256),interpolation=cv2.INTER_AREA)
        large.append(structure(im));small.append(structure(im[64:192,64:192]))
    matrix=np.load(root/'single-device/wide-context/distances.npz')['expanded_strict'].copy();details=[];started=time.perf_counter();attempts=0;accepted=0
    for i,r in enumerate(records):
        raw=cv2.cvtColor(np.asarray(Image.open(r['original']).convert('RGB')),cv2.COLOR_RGB2GRAY)
        source=np.asarray([[1/3,0,64],[0,1/3,64],[0,0,1.]])@parts[i][2]
        for j,target in enumerate(records):
            if i==j or r['cohort']!=target['cohort']:continue
            for scale in [.67,1.,1.5]:
                attempts+=1;result=align(small[j],large[i],scale)
                if result is None:continue
                cc,warp=result
                points=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1.]])@warp.T
                if (points[:,:2]<1).any() or (points[:,:2]>=255).any():continue
                final=np.linalg.inv(warp)@source;corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1.]])@np.linalg.inv(final).T;corners=corners[:,:2]/corners[:,2:]
                if (corners<1).any() or (corners[:,0]>=raw.shape[1]-1).any() or (corners[:,1]>=raw.shape[0]-1).any():continue
                roi=normalize_roi(cv2.warpPerspective(raw,final,(128,128)))[0]
                score=float(matcher.base.match(matcher.base.extract(roi),parts[j][0][0].astype(bool)));matrix[i,j]=min(matrix[i,j],score);accepted+=1
                details.append(dict(query=i,gallery=j,start_scale=scale,correlation=cc,score=score,warp=warp.tolist()))
        if (i+1)%5==0:print(i+1,round(time.perf_counter()-started,1),accepted,'/',attempts,flush=True)
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
    save('results.json',results);save('summary.json',summary);save('timing.json',dict(seconds=time.perf_counter()-started,attempts=attempts,accepted=accepted))


if __name__=='__main__':main()
