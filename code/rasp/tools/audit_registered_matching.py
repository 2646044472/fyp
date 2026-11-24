"""Score appearance after label-free local-feature registration, with pose fallback."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from pklnet_roi import normalize_roi,PKLNET_ROOT
from palm_app.biometric import load_algorithm


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    args=p.parse_args();root=args.root;out=root/'single-device/registered';out.mkdir(exist_ok=False)
    def save(name,value):(out/name).write_text(json.dumps(value,indent=2))
    save('plan.json',dict(registration='reuse RootSIFT .85 partial-affine, >=4 inliers, >=.02 area, .5-2 scale, ±40deg',
                          warp='warp full original into enrollment-aligned coordinates, not padded cropped ROI',
                          score='minimum original nine-pose distance and registered FastCC appearance distance',
                          aggregation=['nearest','mean_best2'],reference_ROI_used=False))
    records=json.loads((root/'stability/records.json').read_text());lookup={r['sample']:i for i,r in enumerate(records)}
    pairs=json.loads((root/'single-device/local-alignment/pairs-0.85.json').read_text())
    baseline=np.load(root/'stability/distances.npz')['FastCCPoseNearest-v1'];distance=baseline.copy()
    banks=np.load(root/'stability/features.npz')['pose'];base=load_algorithm(APP/'vendor/palmprint-recognition-python','FastCC')
    spec=importlib.util.spec_from_file_location('registered_geometry',PKLNET_ROOT/'roiExtractor.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
    details=[]
    for i,r in enumerate(records):
        image=cv2.cvtColor(np.asarray(Image.open(r['original']).convert('RGB')),cv2.COLOR_RGB2BGR)
        q=np.asarray(r['illumination']['details']['roi_quad_full'],np.float32)
        dst=np.array([[384,0],[0,0],[0,384],[384,384]] if geo.isAntiClock(q[:3].reshape(-1)) else [[0,0],[384,0],[384,384],[0,384]],np.float32)
        source=cv2.getPerspectiveTransform(q,dst)
        for pair in [v for v in pairs if v['query']==i and v['valid']]:
            j=pair['gallery'];registration=np.vstack([pair['transform'],[0,0,1]])
            matrix=np.diag([1/3,1/3,1])@registration@source
            inverse=np.linalg.inv(matrix);target=np.array([[0,0,1],[128,0,1],[128,128,1],[0,128,1]],float)@inverse.T;target=target[:,:2]/target[:,2:]
            if (target<0).any() or (target[:,0]>=image.shape[1]).any() or (target[:,1]>=image.shape[0]).any():continue
            raw=cv2.cvtColor(cv2.warpPerspective(image,matrix,(128,128)),cv2.COLOR_BGR2GRAY)
            pixels=normalize_roi(raw)[0];feature=base.extract(pixels);score=float(base.match(feature,banks[j,0].astype(bool)))
            distance[i,j]=min(distance[i,j],score)
            details.append(dict(query=i,gallery=j,baseline=float(baseline[i,j]),aligned=score,inliers=pair['inliers']))
        if (i+1)%10==0:print(i+1,flush=True)
    np.save(out/'distances.npy',distance);save('pair-details.json',details)
    cases=[r for r in json.loads((root/'stability/results.json').read_text()) if r['algorithm']=='FastCCPoseNearest-v1' and '_to_' not in r['case']];results=[]
    for count in [1,2]:
        for c in cases:
            gs={k:[lookup[s] for s in ids] for k,ids in c['gallery'].items()};trials=[]
            for t in c['trials']:
                i=lookup[t['sample']];sc={k:float(np.sort(distance[i,ids])[:count].mean()) for k,ids in gs.items()}
                trials.append(dict(sample=t['sample'],identity=t['identity'],correct=sc[t['identity']]<min(v for k,v in sc.items() if k!=t['identity']),scores=sc))
            results.append(dict(case=c['case'],best_n=count,correct=sum(t['correct'] for t in trials),total=20,trials=trials))
        print(count,[(r['case'],r['correct']) for r in results if r['best_n']==count],flush=True)
    save('results.json',results)


if __name__=='__main__':main()
