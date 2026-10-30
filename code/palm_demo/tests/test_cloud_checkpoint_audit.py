import importlib.util
import json
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location('cloud_audit', Path(__file__).resolve().parents[1] / 'tools/audit_cloud_checkpoint.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_windows_mapping_is_bounded_and_longest_first():
    mappings = [('C:/run', '/wrong'), ('C:/run/inputs', '/inputs')]
    assert audit.relocate(r'C:\run\inputs\a.jpg', mappings) == Path('/inputs/a.jpg')
    assert audit.relocate('C:/runner/a.jpg', mappings) == Path('C:/runner/a.jpg')


def test_prefix_keeps_failures_and_rejects_corruption():
    rows = [dict(sample='a', subject='001', index=5, enrollment=False, identity='smpd:001:right')]
    query = dict(sample='a', identity='smpd:001:right', http_status=400, correct=False)
    raw = (json.dumps(query) + '\n').encode()
    assert audit.validate_prefix(rows, dict(queries=[query]), raw) == ([query], 1)
    with pytest.raises(ValueError, match='Incomplete'):
        audit.validate_prefix(rows, dict(queries=[query]), raw[:-1])
    with pytest.raises(ValueError, match='disagree'):
        audit.validate_prefix(rows, dict(queries=[]), raw)
    changed = dict(query, identity='smpd:002:right')
    with pytest.raises(ValueError, match='truth'):
        audit.validate_prefix(rows, dict(queries=[changed]), (json.dumps(changed)+'\n').encode())


def test_missing_checkpoint_fails_closed_without_creating_files(tmp_path):
    result = audit.audit(tmp_path, tmp_path, tmp_path/'compnet.onnx', tmp_path/'pklnet.onnx')
    assert not result['ready_for_parity_check']
    assert result['errors'] == ['Checkpoint incomplete']
    assert list(tmp_path.iterdir()) == []
