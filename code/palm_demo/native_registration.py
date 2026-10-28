"""Explicitly loaded experimental ARM64 matcher; no automatic compilation/load."""
import ctypes
from pathlib import Path
import cv2
import numpy as np
from registration_accelerated import estimate_pairs
from registered_matcher import registration as reference_registration


def enable_native_registration(algorithm,library,threads=4):
    """Opt in for one matcher instance; leave all other instances untouched."""
    if not hasattr(algorithm,'registration') or not hasattr(getattr(algorithm,'legacy',None),'registration'):
        raise ValueError('This matcher does not support native registration')
    native=NativeRegistration(library,threads)
    algorithm.registration=native
    algorithm.legacy.registration=native
    return native


class NativeRegistration:
    def __init__(self,library,threads=2):
        if threads not in (1,2,4):raise ValueError('Expected 1, 2 or 4 native threads')
        self.library=ctypes.CDLL(str(Path(library).resolve()))
        self.function=self.library.descriptor_neighbours
        self.function.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,
                                ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]
        self.function.restype=ctypes.c_int
        self.threads=threads

    def pairs(self,a,b):
        if np.asarray(a).dtype!=np.float32 or np.asarray(b).dtype!=np.float32:
            raise ValueError('Native kernel requires float32 descriptors')
        a=np.ascontiguousarray(a,dtype=np.float32);b=np.ascontiguousarray(b,dtype=np.float32)
        if (a.ndim!=2 or b.ndim!=2 or a.shape[1]!=128 or b.shape[1]!=128
            or not 4<=len(a)<=4096 or not 4<=len(b)<=4096
            or not np.isfinite(a).all() or not np.isfinite(b).all()
            or (a<0).any() or (b<0).any()
            or max(np.max(np.sum(a*a,axis=1)),np.max(np.sum(b*b,axis=1)))>1.001):
            raise ValueError('Native kernel requires bounded RootSIFT descriptors')
        fi=np.empty((len(a),2),np.int32);fd=np.empty((len(a),2),np.float32)
        ri=np.empty((len(b),2),np.int32);rd=np.empty((len(b),2),np.float32)
        status=self.function(a.ctypes.data,len(a),b.ctypes.data,len(b),self.threads,
                            fi.ctypes.data,fd.ctypes.data,ri.ctypes.data,rd.ctypes.data)
        if status:raise RuntimeError(f'Native descriptor kernel failed: {status}')
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

    def __call__(self,left,right):
        pa,da=left;pb,db=right
        if min(len(da),len(db))<4:return None
        try:pairs=self.pairs(da,db)
        except ValueError:return reference_registration(left,right)
        return estimate_pairs(pa,pb,pairs)
