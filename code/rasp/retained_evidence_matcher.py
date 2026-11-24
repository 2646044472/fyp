"""Opt-in integration of the previously validated retained-FastCC repair.

The staged flow below copies the frozen StagedIndexMatcher.score_gallery and
changes only its terminal fallback. Earlier gates, candidate geometry and the
best-two enrollment aggregation are unchanged. The frozen source is retained
for historical replay and rollback; no runtime patch or tools import is used.
"""

import cv2
import numpy as np

from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher
from pklnet_roi import normalize_roi_pixels
from proposed_index_matcher import proposed_registration
from staged_index_matcher import StagedIndexMatcher


def merge_frame_evidence(before, after, *, score_family="fastcc"):
    """Combine only comparable ordinary FastCC shifted-overlap distances."""
    if score_family != "fastcc":
        raise ValueError("Cannot merge a separate angular or weighted metric")
    if set(before) != set(after):
        raise ValueError("Frame set changed")
    if any(not np.isfinite(value) or not 0 <= value <= 1
           for value in [*before.values(), *after.values()]):
        raise ValueError("Invalid FastCC distance")
    return {key: min(before[key], after[key]) for key in before}


class RetainedEvidenceStages(StagedIndexMatcher):
    def score_gallery(self,probe,groups):
        pairs={(u,j):min(self.base.match(p.astype(bool),s[0]) for p in probe.bank if p[0,0]>=0)
               for u,samples in groups.items() for j,s in enumerate(samples)}
        def aggregate():
            return {u:self._aggregate([pairs[(u,j)] for j in range(len(samples))]) for u,samples in groups.items()}
        scores=aggregate()
        if self.confident(scores):probe.route='pose_confident';return scores
        auxiliary=getattr(self,'_auxiliary_scores',None)
        if auxiliary is not None:
            candidate=auxiliary(probe,groups)
            if candidate is not None and self.confident(candidate):
                probe.route=getattr(probe,'auxiliary_route','compnet_evidence_confident')
                return candidate
        self.prepare_gallery(groups)
        primary,secondary=self._legacy_probe(probe)
        def legacy(key):
            u,j=key
            return key,self._legacy_pair(probe,primary,secondary,groups[u][j])
        pairs.update(self._workers.map(legacy,list(pairs)))
        scores=aggregate()
        if self.confident(scores):
            probe.route='legacy_confident'
            return scores
        linked=getattr(self,'_enrollment_link_stage',None)
        if linked is not None:
            linked(probe,groups,pairs)
            scores=aggregate()
            if self.confident(scores):
                probe.route=getattr(probe,'link_stage_route','enrollment_link_confident')
                return scores
        with self._index_lock:
            if self._index is not None:
                for wide in (False,True):
                    views=self._stage_views(probe,wide);proposals=[]
                    for source,p,d in views:
                        found={}
                        for i,matches in enumerate(self._index.knnMatch(d,k=16) if len(d) else []):
                            for match in matches:
                                found.setdefault(int(self._labels[match.trainIdx]),set()).add(i)
                        proposals.append(found)
                    def pair(key):
                        user,j=key;best=pairs[key]
                        for (source,p,d),found in zip(views,proposals):
                            for group in self._positions[key]:
                                indices=found.get(group,())
                                if len(indices)<4:continue
                                _,_,vi=self._mapping[group];target=groups[user][j][1][vi]
                                transform=proposed_registration((p,d),(target[2],target[3]),indices)
                                if transform is None:continue
                                warp=np.diag([1/3,1/3,1])@transform@source
                                corners=np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])@np.linalg.inv(warp).T
                                corners=corners[:,:2]/corners[:,2:]
                                if (not np.isfinite(corners).all() or (corners<1).any()
                                    or (corners[:,0]>=probe.native.shape[1]-1).any()
                                    or (corners[:,1]>=probe.native.shape[0]-1).any()
                                    or not self._accept_alignment((None,None,probe.source),corners)):continue
                                pixels=normalize_roi_pixels(cv2.warpPerspective(probe.native,warp,(128,128)))
                                best=min(best,self.base.match(self.base.extract(pixels),target[4]))
                        return key,best
                    pairs.update(self._workers.map(pair,list(pairs)))
                    scores=aggregate()
                    if self.confident(scores):
                        probe.route='wide_index_confident' if wide else 'normal_index_confident'
                        return scores
        callback=getattr(probe,'exhaustive',None)
        if not callable(callback):raise ValueError('Uncertain indexed query requires complete original-image fallback')
        full=self._unpack(callback())
        prior_route=getattr(probe,'link_stage_route','')
        if prior_route=='quality_evidence_confident' or prior_route.startswith('compnet_'):
            raise ValueError('Cannot merge a separate angular or weighted metric')
        before=dict(pairs);after={}
        for user,samples in groups.items():
            values=self._workers.map(lambda sample:self._match_unpacked(full,sample[3]),samples)
            after.update({(user,j):value for j,value in enumerate(values)})
        merged=merge_frame_evidence(before,after)
        probe.retained_fastcc_evidence=dict(before=before,after=after,merged=merged)
        # Preserve the validated route's existing acceptance-policy family.
        probe.route='exhaustive_retained_fastcc_pilot'
        return {u:self._aggregate([merged[u,j] for j in range(len(samples))]) for u,samples in groups.items()}


class RetainedCompNetAlternateROIMatcher(CompNetAlternateROIMatcher, RetainedEvidenceStages):
    """V26 geometry/encoders with retained ordinary FastCC fallback evidence.

    The packed byte format (magic) remains v26-compatible. The different name
    deliberately prevents mixing deployed templates: enroll again or prepare
    an explicitly isolated, compatible copy for a controlled replay.

    Cooperative MRO keeps AffineEnrollmentMatcher's query-local cleanup and
    LinkedEnrollmentMatcher's initialization around RetainedEvidenceStages.
    """

    name = 'FastCCRetainedEvidence-v27-experimental'
    magic = CompNetAlternateROIMatcher.magic
