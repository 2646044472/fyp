"""Research-only fixed spatial pyramid; never selected by the app registry.

The original ROI and a standard half/double-scale, five-position pyramid are
evaluated independently. Confident candidates must agree on the identity;
scores are never minimized across mutually different ROI candidates.
"""
import numpy as np


CONTEXT_VIEWS=((1.,0.,0.),)+tuple((s,x,y) for s in (.5,1.,2.)
    for x,y in ((0.,0.),(-.5,0.),(.5,0.),(0.,-.5),(0.,.5)) if (s,x,y)!=(1.,0.,0.))


def context_quads(quad,image_size):
    quad=np.asarray(quad,np.float32);center=quad.mean(axis=0)
    horizontal=quad[1]-quad[0];vertical=quad[3]-quad[0]
    width,height=image_size;result=[]
    for index,(scale,x,y) in enumerate(CONTEXT_VIEWS):
        q=quad.copy() if index==0 else (center+scale*(quad-center)+x*horizontal+y*vertical).astype(np.float32)
        if (np.isfinite(q).all() and (q>=0).all() and (q[:,0]<width).all() and (q[:,1]<height).all()):
            result.append((index,q))
    return result


def confident_identity(scores):
    ranked=sorted(scores,key=scores.get)
    if len(ranked)<2:return None
    a,b=ranked[:2]
    return a if scores[a]<=.32 and scores[b]-scores[a]>=.08 else None


def context_evidence(score_views):
    """Original evidence has precedence, otherwise require confident agreement."""
    if not score_views:return None,[]
    original=confident_identity(score_views[0])
    if original is not None:return original,[0]
    votes=[(i,confident_identity(scores)) for i,scores in enumerate(score_views[1:],1)]
    votes=[(i,u) for i,u in votes if u is not None]
    winners={u for i,u in votes}
    return (next(iter(winners)) if len(winners)==1 else None),[i for i,u in votes]
