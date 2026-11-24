"""Experimental pooling of sparse correspondences through enrollment links.

Every pooled query point appears once, at the median transferred location.
Similarity/affine guards, original-pixel scoring and routing gates are unchanged.
"""
import cv2
import numpy as np
from affine_enrollment_matcher import AffineEnrollmentMatcher, affine_registration
from registration_accelerated import estimate_pairs
from pklnet_roi import normalize_roi_pixels
from registered_matcher import local_features


def pool_correspondences(samples, target_index, channel, query, correspondences, links):
    transferred={}
    for i,sample in enumerate(samples):
        target=sample[2][channel]
        points=target[4] if channel==0 else target[0]
        transforms=([np.eye(3)] if i==target_index else
                    [t for j,t in links[i] if j==target_index])
        pairs=correspondences[id(sample)][channel]
        if not pairs:continue
        query_ids=np.asarray([qi for qi,ti in pairs])
        source=np.column_stack([points[[ti for qi,ti in pairs]],np.ones(len(pairs))])
        for transform in transforms:
            # Retain the original matrix/vector arithmetic per point; batch
            # allocation, division and validity checks instead of tiny NumPy calls.
            mapped=np.asarray([transform@point for point in source])
            mapped=mapped[:,:2]/mapped[:,2:]
            valid=np.isfinite(mapped).all(axis=1)&(mapped>=0).all(axis=1)&(mapped<384).all(axis=1)
            for qi,point in zip(query_ids[valid],mapped[valid]):
                transferred.setdefault(qi,[]).append(point)
    ids=sorted(transferred)
    p=np.asarray([query[0][i] for i in ids],np.float32).reshape(-1,2)
    q=np.empty((len(ids),2),np.float32)
    lengths={}
    for out,i in enumerate(ids):lengths.setdefault(len(transferred[i]),[]).append(out)
    for count,positions in lengths.items():
        values=np.asarray([transferred[ids[out]] for out in positions])
        q[positions]=values[:,0,:] if count==1 else np.median(values,axis=1)
    return p,q


class PooledEnrollmentMatcher(AffineEnrollmentMatcher):
    name='FastCCPooledEnrollment-v20-experimental'
    magic=2801060

    def _legacy_probe(self,probe):
        if probe.legacy is None:
            shift=np.asarray([[1.,0,192],[0,1.,192],[0,0,1.]])
            context=cv2.warpPerspective(probe.native,shift@probe.source,(768,768))
            pixels=normalize_roi_pixels(cv2.warpPerspective(probe.native,probe.source,(384,384)))
            coarse=normalize_roi_pixels(context[192:576,192:576])
            blurred=cv2.GaussianBlur(coarse,(0,0),2.)
            # Called by the main scoring stage before per-enrollment worker jobs.
            # Independent SIFT instances preserve features and use the idle core.
            primary_features,secondary=self._workers.map(local_features,(pixels,blurred))
            primary=(probe.bank,context,probe.source,probe.native.shape[::-1],*primary_features)
            probe.legacy=primary,secondary
        return probe.legacy

    def _pooled_views(self,samples,j,primary,secondary,probe,links):
        return [pool_correspondences(samples,j,channel,query,probe.affine_pairs,links)
                for channel,query in enumerate(((primary[4],primary[5]),secondary))]

    def _enrollment_link_stage(self,probe,groups,pairs):
        super()._enrollment_link_stage(probe,groups,pairs)
        self._pool_stage(probe,groups,pairs)

    def _pool_stage(self,probe,groups,pairs):
        aggregate=lambda:{u:self._aggregate([pairs[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
        if self.confident(aggregate()):return aggregate()
        primary,secondary=self._legacy_probe(probe)
        corners=np.asarray([[0.,0,1],[128.,0,1],[128.,128,1],[0,128.,1]])
        def match_group(item):
            user,samples=item
            links={i:self._links[user,i] for i in range(len(samples))}
            updated={j:pairs[user,j] for j in range(len(samples))}
            for j,target in enumerate(samples):
                for p,q in self._pooled_views(samples,j,primary,secondary,probe,links):
                    if len(p)<4:continue
                    ids=[(i,i) for i in range(len(p))]
                    # Descriptors are unused: correspondence identities are explicit.
                    stub=np.empty((len(p),0),np.float32)
                    transforms=(estimate_pairs(p,q,ids),
                        affine_registration((p,stub),(q,stub),lambda a,b:ids))
                    for transform in transforms:
                        if transform is None:continue
                        warp=np.diag([1/3,1/3,1])@transform@probe.source
                        mapped=corners@np.linalg.inv(warp).T;mapped=mapped[:,:2]/mapped[:,2:]
                        if (not np.isfinite(mapped).all() or (mapped<1).any()
                            or (mapped[:,0]>=probe.native.shape[1]-1).any()
                            or (mapped[:,1]>=probe.native.shape[0]-1).any()
                            or not self._accept_alignment((None,None,probe.source),mapped)):continue
                        pixels=normalize_roi_pixels(cv2.warpPerspective(probe.native,warp,(128,128)))
                        updated[j]=min(updated[j],self.base.match(self.base.extract(pixels),target[0]))
            return user,updated
        for user,updated in self._workers.map(match_group,groups.items()):
            pairs.update({(user,j):score for j,score in updated.items()})
        probe.link_stage_route='pooled_enrollment_confident'
        return aggregate()

