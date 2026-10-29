import numpy as np
from pooled_enrollment_matcher import pool_correspondences,PooledEnrollmentMatcher


def sample(points):
    primary=(None,None,None,None,np.asarray(points,np.float32),None)
    secondary=(np.asarray(points,np.float32),None)
    return None,None,(primary,secondary)


def test_pool_transfers_geometry_and_counts_each_query_point_once():
    a=sample([[30,40],[100,150]])
    b=sample([[40,60],[110,170],[220,240]])
    query=(np.asarray([[1,2],[3,4],[5,6]],np.float32),None)
    correspondences={id(a):[[(0,0),(1,1)],[]],id(b):[[(0,0),(1,1),(2,2)],[]]}
    transform=np.asarray([[1.,0,10],[0,1.,20],[0,0,1.]])
    p,q=pool_correspondences([a,b],1,0,query,correspondences,{0:[(1,transform)],1:[]})
    np.testing.assert_array_equal(p,query[0])
    np.testing.assert_array_equal(q,[[40,60],[110,170],[220,240]])
    assert len(p)==3  # Five observations must not fake five independent inliers.


def test_pool_drops_outside_target_and_unlinked_observations():
    a=sample([[30,40]])
    b=sample([[500,60]])
    c=sample([[40,60]])
    observations={id(a):[[(0,0)],[]],id(b):[[(0,0)],[]],id(c):[[(1,0)],[]]}
    query=(np.asarray([[1,2],[3,4]],np.float32),None)
    p,q=pool_correspondences([a,b,c],1,0,query,observations,{0:[],1:[],2:[]})
    assert p.shape==(0,2) and q.shape==(0,2)


def test_pool_retains_original_routing_gate_and_full_search():
    assert PooledEnrollmentMatcher.requires_exhaustive_fallback
    assert not PooledEnrollmentMatcher.confident({'a':.33,'b':.5})
    assert not PooledEnrollmentMatcher.confident({'a':.30,'b':.37})
    assert PooledEnrollmentMatcher.confident({'a':.30,'b':.40})


def test_batched_transfer_is_bit_exact_with_scalar_reference():
    rng=np.random.default_rng(20)
    points=[rng.uniform(-20,410,(30,2)).astype(np.float32) for _ in range(5)]
    samples=[sample(p) for p in points]
    query=(rng.uniform(0,384,(30,2)).astype(np.float32),None)
    observations={id(s):[[(i,i) for i in range(30) if (i+j)%3],[]] for j,s in enumerate(samples)}
    links={i:[(j,np.asarray([[1.,.03,j-i],[-.02,1.,i-j],[0,0,1.]]))
              for j in range(5) if i!=j] for i in range(5)}
    for target in range(5):
        found={}
        for i,s in enumerate(samples):
            transforms=[np.eye(3)] if i==target else [t for j,t in links[i] if j==target]
            for transform in transforms:
                for qi,ti in observations[id(s)][0]:
                    point=transform@np.r_[points[i][ti],1.]
                    point=point[:2]/point[2]
                    if np.isfinite(point).all() and (point>=0).all() and (point<384).all():
                        found.setdefault(qi,[]).append(point)
        ids=sorted(found)
        expected=np.asarray([np.median(found[i],axis=0) for i in ids],np.float32)
        p,q=pool_correspondences(samples,target,0,query,observations,links)
        np.testing.assert_array_equal(p,query[0][ids])
        np.testing.assert_array_equal(q,expected)

