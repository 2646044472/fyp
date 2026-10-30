"""Isolated, opt-in recovery for an existing out-of-bounds PKLNet result.

No identity/filename/score input. Valid primary results pass through verbatim.
Only one half-turn retry is permitted, retaining the existing geometry and
illumination-overlap guard. This is not an anatomical visibility detector.
"""
import copy
import time

import cv2
import numpy as np
from PIL import Image

from pklnet_roi import MIN_ILLUMINATION_IOU

POLICY='out-of-bounds-halfturn-recovery-pilot-v1'


def map_points(points, size):
    value=np.asarray(points,np.float32)
    if value.size%2 or not np.isfinite(value).all():
        raise ValueError('Expected finite xy points')
    return (np.asarray(size,np.float32)-1-value.reshape(-1,2)).reshape(value.shape)


def quad_iou(left, right):
    a,b=np.asarray(left,np.float32),np.asarray(right,np.float32)
    if a.shape!=(4,2) or b.shape!=(4,2) or not np.isfinite(np.r_[a,b]).all():
        return 0.
    intersection=max(0.,float(cv2.intersectConvexConvex(a,b)[0]))
    union=abs(cv2.contourArea(a))+abs(cv2.contourArea(b))-intersection
    return float(np.clip(intersection/max(union,1e-12),0,1))


def mapped_details(details, size):
    """Map all existing localization candidate/diagnostic coordinates back."""
    result=copy.deepcopy(details)
    for key in ('pklnet_keypoints','pklnet_heatmap_keypoints','pklnet_fc_keypoints',
                'pklnet_full_frame_keypoints','roi_quad_full','pklnet_heatmap_quad',
                'pklnet_fc_quad','pklnet_full_frame_quad'):
        if key in result:
            result[key]=map_points(result[key],size).tolist()
    for candidate in result.get('pklnet_roi_candidates',[]):
        candidate['quad']=map_points(candidate['quad'],size).tolist()
    if 'pklnet_retry_box' in result:
        left,top,right,bottom=result['pklnet_retry_box'];width,height=size
        result['pklnet_retry_box']=[width-right,height-bottom,width-left,height-top]
    return result


class HalfTurnROIRecovery:
    def __init__(self, base):
        self.base=base
        self.last_trace=None

    def __getattr__(self,name):
        return getattr(self.base,name)

    def extract(self,image,*,side=128):
        return self.recover(image,self.base.extract(image,side=side),side=side)

    def recover(self,image,primary,*,side=128):
        """Also accepts an observed primary for a paired localization audit."""
        raw,quad,details=primary
        trace=dict(policy=POLICY,retry=False,recovered=False,
            primary_valid=bool(details['roi_geometry_valid']),
            primary_reason=details.get('roi_geometry_reason'))
        self.last_trace=trace
        if details['roi_geometry_valid']:
            trace['reason']='valid_primary_passthrough';return primary
        if details.get('roi_geometry_reason')!='roi_out_of_bounds':
            trace['reason']='failure_outside_candidate_scope';return primary
        trace['retry']=True;started=time.perf_counter()
        rotated=image.transpose(Image.Transpose.ROTATE_180)
        _,candidate,other=self.base.extract(rotated,side=side)
        trace['retry_ms']=(time.perf_counter()-started)*1000
        trace['retry_geometry_valid']=bool(other['roi_geometry_valid'])
        if not other['roi_geometry_valid']:
            trace['reason']='retry_geometry_invalid';return primary
        mapped=map_points(candidate,image.size)
        in_bounds=(mapped.shape==(4,2) and np.isfinite(mapped).all() and (mapped>=0).all()
            and (mapped[:,0]<image.width).all() and (mapped[:,1]<image.height).all())
        if not in_bounds:
            trace['reason']='mapped_retry_out_of_bounds';return primary
        overlap=quad_iou(quad,mapped);trace['primary_retry_iou']=overlap
        trace['min_iou']=MIN_ILLUMINATION_IOU
        if overlap<MIN_ILLUMINATION_IOU:
            trace['reason']='orientation_localization_disagreement';return primary
        rgb=np.asarray(image.convert('RGB'),np.uint8)
        recovered=self.base._roi_extractor.getROIimg(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mapped,side=side,ratio=1.)
        if recovered is None or recovered.shape!=(side,side):
            raise ValueError('Half-turn recovery perspective sampling failed')
        revised=mapped_details(other,image.size)
        revised.update(roi_quad_full=mapped.tolist(),roi_in_bounds=True,
            roi_geometry_valid=True,roi_geometry_reason=None,
            pklnet_recovery_policy=POLICY,pklnet_recovery_turns=2,
            pklnet_recovery_primary_reason=details['roi_geometry_reason'],
            pklnet_recovery_primary_quad=np.asarray(quad).tolist(),
            pklnet_recovery_iou=overlap)
        trace.update(recovered=True,reason='recovered_geometry_only',mapped_quad=mapped.tolist())
        return recovered.astype(np.uint8),mapped,revised
