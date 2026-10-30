"""Opt-in terminal RF evidence, preserving every original confident path.

One-request code-pair capture only; no images, labels or cross-query answers.
Ordinary scores drive the unchanged staged pipeline. A completed exhaustive
query gets a separate whole-gallery RF score vector over its actual compared
pairs. Old and new distances never share a minimum/accumulator.
"""
import threading
import time

import numpy as np

from fastcc_valid_support import ReceptiveFieldFastCC

POLICY='original-confident-paths-terminal-rf-v1'
ORIGINAL_TERMINAL='exhaustive_retained_fastcc_pilot'
TERMINAL_ROUTE='exhaustive_terminal_rf_evidence'


def packed(code):
    code=np.asarray(code)
    if code.shape!=(32,32):raise ValueError('Expected original 32x32 FastCC code')
    return np.packbits(code.astype(bool),bitorder='little').tobytes()


def install(algorithm):
    if getattr(algorithm,'_terminal_rf_installed',False) or getattr(algorithm,'_rf_distance_installed',False):
        raise ValueError('Distance experiment already installed')
    assert algorithm.base is algorithm.legacy.base and algorithm.base is algorithm._pose.base
    assert getattr(algorithm,'_retain_fastcc_evidence_pilot',False)
    old_score=algorithm.score_gallery;old_match=algorithm.base.match
    old_pair=algorithm._match_unpacked;old_legacy=algorithm._legacy_pair
    state=[None];local=threading.local();serial=threading.RLock();kernel=ReceptiveFieldFastCC()

    def scoped(call,target,*args):
        context=state[0];key=context['target_objects'].get(id(target)) if context is not None else None
        previous=getattr(local,'target',None);local.target=key
        try:return call(*args)
        finally:local.target=previous

    def pair(query,target,details=None):return scoped(old_pair,target,query,target,details)

    def legacy(probe,primary,secondary,target):return scoped(old_legacy,target,probe,primary,secondary,target)

    def matching(left,right):
        value=old_match(left,right);context=state[0]
        if context is None:return value
        key=context['code_objects'].get(id(right))
        if key is None:key=getattr(local,'target',None)
        if key is None:
            with context['lock']:context['unknown_calls']+=1
            return value
        codes=(packed(left),packed(right))
        with context['lock']:
            context['pairs'][key].add(codes);context['ordinary_calls']+=1
        return value

    def score(probe,groups):
        with serial:
            if state[0] is not None:raise RuntimeError('Nested query context is unsupported')
            keys=[(user,j) for user,samples in groups.items() for j in range(len(samples))]
            context=dict(code_objects={},target_objects={},pairs={key:set() for key in keys},ordinary_calls=0,
                unknown_calls=0,lock=threading.Lock(),exhaustive_callback_calls=0)
            def bind(mapping,obj,key):
                old=mapping.get(id(obj),key)
                if old!=key:raise ValueError('Prepared code object shared across enrollment frames')
                mapping[id(obj)]=key
            for user,samples in groups.items():
                for j,sample in enumerate(samples):
                    key=(user,j);bind(context['target_objects'],sample,key);bind(context['target_objects'],sample[3],key)
                    bind(context['code_objects'],sample[0],key)
                    for view in sample[1]:bind(context['code_objects'],view[4],key)
            callback=getattr(probe,'exhaustive',None)
            if callable(callback):
                def exhaustive():
                    context['exhaustive_callback_calls']+=1
                    return callback()
                probe.exhaustive=exhaustive
            state[0]=context;begin=time.perf_counter()
            try:
                original=old_score(probe,groups);original_ms=(time.perf_counter()-begin)*1000
                route=getattr(probe,'route',None)
                trace=dict(policy=POLICY,original_route=route,original_scores={u:float(s) for u,s in original.items()},
                    ordinary_calls=context['ordinary_calls'],unknown_calls=context['unknown_calls'],
                    exhaustive_callback_calls=context['exhaustive_callback_calls'],original_scoring_ms=original_ms,
                    captured_pairs=sum(len(v) for v in context['pairs'].values()),rf_applied=False,rf_unique_comparisons=0,rf_ms=0.)
                algorithm._terminal_rf_trace=trace
                if route!=ORIGINAL_TERMINAL:
                    trace['reason']='original_confident_path_verbatim'
                    return original
                if context['unknown_calls'] or any(not v for v in context['pairs'].values()):
                    raise ValueError('Incomplete per-frame comparison provenance; cannot apply terminal RF')
                tick=time.perf_counter();decoded={};distances={}
                def decode(value):
                    if value not in decoded:decoded[value]=np.unpackbits(np.frombuffer(value,np.uint8),bitorder='little').reshape(32,32)
                    return decoded[value]
                per_frame={}
                for key,pairs in context['pairs'].items():
                    for a,b in pairs:
                        if (a,b) not in distances:distances[a,b]=kernel.match(decode(a),decode(b))
                    per_frame[key]=min(distances[pair] for pair in pairs)
                scores={u:algorithm._aggregate([per_frame[u,j] for j in range(len(samples))]) for u,samples in groups.items()}
                trace.update(rf_applied=True,reason='original_exhaustive_branch_only',rf_unique_comparisons=len(distances),
                    rf_ms=(time.perf_counter()-tick)*1000,rf_scores={u:float(s) for u,s in scores.items()})
                probe.route=TERMINAL_ROUTE
                return scores
            finally:
                state[0]=None
                if callable(callback):probe.exhaustive=callback
    algorithm._match_unpacked=pair;algorithm._legacy_pair=legacy
    algorithm.base.match=matching;algorithm.score_gallery=score
    algorithm._terminal_rf_installed=True
    return algorithm
