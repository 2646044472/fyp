"""Reject spatially detached candidates without labels or reference annotations.

This is a consistency guard, not a semantic hand mask. A wrong anchor can still
reject a useful candidate; retain v4 and evaluate every original split.
"""
import cv2
import numpy as np
from union_matcher import FastCCWindowUnionMatcher, MAGIC


def source_quad(source):
    corners=np.asarray([[0.,0.,1.],[384.,0.,1.],[384.,384.,1.],[0.,384.,1.]])
    mapped=corners@np.linalg.inv(source).T
    return (mapped[:,:2]/mapped[:,2:]).astype(np.float32)


def overlaps_anchor(quad,anchor):
    a=np.asarray(quad,np.float32);b=np.asarray(anchor,np.float32)
    if a.shape!=(4,2) or b.shape!=(4,2) or not np.isfinite(a).all() or not np.isfinite(b).all():return False
    if not cv2.isContourConvex(a) or not cv2.isContourConvex(b):return False
    # One pixel squared excludes numerical boundary touching, not an identity-
    # or dataset-selected relative-overlap threshold.
    return cv2.intersectConvexConvex(a,b)[0]>1.


class FastCCAnchoredUnionMatcher(FastCCWindowUnionMatcher):
    name='FastCCAnchoredUnion-v5'
    magic=MAGIC+1

    @staticmethod
    def candidate_decisions(quad,hypotheses):
        return [dict(index=i,valid=bool(h.get('valid',False)),
                     retained=bool(h.get('valid',False) and overlaps_anchor(h.get('quad'),quad)),
                     reason='invalid_geometry' if not h.get('valid',False) else
                     ('overlaps_anchor' if overlaps_anchor(h.get('quad'),quad) else 'disjoint_from_anchor'),
                     quad=h.get('quad'),kind=h.get('kind','base')) for i,h in enumerate(hypotheses)]

    def extract_with_hypotheses(self,full,quad,normalized_roi,hypotheses):
        if len(hypotheses)>8:raise ValueError('Expected at most eight hypotheses')
        decisions=self.candidate_decisions(quad,hypotheses)
        retained=[h for h,d in zip(hypotheses,decisions) if d['retained']]
        return super().extract_with_hypotheses(full,quad,normalized_roi,retained)

    def upgrade_v4_template(self,feature):
        """Exact descriptor reuse for audit/migration; no recognition labels."""
        old=FastCCWindowUnionMatcher(self.base)
        legacy,primary,_,native,gallery,queries=old._unpack(feature)
        if native is None:return self._pack(legacy,np.empty(0,np.uint8),[],[])
        ok,png=cv2.imencode('.png',native,[cv2.IMWRITE_PNG_COMPRESSION,1])
        if not ok:raise ValueError('Native grayscale encoding failed')
        anchor=source_quad(primary[2])
        # Recover field bounds by walking the validated packed payload.
        from union_matcher import HEADER
        from registered_matcher import DUAL_SIZE
        pos=HEADER+DUAL_SIZE+int(np.asarray(feature)[:HEADER].view('<i4')[2]);packed_gallery=[];packed_queries=[]
        for index,(sigma,source,p,d) in enumerate(gallery+queries):
            header=np.asarray(feature)[pos:pos+16].view('<i4');lower,upper=map(int,header[2:4]);pos+=88+len(p)*520
            encoded=self._encode_view(sigma,source,p,d,lower,upper)
            if index<len(gallery):packed_gallery.append(encoded)
            elif overlaps_anchor(source_quad(source),anchor):packed_queries.append(encoded)
        return self._pack(legacy,png.ravel(),packed_queries,packed_gallery)

    def _accept_alignment(self,primary,mapped):
        return overlaps_anchor(mapped,source_quad(primary[2]))
