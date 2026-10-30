"""Geometric sampling support and FastCC receptive-field diagnostics.

Mask propagation uses an independent all-valid source plane and the actual
warp chain, never image intensity. Full 17x17 filter support is required before
sampling at stride four. Feature arrays and masks stay in process memory.
"""
import cv2,numpy as np


def propagate_support(native_shape, chain, source_mask=None):
    support=np.ones(native_shape,np.float32)if source_mask is None else np.asarray(source_mask,np.float32)
    if support.shape!=tuple(native_shape):raise ValueError('Mask/native shape mismatch')
    for matrix,size in chain:
        support=cv2.warpPerspective(support,np.asarray(matrix,np.float64),tuple(size),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    if support.shape!=(128,128):raise ValueError('Final support must have 128px crop geometry')
    pixels=(support>=1-4*np.finfo(np.float32).eps).astype(np.uint8)
    valid=cv2.erode(pixels,np.ones((17,17),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)[::4,::4].astype(bool)
    return valid,dict(valid_pixels=int(pixels.sum()),invalid_pixels=int(pixels.size-pixels.sum()),valid_features=int(valid.sum()),total_features=1024)


def overlap_slices(dy,dx):
    return ((slice(max(-dy,0),32-max(dy,0)),slice(max(-dx,0),32-max(dx,0))),
            (slice(max(dy,0),32-max(-dy,0)),slice(max(dx,0),32-max(-dx,0))))


def compare_codes(left,right,left_valid,right_valid):
    left,right,left_valid,right_valid=[np.asarray(v,bool)for v in(left,right,left_valid,right_valid)]
    if any(v.shape!=(32,32)for v in(left,right,left_valid,right_valid)):raise ValueError('FastCC support requires 32x32 arrays')
    rows=[]
    for dy in range(-4,5):
        for dx in range(-4,5):
            a,b=overlap_slices(dy,dx);different=left[a]!=right[b];valid=left_valid[a]&right_valid[b]
            total=different.size;count=int(valid.sum());mismatch=int(different.sum());vm=int(np.count_nonzero(different&valid));invalid=total-count
            rows.append(dict(dx=dx,dy=dy,total_bits=total,valid_bits=count,invalid_bits=invalid,
                mismatches=mismatch,valid_mismatches=vm,invalid_mismatches=mismatch-vm,invalid_agreements=invalid-(mismatch-vm),
                original_score=mismatch/total,supported_score=vm/count if count else 1.))
    old=min(v['original_score']for v in rows);new=min(v['supported_score']for v in rows)
    return dict(original_score=old,supported_score=new,
        original_winners=[v for v in rows if v['original_score']==old],
        supported_winners=[v for v in rows if v['supported_score']==new])


def constant_rf_mask():
    mask=np.zeros((32,32),bool);mask[2:30,2:30]=True;return mask


class ReceptiveFieldFastCC:
    """Ablation only: ordinary matching over fully supported filter responses.

Use only after the geometric audit establishes no additional invalid interior
support in the scoring paths. Thresholds are not changed. This is a different
distance definition, not an exact acceleration of the old score.
"""
    def __init__(self):
        self.mask=constant_rf_mask().astype(np.float32)
        self.denominator=self._correlate(self.mask,self.mask)

    @staticmethod
    def _correlate(left,right):
        return np.rint(cv2.matchTemplate(np.pad(left,4),right,cv2.TM_CCORR))[::-1,::-1].astype(np.float64)

    def match(self,left,right):
        left=np.asarray(left,bool).astype(np.float32)*self.mask;right=np.asarray(right,bool).astype(np.float32)*self.mask
        different=self._correlate(left,self.mask)+self._correlate(self.mask,right)-2*self._correlate(left,right)
        return float(np.min(different/self.denominator))
