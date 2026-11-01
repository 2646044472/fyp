import copy
import importlib
from pathlib import Path

import pytest
from types import SimpleNamespace


@pytest.fixture
def guard(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('pilot_device_halfturn_guard')


def test_selection_keeps_remaining_error_and_prior_correction(guard):
    def row(name, correct, route):
        return dict(sample=name,correct=correct,result=dict(recognition_route=route))
    current = dict(runs=[dict(case='fixture-case', queries=[
        row('fast',True,'pose_confident'), row('correction',True,'exhaustive_terminal_rf_evidence'),
        row('wrong',False,'exhaustive_terminal_rf_evidence')])])
    previous = copy.deepcopy(current)
    previous['runs'][0]['queries'][1]['correct'] = False
    panel = guard.select_panel(current, previous)
    assert panel['queries'] == ['fast','correction','wrong']
    assert panel['case'] == 'fixture-case'


def test_exact_pair_rejects_score_drift_even_with_same_identity(guard):
    a = dict(http_status=200,scores={'a':.1,'b':.4},result=dict(status='MATCH',user_id='a',score=.1))
    b = copy.deepcopy(a); b['scores']['b'] = .40000001
    assert not guard.exact_decision(a,b)
    b = copy.deepcopy(a); b['result']['recognition_route'] = 'changed'
    assert not guard.exact_decision(a,b)


def test_roi_guard_rejects_geometry_or_pixel_changes(guard):
    keys = ['primary_quad','primary_details','primary_roi_sha256','candidate_quad',
            'candidate_details','candidate_roi_sha256','verbatim']
    a = {'localizations':[{k:'fixture' for k in keys}]}
    assert guard.exact_roi(a, copy.deepcopy(a))
    for k in keys:
        b = copy.deepcopy(a); b['localizations'][0][k] = 'changed'
        assert not guard.exact_roi(a,b)
    assert not guard.exact_roi(a, {'localizations':[]})


def test_observer_forwards_context_extractor_attributes(guard):
    engine = SimpleNamespace(root=Path('synthetic-model-root'), threads=3, policy='illumination')
    calls = []
    adapter = guard.ExtractorObserver(engine, lambda image, **kw: calls.append((image,kw)) or 'fixture-output')
    assert adapter.root == engine.root and adapter.threads == 3 and adapter.policy == 'illumination'
    assert adapter.extract('synthetic-frame', side=128) == 'fixture-output'
    assert calls == [('synthetic-frame', {'side':128})]
