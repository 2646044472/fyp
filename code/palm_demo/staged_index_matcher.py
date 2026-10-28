"""Research-only staged context search with the same exhaustive fallback gate."""
import cv2
import numpy as np
from guarded_index_matcher import GuardedIndexMatcher
from proposed_index_matcher import proposed_registration
from demo_matcher import FastCCDemoMatcher
from registered_matcher import local_features
from pklnet_roi import normalize_roi_pixels


class StagedIndexMatcher(GuardedIndexMatcher):
    name='FastCCStagedIndex-v10-experimental'

    @staticmethod
    def confident(scores):
        ranking=sorted(scores.values())
        return len(ranking)>=2 and ranking[0]<=.32 and ranking[1]-ranking[0]>=.08

    def _stage_views(self,probe,wide):
        scale,offset,unoffset=(.5,288.,576.) if wide else (1.,192.,192.)
        transform=np.asarray([[scale,0,offset],[0,scale,offset],[0,0,1.]])
        pixels=normalize_roi_pixels(cv2.warpPerspective(probe.native,transform@probe.source,(768,768)))
        def extract(sigma):
            p,d=local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
            return probe.source,p/scale-unoffset,d
        return list(self._workers.map(extract,(0,2)))

    def score_gallery(self,probe,groups):
        pairs={(u,j):min(self.base.match(p.astype(bool),s[0]) for p in probe.bank if p[0,0]>=0)
               for u,samples in groups.items() for j,s in enumerate(samples)}
        def aggregate():
            return {u:self._aggregate([pairs[(u,j)] for j in range(len(samples))]) for u,samples in groups.items()}
        scores=aggregate()
        if self.confident(scores):probe.route='pose_confident';return scores
        self.prepare_gallery(groups)
        primary,secondary=self._legacy_probe(probe)
        def legacy(key):
            u,j=key;tp,ts=groups[u][j][2]
            return key,self.legacy._match_parts(primary,tp,[(secondary,ts)])
        pairs.update(self._workers.map(legacy,list(pairs)))
        scores=aggregate()
        if self.confident(scores):
            probe.route='legacy_confident'
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
        full=self._unpack(callback());probe.route='exhaustive_fallback'
        return {u:FastCCDemoMatcher.score_prepared(self,full,[s[3] for s in samples]) for u,samples in groups.items()}
