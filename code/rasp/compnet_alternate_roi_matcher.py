"""Opt-in existing-base-ROI evidence; no extra localization or context search."""
import cv2
import numpy as np
from anchored_matcher import source_quad,overlaps_anchor
from compnet_evidence_matcher import CompNetEvidenceMatcher


class CompNetAlternateROIMatcher(CompNetEvidenceMatcher):
    name='FastCCCompNetAlternateROI-v26-experimental'
    magic=2801066
    needs_localization_candidates=True

    def _auxiliary_scores(self,probe,groups):
        original=super()._auxiliary_scores(probe,groups)
        if original is None or self.confident(original):return original
        candidates=getattr(probe,'localization_candidates',None)
        if not candidates or len(candidates)>2:
            raise ValueError('Alternate ROI evidence requires the original/gamma base localization candidates')
        anchor=source_quad(probe.source);accepted=[];seen=[]
        keys=[(u,j) for u,ss in groups.items() for j in range(len(ss))]
        gallery=np.asarray([groups[u][j][5] for u,j in keys])
        for candidate in candidates:
            if not candidate.get('valid',False):continue
            q=np.asarray(candidate['quad'],np.float32)
            if (q.shape!=(4,2) or not np.isfinite(q).all() or (q<0).any()
                or (q[:,0]>=probe.native.shape[1]).any() or (q[:,1]>=probe.native.shape[0]).any()):
                raise ValueError('Invalid alternate ROI geometry')
            if not overlaps_anchor(q,anchor):continue
            dst=np.asarray([[384,0],[0,0],[0,384],[384,384]] if self.geometry.isAntiClock(q[:3].reshape(-1))
                else [[0,0],[384,0],[384,384],[0,384]],np.float32)
            source=cv2.getPerspectiveTransform(q,dst)
            if np.array_equal(source,probe.source) or any(np.array_equal(source,m) for m in seen):continue
            seen.append(source)
            query=self._embedding(probe.native,source)
            distances=np.arccos(np.clip(gallery@query,-1,1))/np.pi
            pairs=dict(zip(keys,distances))
            scores={u:self._aggregate([pairs[u,j] for j in range(len(ss))]) for u,ss in groups.items()}
            if self.confident(scores):accepted.append((min(scores,key=scores.get),scores,source_quad(source)))
        if accepted and len({u for u,s,q in accepted})==1:
            probe.auxiliary_route='compnet_alternate_roi_confident'
            probe.auxiliary_roi_quad=accepted[0][2]
            return accepted[0][1]
        return original
