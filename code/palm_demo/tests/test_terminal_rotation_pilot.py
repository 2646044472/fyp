import importlib
from pathlib import Path
import pytest


@pytest.fixture
def pilot(monkeypatch):
    app=Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(app)); monkeypatch.syspath_prepend(str(app/'tools'))
    return importlib.import_module('pilot_terminal_rotation')


def q(sample,outcome,route='exhaustive_terminal_rf_evidence',conflict=True):
    return dict(sample=sample,outcome=outcome,result=dict(recognition_route=route),
                localizations=[dict(primary_details=dict(pklnet_consensus_valid=not conflict))])


def test_roles_fixed_before_inference_and_keep_conflicting_correct_controls(pilot):
    rows=[q('e2','wrong_identity_accepted'),q('f','correct','pose_confident'),
          q('e1','wrong_identity_accepted'),q('c','correct')]
    runs=[dict(case='case',variant='baseline',queries=rows)]
    assert [s for _,s,_ in pilot.select_device(runs)]==['e1','e2','c','f']
    runs[0]['queries'].pop()
    with pytest.raises(ValueError,match='controls'):pilot.select_device(runs)


def paired(outcomes):
    rows=[]
    for i,(before,after) in enumerate(outcomes):
        for variant,value in [('baseline',before),('candidate',after)]:
            rows.append(dict(label=str(i),variant=variant,outcome=value,historical_exact=True,shadow_exact=True))
    return rows


def test_rejection_not_correct_and_no_gain_not_pass(pilot):
    rows=paired([('wrong_identity_accepted','rejected')]+[('correct','correct')]*5)
    gates=pilot.gates(rows)
    assert not gates['real_correction'] and not gates['no_new_failure_rejection_or_wrong']
    assert not all(pilot.gates(paired([('correct','correct')]*6)).values())


def test_old_correct_loss_kills_even_with_net_gain_and_duplicate_rejected(pilot):
    rows=paired([('wrong_identity_accepted','correct')]*2+[('correct','wrong_identity_accepted')]+[('correct','correct')]*3)
    assert not pilot.gates(rows)['all_correct_preserved']
    with pytest.raises(ValueError,match='Duplicate'):pilot.gates(rows+[rows[0]])


def test_incomplete_or_failed_shadow_never_passes(pilot):
    rows=paired([('wrong_identity_accepted','correct')]+[('correct','correct')]*5)
    assert all(pilot.gates(rows).values())
    assert not pilot.gates(rows[:-1])['all_six_paired']
    rows[1]['shadow_exact']=False
    assert not pilot.gates(rows)['candidate_original_shadow_exact']
