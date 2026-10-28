"""Fixed pose-tolerant matching, with unchanged clean five-image enrollment.

All identities receive the same pose grid. One query pose must agree with the
median of all five templates; no label-dependent ROI choice or probe deletion.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP))
from pklnet_roi import PKLNET_ROOT, normalize_roi
from palm_app.biometric import load_algorithm


def fast_don_match(left,right):
    """Exact original weighted XOR minimum, via rounded binary correlations."""
    if left.shape!=right.shape or left.ndim!=3 or left.shape[0]!=3:
        raise ValueError('Expected equal 3xHxW DoN codes')
    _,h,w=left.shape;sh=7;ch,cw=h-2*sh,w-2*sh
    if ch<=0 or cw<=0:raise ValueError('DoN code is too small')
    total=np.zeros((2*sh,2*sh),np.int64)
    for c,weight in enumerate([6,2,2]):
        template=np.asarray(left[c,sh:-sh,sh:-sh],np.float32)
        target=np.asarray(right[c],np.float32)
        correlations=np.rint(cv2.matchTemplate(target,template,cv2.TM_CCORR)).astype(np.int64)
        summed=cv2.integral(target,sdepth=cv2.CV_64F)
        counts=summed[ch:,cw:]-summed[:-ch,cw:]-summed[ch:,:-cw]+summed[:-ch,:-cw]
        xor=template.sum(dtype=np.float64)+counts-2*correlations
        total+=np.rint(xor[:2*sh,:2*sh]).astype(np.int64)*weight
    return float(total.min()/(10*3*h*w))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('replay',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--roi-transform',action='store_true',help='Test transforms of saved ROI rather than expanded full-image context')
    p.add_argument('--condition',choices=['dark_065','blur_sigma3','shift_3pct'])
    p.add_argument('--stress-diagnostics',type=Path)
    p.add_argument('--wide',action='store_true',help='Additional fixed25-pose development control')
    args=p.parse_args()
    if bool(args.condition)!=bool(args.stress_diagnostics):p.error('Provide both --condition and --stress-diagnostics')
    args.output.mkdir(parents=True,exist_ok=False)
    def save(name,obj):(args.output/name).write_text(json.dumps(obj,indent=2))
    poses=[(0,1),(-12,1),(12,1),(0,.85),(0,1.15),(-12,.85),(-12,1.15),(12,.85),(12,1.15)]
    if args.wide:
        poses=[(0,1)]+[(angle,scale) for angle in [-24,-12,0,12,24] for scale in [.75,.85,1,1.15,1.3] if (angle,scale)!=(0,1)]
    save('plan.json',dict(poses=poses,controls=['baseline','rotation','scale','rotation_scale'],roi_transform=args.roi_transform,condition=args.condition,
         aggregation='min across query poses of median distance to all5 templates for each identity',
         limitation='Repeatedly inspected development data; not independent validation; same grid for every identity'))
    rows=json.loads((args.replay/'extraction.json').read_text())
    diagnostics={r['sample']:r for r in json.loads(args.stress_diagnostics.read_text()) if r['policy']=='v5' and r['condition']==args.condition} if args.condition else None
    algorithms={name:load_algorithm(APP/'vendor/palmprint-recognition-python',name) for name in ['DoN','FastCC']}
    rng=np.random.default_rng(48);errors=[]
    for _ in range(6):
        a=rng.random((3,128,128))>.5;b=rng.random((3,128,128))>.5
        errors.append(abs(fast_don_match(a,b)-algorithms['DoN'].match(a,b)))
    assert max(errors)<1e-12
    identities=sorted({r['identity'] for r in rows});gallery={k:[i for i,r in enumerate(rows) if r['identity']==k and r['index']<=5] for k in identities}
    pixels=[np.asarray(Image.open(args.replay/'rois'/r['sample']/'illumination/roi_128.png').convert('L')) for r in rows]
    features={name:[alg.extract(im) for im in pixels] for name,alg in algorithms.items()}
    # Check the optimized distance on real palm codes, not just random bits.
    for a,b in [(0,1),(2,12),(4,31),(10,39)]:errors.append(abs(fast_don_match(features['DoN'][a],features['DoN'][b])-algorithms['DoN'].match(features['DoN'][a],features['DoN'][b])))
    assert max(errors)<1e-12;save('distance-parity.json',dict(max_error=max(errors),checks=len(errors)))
    spec=importlib.util.spec_from_file_location('pose_geometry',PKLNET_ROOT/'roiExtractor.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
    trials=[]
    for i,row in enumerate(rows):
        if row['index']<=5:continue
        image=np.asarray(Image.open(row['original']).convert('RGB'))
        q=np.asarray(row['illumination']['details']['roi_quad_full'],np.float32)
        if diagnostics is not None:
            from stress_roi_pipeline import perturb
            image,_=perturb(image,args.condition)
            diagnostic=diagnostics[row['sample']]
            if not diagnostic.get('details',{}).get('roi_geometry_valid',False):
                trials.append(dict(sample=row['sample'],identity=row['identity'],poses=[],ms=0,invalid_geometry=True))
                continue
            q=np.asarray(diagnostic['quad'],np.float32)
        bgr=cv2.cvtColor(image,cv2.COLOR_RGB2BGR);center=q.mean(0)
        if diagnostics is not None:pixels[i]=normalize_roi(geo.getROIimg(bgr,q))[0]
        pose_results=[];started=time.perf_counter()
        for index,(angle,scale) in enumerate(poses):
            rad=np.deg2rad(angle);rotation=np.array([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]])
            quad=((q-center)@rotation.T*scale+center).astype(np.float32)
            valid=bool((quad>=0).all() and (quad[:,0]<image.shape[1]).all() and (quad[:,1]<image.shape[0]).all())
            if not valid:continue
            if index==0:im=pixels[i]
            elif args.roi_transform:
                matrix=cv2.getRotationMatrix2D((64,64),-angle,1/scale)
                im=cv2.warpAffine(pixels[i],matrix,(128,128),borderMode=cv2.BORDER_REFLECT_101)
            else:im=normalize_roi(geo.getROIimg(bgr,quad))[0]
            scores={};template_scores={}
            for name,alg in algorithms.items():
                f=features[name][i] if index==0 and diagnostics is None else alg.extract(im)
                matcher=fast_don_match if name=='DoN' else alg.match
                template_scores[name]={k:[float(matcher(f,features[name][j])) for j in js] for k,js in gallery.items()}
                scores[name]={k:float(np.median(v)) for k,v in template_scores[name].items()}
            pose_results.append(dict(angle=angle,scale=scale,scores=scores,template_scores=template_scores))
        trials.append(dict(sample=row['sample'],identity=row['identity'],poses=pose_results,ms=(time.perf_counter()-started)*1000))
        print(row['sample'],round(trials[-1]['ms']),flush=True)
    results=[]
    for name in algorithms:
        for condition in ['baseline','rotation','scale','rotation_scale']:
            scores=[]
            for t in trials:
                allowed=[p for p in t['poses'] if condition=='rotation_scale' or condition=='baseline' and p['angle']==0 and p['scale']==1 or condition=='rotation' and p['scale']==1 or condition=='scale' and p['angle']==0]
                if not allowed:
                    scores.append(dict(sample=t['sample'],identity=t['identity'],correct=False,scores={}))
                    continue
                aggregated={k:min(p['scores'][name][k] for p in allowed) for k in identities}
                correct=aggregated[t['identity']]<min(v for k,v in aggregated.items() if k!=t['identity'])
                scores.append(dict(sample=t['sample'],identity=t['identity'],correct=correct,scores=aggregated))
            result=dict(algorithm=name,condition=condition,correct=sum(t['correct'] for t in scores),total=len(scores),trials=scores);results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='trials'}),flush=True)
    save('trials.json',trials);save('recognition.json',results)


if __name__=='__main__':main()
