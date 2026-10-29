"""Runtime counterpart of window-coarse-union; no sample/identity inputs.

Fixed numeric envelope supports existing stacked NPZ templates. Payload contains
v2 fallback, lossless native gray PNG, two coarse gallery views and query views.
Padding is zero and compresses; exceeding capacity fails, never drops candidates.
"""
import cv2
import numpy as np
from pklnet_roi import PKLNetROI, normalize_roi_pixels
from registered_matcher import DUAL_SIZE, MAX_POINTS, FastCCDualRegisteredMatcher, local_features, registration
from window_roi import window_candidates

NAME='FastCCWindowUnion-v4'
MAGIC=2801029
FEATURE_SIZE=16*1024*1024
HEADER=20
MAX_VIEWS=42


class FastCCWindowUnionMatcher:
    name=NAME
    magic=MAGIC
    allow_gallery_only=False
    registration=staticmethod(registration)
    local_features=staticmethod(local_features)

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
        f[:HEADER]=np.asarray([self.magic,used,len(png),len(queries),len(gallery)],'<i4').view(np.uint8)
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
        pixels=normalize_roi_pixels(primary[1][192:576,192:576])
        for sigma in [4,8]:
            p,d=self.local_features(cv2.GaussianBlur(pixels,(0,0),sigma))
            gallery.append(self._encode_view(sigma,np.eye(3),p,d))
        # Exactly the expanded_strict baseline: descriptors from stored v2
        # context, native appearance. base_full is a separate unused control.
        pixels=normalize_roi_pixels(primary[1])
        for sigma in [0,2]:
            p,d=self.local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
            queries.append(self._encode_view(sigma,primary[2],p-192,d,-192,576))
        if len(hypotheses)>8:raise ValueError('Expected at most two base and six window hypotheses')
        queries.extend(self._all_hypothesis_views(gray,full.size,hypotheses))
        if len(queries)>MAX_VIEWS:raise ValueError('Too many union views')
        return self._pack(legacy,png.ravel(),queries,gallery)

    def _all_hypothesis_views(self,gray,image_size,hypotheses):
        return [view for h in hypotheses for view in self._hypothesis_views(gray,image_size,h)]

    def _hypothesis_views(self,gray,image_size,h):
        if not h.get('valid',False):return []
        q=np.asarray(h['quad'],np.float32)
        if (q.shape!=(4,2) or not np.isfinite(q).all() or (q<0).any()
                or (q[:,0]>=image_size[0]).any() or (q[:,1]>=image_size[1]).any()
                or cv2.contourArea(q)<1):raise ValueError('Invalid candidate geometry')
        dst=np.asarray([[384,0],[0,0],[0,384],[384,384]] if self.geometry.isAntiClock(q[:3].reshape(-1))
                       else [[0,0],[384,0],[384,384],[0,384]],np.float32)
        source=cv2.getPerspectiveTransform(q,dst);views=[]
        for size in [384,768]:
            offset=(size-384)/2;shift=np.asarray([[1.,0,offset],[0,1.,offset],[0,0,1.]])
            pixels=normalize_roi_pixels(cv2.warpPerspective(gray,shift@source,(size,size)))
            for sigma in ([0,2] if h.get('kind')=='window' else [0,2,4,8]):
                p,d=self.local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
                views.append(self._encode_view(sigma,source,p-offset,d,int(-offset),int(size-offset)))
        return views

    def _unpack(self,feature,*,decode_native=True):
        f=np.asarray(feature)
        if f.dtype!=np.uint8 or f.shape!=(FEATURE_SIZE,):raise ValueError('Incompatible union template shape or dtype')
        magic,used,encoded,nq,ng=map(int,f[:HEADER].view('<i4'))
        if (magic!=self.magic or not HEADER+DUAL_SIZE<=used<=FEATURE_SIZE or not 0<=encoded<=used-HEADER-DUAL_SIZE
                or not 0<=nq<=MAX_VIEWS or ng not in (0,2)
                or (bool(nq)!=bool(ng) and not (self.allow_gallery_only and nq==0 and ng==2))):
            raise ValueError('Invalid union header')
        legacy=f[HEADER:HEADER+DUAL_SIZE];primary,secondary=self.legacy._views(legacy)
        pos=HEADER+DUAL_SIZE;native=None
        if encoded:
            data=f[pos:pos+encoded]
            # Validate PNG dimensions before invoking the decoder.
            if (encoded<24 or bytes(data[:8])!=b'\x89PNG\r\n\x1a\n'
                    or (int.from_bytes(data[16:20].tobytes(),'big'),int.from_bytes(data[20:24].tobytes(),'big'))!=primary[3]):
                raise ValueError('Native PNG dimensions mismatch')
            if decode_native:
                native=cv2.imdecode(data,cv2.IMREAD_GRAYSCALE)
                if native is None or native.shape!=primary[3][::-1]:raise ValueError('Invalid native PNG')
        if nq and not encoded:raise ValueError('Missing native pixels')
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
        return self._match_unpacked(self._unpack(probe),self._unpack(candidate,decode_native=False))

    def match_with_diagnostics(self,probe,candidate):
        details=[]
        score=self._match_unpacked(self.prepare_probe(probe),self._unpack(candidate,decode_native=False),details)
        winner=min((r for r in details if 'score' in r),key=lambda r:r['score'])
        return dict(score=score,winner=winner,attempts=details)

    def _accept_alignment(self,primary,mapped):
        return True

    def _match_unpacked(self,query,target,details=None):
        left,a,_,native,_,queries=query
        right,b,bs,_,coarse,_=target
        # Both parts were already validated while unpacking; do not parse the
        # 1.6MB legacy envelope again for every candidate.
        score=self.legacy._match_parts(a,b,[(query[2],bs)])
        if details is not None:details.append(dict(branch='legacy_v2',score=score,aligned_quad=None))
        gallery={0:(b[4],b[5]),2:bs,**{s:(p,d) for s,_,p,d in coarse}}
        corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])
        for index,(sigma,source,p,d) in enumerate(queries):
            entry=dict(branch='union',view_index=index,sigma=sigma,source_matrix=source.tolist())
            if sigma not in gallery:continue
            transform=self.registration((p,d),gallery[sigma])
            if transform is None:
                if details is not None:details.append(dict(entry,rejected='correspondence_or_geometry'))
                continue
            warp=np.diag([1/3,1/3,1])@transform@source
            mapped=corners@np.linalg.inv(warp).T;mapped=mapped[:,:2]/mapped[:,2:]
            if (not np.isfinite(mapped).all() or (mapped<1).any() or (mapped[:,0]>=native.shape[1]-1).any()
                    or (mapped[:,1]>=native.shape[0]-1).any()):
                if details is not None:details.append(dict(entry,rejected='sampling_bounds'))
                continue
            if not self._accept_alignment(a,mapped):
                if details is not None:details.append(dict(entry,rejected='disjoint_aligned_region',aligned_quad=mapped.tolist()))
                continue
            pixels=normalize_roi_pixels(cv2.warpPerspective(native,warp,(128,128)))
            distance=float(self.base.match(self.base.extract(pixels),b[0][0].astype(bool)))
            score=min(score,distance)
            if details is not None:details.append(dict(entry,score=distance,aligned_quad=mapped.tolist()))
        return score

    def score_enrollment(self,probe,enrolled):
        if not len(enrolled):raise ValueError('At least one enrollment feature is required')
        query=self._unpack(probe)
        return float(np.mean(sorted(self._match_unpacked(query,self._unpack(f,decode_native=False)) for f in enrolled)[:2]))

    def prepare_probe(self,probe):
        return self._unpack(probe)

    def prepare_enrollment(self,enrolled):
        prepared=[]
        for f in enrolled:
            _,b,bs,_,coarse,_=self._unpack(f,decode_native=False)
            # Gallery matching needs neither native PNG nor query hypotheses.
            # Copies release the large original packed arrays after loading.
            compact=(b[0].copy(),None,None,b[3],b[4].copy(),b[5].copy())
            prepared.append((None,compact,tuple(x.copy() for x in bs),None,
                             [(s,m.copy(),p.copy(),d.copy()) for s,m,p,d in coarse],[]))
        return prepared

    @staticmethod
    def prepared_bytes(value):
        if isinstance(value,np.ndarray):return value.nbytes
        if isinstance(value,(list,tuple)):return sum(FastCCWindowUnionMatcher.prepared_bytes(x) for x in value)
        return 0

    def score_prepared(self,probe,enrolled):
        if not enrolled:raise ValueError('At least one enrollment feature is required')
        return float(np.mean(sorted(self._match_unpacked(probe,f) for f in enrolled)[:2]))
