"""Frozen, identity-independent additional localizer windows."""
import numpy as np
from PIL import Image
from pklnet_roi import LOCALIZER_GAMMA, MIN_KEYPOINT_SPAN_RATIO


def window_candidates(image, engine):
    w,h=image.size; boxes=[]
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
            # Model/runtime failures must surface, not silently reduce candidates.
            _,q,d=engine.extract(view)
            offset=np.asarray(box[:2]);q=np.asarray(q)+offset
            k=np.asarray(d['pklnet_keypoints']).reshape(3,2)+offset
            valid=bool(np.isfinite(q).all() and (q>=0).all() and (q[:,0]<w).all() and (q[:,1]<h).all()
                       and np.linalg.norm(k[0]-k[1])/min(w,h)>=MIN_KEYPOINT_SPAN_RATIO)
            candidates.append(dict(box=list(box),gamma=gamma,quad=q.tolist(),valid=valid,kind='window'))
    return candidates
