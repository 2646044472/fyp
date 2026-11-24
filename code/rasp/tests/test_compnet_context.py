import numpy as np
from compnet_context_pilot import context_quads,context_evidence


def test_original_crop_is_exact_and_optional_tiles_stay_in_frame():
    quad=np.asarray([[70.1,40.2],[150.7,50.3],[140.6,130.8],[60.,120.7]],np.float32)
    crops=context_quads(quad,(160,150))
    assert crops[0][0]==0 and np.array_equal(crops[0][1],quad)
    assert len(crops)<15
    for _,q in crops:
        assert (q>=0).all() and (q[:,0]<160).all() and (q[:,1]<150).all()


def test_original_confidence_keeps_precedence():
    assert context_evidence([{'a':.2,'b':.5},{'a':.5,'b':.1}])==('a',[0])


def test_context_conflict_does_not_select_the_most_favorable_crop():
    identity,votes=context_evidence([{'a':.4,'b':.42},{'a':.2,'b':.5},{'a':.5,'b':.1}])
    assert identity is None and votes==[1,2]


def test_uncertain_candidates_cannot_vote_and_distance_margin_is_preserved():
    assert context_evidence([{'a':.4,'b':.42},{'a':.29,'b':.33}])==(None,[])
    assert context_evidence([{'a':.4,'b':.42},{'a':.2,'b':.5},{'a':.3,'b':.35}])==('a',[1])


def test_single_identity_is_not_confident():
    assert context_evidence([{'a':.1},{'a':.05}])==(None,[])
