import copy
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def sample(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    module=importlib.import_module('summarize_device_halfturn_guard')
    selected=[f'fixture-frame-{i}' for i in range(5)]
    case=dict(name='fixture-case',queries=['fixture-query-a','fixture-query-b'],enrollment={'fixture-user':selected})
    run=dict(case=case['name'],queries=[dict(sample=q) for q in case['queries']],zero_transactions=True,
             enrollments=[dict(identity='fixture-user',http_status=200,result={'recognition_ready':True},
                               localizations=[dict(sample=s) for s in selected])])
    runs=[dict(copy.deepcopy(run),variant=v) for v in ['baseline','candidate']]
    return module,dict(runs=runs),dict(protocol={'cases':[case]})


def test_complete_fixed_keys_pass(sample):
    module,report,plan=sample
    assert all(module.audit_coverage(report,plan).values())


def test_duplicate_query_cannot_hide_missing_query(sample):
    module,report,plan=sample
    report['runs'][1]['queries'][1]=copy.deepcopy(report['runs'][1]['queries'][0])
    assert not module.audit_coverage(report,plan)['fixed_query_keys']


def test_missing_variant_is_not_a_complete_regression(sample):
    module,report,plan=sample
    report['runs'].pop()
    assert not module.audit_coverage(report,plan)['exact_case_variant_set']


def test_five_frame_count_does_not_allow_frame_replacement(sample):
    module,report,plan=sample
    frames=report['runs'][0]['enrollments'][0]['localizations']
    frames[-1]=copy.deepcopy(frames[0])
    assert not module.audit_coverage(report,plan)['fixed_five_frame_enrollments']


def test_continuation_merge_keeps_parent_stop_immutable(sample):
    module,_,_=sample
    parent=dict(complete=False,failure='MemoryError: frozen resource gate',runs=[dict(case='fixture-a',variant='candidate')])
    child=dict(complete=True,**{'pass':True},runs=[dict(case='fixture-b',variant='candidate')])
    merged=module.merge_preserved_case(parent,child)
    assert len(merged['runs'])==2 and merged['complete']
    assert not parent['complete'] and len(parent['runs'])==1 and 'failure' in parent


def test_continuation_cannot_double_count_a_case(sample):
    module,_,_=sample
    parent=dict(complete=False,failure='MemoryError: frozen resource gate',runs=[dict(case='fixture-a',variant='candidate')])
    child=dict(complete=True,**{'pass':True},runs=[dict(case='fixture-a',variant='candidate')])
    with pytest.raises(ValueError,match='duplicated'):module.merge_preserved_case(parent,child)
