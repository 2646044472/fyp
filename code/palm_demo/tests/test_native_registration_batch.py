"""Batching exact OpenCV rechecks must preserve the original rowwise pairs."""

import ctypes

import cv2
import numpy as np
import pytest

from native_registration import NativeRegistration


def descriptors(count, seed):
    values=np.random.default_rng(seed).random((count,128),dtype=np.float32)
    return np.ascontiguousarray(values/np.linalg.norm(values,axis=1,keepdims=True))


def kernel_outputs(a,b):
    # A small deterministic stand-in for the native nearest-neighbor kernel.
    # No compiled library or camera is needed to exercise the Python adapter.
    distances=np.sum((a[:,None]-b[None,:])**2,axis=2)
    fi=np.argsort(distances,axis=1,kind='stable')[:,:2].astype(np.int32)
    ri=np.argsort(distances.T,axis=1,kind='stable')[:,:2].astype(np.int32)
    fd=np.take_along_axis(distances,fi,axis=1).astype(np.float32)
    rd=np.take_along_axis(distances.T,ri,axis=1).astype(np.float32)
    return fi,fd,ri,rd


def rowwise_oracle(a,b,outputs):
    # Original pre-batch Python implementation, deliberately kept rowwise.
    fi,fd,ri,rd=(value.copy() for value in outputs)
    tolerance=1e-4
    accepted=fd[:,0]<(.85**2)*fd[:,1]
    uncertain=(np.abs(fd[:,0]-(.85**2)*fd[:,1])<=tolerance) | (fd[:,1]-fd[:,0]<=tolerance)
    for i in np.flatnonzero(uncertain):
        m,n=cv2.BFMatcher().knnMatch(a[i:i+1],b,k=2)[0]
        fi[i,0]=m.trainIdx;accepted[i]=m.distance<.85*n.distance
    pairs=[]
    for i in np.flatnonzero(accepted):
        j=fi[i,0];nearest=ri[j,0]
        if rd[j,1]-rd[j,0]<=tolerance:
            nearest=cv2.BFMatcher().knnMatch(b[j:j+1],a,k=1)[0][0].trainIdx
        if nearest==i:pairs.append((int(i),int(j)))
    return pairs


def fake_registration(outputs, *, status=0):
    adapter=NativeRegistration.__new__(NativeRegistration)
    adapter.threads=1
    calls=[]

    def kernel(a_ptr,a_count,b_ptr,b_count,threads,*output_pointers):
        calls.append((a_count,b_count,threads))
        for value,address in zip(outputs,output_pointers):
            ctype=ctypes.c_int32 if value.dtype==np.int32 else ctypes.c_float
            target=np.ctypeslib.as_array((ctype*value.size).from_address(address))
            target[:]=value.ravel()
        return status

    adapter.function=kernel
    return adapter,calls


def track_bf_calls(monkeypatch):
    factory=cv2.BFMatcher
    calls=[]

    class TrackedMatcher:
        def __init__(self):self.matcher=factory()

        def knnMatch(self,query,train,k):
            calls.append((len(query),len(train),k))
            return self.matcher.knnMatch(query,train,k=k)

    monkeypatch.setattr(cv2,'BFMatcher',TrackedMatcher)
    return calls


@pytest.mark.parametrize('case', ['random','matched','duplicates','forward-ratio','forward-tie','reverse-tie','both'])
def test_batch_pairs_equal_original_rowwise_rechecks(monkeypatch,case):
    a=descriptors(9,17)
    b=descriptors(12,31)
    if case!='random':b[:len(a)]=a
    if case=='duplicates':
        a[:]=a[0]
        b[:]=a[0]
    outputs=kernel_outputs(a,b)
    fi,fd,ri,rd=outputs
    if case in ('forward-ratio','both'):
        # Native arithmetic near the squared ratio cutoff must defer to exact
        # OpenCV distances, regardless of which side of the cutoff it reports.
        fd[:,0]=(.85**2)*fd[:,1]+np.linspace(-5e-5,5e-5,len(a),dtype=np.float32)
    elif case=='forward-tie':
        fd[:,1]=fd[:,0]+np.float32(5e-5)
    if case in ('reverse-tie','both'):
        rd[:,1]=rd[:,0]+np.float32(5e-5)
    expected=rowwise_oracle(a,b,outputs)
    bf_calls=track_bf_calls(monkeypatch)
    adapter,kernel_calls=fake_registration(outputs)

    actual=adapter.pairs(a,b)

    assert actual==expected
    assert kernel_calls==[(len(a),len(b),1)]
    assert all(type(i) is int and type(j) is int for i,j in actual)
    assert [i for i,j in actual]==sorted(i for i,j in actual)
    assert sum(k==2 for _,_,k in bf_calls)<=1
    assert sum(k==1 for _,_,k in bf_calls)<=1
    if case=='duplicates':
        assert actual==[]
        assert bf_calls==[(len(a),len(b),2)]
    if case=='matched':
        assert actual==[(i,i) for i in range(len(a))]
        assert bf_calls==[]
    if case=='both':
        assert bf_calls==[(len(a),len(b),2),(len(a),len(a),1)]


def test_reverse_rechecks_deduplicate_many_queries_for_one_target(monkeypatch):
    a=np.repeat(descriptors(1,41),8,axis=0)
    b=descriptors(5,43)
    b[0]=a[0]
    outputs=kernel_outputs(a,b)
    expected=rowwise_oracle(a,b,outputs)
    bf_calls=track_bf_calls(monkeypatch)
    adapter,_=fake_registration(outputs)

    assert adapter.pairs(a,b)==expected==[(0,0)]
    assert bf_calls==[(1,len(a),1)]


def test_no_accepted_queries_need_no_reverse_recheck(monkeypatch):
    a=descriptors(5,47)
    b=descriptors(6,53)
    outputs=kernel_outputs(a,b)
    outputs[1][:]=np.asarray([.9,1.],np.float32)
    bf_calls=track_bf_calls(monkeypatch)
    adapter,_=fake_registration(outputs)

    assert adapter.pairs(a,b)==[]
    assert bf_calls==[]


@pytest.mark.parametrize('damage',['dtype','empty','too-few','nan','negative','norm','width'])
def test_invalid_descriptors_still_fail_before_native_call(damage):
    a=descriptors(5,59)
    b=descriptors(6,61)
    adapter,calls=fake_registration(kernel_outputs(a,b))
    if damage=='dtype':a=a.astype(np.float64)
    elif damage=='empty':a=a[:0]
    elif damage=='too-few':a=a[:3]
    elif damage=='nan':a[0,0]=np.nan
    elif damage=='negative':a[0,0]=-1
    elif damage=='norm':a[0]*=2
    elif damage=='width':a=a[:,:127]

    with pytest.raises(ValueError):adapter.pairs(a,b)
    assert calls==[]


def test_native_failure_still_raises_without_bf_rechecks(monkeypatch):
    a=descriptors(5,67)
    b=descriptors(6,71)
    adapter,_=fake_registration(kernel_outputs(a,b),status=3)
    bf_calls=track_bf_calls(monkeypatch)

    with pytest.raises(RuntimeError,match='Native descriptor kernel failed: 3'):
        adapter.pairs(a,b)
    assert bf_calls==[]


def test_too_few_points_in_registration_still_return_none():
    adapter,_=fake_registration(())
    points=np.zeros((3,2),np.float32)
    feature=(points,np.zeros((3,128),np.float32))
    assert adapter(feature,feature) is None
