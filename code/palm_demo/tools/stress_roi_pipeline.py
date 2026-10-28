"""Fixed probe-only synthetic stress; clean enrollment is held constant.

These are synthetic variants of development photos, not independent captures.
All 20 probes remain in every denominator, including extraction failures.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from pklnet_roi import PKLNetROI, normalize_roi, PKLNetUnavailable
from palm_app.biometric import load_algorithm


def save(path,value):
    path.write_text(json.dumps(value,indent=2),encoding='utf-8')


def perturb(rgb, name):
    h,w=rgb.shape[:2]
    if name=='dark_065':return np.rint(rgb.astype(np.float32)*.65).astype(np.uint8), np.zeros(2)
    if name=='blur_sigma3':return cv2.GaussianBlur(rgb,(0,0),3),np.zeros(2)
    if name=='shift_3pct':
        offset=np.array([round(w*.03),round(-h*.03)])
        return cv2.warpAffine(rgb,np.array([[1,0,offset[0]],[0,1,offset[1]]],np.float32),(w,h),borderMode=cv2.BORDER_REFLECT_101),offset
    raise ValueError(name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    conditions=['dark_065','blur_sigma3','shift_3pct']
    save(args.output/'plan.json',dict(conditions=conditions,split='clean index1-5 enrollment, perturbed index6-10 probes',
         denominator='all20 per condition; failures count wrong',limitations='synthetic development stress, not new sessions',
         policy='fixed v4 and v5; no recognition-dependent view selection',
         script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    rows=json.loads((args.experiment/'new-camera/records.json').read_text())
    v4=np.load(args.experiment/'new-camera/pixels.npz')['v4']
    v5=np.load(args.experiment/'consistency-new/pixels.npz')['consistent_gamma']
    clean={'v4':v4,'v5':v5}
    extractors={'v4':PKLNetROI(policy='aspect',threads=2),'v5':PKLNetROI(threads=2)}
    algs={n:load_algorithm(APP/'vendor/palmprint-recognition-python',n) for n in ['DoN','FastCC']}
    identities=sorted({r['identity'] for r in rows})
    gallery={k:[i for i,r in enumerate(rows) if r['identity']==k and r['index']<=5] for k in identities}
    features={p:{n:{i:a.extract(normalize_roi(images[i])[0]) for ids in gallery.values() for i in ids}
                  for n,a in algs.items()} for p,images in clean.items()}
    results=[];diagnostics=[]
    for condition in conditions:
        trials={p:{n:[] for n in algs} for p in extractors}
        for i,r in enumerate(rows):
            if r['index']<=5:continue
            path=Path(r['original']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
            altered,offset=perturb(np.asarray(Image.open(path).convert('RGB')),condition)
            for policy,extractor in extractors.items():
                scores={};valid=False
                try:
                    raw,quad,d=extractor.extract(Image.fromarray(altered));valid=d['roi_geometry_valid']
                    normalized=normalize_roi(raw)[0] if valid else None
                    diagnostics.append(dict(sample=r['sample'],condition=condition,policy=policy,details=d,quad=quad.tolist()))
                except (PKLNetUnavailable,ValueError) as error:
                    diagnostics.append(dict(sample=r['sample'],condition=condition,policy=policy,error=str(error)))
                    valid=False
                for name,alg in algs.items():
                    scores={}
                    if valid:
                        f=alg.extract(normalized)
                        scores={k:float(np.median([alg.match(f,features[policy][name][j]) for j in ids])) for k,ids in gallery.items()}
                    correct=bool(scores and scores[r['identity']] < min(v for k,v in scores.items() if k!=r['identity']))
                    trials[policy][name].append(dict(sample=r['sample'],identity=r['identity'],valid=valid,correct=correct,scores=scores))
            print(f'{condition} {i+1}/{len(rows)}',flush=True)
        for policy in extractors:
            for name,values in trials[policy].items():
                results.append(dict(condition=condition,policy=policy,algorithm=name,correct=sum(t['correct'] for t in values),
                                    total=len(values),valid=sum(t['valid'] for t in values),trials=values))
        save(args.output/'results.json',results);save(args.output/'diagnostics.json',diagnostics)
        print(json.dumps([{k:v for k,v in r.items() if k!='trials'} for r in results if r['condition']==condition]),flush=True)
    save(args.output/'integrity.json',dict(originals_unchanged=all(hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256'] for r in rows)))


if __name__=='__main__':main()
