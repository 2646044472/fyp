"""Independent UAA-inspired random similarity, not official UAA."""
import cv2 as cv
import numpy as np
def augment_rgb(image_uint8, mode, rng_numpy_generator):
    if mode == 'none':return image_uint8
    if mode != 'geometry':raise ValueError('Only none/geometry implemented; not texture or loss-adversarial.')
    assert image_uint8.shape==(112,112,3) and image_uint8.dtype==np.uint8
    z=rng_numpy_generator.uniform(-1,1,4)
    ang,sc=.25*z[0],1+.2*z[1];c,b=sc*np.cos(ang),sc*np.sin(ang)
    A=np.array([[c,-b],[b,c]])
    # inverse-map convention matches torch affine_grid(align_corners=False)
    center=np.array([55.5,55.5])
    T=np.column_stack([A, center-A@center+22.4*z[2:]])
    return cv.warpAffine(image_uint8,T,(112,112),flags=cv.INTER_LINEAR|cv.WARP_INVERSE_MAP,borderMode=cv.BORDER_REPLICATE)
