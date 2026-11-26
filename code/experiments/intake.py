"""Portable helpers adapted from the MPD matched training intake, not a dataset."""
from hashlib import sha256
import cv2 as cv
import numpy as np


def select_two(names):
    """In ONE person/session/device/hand group, choose up to two filenames."""
    return sorted(names, key=lambda s: sha256(('arc18v1:' + s).encode()).digest())[:2]


def crop_marks(rgb, marks, slots):
    """MPD .mat uses 1-based slots and half-pixel coordinates. Input is raw-frame RGB."""
    h, w = rgb.shape[:2]
    marks = np.asarray(marks, dtype=float)
    idx = np.ravel(slots)
    if len(idx) != 4 or not np.all(np.isfinite(idx)) or np.any(idx != idx.astype(int)) or np.any(idx < 1) or np.any(idx > len(marks)):
        raise ValueError('Expected four valid 1-based slots')
    v = marks[idx.astype(int)-1,:2] - .5
    a, b = (v[0]+v[1])/2, (v[2]+v[3])/2
    e = b-a
    t = np.array([-e[1], e[0]])
    u = (a+b)/2 + .5*t - 1.25*e
    q = np.float32([u,u+2.5*e,u+2.5*t])
    corners = np.vstack([q,q[1]+q[2]-q[0]])
    if not np.isfinite(corners).all() or np.linalg.norm(e)<=2 or np.any(corners<0) or np.any(corners>=[w,h]):
        raise ValueError('Unusable mark-defined crop; retain failure in intake')
    transform = cv.getAffineTransform(q, np.float32([[0,0],[111,0],[0,111]]))
    return cv.warpAffine(rgb, transform, (112,112))
