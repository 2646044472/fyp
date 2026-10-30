"""Opt-in geometric web-row evidence; never imported by production.

Uses image geometry only to define one alternative ROI per frame. Full gallery
and five-frame aggregation stay intact; existing confident evidence wins first.
"""
import itertools
import types

import cv2
import numpy as np

from observe_contour_valleys import silhouettes
from anchored_matcher import source_quad,overlaps_anchor
from pklnet_policy import MIN_KEYPOINT_SPAN_RATIO

POLICY='four-web-silhouette-compnet-pilot-v1'


def proposal(native,anchor,geometry):
    gray=np.asarray(native,np.uint8)
    if gray.ndim!=2:raise ValueError('Native grayscale frame required')
    rgb=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB);small,observations,_=silhouettes(rgb)
    height,width=gray.shape;sy,sx=height/small.shape[0],width/small.shape[1]
    accepted=[];diagnostics=[]
    for item in observations:
        trace=dict(polarity=item['polarity'],candidate_count=item['candidate_count'],accepted=False)
        diagnostics.append(trace)
        if item['error'] or item['candidate_count']!=4 or item['touched_image_edges']>2:
            trace['reason']='noncanonical_or_background_component';continue
        points=np.asarray(item['candidate_valleys'],np.float64);triples=[]
        for indices in itertools.combinations(range(4),3):
            p=points[list(indices)]
            i,j=max(itertools.combinations(range(3),2),key=lambda pair:np.linalg.norm(p[pair[0]]-p[pair[1]]))
            k=next(v for v in range(3) if v not in (i,j));a,b,c=p[i],p[j],p[k]
            span=float(np.linalg.norm(b-a));left=c-a;right=b-c
            cosine=float(np.dot(left,right)/max(1e-12,np.linalg.norm(left)*np.linalg.norm(right)))
            residual=abs(float((b-a)[0]*(c-a)[1]-(b-a)[1]*(c-a)[0]))/max(span*span,1e-12)
            triples.append((residual,cosine,a,b,indices))
        triples.sort(key=lambda v:v[0]);best=triples[0]
        if best[1]<.8 or np.isclose(best[0],triples[1][0],rtol=0,atol=1e-6):
            trace['reason']='ambiguous_or_bent_web_row';continue
        to_native=lambda p:(np.asarray(p,np.float64)+.5)*np.asarray([sx,sy])-.5
        a,b=to_native(best[2]),to_native(best[3]);center=to_native(item['distance_center'])
        trace.update(row_residual=best[0],row_cosine=best[1],keypoints=np.r_[a,b,center].tolist())
        if np.linalg.norm(b-a)/min(width,height)<MIN_KEYPOINT_SPAN_RATIO:
            trace['reason']='span_too_small';continue
        quad=np.asarray(geometry.getROIckp(a,b,geometry.isAntiClock(np.r_[a,b,center])),np.float32)
        if not ((quad>=0).all() and (quad[:,0]<width).all() and (quad[:,1]<height).all()):
            trace['reason']='out_of_bounds';continue
        # All four corners must remain inside this silhouette's component.
        gr=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
        _,binary=cv2.threshold(gr,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        if item['polarity']=='dark':binary=255-binary
        contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contour=np.asarray(max(contours,key=cv2.contourArea),np.int32).reshape(-1,1,2)
        local=(quad+.5)/np.asarray([sx,sy])-.5
        if any(cv2.pointPolygonTest(contour,tuple(map(float,p)),False)<0 for p in local):
            trace['reason']='roi_corners_outside_silhouette';continue
        if not overlaps_anchor(quad,anchor):
            trace['reason']='disjoint_from_existing_anchor';continue
        trace.update(accepted=True,reason='geometric_candidate_only',quad=quad.tolist());accepted.append(quad)
    return (accepted[0] if len(accepted)==1 else None),dict(policy=POLICY,polarities=diagnostics,
        reason='unique_candidate' if len(accepted)==1 else 'none_or_ambiguous_polarity')


def matrix(quad,geometry):
    dst=np.asarray([[384,0],[0,0],[0,384],[384,384]] if geometry.isAntiClock(quad[:3].reshape(-1))
        else [[0,0],[384,0],[384,384],[0,384]],np.float32)
    return cv2.getPerspectiveTransform(quad,dst)


def install(algorithm):
    if getattr(algorithm,'_contour_pilot_installed',False):
        raise ValueError('Contour pilot already installed')
    old_prepare=algorithm.prepare_enrollment;old_aux=algorithm._auxiliary_scores
    algorithm._contour_preparation_trace=[];algorithm._contour_query_trace=[]
    def prepare(self,features):
        samples=old_prepare(features);result=[]
        if len(samples)!=len(features):raise ValueError('Enrollment frame count changed')
        for feature,sample in zip(features,samples):
            if len(sample)!=6:raise ValueError('Expected frozen six-field enrollment tuple')
            unpacked=self._unpack(feature)
            quad,trace=proposal(unpacked[3],source_quad(unpacked[1][2]),self.geometry)
            vector=sample[5] if quad is None else self._embedding(unpacked[3],matrix(quad,self.geometry))
            self._contour_preparation_trace.append(trace);result.append((*sample,vector))
        return result
    def auxiliary(self,probe,groups):
        original=old_aux(probe,groups)
        if original is None or self.confident(original):return original
        quad,trace=proposal(probe.native,source_quad(probe.source),self.geometry)
        self._contour_query_trace.append(trace)
        if quad is None:return original
        keys=[(u,j) for u,ss in groups.items() for j in range(len(ss))]
        vectors=np.asarray([groups[u][j][6] for u,j in keys]);assert vectors.shape==(len(keys),512)
        query=self._embedding(probe.native,matrix(quad,self.geometry))
        distances=np.arccos(np.clip(vectors@query,-1,1))/np.pi;pairs=dict(zip(keys,distances))
        scores={u:self._aggregate([pairs[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
        trace.update(scores={k:float(v) for k,v in scores.items()},confident=bool(self.confident(scores)))
        if self.confident(scores):
            probe.auxiliary_route='compnet_contour_roi_confident';probe.auxiliary_roi_quad=quad
            return scores
        return original
    algorithm.prepare_enrollment=types.MethodType(prepare,algorithm)
    algorithm._auxiliary_scores=types.MethodType(auxiliary,algorithm)
    algorithm._contour_pilot_installed=True
    return algorithm
