import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from terminal_binary_bias import BinaryMarginalRF, distances, paired_scores, classify
from fastcc_valid_support import ReceptiveFieldFastCC, constant_rf_mask, overlap_slices


def direct(left, right):
    rows = []
    mask = constant_rf_mask()
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            aa, bb = overlap_slices(dy, dx)
            valid = mask[aa] & mask[bb]
            x, y = left[aa][valid].astype(float), right[bb][valid].astype(float)
            n, a, b, c = len(x), int(x.sum()), int(y.sum()), int((x*y).sum())
            sx, sy = 2*x-1, 2*y-1
            cx, cy = sx-sx.mean(), sy-sy.mean()
            norm = np.linalg.norm(cx)*np.linalg.norm(cy)
            rows.append(([n,a,b,c], np.mean(x != y),
                         .5*(1-np.mean(cx*cy)),
                         1. if norm == 0 else .5*(1-np.dot(cx,cy)/norm)))
    return rows


@pytest.mark.parametrize('seed',[0,1,20261102])
def test_integer_counts_and_three_metrics_match_independent_pixel_reference(seed):
    rng = np.random.default_rng(seed)
    left, right = rng.random((2,32,32)) < .72
    counts = BinaryMarginalRF().counts(left,right)
    reference = direct(left,right)
    assert np.array_equal(counts, np.asarray([r[0] for r in reference]))
    metrics = distances(counts)
    for arm, column in [('A',1),('B',2),('C',3)]:
        np.testing.assert_allclose(metrics[arm], np.asarray([r[column] for r in reference]), atol=1e-14,rtol=1e-14)
    assert paired_scores(counts)['A'] == ReceptiveFieldFastCC().match(left,right)


@pytest.mark.parametrize('lv,rv',[(0,0),(0,1),(1,0),(1,1)])
def test_constants_are_retained_with_worst_candidate_distance(lv,rv):
    counts = BinaryMarginalRF().counts(np.full((32,32),lv),np.full((32,32),rv))
    got = distances(counts)
    assert got['constant'].all()
    assert np.array_equal(got['C'],np.ones(81))
    assert np.all(got['B']==.5)


def test_balanced_inputs_identity_complement_and_nearly_constant_stability():
    for n,a,b,c in [(784,392,392,392),(784,392,392,0),(784,1,1,1),(784,783,783,783)]:
        r=distances([[n,a,b,c]])
        assert np.isfinite(r['C']).all()
        assert r['C'][0] == (1 if c==0 else 0)
    r=distances([[784,392,392,230]])
    np.testing.assert_allclose(r['A'],r['C'],atol=1e-15)


@pytest.mark.parametrize('bad',[[[0,0,0,0]],[[784,785,1,1]],[[784,2,2,3]],[[784,783,783,0]],[[784,.5,2,0]],[[784,np.nan,2,0]]])
def test_invalid_counts_abort_instead_of_silent_clipping(bad):
    with pytest.raises(ValueError):distances(bad)


def test_uniform_shift_symmetry_and_no_mutation():
    rng=np.random.default_rng(4);x,y=rng.integers(0,2,(2,32,32),dtype=np.uint8)
    before=x.copy();kernel=BinaryMarginalRF()
    assert paired_scores(kernel.counts(x,y)) == paired_scores(kernel.counts(y,x))
    assert np.array_equal(x,before)


def test_ranking_preserves_worst_tie_as_failure_and_constant_cells_stay_in_denominator():
    result=classify({'a':1.,'b':1.},'a',['a','b'])
    assert result['status']=='MATCH' and result['tied']
    assert result['outcome']=='true_identity_nonunique'
    assert classify({'a':.2,'b':.3},'a',['a','b'])['outcome']=='correct'
    assert classify({'a':.2,'b':.3},'b',['a','b'])['outcome']=='wrong_identity_accepted'


def test_optional_pair_capture_is_immutable_and_preserves_confident_identity_object(monkeypatch):
    module=importlib.import_module('terminal_rf_evidence')
    left=np.zeros((32,32),bool);target=np.ones((32,32),bool)
    base=SimpleNamespace(match=lambda a,b:float(np.mean(a!=b)))
    groups={'x':[(target,[],None,object()) for _ in range(5)]}
    expected={'x':.123};observations=[]
    algorithm=SimpleNamespace(base=base,legacy=SimpleNamespace(base=base),_pose=SimpleNamespace(base=base),
        _retain_fastcc_evidence_pilot=True,_match_unpacked=lambda *a:None,_legacy_pair=lambda *a:None)
    def score(probe,groups):
        for row in groups['x']:base.match(left,row[0])
        probe.route='pose_confident'
        return expected
    algorithm.score_gallery=score
    # Repeated code object across frames is correctly rejected; make distinct copies.
    groups={'x':[(target.copy(),[],None,object()) for _ in range(5)]}
    module.install(algorithm,capture=lambda pairs,trace:observations.append((pairs,trace)))
    assert algorithm.score_gallery(SimpleNamespace(),groups) is expected
    assert len(observations[0][0])==5
    assert all(isinstance(p,frozenset) for p in observations[0][0].values())


@pytest.mark.parametrize('scores',[{'a':.2,'b':.3},{'a':1.,'b':1.},{'a':1.01,'b':1.02}])
def test_offline_decision_uses_exact_frozen_gallery_threshold_and_stable_order(scores):
    from gallery import Gallery
    store=SimpleNamespace(list_users=lambda:['a','b'])
    algorithm=SimpleNamespace(prepare_probe=lambda p:p,prepare_enrollment=lambda f:f,
        prepared_bytes=lambda f:0,score_prepared=lambda p,f:0,score_gallery=lambda p,g:scores)
    gallery=Gallery(store,algorithm,threshold=1.,min_margin=0.)
    gallery._load_prepared=lambda user:([],{'capture_profile':'rgb'})
    actual=gallery.identify(None)
    offline=classify(scores,'a',['a','b'])
    assert (actual.status,actual.user_id,actual.score,actual.second_score)==tuple(offline[k] for k in ['status','user_id','score','second_score'])


def test_gate_never_selects_diagnostic_B_and_requires_all_four_controls():
    from pilot_terminal_binary_bias import evaluate
    rows=[dict(label='D'+str(i+1),mechanism={'bias_supported':True} if i<2 else None,
               arms={a:{'decision':{'outcome':('wrong_identity_accepted' if i<2 and a=='C' else 'correct'),'tied':False}} for a in ['A','B','C']}) for i in range(4)]
    assert not evaluate(rows)['pilot_pass']  # B succeeding cannot substitute for C.
    rows[0]['arms']['C']['decision']['outcome']='correct'
    assert evaluate(rows)['pilot_pass']
    rows[2]['arms']['C']['decision']['outcome']='rejected'
    assert not evaluate(rows)['pilot_pass']
    with pytest.raises(ValueError):evaluate(rows[:3])
