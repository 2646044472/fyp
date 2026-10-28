"""Fixed descriptor-only smoothing controls; appearance scores stay unchanged."""
import argparse
import json
from pathlib import Path
import sys

import cv2
import numpy as np

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from registered_matcher import local_features
from pklnet_roi import normalize_roi
from palm_app.biometric import load_algorithm


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);args=parser.parse_args();root=args.root
    out=root/'single-device/descriptor-smoothing';out.mkdir(exist_ok=False)
    def save(name,v):(out/name).write_text(json.dumps(v,indent=2))
    save('plan.json',dict(sigmas=[2.,4.],pixels='384x384 canonical ROI; Gaussian only for RootSIFT; raw matching pixels unchanged',
                          purpose='Test whether high-frequency capture texture prevents stable local correspondences',
                          selection='same setting for every image, no reference or identity used by matcher',
                          limitation='development ablations, including additional splits still from same images'))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    cases=[r for r in json.loads((root/'single-device/runtime/results.json').read_text()) if r['method']=='registered_best2']
    matcher=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCCRegisteredBest2-v1');results=[]
    for sigma in [2.,4.]:
        features=[]
        for r in records:
            with np.load(root/'single-device/runtime'/(r['sample']+'.npz'),allow_pickle=False) as archive:f=archive['feature']
            bank,context,matrix,size,_,_=matcher._unpack(f)
            raw=context[192:576,192:576]
            pixels=normalize_roi(raw)[0]
            points,desc=local_features(cv2.GaussianBlur(pixels,(0,0),sigma))
            features.append(matcher._pack(bank,context,matrix,size,points,desc))
        distances=np.full((80,80),np.nan)
        for i,left in enumerate(features):
            for j,right in enumerate(features):
                if records[i]['cohort']==records[j]['cohort']:
                    distances[i,j]=0 if i==j else matcher.match(left,right)
            if (i+1)%20==0:print(sigma,i+1,flush=True)
        np.save(out/f'distances-{sigma}.npy',distances)
        for c in cases:
            gallery={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
            for t in c['trials']:
                i=lookup[t['sample']];scores={k:float(np.sort(distances[i,ids])[:2].mean()) for k,ids in gallery.items()}
                trials.append(dict(sample=t['sample'],identity=t['identity'],correct=scores[t['identity']]<min(v for k,v in scores.items() if k!=t['identity']),scores=scores))
            results.append(dict(case=c['case'],sigma=sigma,correct=sum(t['correct'] for t in trials),total=20,trials=trials))
        save('results.json',results)
        for cohort in ['new','old']:
            for split in ['original','reverse','random','extra']:
                values=[r['correct'] for r in results if r['sigma']==sigma and r['case'].startswith(cohort+'_'+split)]
                print(sigma,cohort,split,min(values),max(values),float(np.mean(values)),flush=True)


if __name__=='__main__':main()
