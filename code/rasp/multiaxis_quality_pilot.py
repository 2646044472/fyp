"""Three fixed orthogonal Gabor comparisons, research-only proposal distance.

Not registered in the application. This changes the biometric distance and
requires accuracy, latency and unknown-person calibration before adoption.
"""
import cv2,numpy as np
from pklnet_roi import normalize_roi_pixels
from pose_matcher import POSES


def multiaxis_bank(native,source,kernels,poses=POSES):
    center=np.asarray([[1.,0,192],[0,1.,192],[0,0,1.]])
    uncenter=np.asarray([[1.,0,-192],[0,1.,-192],[0,0,1.]])
    corners=np.asarray([[0.,0,1],[128.,0,1],[128.,128,1],[0,128.,1]])
    signs=[];weights=[]
    for angle,scale in poses:
        angle=np.deg2rad(angle)
        inverse=np.asarray([[np.cos(angle),np.sin(angle),0],[-np.sin(angle),np.cos(angle),0],[0,0,scale]])/scale
        warp=np.diag([1/3,1/3,1])@center@inverse@uncenter@source
        mapped=corners@np.linalg.inv(warp).T;mapped=mapped[:,:2]/mapped[:,2:]
        if (not np.isfinite(mapped).all() or (mapped<1).any()
            or (mapped[:,0]>=native.shape[1]-1).any() or (mapped[:,1]>=native.shape[0]-1).any()):continue
        pixels=normalize_roi_pixels(cv2.warpPerspective(native,warp,(128,128)))
        responses=np.asarray([cv2.filter2D(pixels.astype(np.float64),cv2.CV_64F,k,borderType=cv2.BORDER_CONSTANT)[::4,::4] for k in kernels])
        weight=np.sqrt(np.abs(responses))
        weight[:,:2]=0;weight[:,-2:]=0;weight[:,:,:2]=0;weight[:,:,-2:]=0
        signs.append(np.where(responses>0,1.,-1.));weights.append(weight)
    return (np.asarray(signs),np.asarray(weights)) if signs else None


def multiaxis_distances(query,gallery):
    qs,qw=query;gs,gw=gallery
    qws=qs*qw;gws=gs*gw;best=np.ones(len(gs),np.float64)
    for dy in range(-4,5):
        for dx in range(-4,5):
            a=(slice(max(-dy,0),32-max(dy,0)),slice(max(-dx,0),32-max(dx,0)))
            b=(slice(max(dy,0),32-max(-dy,0)),slice(max(dx,0),32-max(-dx,0)))
            left=np.ascontiguousarray(qw[:,:,a[0],a[1]].reshape(len(qw),-1))
            right=np.ascontiguousarray(gw[:,:,b[0],b[1]].reshape(len(gw),-1))
            denominator=cv2.gemm(left,right,1,None,0,flags=cv2.GEMM_2_T)
            left=np.ascontiguousarray(qws[:,:,a[0],a[1]].reshape(len(qw),-1))
            right=np.ascontiguousarray(gws[:,:,b[0],b[1]].reshape(len(gw),-1))
            correlation=cv2.gemm(left,right,1,None,0,flags=cv2.GEMM_2_T)
            distance=np.ones_like(denominator)
            np.divide(correlation,denominator,out=distance,where=denominator>0)
            distance=np.where(denominator>0,.5*(1-distance),1.)
            best=np.minimum(best,np.clip(distance,0,1).min(axis=0))
    return best
