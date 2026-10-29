from types import SimpleNamespace
import numpy as np
import pytest
from PIL import Image
from compnet_pilot import preprocess_compnet
from compnet_evidence_matcher import CompNetEvidenceMatcher
from staged_index_matcher import StagedIndexMatcher


def test_existing_pose_result_wins_without_auxiliary_inference():
    matcher=StagedIndexMatcher.__new__(StagedIndexMatcher)
    matcher.base=SimpleNamespace(match=lambda q,g:g)
    matcher._auxiliary_scores=lambda *a:pytest.fail('Must not run an extra model for existing confident pose')
    probe=SimpleNamespace(bank=np.zeros((1,32,32)))
    assert matcher.score_gallery(probe,{'a':[(.1,)],'b':[(.5,)]})=={'a':.1,'b':.5}
    assert probe.route=='pose_confident'


@pytest.mark.parametrize('candidate,accepted', [({'a':.2,'b':.5},True),({'a':.30,'b':.35},False)])
def test_auxiliary_does_not_bypass_margin_guard(candidate,accepted):
    matcher=StagedIndexMatcher.__new__(StagedIndexMatcher)
    matcher.base=SimpleNamespace(match=lambda q,g:g)
    matcher._auxiliary_scores=lambda *a:candidate
    matcher.prepare_gallery=lambda groups:None
    def legacy(probe):raise RuntimeError('original_fallback_continues')
    matcher._legacy_probe=legacy
    probe=SimpleNamespace(bank=np.zeros((1,32,32)))
    if accepted:
        assert matcher.score_gallery(probe,{'a':[(.4,)],'b':[(.45,)]})==candidate
        assert probe.route=='compnet_evidence_confident'
    else:
        with pytest.raises(RuntimeError,match='original_fallback_continues'):
            matcher.score_gallery(probe,{'a':[(.4,)],'b':[(.45,)]})


def test_encoder_is_query_local_and_single_identity_has_no_extra_inference():
    matcher=CompNetEvidenceMatcher.__new__(CompNetEvidenceMatcher);calls=[]
    a=np.zeros(512,np.float32);a[0]=1;b=np.zeros(512,np.float32);b[1]=1
    def embedding(*args):calls.append(True);return a
    matcher._embedding=embedding
    sample=lambda v:(None,None,None,None,None,v)
    groups={'a':[sample(a),sample(a)],'b':[sample(b),sample(b)]}
    probe=SimpleNamespace(native=None,source=None)
    for _ in range(2):
        scores=matcher._auxiliary_scores(probe,groups)
        assert scores['a']==0 and abs(scores['b']-.5)<1e-6
    assert len(calls)==2
    assert matcher._auxiliary_scores(probe,{'a':groups['a']}) is None and len(calls)==2


def test_positive_pixel_standardization_preserves_black_mask_and_rejects_empty():
    pixels=np.arange(128*128,dtype=np.uint16).reshape(128,128)%256
    result=preprocess_compnet(Image.fromarray(pixels.astype(np.uint8)))[0,0]
    assert not result[pixels==0].any()
    assert abs(result[pixels>0].mean())<1e-6
    assert abs(result[pixels>0].std(ddof=1)-1)<1e-4
    with pytest.raises(ValueError,match='nonzero'):
        preprocess_compnet(Image.fromarray(np.zeros((128,128),np.uint8)))
