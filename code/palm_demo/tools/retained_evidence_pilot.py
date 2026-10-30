"""Opt-in accuracy pilot: retain only same-metric FastCC frame evidence.

Installed in an isolated process, never imported by production. The exact
frozen staged source is checked and only its terminal fallback is replaced.
"""
import hashlib,inspect,textwrap
import numpy as np


def merge_frame_evidence(before,after):
    if set(before)!=set(after):raise ValueError('Frame set changed')
    if any(not np.isfinite(v)or not 0<=v<=1 for v in[*before.values(),*after.values()]):raise ValueError('Invalid FastCC distance')
    return {key:min(before[key],after[key])for key in before}


def install_retained_evidence_pilot():
    import staged_index_matcher as module
    source=inspect.getsource(module.StagedIndexMatcher.score_gallery)
    path=inspect.getsourcefile(module.StagedIndexMatcher)
    if hashlib.sha256(open(path,'rb').read()).hexdigest()!='d9a17b834f17c720d27fc4865961a5f7117edce6ddd62c926178d65d3b7821f2':
        raise ValueError('Pilot requires the exact frozen v26 staged source')
    tail="        return {u:FastCCDemoMatcher.score_prepared(self,full,[s[3] for s in samples]) for u,samples in groups.items()}"
    assert source.count(tail)==1
    replacement='''        if not getattr(self,'_retain_fastcc_evidence_pilot',False):
            return {u:FastCCDemoMatcher.score_prepared(self,full,[s[3] for s in samples]) for u,samples in groups.items()}
        if getattr(probe,'link_stage_route',None)=='quality_evidence_confident':
            raise ValueError('Cannot merge the separate weighted metric')
        before=dict(pairs);after={}
        for user,samples in groups.items():
            values=self._workers.map(lambda sample:self._match_unpacked(full,sample[3]),samples)
            after.update({(user,j):value for j,value in enumerate(values)})
        merged=_merge_frame_evidence(before,after)
        self._retained_evidence_trace=dict(before=before,after=after,merged=merged)
        probe.route='exhaustive_retained_fastcc_pilot'
        return {u:self._aggregate([merged[u,j] for j in range(len(samples))]) for u,samples in groups.items()}'''
    candidate=textwrap.dedent(source.replace(tail,replacement));namespace=dict(module.__dict__,_merge_frame_evidence=merge_frame_evidence)
    exec(compile(candidate,'<isolated-retained-fastcc-pilot>','exec'),namespace)
    original=module.StagedIndexMatcher.score_gallery;module.StagedIndexMatcher.score_gallery=namespace['score_gallery']
    return dict(original=original,source_sha256=hashlib.sha256(source.encode()).hexdigest(),candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest())
