import copy
import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def policy(monkeypatch):
    app = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(app)); monkeypatch.syspath_prepend(str(app/'tools'))
    return importlib.import_module('terminal_rotation_consensus')


def quad(x=20):
    return np.asarray([[x,20],[x+40,20],[x+40,60],[x,60]], np.float32)


def view(turns, q=None, valid=True):
    return dict(turns=turns, quad=quad().tolist() if q is None else np.asarray(q).tolist(), valid=valid)


def result(q=None, **details):
    q = quad() if q is None else q
    return np.zeros((16,16), np.uint8), q, dict(roi_geometry_valid=True, pklnet_consensus_valid=False,
        pklnet_roi_candidates=[dict(quad=q.tolist(), valid=True)], **details)


def test_inverse_all_turns_matches_non_square_pil_pixels(policy):
    pixels = np.arange(7*11, dtype=np.uint8).reshape(7,11)
    image = Image.fromarray(pixels)
    for turns, op in enumerate((None, Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_180, Image.Transpose.ROTATE_270)):
        rotated = image if op is None else image.transpose(op)
        for y in range(rotated.height):
            for x in range(rotated.width):
                a, b = policy.unrotate([x,y], image.size, turns).astype(int)
                assert rotated.getpixel((x,y)) == image.getpixel((a,b))


def test_unique_quorum_excludes_outlier_and_uses_actual_medoid(policy):
    views = [view(0,quad(100)), view(1), view(2,quad(21)), view(3,quad(22))]
    chosen, trace = policy.choose_quorum(views)
    assert chosen == 2 and trace['quorum'] == [1,2,3]
    assert trace['min_iou'] == .5 and trace['minimum_views'] == 3


def test_ties_prefer_primary_and_corner_start_does_not_change_overlap(policy):
    chosen, trace = policy.choose_quorum([view(k,np.roll(quad(), k, axis=0)) for k in range(4)])
    assert chosen == 0 and trace['quorum'] == [0,1,2,3]


def test_two_agreeing_views_insufficient_and_duplicate_views_error(policy):
    assert policy.choose_quorum([view(0),view(1),view(2,valid=False),view(3,quad(100))])[0] is None
    with pytest.raises(ValueError, match='One observation'):
        policy.choose_quorum([view(0),view(0),view(1)])


def test_two_maximum_cliques_do_not_cherry_pick(policy):
    chosen, trace = policy.choose_quorum([view(0),view(1),view(2,quad(10)),view(3,quad(30))])
    assert chosen is None and trace['reason'] == 'ambiguous_maximum_quorum'


def test_repair_samples_original_bytes_and_keeps_semantic_corner_order(policy):
    image = Image.fromarray(np.arange(100*90*3,dtype=np.uint8).reshape(90,100,3))
    desired = np.roll(quad(), 2, axis=0); observations=[]; sample={}
    primary = result(quad(55)); saved=copy.deepcopy(primary[2])
    # A 180-degree inverse is itself. k=1/3 inverse each other, using the rotated size.
    def extract(rotated, **kw):
        turns = len(observations)+1; observations.append(turns)
        inverse_turns = (4-turns)%4
        mapped = policy.unrotate(desired, rotated.size, inverse_turns)
        return result(mapped)
    def sample_original(bgr, q, **kw):
        sample.update(bgr=bgr, quad=q.copy()); return np.full((16,16),73,np.uint8)
    localizer=SimpleNamespace(extract=extract, _roi_extractor=SimpleNamespace(getROIimg=sample_original))
    candidate=policy.RotationConsensus(localizer)
    raw,q,d=candidate.repair(image,primary)
    np.testing.assert_array_equal(q,desired)
    np.testing.assert_array_equal(sample['bgr'],np.asarray(image)[:,:,::-1])
    np.testing.assert_array_equal(d['pklnet_roi_candidates'][0]['quad'],desired)
    assert primary[2] == saved and np.all(raw==73) and candidate.trace['changed']


def test_mapping_rejects_nonfinite_and_out_of_frame(policy):
    with pytest.raises(ValueError): policy.unrotate([np.nan,1],(20,30),1)
    assert not policy.valid_quad(quad(), (40,40))


def algorithm(route, first, second=None):
    state=SimpleNamespace(_terminal_rf_installed=True, _terminal_rf_trace={}, calls=0)
    def scorer(probe, groups):
        state.calls += 1; probe.route = route if state.calls == 1 else 'pose_confident'
        state._terminal_rf_trace = dict(epoch=state.calls)
        return first if state.calls == 1 else second
    state.score_gallery=scorer
    return state


@pytest.mark.parametrize('route,valid,consensus', [('pose_confident',True,False),
    ('exhaustive_terminal_rf_evidence',True,True),('exhaustive_terminal_rf_evidence',False,False)])
def test_original_paths_return_exact_score_object_without_new_localization(policy,route,valid,consensus):
    scores={'a':.2,'b':.8}; model=algorithm(route,scores)
    localizer=SimpleNamespace(extract=lambda *a,**kw:pytest.fail('Unexpected localization'))
    installed=policy.TerminalRepair(model,localizer)
    primary=result(); primary[2].update(roi_geometry_valid=valid,pklnet_consensus_valid=consensus)
    installed.observe(Image.new('RGB',(100,90)),primary)
    assert model.score_gallery(SimpleNamespace(),{}) is scores
    assert model.calls == 1 and not installed.trace['attempted']


def test_rescore_once_returns_new_vector_even_if_scores_are_worse(policy):
    old={'a':.1,'b':.6}; new={'a':.8,'b':.9}; model=algorithm(policy.TERMINAL_ROUTE,old,new)
    model.extract_probe_with_context=lambda *args:SimpleNamespace()
    localizer=SimpleNamespace()
    installed=policy.TerminalRepair(model,localizer)
    first=result(quad(10)); different=result(quad(12)); different[0][:]=np.arange(16,dtype=np.uint8)*12
    installed.geometry.repair=lambda *args:different
    installed.geometry.trace={'changed':True}
    installed.observe(Image.new('RGB',(100,90)),first)
    assert model.score_gallery(SimpleNamespace(),{}) is new
    assert model.calls==2 and installed.trace['rescored'] and installed.trace['original_scores']==old

