import numpy as np
import pytest

from roi_sampling import sample_palm_quad


def test_half_pixel_ramp_retains_fraction_and_target_extent():
    ramp=np.tile(np.arange(20,dtype=np.uint8),(20,1));rgb=np.repeat(ramp[:,:,None],3,axis=2)
    q=np.array([[2.5,2],[10.5,2],[10.5,10],[2.5,10]])
    actual=sample_palm_quad(rgb,q,side=8)
    np.testing.assert_array_equal(actual,np.tile(np.arange(2.5,10.5),(8,1)))
    assert actual.dtype==np.float32


def test_reverse_winding_uses_same_canonical_pixels():
    rgb=np.random.default_rng(8).integers(0,255,(32,32,3),dtype=np.uint8)
    q=np.array([[2,2],[20,2],[20,20],[2,20]],float)
    np.testing.assert_array_equal(sample_palm_quad(rgb,q),sample_palm_quad(rgb,q[[1,0,3,2]]))


def test_outside_taps_are_zero_not_edge_replication():
    rgb=np.full((4,4,3),100,dtype=np.uint8)
    q=np.array([[-.5,0],[3.5,0],[3.5,4],[-.5,4]])
    result=sample_palm_quad(rgb,q,side=4)
    assert result[0,0]==50 and result[0,1]==100


def test_nonfinite_geometry_is_not_sampled():
    with pytest.raises(ValueError):sample_palm_quad(np.zeros((10,10,3)),np.full((4,2),np.nan))
