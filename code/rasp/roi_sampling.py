"""Float palm-square sampling without platform-specific uint8 warp rounding."""
from __future__ import annotations

import numpy as np


def sample_palm_quad(rgb: np.ndarray, quad: np.ndarray, side: int = 128) -> np.ndarray:
    """Sample a PKLNet square/parallelogram, retaining sub-byte gray precision.

    Match PalmKit's corner order and target coordinates [0, side]. Interpolate
    the four corners directly rather than invert a nearly affine homography.
    Out-of-image taps contribute zero, matching the historical warp border.
    """
    rgb = np.asarray(rgb)
    q = np.asarray(quad, dtype=np.float64)
    if rgb.ndim != 3 or rgb.shape[2] != 3 or q.shape != (4, 2) or side <= 0 or not np.isfinite(q).all():
        raise ValueError('Expected RGB image, finite 4x2 quad, and positive side')
    a, b = q[1]-q[0], q[2]-q[0]
    if a[0]*b[1]-a[1]*b[0] < 0:
        q = q[[1, 0, 3, 2]]
    u, v = np.meshgrid(np.arange(side, dtype=np.float64)/side, np.arange(side, dtype=np.float64)/side)
    xy = ((1-u)*(1-v))[...,None]*q[0] + (u*(1-v))[...,None]*q[1] + (u*v)[...,None]*q[2] + ((1-u)*v)[...,None]*q[3]
    x, y = xy[...,0], xy[...,1]
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x-ix, y-iy
    gray = np.zeros((side, side), dtype=np.float64)
    height, width = rgb.shape[:2]
    # Fixed coefficients; no intermediate color or interpolation quantization.
    for dx, dy, weight in [(0,0,(1-fx)*(1-fy)), (1,0,fx*(1-fy)), (0,1,(1-fx)*fy), (1,1,fx*fy)]:
        xx, yy = ix+dx, iy+dy
        valid = (xx>=0)&(xx<width)&(yy>=0)&(yy<height)
        color = rgb[np.clip(yy,0,height-1),np.clip(xx,0,width-1)].astype(np.float64)
        luminance = (4899*color[...,0]+9617*color[...,1]+1868*color[...,2])/16384
        gray += weight*luminance*valid
    return gray.astype(np.float32)
