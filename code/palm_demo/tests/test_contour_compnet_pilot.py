"""Safety checks for the isolated auxiliary metric and its gallery contract."""
import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def setup(monkeypatch,confident=False):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('contour_compnet_pilot')
    from staged_index_matcher import StagedIndexMatcher
    a=np.eye(1,512,0,dtype=np.float32)[0]
    b=np.eye(1,512,1,dtype=np.float32)[0]
    base={'a':0.,'b':.5} if confident else {'a':.4,'b':.41}
    frames=[np.full((2,2),i,np.uint8) for i in range(5)]
    original=[(None,None,None,None,None,b) for _ in frames]
    calls=[]
    matcher=SimpleNamespace(prepare_enrollment=lambda features:original,
        _auxiliary_scores=lambda probe,groups:base,
        _unpack=lambda feature:(None,(None,None,np.eye(3)),None,feature),
        _embedding=lambda native,source:(calls.append(source) or a),
        geometry=SimpleNamespace(isAntiClock=lambda pts:False),
        confident=StagedIndexMatcher.confident,_aggregate=lambda values:float(np.mean(sorted(values)[:2])))
    quad=np.array([[0,0],[384,0],[384,384],[0,384]],np.float32)
    monkeypatch.setattr(module,'proposal',lambda *args:(quad,{'geometry_only':True}))
    module.install(matcher)
    groups={'a':[(None,)*6+(a,) for _ in range(5)],'b':[(None,)*6+(b,) for _ in range(5)]}
    probe=SimpleNamespace(native=np.ones((500,500),np.uint8),source=np.eye(3))
    return module,matcher,frames,original,groups,probe,calls,base


def test_full_five_frame_gallery_and_six_field_prefix_are_retained(monkeypatch):
    module,matcher,frames,original,groups,probe,calls,base=setup(monkeypatch)
    result=matcher.prepare_enrollment(frames)
    assert len(result)==5 and all(len(row)==7 for row in result)
    assert all(all(a is b for a,b in zip(row[:6],old)) for row,old in zip(result,original))
    assert len(calls)==5
    scores=matcher._auxiliary_scores(probe,groups)
    assert set(scores)==set(groups) and scores['a']==0 and scores['b']==.5
    assert probe.auxiliary_route=='compnet_contour_roi_confident'
    assert all(len(samples)==5 for samples in groups.values())


def test_confident_original_skips_geometry_and_additional_embedding(monkeypatch):
    module,matcher,frames,original,groups,probe,calls,base=setup(monkeypatch,True)
    monkeypatch.setattr(module,'proposal',lambda *args:pytest.fail('Must preserve original confident result'))
    assert matcher._auxiliary_scores(probe,groups) is base
    assert not calls and not matcher._contour_query_trace


def test_unsupported_geometry_keeps_original_vectors_and_scores(monkeypatch):
    module,matcher,frames,original,groups,probe,calls,base=setup(monkeypatch)
    monkeypatch.setattr(module,'proposal',lambda *args:(None,{'unsupported':True}))
    result=matcher.prepare_enrollment(frames)
    assert all(row[6] is old[5] for row,old in zip(result,original))
    assert matcher._auxiliary_scores(probe,groups) is base
    assert not calls and not hasattr(probe,'auxiliary_route')


def test_uncertain_new_metric_does_not_replace_original_or_merge_distances(monkeypatch):
    module,matcher,frames,original,groups,probe,calls,base=setup(monkeypatch)
    groups['b']=groups['a']
    assert matcher._auxiliary_scores(probe,groups) is base
    assert not hasattr(probe,'auxiliary_route')


def test_duplicate_install_and_unexpected_template_contract_fail_closed(monkeypatch):
    module,matcher,frames,original,groups,probe,calls,base=setup(monkeypatch)
    with pytest.raises(ValueError,match='already installed'):module.install(matcher)
    original[0]=(*original[0],None)
    with pytest.raises(ValueError,match='six-field'):matcher.prepare_enrollment(frames)


def test_versioned_copy_preserves_every_payload_byte_and_source_metadata(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('replay_contour_compnet_pilot')
    original=np.arange(5*128,dtype=np.uint8).reshape(5,128)
    original[:,:4]=np.asarray([2801064],'<i4').view(np.uint8)
    saved=original.copy();metadata={'algorithm':'FastCCQualityEvidence-v24-experimental','user':'example'}
    changed,info,payload=module.versioned_copy(original,metadata)
    assert np.array_equal(original,saved) and info['user']==metadata['user']
    assert metadata['algorithm']=='FastCCQualityEvidence-v24-experimental'
    assert info['algorithm']==module.MATCHER and np.array_equal(changed[:,4:],original[:,4:])
    assert all(row[:4].view('<i4')[0]==2801066 for row in changed)
    assert len(payload)==64
    with pytest.raises(AssertionError):module.versioned_copy(changed,metadata)
