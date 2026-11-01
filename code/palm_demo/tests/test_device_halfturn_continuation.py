import copy
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def fixture(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    m=importlib.import_module('continue_device_halfturn_guard')
    cases=[dict(name=n,queries=[n+'-q'],enrollment={n+'-user':['a','b','c','d','e']}) for n in ['first','last']]
    runs=[]
    for c in cases:
        for v in ['baseline','candidate']:
            if c['name']=='last' and v=='candidate':continue
            runs.append(dict(case=c['name'],variant=v,complete=True,queries=[dict(sample=s) for s in c['queries']],enrollments=[dict(identity=u) for u in c['enrollment']]))
    return m,dict(protocol={'cases':cases}),dict(complete=False,failure='MemoryError: fixture resource stop',runs=runs)


def test_continuation_only_selects_wholly_unstarted_case(fixture):
    m,p,r=fixture
    assert m.remaining_case(p,r)['name']=='last'


def test_cannot_repeat_partially_completed_case(fixture):
    m,p,r=fixture
    r['runs'][-1]['queries']=[]
    with pytest.raises(ValueError,match='wholly unstarted'):m.remaining_case(p,r)


def test_no_continuation_after_algorithm_failure_or_complete_run(fixture):
    m,p,r=fixture
    for changes in [dict(complete=True),dict(failure='ValueError: score provenance')]:
        trial=dict(copy.deepcopy(r),**changes)
        with pytest.raises(ValueError,match='resource stop'):m.remaining_case(p,trial)
