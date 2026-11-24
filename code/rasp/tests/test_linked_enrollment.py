from types import SimpleNamespace
import threading
import numpy as np
import pytest
from linked_enrollment_matcher import LinkedEnrollmentMatcher, composed_transform
from staged_index_matcher import StagedIndexMatcher
from pose_matcher import FastCCPoseMatcher


def test_composition_maps_query_through_enrollment_coordinates():
    direct = np.asarray([[1.,0,20],[0,1.,-8],[0,0,1]])
    link = np.asarray([[.8,0,-5],[0,.8,12],[0,0,1]])
    points = np.asarray([[12.,30.,1.],[200.,100.,1.]])
    result = composed_transform(link,direct)
    np.testing.assert_allclose(points@result.T,(points@direct.T)@link.T)


@pytest.mark.parametrize('bad', [np.diag([-1.,1.,1.]),np.diag([3.,3.,1.]),
    np.asarray([[1.,0,0],[0,1.,0],[.01,0,1.]]), np.full((3,3),np.nan)])
def test_composition_rejects_outside_geometry_policy(bad):
    assert composed_transform(bad,np.eye(3)) is None


def test_legacy_stage_score_is_preserved_and_transforms_are_retained(monkeypatch):
    algorithm = object.__new__(LinkedEnrollmentMatcher)
    monkeypatch.setattr(FastCCPoseMatcher,'match',lambda *_: .4)
    transforms = [np.eye(3),np.asarray([[1.,0,2],[0,1.,0],[0,0,1]])]
    calls = iter(transforms)
    algorithm.legacy = SimpleNamespace(registration=lambda *_:next(calls),
        _aligned_score=lambda context,source,size,bank,transform,current: .25 if transform[0,2] else .3)
    primary = (None,None,np.eye(3),(640,480),None,None)
    target = (None,None,(primary,(None,None)),None)
    probe = SimpleNamespace(enrollment_direct={})
    assert algorithm._legacy_pair(probe,primary,(None,None),target)==.25
    assert len(probe.enrollment_direct[id(target)])==2


def test_gallery_links_never_cross_users_and_rebuild_after_gallery_change(monkeypatch):
    algorithm = object.__new__(LinkedEnrollmentMatcher)
    algorithm._index_lock = threading.RLock()
    def parent(self,groups):
        self._index_key = tuple((u,id(v)) for u,v in sorted(groups.items()))
    monkeypatch.setattr(StagedIndexMatcher,'prepare_gallery',parent)
    def sample(value):
        primary = (None,None,None,None,value,value)
        return (None,None,(primary,(value,value)),None)
    seen = []
    def register(left,right):
        seen.append((left[0],right[0]))
        return np.eye(3)
    algorithm.registration = register
    groups={'a':[sample(1),sample(2)],'b':[sample(10),sample(20)]}
    algorithm.prepare_gallery(groups)
    assert set(seen)=={(1,2),(2,1),(10,20),(20,10)}
    count=len(seen)
    algorithm.prepare_gallery(groups)
    assert len(seen)==count
    old_b=algorithm._links['b',0]
    groups['a']=[sample(3),sample(4)]
    algorithm.prepare_gallery(groups)
    assert (3,4) in seen and (4,3) in seen
    assert len(seen)==count+4
    assert algorithm._links['b',0] is old_b
    # A newly assembled list of the exact same immutable samples is reusable.
    groups={u:list(samples) for u,samples in groups.items()}
    algorithm.prepare_gallery(groups)
    assert len(seen)==count+4
    # Adding a user computes only within that new user's templates.
    groups['c']=[sample(30),sample(40)]
    algorithm.prepare_gallery(groups)
    assert len(seen)==count+8
    assert set(seen[-4:])=={(30,40),(40,30)}
    # Ordering is part of the key: edges must address the new template indices.
    groups['b']=list(reversed(groups['b']))
    algorithm.prepare_gallery(groups)
    assert len(seen)==count+12
    removed=groups.pop('a')
    algorithm.prepare_gallery(groups)
    assert len(seen)==count+12
    assert 'a' not in algorithm._link_sources
    assert not any(user=='a' for user,index in algorithm._links)
    groups['a']=removed
    algorithm.prepare_gallery(groups)
    assert len(seen)==count+16
