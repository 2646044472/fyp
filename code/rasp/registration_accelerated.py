"""Experimental shared-distance registration; reference path handles near ties.

Both directions of descriptor matching use one distance matrix. No descriptor,
candidate, ratio test, mutual check or geometric guard is intentionally removed.
Numerical parity must be audited on the target CPU before enabling this path.
The dense-matrix path proved slower on Pi and is NOT enabled by either matcher.
The proposal matcher reuses only the unchanged geometric estimator below.
"""
import cv2
import numpy as np
from registered_matcher import _RANSAC_LOCK, SIDE


def mutual_pairs(left, right):
    """Return query/train pairs passing the original ratio and mutual tests."""
    a, b = np.asarray(left), np.asarray(right)
    if min(len(a), len(b)) < 4:
        return []
    if (a.dtype != np.float32 or b.dtype != np.float32 or a.shape[1:] != (128,)
            or b.shape[1:] != (128,) or not np.isfinite(a).all() or not np.isfinite(b).all()
            or (a<0).any() or (b<0).any()
            or np.max(np.sum(a*a,axis=1))>1.001 or np.max(np.sum(b*b,axis=1))>1.001):
        forward=cv2.BFMatcher().knnMatch(a,b,k=2)
        reverse=cv2.BFMatcher().knnMatch(b,a,k=1)
        return [(m.queryIdx,m.trainIdx) for m,n in forward
                if m.distance<.85*n.distance and reverse[m.trainIdx][0].trainIdx==m.queryIdx]
    distances=-2*(a@b.T)
    distances+=np.sum(a*a,axis=1)[:,None]
    distances+=np.sum(b*b,axis=1)[None,:]
    reverse=distances.argmin(axis=0)
    rows=np.arange(len(a));first=distances.argmin(axis=1)
    best=distances[rows,first].copy()
    distances[rows,first]=np.inf
    second=distances.min(axis=1)
    distances[rows,first]=best
    # RootSIFT vectors have squared norm <= 1.001. This intentionally loose
    # tolerance covers float32 dot/subtraction error; ambiguous decisions are
    # recomputed in the unchanged OpenCV BF implementation.
    tolerance=1e-4
    accepted=best < (.85**2)*second
    uncertain=(np.abs(best-(.85**2)*second)<=tolerance) | ((second-best)<=tolerance)
    for i in np.flatnonzero(uncertain):
        m,n=cv2.BFMatcher().knnMatch(a[i:i+1],b,k=2)[0]
        first[i]=m.trainIdx
        accepted[i]=m.distance<.85*n.distance
    pairs=[]
    for i in np.flatnonzero(accepted):
        j=first[i];column=distances[:,j];nearest=reverse[j]
        if np.count_nonzero(column<=column[nearest]+tolerance)>1:
            nearest=cv2.BFMatcher().knnMatch(b[j:j+1],a,k=1)[0][0].trainIdx
        if nearest==i:pairs.append((int(i),int(j)))
    return pairs


def registration(left, right):
    pa,da=left;pb,db=right
    pairs=mutual_pairs(da,db)
    return estimate_pairs(pa,pb,pairs)


def estimate_pairs(pa,pb,pairs):
    if len(pairs)<4:return None
    p=np.asarray([pa[i] for i,j in pairs],np.float32)
    q=np.asarray([pb[j] for i,j in pairs],np.float32)
    with _RANSAC_LOCK:
        cv2.setRNGSeed(20261028)
        transform,mask=cv2.estimateAffinePartial2D(p,q,method=cv2.RANSAC,
            ransacReprojThreshold=3.,maxIters=2000,confidence=.99,refineIters=10)
    if transform is None or not np.isfinite(transform).all():return None
    keep=mask.ravel().astype(bool)
    if keep.sum()<4:return None
    coverage=min(cv2.contourArea(cv2.convexHull(v[keep])) for v in (p,q))/(SIDE*SIDE)
    scale=float(np.hypot(transform[0,0],transform[1,0]))
    angle=float(np.rad2deg(np.arctan2(transform[1,0],transform[0,0])))
    if coverage<.02 or not .5<=scale<=2 or abs(angle)>40:return None
    return np.vstack([transform,[0.,0.,1.]])
