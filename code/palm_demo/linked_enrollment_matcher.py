"""Experimental single-hop enrollment geometry reuse; unchanged v10 fallback.

Enrollment links use pixels/descriptors only, within each supplied enrollment
group. A query's already-computed direct registrations seed composed proposals.
Composed geometry is only a proposal: original query pixels receive FastCC
scoring against the target enrollment. No acceptance/routing gates are relaxed.
"""
import cv2
import numpy as np
from staged_index_matcher import StagedIndexMatcher
from pose_matcher import FastCCPoseMatcher
from pklnet_roi import normalize_roi_pixels


def composed_transform(link, direct):
    transform = np.asarray(link) @ np.asarray(direct)
    if (transform.shape != (3,3) or not np.isfinite(transform).all()
        or not np.allclose(transform[2], [0,0,1], atol=1e-8)
        or np.linalg.det(transform[:2,:2]) <= 0):
        return None
    singular = np.linalg.svd(transform[:2,:2], compute_uv=False)
    angle = float(np.rad2deg(np.arctan2(transform[1,0],transform[0,0])))
    if singular.min() < .5 or singular.max() > 2 or abs(angle) > 40:
        return None
    return transform


class LinkedEnrollmentMatcher(StagedIndexMatcher):
    name = 'FastCCLinkedEnrollment-v12-experimental'
    magic = 2801052

    def prepare_gallery(self, groups):
        super().prepare_gallery(groups)
        with self._index_lock:
            if getattr(self,'_link_key',None) == self._index_key:
                return
            linked = {}
            previous_sources = getattr(self, '_link_sources', {})
            previous_links = getattr(self, '_links', {})
            sources = {}
            for user,samples in groups.items():
                # Prepared samples are immutable snapshots supplied by Gallery.
                # Retain their objects, not just IDs, to prevent ID reuse. A new
                # snapshot or order invalidates only this identity's links.
                snapshot = tuple(samples)
                sources[user] = snapshot
                previous = previous_sources.get(user)
                if (previous is not None and len(previous) == len(snapshot)
                        and all(a is b for a,b in zip(previous,snapshot))):
                    for i in range(len(samples)):
                        linked[user,i] = previous_links[user,i]
                    continue
                for i,sample in enumerate(samples):
                    primary,secondary = sample[2]
                    edges = []
                    for j,target in enumerate(samples):
                        if i == j:
                            continue
                        tp,ts = target[2]
                        for left,right in (((primary[4],primary[5]),(tp[4],tp[5])),(secondary,ts)):
                            transform = self.registration(left,right)
                            if transform is not None:
                                edges.append((j,transform.copy()))
                    linked[(user,i)] = edges
            # Removed identities and their strong references are evicted here.
            self._links,self._link_sources,self._link_key = linked,sources,self._index_key

    def score_gallery(self, probe, groups):
        probe.enrollment_direct = {}
        return super().score_gallery(probe,groups)

    def _legacy_pair(self, probe, primary, secondary, target):
        tp, ts = target[2]
        score = FastCCPoseMatcher.match(self.legacy,primary[0],tp[0])
        found = []
        for left,right in (((primary[4],primary[5]),(tp[4],tp[5])),(secondary,ts)):
            transform = self.legacy.registration(left,right)
            if transform is not None:
                found.append(transform)
                score = min(score,self.legacy._aligned_score(primary[1],primary[2],primary[3],tp[0],transform,score))
        probe.enrollment_direct[id(target)] = found
        return score

    def _enrollment_link_stage(self, probe, groups, pairs):
        corners = np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])
        links = self._links
        def group_job(item):
            user,samples = item
            updated = {j:pairs[(user,j)] for j in range(len(samples))}
            for i,sample in enumerate(samples):
                for direct in probe.enrollment_direct.get(id(sample),()):
                    for j,link in links[(user,i)]:
                        transform = composed_transform(link,direct)
                        if transform is None:
                            continue
                        warp = np.diag([1/3,1/3,1]) @ transform @ probe.source
                        mapped = corners @ np.linalg.inv(warp).T
                        mapped = mapped[:,:2]/mapped[:,2:]
                        if (not np.isfinite(mapped).all() or (mapped<1).any()
                            or (mapped[:,0]>=probe.native.shape[1]-1).any()
                            or (mapped[:,1]>=probe.native.shape[0]-1).any()
                            or not self._accept_alignment((None,None,probe.source),mapped)):
                            continue
                        pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native,warp,(128,128)))
                        score = self.base.match(self.base.extract(pixels),samples[j][0])
                        updated[j] = min(updated[j],score)
            return user,updated
        for user,updated in self._workers.map(group_job,groups.items()):
            pairs.update({(user,j):score for j,score in updated.items()})
