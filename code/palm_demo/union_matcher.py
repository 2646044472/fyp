"""Runtime counterpart of window-coarse-union; no sample/identity inputs.

Fixed numeric envelope supports existing stacked NPZ templates. Payload contains
v2 fallback, lossless native gray PNG, two coarse gallery views and query views.
Padding is zero and compresses; exceeding capacity fails, never drops candidates.
"""
import cv2
import numpy as np
from pklnet_roi import PKLNetROI, normalize_roi
from registered_matcher import DUAL_SIZE, MAX_POINTS, FastCCDualRegisteredMatcher, local_features, registration
from window_roi import window_candidates

NAME='FastCCWindowUnion-v4'
MAGIC=2801029
FEATURE_SIZE=16*1024*1024
HEADER=20
MAX_VIEWS=42


class FastCCWindowUnionMatcher:
    name=NAME

    def __init__(self,base):
        self.base=base;self.legacy=FastCCDualRegisteredMatcher(base);self.geometry=self.legacy.geometry
        self._window_engine=None

    def complete_hypotheses(self,full,candidates,localizer):
        if self._window_engine is None:
            self._window_engine=PKLNetROI(root=localizer.root,weights=localizer.weights,
                                        backend=localizer.backend,threads=localizer.threads,policy='heatmap')
        return list(candidates)+window_candidates(full,self._window_engine)

    @staticmethod
    def _encode_view(sigma,source,points,desc,lower=0,upper=384):
        return np.concatenate([np.asarray([sigma,len(points),lower,upper],'<i4').view(np.uint8),
                               np.asarray(source,'<f8').ravel().view(np.uint8),
                               np.asarray(points,'<f4').ravel().view(np.uint8),
                               np.asarray(desc,'<f4').ravel().view(np.uint8)])

    def _pack(self,legacy,png,queries,gallery):
        chunks=[legacy,png,*gallery,*queries];used=HEADER+sum(c.size for c in chunks)
        if used>FEATURE_SIZE:raise ValueError('Union template capacity exceeded; no views were dropped')
        f=np.zeros(FEATURE_SIZE,np.uint8)
        f[:HEADER]=np.asarray([MAGIC,used,len(png),len(queries),len(gallery)],'<i4').view(np.uint8)
        start=HEADER
        for c in chunks:f[start:start+c.size]=c;start+=c.size
        return f

    def extract(self,roi):
        return self._pack(self.legacy.extract(roi),np.empty(0,np.uint8),[],[])

    def extract_with_hypotheses(self,full,quad,normalized_roi,hypotheses):
        legacy=self.legacy.extract_with_context(full,quad,normalized_roi)
        primary,_=self.legacy._views(legacy)
        gray=cv2.cvtColor(np.asarray(full.convert('RGB')),cv2.COLOR_RGB2GRAY)
        ok,png=cv2.imencode('.png',gray,[cv2.IMWRITE_PNG_COMPRESSION,1])
        if not ok:raise ValueError('Native grayscale encoding failed')
        gallery=[];queries=[]
        pixels=normalize_roi(primary[1][192:576,192:576])[0]
        for sigma in [4,8]:
            p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma))
            gallery.append(self._encode_view(sigma,np.eye(3),p,d))
        # Exactly the expanded_strict baseline: descriptors from stored v2
        # context, native appearance. base_full is a separate unused control.
        pixels=normalize_roi(primary[1])[0]
        for sigma in [0,2]:
            p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
            queries.append(self._encode_view(sigma,primary[2],p-192,d,-192,576))
        if len(hypotheses)>8:raise ValueError('Expected at most two base and six window hypotheses')
        for h in hypotheses:
            if not h.get('valid',False):continue
            q=np.asarray(h['quad'],np.float32)
            if (q.shape!=(4,2) or not np.isfinite(q).all() or (q<0).any()
                    or (q[:,0]>=full.width).any() or (q[:,1]>=full.height).any()
                    or cv2.contourArea(q)<1):raise ValueError('Invalid candidate geometry')
            dst=np.asarray([[384,0],[0,0],[0,384],[384,384]] if self.geometry.isAntiClock(q[:3].reshape(-1))
                           else [[0,0],[384,0],[384,384],[0,384]],np.float32)
            source=cv2.getPerspectiveTransform(q,dst)
            for size in [384,768]:
                offset=(size-384)/2;shift=np.asarray([[1.,0,offset],[0,1.,offset],[0,0,1.]])
                pixels=normalize_roi(cv2.warpPerspective(gray,shift@source,(size,size)))[0]
                for sigma in ([0,2] if h.get('kind')=='window' else [0,2,4,8]):
                    p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
                    queries.append(self._encode_view(sigma,source,p-offset,d,int(-offset),int(size-offset)))
        if len(queries)>MAX_VIEWS:raise ValueError('Too many union views')
        return self._pack(legacy,png.ravel(),queries,gallery)

    def _unpack(self,feature):
        f=np.asarray(feature)
        if f.dtype!=np.uint8 or f.shape!=(FEATURE_SIZE,):raise ValueError('Incompatible union template shape or dtype')
        magic,used,encoded,nq,ng=map(int,f[:HEADER].view('<i4'))
        if (magic!=MAGIC or not HEADER+DUAL_SIZE<=used<=FEATURE_SIZE or not 0<=encoded<=used-HEADER-DUAL_SIZE
                or not 0<=nq<=MAX_VIEWS or ng not in (0,2) or bool(nq)!=bool(ng)):
            raise ValueError('Invalid union header')
        legacy=f[HEADER:HEADER+DUAL_SIZE];primary,secondary=self.legacy._views(legacy)
        pos=HEADER+DUAL_SIZE;native=None
        if encoded:
            data=f[pos:pos+encoded]
            # Validate PNG dimensions before invoking the decoder.
            if (encoded<24 or bytes(data[:8])!=b'\x89PNG\r\n\x1a\n'
                    or (int.from_bytes(data[16:20].tobytes(),'big'),int.from_bytes(data[20:24].tobytes(),'big'))!=primary[3]):
                raise ValueError('Native PNG dimensions mismatch')
            native=cv2.imdecode(data,cv2.IMREAD_GRAYSCALE)
            if native is None or native.shape!=primary[3][::-1]:raise ValueError('Invalid native PNG')
        if nq and native is None:raise ValueError('Missing native pixels')
        pos+=encoded;views=[]
        for index in range(ng+nq):
            if pos+88>used:raise ValueError('Truncated union view')
            sigma,n,lower,upper=map(int,f[pos:pos+16].view('<i4'))
            if (sigma not in (0,2,4,8) or not 0<=n<=MAX_POINTS or (lower,upper) not in ((0,384),(-192,576))
                    or pos+88+n*520>used):raise ValueError('Invalid union view header')
            source=f[pos+16:pos+88].view('<f8').reshape(3,3);pos+=88
            p=f[pos:pos+n*8].view('<f4').reshape(n,2);pos+=n*8
            d=f[pos:pos+n*512].view('<f4').reshape(n,128);pos+=n*512
            if (not np.isfinite(source).all() or abs(np.linalg.det(source))<1e-12 or not np.isfinite(p).all()
                    or (p<lower).any() or (p>=upper).any() or not np.isfinite(d).all() or (d<0).any()):
                raise ValueError('Invalid union descriptor data')
            views.append((sigma,source,p,d))
        if pos!=used or (ng and [v[0] for v in views[:ng]]!=[4,8]):raise ValueError('Invalid union payload layout')
        return legacy,primary,secondary,native,views[:ng],views[ng:]

    def match(self,probe,candidate):
        left,a,_,native,_,queries=self._unpack(probe)
        right,b,bs,_,coarse,_=self._unpack(candidate)
        score=self.legacy.match(left,right)
        gallery={0:(b[4],b[5]),2:bs,**{s:(p,d) for s,_,p,d in coarse}}
        corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])
        for sigma,source,p,d in queries:
            if sigma not in gallery:continue
            transform=registration((p,d),gallery[sigma])
            if transform is None:continue
            warp=np.diag([1/3,1/3,1])@transform@source
            mapped=corners@np.linalg.inv(warp).T;mapped=mapped[:,:2]/mapped[:,2:]
            if (not np.isfinite(mapped).all() or (mapped<1).any() or (mapped[:,0]>=native.shape[1]-1).any()
                    or (mapped[:,1]>=native.shape[0]-1).any()):continue
            pixels=normalize_roi(cv2.warpPerspective(native,warp,(128,128)))[0]
            score=min(score,float(self.base.match(self.base.extract(pixels),b[0][0].astype(bool))))
        return score

    def score_enrollment(self,probe,enrolled):
        if not len(enrolled):raise ValueError('At least one enrollment feature is required')
        return float(np.mean(sorted(self.match(probe,f) for f in enrolled)[:2]))
