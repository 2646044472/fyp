import cv2
import numpy as np
from registered_matcher import registration as reference_registration
from registration_accelerated import mutual_pairs, registration
from proposed_index_matcher import proposed_pairs, proposed_registration


def reference_pairs(a,b):
    forward=cv2.BFMatcher().knnMatch(a,b,k=2)
    reverse=cv2.BFMatcher().knnMatch(b,a,k=1)
    return [(m.queryIdx,m.trainIdx) for m,n in forward
            if m.distance<.85*n.distance and reverse[m.trainIdx][0].trainIdx==m.queryIdx]


def test_shared_distances_retain_mutual_ratio_decisions_and_transform():
    rng=np.random.default_rng(64)
    for n in (4,32,200):
        a=rng.random((n,128),dtype=np.float32)
        a=np.sqrt(a/a.sum(axis=1,keepdims=True))
        for noise in (0.,.001,.02,.1):
            b=np.maximum(a+rng.normal(0,noise,a.shape).astype(np.float32),0)
            b/=np.maximum(np.linalg.norm(b,axis=1,keepdims=True),1e-10)
            # Exact and near duplicates exercise BF tie/ratio recomputation.
            b[1]=b[0];b[2]=np.nextafter(b[0],np.float32(1))
            assert mutual_pairs(a,b)==reference_pairs(a,b)
            indices=list(range(0,n,2)) if n>4 else list(range(n))
            assert proposed_pairs(a,b,indices)==[(i,j) for i,j in reference_pairs(a,b) if i in indices]
            points=rng.uniform(0,384,(n,2)).astype(np.float32)
            shifted=points+np.array([10,5],np.float32)
            expected=reference_registration((points,a),(shifted,b))
            actual=registration((points,a),(shifted,b))
            if expected is None:assert actual is None
            else:np.testing.assert_array_equal(actual,expected)
            proposed=proposed_registration((points,a),(shifted,b),range(n))
            if expected is None:assert proposed is None
            else:np.testing.assert_array_equal(proposed,expected)
    a=np.zeros((10,128),np.float32)
    assert mutual_pairs(a,a)==reference_pairs(a,a)==[]
