"""Experimental fast retrieval with exhaustive fallback for uncertain rankings.

The same existing confidence rule gates both the initial pose result and the
indexed result. This is a routing heuristic, not an open-set acceptance policy
or proof of equivalence for unseen people. Fallback latency remains unbounded.
"""
from proposed_index_matcher import ProposedIndexMatcher
from demo_matcher import FastCCDemoMatcher


class GuardedIndexMatcher(ProposedIndexMatcher):
    name='FastCCGuardedIndex-v9-experimental'
    requires_exhaustive_fallback=True

    def prepare_enrollment(self,features):
        indexed=super().prepare_enrollment(features)
        exhaustive=FastCCDemoMatcher.prepare_enrollment(self,features)
        return [(*a,b) for a,b in zip(indexed,exhaustive)]

    def score_gallery(self,probe,groups):
        scores=super().score_gallery(probe,groups)
        ranking=sorted(scores.values())
        if len(ranking)>=2 and ranking[0]<=.32 and ranking[1]-ranking[0]>=.08:
            return scores
        callback=getattr(probe,'exhaustive',None)
        if not callable(callback):
            raise ValueError('Uncertain indexed query requires complete original-image fallback')
        # Callback retains the original image and original localization results;
        # the normal v6 candidate generation and scoring run without omissions.
        full=self._unpack(callback())
        probe.route='exhaustive_fallback'
        return {user:FastCCDemoMatcher.score_prepared(self,full,[sample[3] for sample in samples])
                for user,samples in groups.items()}
