"""Research-only indexed correspondences; not approved for deployment."""
import cv2
import numpy as np
from indexed_demo_matcher import IndexedDemoMatcher
from registration_accelerated import estimate_pairs
from pklnet_roi import normalize_roi_pixels


def proposed_pairs(da,db,indices):
    indices=np.asarray(sorted(indices),np.int32)
    if min(len(indices),len(db))<4:return []
    forward=cv2.BFMatcher().knnMatch(da[indices],db,k=2)
    good=[(int(indices[m.queryIdx]),m.trainIdx) for m,n in forward if m.distance<.85*n.distance]
    if not good:return []
    targets=sorted({j for i,j in good})
    reverse=cv2.BFMatcher().knnMatch(db[targets],da,k=1)
    nearest={j:matches[0].trainIdx for j,matches in zip(targets,reverse)}
    return [(i,j) for i,j in good if nearest[j]==i]


def proposed_registration(left,right,indices):
    pa,da=left;pb,db=right
    return estimate_pairs(pa,pb,proposed_pairs(da,db,indices))


class ProposedIndexMatcher(IndexedDemoMatcher):
    name='FastCCProposedIndex-v8-experimental'
    # Enrollment representation is unchanged; audit-only descriptor reuse.

    def score_gallery(self,probe,groups):
        pairs={(u,j):min(self.base.match(p.astype(bool),s[0]) for p in probe.bank if p[0,0]>=0)
               for u,samples in groups.items() for j,s in enumerate(samples)}
        scores={u:self._aggregate([pairs[(u,j)] for j in range(len(samples))]) for u,samples in groups.items()}
        ranked=sorted(scores.values())
        if len(ranked)>=2 and ranked[0]<=.32 and ranked[1]-ranked[0]>=.08:
            probe.route='pose_confident';return scores
        probe.route='proposed_alignment'
        self.prepare_gallery(groups)
        with self._index_lock:
            if self._index is None:return scores
            primary,secondary=self._legacy_probe(probe)
            views=self._query_views(probe)
            proposals=[]
            for source,p,d in views:
                found={}
                for i,matches in enumerate(self._index.knnMatch(d,k=16) if len(d) else []):
                    for match in matches:
                        group=int(self._labels[match.trainIdx])
                        found.setdefault(group,set()).add(i)
                proposals.append(found)
            def pair(key):
                user,j=key
                tp,ts=groups[user][j][2]
                best=self.legacy._match_parts(primary,tp,[(secondary,ts)])
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
        return {u:self._aggregate([pairs[(u,j)] for j in range(len(samples))]) for u,samples in groups.items()}
