"""Experimental response-weighted FastCC rescue with fixed original pose box.

This is a new distance, not an exact implementation of ordinary Hamming.
It requires separate generalization and unknown-person calibration evidence.
"""
import cv2
import numpy as np
from pooled_enrollment_matcher import PooledEnrollmentMatcher
from pklnet_roi import normalize_roi_pixels
from pose_matcher import POSES


def quality_bank(native,source,kernel,poses=POSES):
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
        response=cv2.filter2D(pixels.astype(np.float64),cv2.CV_64F,kernel,borderType=cv2.BORDER_CONSTANT)[::4,::4]
        weight=np.sqrt(np.abs(response))
        # Kernel radius is eight pixels; feature stride is four pixels.
        # Exclude responses that depend on artificial zero padding.
        weight[:2]=0;weight[-2:]=0;weight[:,:2]=0;weight[:,-2:]=0
        signs.append(np.where(response>0,1.,-1.));weights.append(weight)
    return (np.asarray(signs),np.asarray(weights)) if signs else None


def weighted_distances(query,gallery):
    qs,qw=query;gs,gw=gallery
    qws=qs*qw;gws=gs*gw
    best=np.ones(len(gs),np.float64)
    for dy in range(-4,5):
        for dx in range(-4,5):
            a=(slice(max(-dy,0),32-max(dy,0)),slice(max(-dx,0),32-max(dx,0)))
            b=(slice(max(dy,0),32-max(-dy,0)),slice(max(dx,0),32-max(-dx,0)))
            left=np.ascontiguousarray(qw[:,a[0],a[1]].reshape(len(qw),-1))
            right=np.ascontiguousarray(gw[:,b[0],b[1]].reshape(len(gw),-1))
            denominator=cv2.gemm(left,right,1,None,0,flags=cv2.GEMM_2_T)
            left=np.ascontiguousarray(qws[:,a[0],a[1]].reshape(len(qw),-1))
            right=np.ascontiguousarray(gws[:,b[0],b[1]].reshape(len(gw),-1))
            correlation=cv2.gemm(left,right,1,None,0,flags=cv2.GEMM_2_T)
            distance=np.ones_like(denominator)
            np.divide(correlation,denominator,out=distance,where=denominator>0)
            distance=np.where(denominator>0,.5*(1-distance),1.)
            best=np.minimum(best,np.clip(distance,0,1).min(axis=0))
    return best


class QualityEvidenceMatcher(PooledEnrollmentMatcher):
    name='FastCCQualityEvidence-v24-experimental'
    magic=2801064
    template_compression_level=1

    def prepare_enrollment(self,features):
        prepared=super().prepare_enrollment(features)
        result=[]
        for sample,feature in zip(prepared,features):
            q=self._unpack(feature)
            try:bank=quality_bank(q[3],q[1][2],self.base._difference,POSES[:1])
            except ValueError:bank=None
            result.append((*sample,bank))
        return result

    def _enrollment_link_stage(self,probe,groups,pairs):
        super()._enrollment_link_stage(probe,groups,pairs)
        aggregate=lambda:{u:self._aggregate([pairs[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
        if self.confident(aggregate()):return
        keys=[(u,j) for u,ss in groups.items() for j in range(len(ss))]
        banks=[groups[u][j][4] for u,j in keys]
        if any(bank is None for bank in banks):return
        try:query=quality_bank(probe.native,probe.source,self.base._difference)
        except ValueError:return
        if query is None:return
        gallery=(np.concatenate([b[0] for b in banks]),np.concatenate([b[1] for b in banks]))
        weighted=dict(zip(keys,weighted_distances(query,gallery)))
        scores={u:self._aggregate([weighted[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
        if self.confident(scores):
            # Keep this new metric separate: replace all pair scores together,
            # never take minima across distances with different definitions.
            pairs.update(weighted)
            probe.link_stage_route='quality_evidence_confident'
