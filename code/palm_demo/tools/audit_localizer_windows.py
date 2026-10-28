"""Retain individual fixed 4:3-window predictions instead of their median.

The localizer and weights are frozen; no labels or manual points are inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from PIL import Image

APP=Path(__file__).resolve().parents[1];sys.path.insert(0,str(APP))
from pklnet_roi import PKLNetROI,LOCALIZER_GAMMA,MIN_KEYPOINT_SPAN_RATIO


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);args=p.parse_args();root=args.root;out=root/'single-device/localizer-windows';out.mkdir(exist_ok=False)
    def save(n,v):(out/n).write_text(json.dumps(v,indent=2))
    save('plan.json',dict(inference='frozen heatmap model, original and gamma0.6; largest4:3 windows at three equally-spaced positions',
        skip='aspect ratio already within .05 of4/3; this is an image-geometry rule, not a device or identity rule',
        geometry='finite, all corners in original image, keypoint span/original short side >= existing .1',
        purpose='Test whether valid but small full-frame predictions miss a palm region; retain hypotheses rather than coordinate median',
        labels='only carried into records, never used for inference'))
    rows=json.loads((root/'stability/records.json').read_text());engine=PKLNetROI(policy='heatmap',threads=2);results=[];started=time.perf_counter()
    for n,r in enumerate(rows):
        assert hashlib.sha256(Path(r['original']).read_bytes()).hexdigest()==r['sha256']
        image=Image.open(r['original']).convert('RGB');w,h=image.size;boxes=[]
        if abs(w/h-4/3)>.05:
            if w/h>4/3:
                cw=int(h*4/3);boxes=[(int(v*(w-cw)),0,int(v*(w-cw))+cw,h) for v in [0,.5,1]]
            else:
                ch=int(w*3/4);boxes=[(0,int(v*(h-ch)),w,int(v*(h-ch))+ch) for v in [0,.5,1]]
        candidates=[]
        for box in boxes:
            for gamma in [False,True]:
                view=image.crop(box)
                if gamma:view=Image.fromarray(np.rint((np.asarray(view,dtype=np.float32)/255)**LOCALIZER_GAMMA*255).astype(np.uint8))
                try:
                    _,q,d=engine.extract(view);offset=np.array(box[:2]);q=np.asarray(q)+offset;k=np.asarray(d['pklnet_keypoints']).reshape(3,2)+offset
                    valid=bool(np.isfinite(q).all() and (q>=0).all() and (q[:,0]<w).all() and (q[:,1]<h).all() and np.linalg.norm(k[0]-k[1])/min(w,h)>=MIN_KEYPOINT_SPAN_RATIO)
                    candidates.append(dict(box=list(box),gamma=gamma,quad=q.tolist(),keypoints=k.tolist(),valid=valid))
                except Exception as e:
                    candidates.append(dict(box=list(box),gamma=gamma,valid=False,error=str(e)))
        results.append(dict(sample=r['sample'],sha256=r['sha256'],candidates=candidates));save('candidates.json',results)
        print(n+1,len(candidates),sum(c['valid'] for c in candidates),round(time.perf_counter()-started,1),flush=True)
    save('timing.json',dict(seconds=time.perf_counter()-started))


if __name__=='__main__':main()
