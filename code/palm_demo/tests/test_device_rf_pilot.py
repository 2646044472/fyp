import copy
import importlib
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'tools'))
    return importlib.import_module('pilot_device_rf_distance')


def test_shared_distance_changes_padding_agreement_without_changing_extraction(module):
    from fastcc_valid_support import constant_rf_mask
    extraction=lambda pixels:np.asarray(pixels)>0
    base=SimpleNamespace(extract=extraction,match=lambda a,b:0.)
    algorithm=SimpleNamespace(base=base,legacy=SimpleNamespace(base=base),_pose=SimpleNamespace(base=base))
    module.install(algorithm)
    left=np.zeros((32,32),bool);right=constant_rf_mask()
    # Every valid interior bit differs; agreeing artificial-border bits cannot
    # lower this score. All references see the same metric; extraction is intact.
    assert algorithm.base.match(left,right)==1.
    assert algorithm.legacy.base.match(left,right)==1.
    assert algorithm.base.extract is extraction
    with pytest.raises(ValueError,match='already installed'):module.install(algorithm)
    with pytest.raises(ValueError,match='geometry'):algorithm.base.match(left[:16],right)


def test_disjoint_matchers_fail_before_partial_metric_replacement(module):
    base=SimpleNamespace(match=lambda a,b:0.)
    algorithm=SimpleNamespace(base=base,legacy=SimpleNamespace(base=object()),_pose=SimpleNamespace(base=base))
    original=base.match
    with pytest.raises(AssertionError):module.install(algorithm)
    assert base.match is original


def test_incomplete_observational_provenance_cannot_qualify_ablation(module):
    query=dict(reference_equal=True,missing=[],matching_coverage=dict(calls=1,geometric_calls=0,pose_calls=1,unknown_query=0,unknown_target=0),
        poses=[dict(full_rf_support=True)],geometry_matches=[])
    audit=dict(complete=True,matcher=module.MATCHER,queries=[copy.deepcopy(query) for _ in range(7)],originals_unchanged=True,source_templates_unchanged=True)
    module.validate_audit(audit)
    for mutate in (
        lambda a:a['queries'][0]['matching_coverage'].update(unknown_query=1),
        lambda a:a['queries'][0]['poses'][0].update(full_rf_support=False),
        lambda a:a['queries'][0].update(reference_equal=False),
    ):
        changed=copy.deepcopy(audit);mutate(changed)
        with pytest.raises(AssertionError):module.validate_audit(changed)
