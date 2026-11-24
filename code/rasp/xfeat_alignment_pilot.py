"""Isolated XFeat proposal adapter. Not registered as an application matcher.

Exports and third-party weights live outside source control. This decoder
follows upstream sparse extraction (5x5 NMS, .05 detection, best1000,
bicubic descriptors); target-device speed/recognition require separate checks.
"""
import hashlib,json
from pathlib import Path
import cv2,numpy as np
from pklnet_roi import normalize_roi_pixels


def xfeat_pairs(a,b):
    """Upstream MNN with default cosine >.82 on L2-normalized descriptors."""
    if not len(a) or not len(b):return []
    forward=cv2.BFMatcher().knnMatch(a,b,k=1)
    reverse=cv2.BFMatcher().knnMatch(b,a,k=1)
    return [(m.queryIdx,m.trainIdx) for (m,) in forward
        if m.distance*m.distance<2*(1-.82) and reverse[m.trainIdx][0].trainIdx==m.queryIdx]


def decode_sparse(features,logits,reliability,side,top_k=1000):
    f=features[0];f=f/np.maximum(np.linalg.norm(f,axis=0,keepdims=True),1e-12)
    logits=logits[0];prob=np.exp(logits-logits.max(axis=0,keepdims=True))
    prob/=prob.sum(axis=0,keepdims=True)
    h,w=prob.shape[1:]
    heat=prob[:64].transpose(1,2,0).reshape(h,w,8,8).transpose(0,2,1,3).reshape(h*8,w*8)
    y,x=np.nonzero((heat==cv2.dilate(heat,np.ones((5,5),np.uint8)))&(heat>.05))
    if not len(x):return np.empty((0,2),np.float32),np.empty((0,64),np.float32)
    xy=np.column_stack([x,y]).astype(np.float32)
    def sample(image,mode):
        # Upstream normalizes by original W-1/H-1, then grid_sample uses
        # align_corners=False. Include the half-pixel offset explicitly.
        # Compute the normalize/unnormalize steps in the upstream order.
        grid=2*(xy/np.float32(side-1))-1
        mx=((grid[:,0]+1)*image.shape[1]-1)/2
        my=((grid[:,1]+1)*image.shape[0]-1)/2
        values=image[...,None] if image.ndim==2 else image
        out=np.zeros((len(x),values.shape[2]),np.float32)
        def add(ix,iy,weight):
            valid=(ix>=0)&(ix<image.shape[1])&(iy>=0)&(iy<image.shape[0])
            out[valid]+=values[iy[valid],ix[valid]]*weight[valid,None]
        if mode==cv2.INTER_NEAREST:
            add(np.rint(mx).astype(int),np.rint(my).astype(int),np.ones(len(x),np.float32))
            return out
        fx=np.floor(mx).astype(int);fy=np.floor(my).astype(int)
        if mode==cv2.INTER_LINEAR:
            for iy in (0,1):
                for ix in (0,1):
                    add(fx+ix,fy+iy,(1-np.abs(mx-fx-ix))*(1-np.abs(my-fy-iy)))
        else:
            def cubic(t):
                t=np.abs(t);a=-.75
                return np.where(t<=1,((a+2)*t-(a+3))*t*t+1,
                    np.where(t<2,((a*t-5*a)*t+8*a)*t-4*a,0))
            for iy in (-1,0,1,2):
                for ix in (-1,0,1,2):add(fx+ix,fy+iy,cubic(mx-fx-ix)*cubic(my-fy-iy))
        return out
    # Integer NMS positions sample their own heatmap cells under the upstream
    # nearest convention; reliability is interpolated at coarse resolution.
    score=sample(heat,cv2.INTER_NEAREST).ravel()*sample(reliability[0,0],cv2.INTER_LINEAR).ravel()
    score[(x==0)&(y==0)]=-1
    ids=np.argsort(-score,kind='stable')[:top_k];ids=ids[score[ids]>0]
    desc=sample(f.transpose(1,2,0).copy(),cv2.INTER_CUBIC)
    desc/=np.maximum(np.linalg.norm(desc,axis=1,keepdims=True),1e-12)
    return xy[ids],desc[ids].astype(np.float32)


class XFeatProposal:
    def __init__(self,root,threads=1):
        import onnxruntime as ort
        root=Path(root);meta=json.loads((root/'metadata.json').read_text(encoding='utf-8'))
        self.sessions={}
        for side in (384,768):
            path=root/f'xfeat-{side}.onnx'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['models'][str(side)]
            options=ort.SessionOptions();options.intra_op_num_threads=threads;options.inter_op_num_threads=1
            self.sessions[side]=ort.InferenceSession(str(path),sess_options=options,providers=['CPUExecutionProvider'])

    def __call__(self,native,source,wide):
        side=768 if wide else 384;offset=192 if wide else 0
        shift=np.asarray([[1.,0,offset],[0,1.,offset],[0,0,1.]])
        pixels=normalize_roi_pixels(cv2.warpPerspective(native,shift@source,(side,side)))
        values=self.sessions[side].run(None,{'image':pixels[None,None].astype(np.float32)/255})
        p,d=decode_sparse(*values,side)
        return [(p-offset,d)]
