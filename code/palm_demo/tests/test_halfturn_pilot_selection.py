import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def selection(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'tools'))
    module = importlib.import_module('halfturn_pilot_selection')
    for name in ['parent', 'continuation', 'geometry', 'output', 'private']:
        (tmp_path / name).mkdir()
    path = tmp_path / 'private/selection.json'
    value = dict(enrollment=[f'fixture-001-E-{i}' for i in range(5)],
                 queries=[f'fixture-001-Q-{i}' for i in range(8)],
                 controls=['fixture-001-Q-5', 'fixture-001-Q-6'],
                 recovered_enrollment='fixture-001-E-3', candidate_user='fixture-user')
    path.write_text(json.dumps(value))
    args = SimpleNamespace(output=tmp_path / 'output', parent=tmp_path / 'parent',
                           continuation=tmp_path / 'continuation',
                           geometry=tmp_path / 'geometry', selection=path)
    return module, args, value


def test_binding_changes_when_private_selection_changes(selection):
    module, args, value = selection
    first = module.bind('identification', args)
    value['recovered_enrollment'] = value['enrollment'][2]
    args.selection.write_text(json.dumps(value))
    second = module.bind('identification', args)
    assert first['BINDING'] != second['BINDING']
    assert first['ENROLL'] == second['ENROLL']


@pytest.mark.parametrize('alias', ['parent', 'continuation', 'geometry', 'ancestor'])
def test_no_output_can_alias_or_contain_protected_roots(selection, alias):
    module, args, _ = selection
    args.output = args.parent.parent if alias == 'ancestor' else getattr(args, alias)
    with pytest.raises(ValueError, match='protected source'):
        module.bind('identification', args)


def test_reject_path_traversal_in_private_sample_identifiers(selection):
    module, args, value = selection
    value['queries'][0] = '../escaped-record'
    args.selection.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='safe filename'):
        module.bind('identification', args)


def test_no_overlapping_enrollment_and_query_samples(selection):
    module, args, value = selection
    value['queries'][0] = value['enrollment'][0]
    args.selection.write_text(json.dumps(value))
    with pytest.raises(ValueError, match='distinct'):
        module.bind('identification', args)


def test_geometry_binds_exact_eight_with_negative_last(selection):
    module, args, _ = selection
    samples = [f'fixture-{i}' for i in range(8)]
    args.selection.write_text(json.dumps(dict(samples=samples, negative=samples[-1])))
    assert module.bind('geometry', args)['SAMPLES'] == samples
    args.selection.write_text(json.dumps(dict(samples=samples, negative=samples[0])))
    with pytest.raises(ValueError, match='negative last'):
        module.bind('geometry', args)
