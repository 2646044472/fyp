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
        matcher=None
        uncertain_rows=np.flatnonzero(uncertain)
        if len(uncertain_rows):
            # Exact OpenCV distances still decide all borderline cases. Batch
            # independent query rows instead of rebuilding a matcher per row.
            matcher=cv2.BFMatcher()
            matches=matcher.knnMatch(a[uncertain_rows],b,k=2)
            for row,i in enumerate(uncertain_rows):
                m,n=matches[row]
                fi[i,0]=m.trainIdx;accepted[i]=m.distance<.85*n.distance
        accepted_rows=np.flatnonzero(accepted)
        targets=fi[accepted_rows,0]
        reverse_rows=np.unique(targets[rd[targets,1]-rd[targets,0]<=tolerance])
        exact_reverse={}
        if len(reverse_rows):
            if matcher is None:matcher=cv2.BFMatcher()
            matches=matcher.knnMatch(b[reverse_rows],a,k=1)
            for row,j in enumerate(reverse_rows):
                exact_reverse[int(j)]=matches[row][0].trainIdx
        pairs=[]
        for i,j in zip(accepted_rows,targets):
            nearest=exact_reverse.get(int(j),ri[j,0])
            if nearest==i:pairs.append((int(i),int(j)))
        return pairs

    def __call__(self,left,right):
        pa,da=left;pb,db=right
        if min(len(da),len(db))<4:return None
        try:pairs=self.pairs(da,db)
        except ValueError:return reference_registration(left,right)
        return estimate_pairs(pa,pb,pairs)
