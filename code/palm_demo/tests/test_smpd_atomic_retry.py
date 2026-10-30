"""Filesystem publication checks only; no inference or evaluation restart."""
import errno
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def journal(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'tools'))
    return importlib.import_module('smpd_run_journal')


def access_denied():
    error = PermissionError(errno.EACCES, 'simulated Windows access denial')
    error.winerror = 5
    return error


def test_one_access_denial_reuses_complete_closed_temp(journal, tmp_path, monkeypatch):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old'})
    before = target.read_bytes()
    expected = journal.canonical({'state': 'new'}) + b'\n'
    real_replace = journal.os.replace
    attempts, sleeps = [], []
    failure = access_denied()

    def replace(source, destination):
        assert target.read_bytes() == before
        assert source.read_bytes() == expected
        attempts.append(source)
        if len(attempts) == 1:
            raise failure
        real_replace(source, destination)

    monkeypatch.setattr(journal.os, 'replace', replace)
    monkeypatch.setattr(journal.time, 'sleep', sleeps.append)
    journal.atomic(target, {'state': 'new'})
    assert len(attempts) == 2 and attempts[0] == attempts[1]
    assert sleeps == [.05]
    assert target.read_bytes() == expected
    assert not list(tmp_path.glob('*.tmp'))


def test_persistent_access_denial_preserves_old_bytes(journal, tmp_path, monkeypatch):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old', 'completed_queries': 216})
    before = target.read_bytes()
    attempts, sleeps = [], []
    failure = access_denied()

    def replace(source, destination):
        assert target.read_bytes() == before
        attempts.append(source)
        raise failure

    monkeypatch.setattr(journal.os, 'replace', replace)
    monkeypatch.setattr(journal.time, 'sleep', sleeps.append)
    with pytest.raises(PermissionError) as caught:
        journal.atomic(target, {'state': 'new'})
    assert caught.value is failure
    assert len(attempts) == 6 and len(set(attempts)) == 1
    assert sleeps == [.05, .1, .2, .4, .8]
    assert target.read_bytes() == before
    assert journal.load(target) == {'state': 'old', 'completed_queries': 216}
    assert not list(tmp_path.glob('*.tmp'))


def test_normal_publish_fsyncs_then_replaces_complete_json(journal, tmp_path, monkeypatch):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old'})
    before = target.read_bytes()
    real_fsync, real_replace = journal.os.fsync, journal.os.replace
    events = []

    def fsync(fd):
        real_fsync(fd)
        events.append('fsync')

    def replace(source, destination):
        assert events == ['fsync']
        assert target.read_bytes() == before
        assert journal.load(source) == {'state': 'new', 'data': list(range(1000))}
        real_replace(source, destination)
        events.append('replace')
        assert journal.load(target)['state'] == 'new'

    monkeypatch.setattr(journal.os, 'fsync', fsync)
    monkeypatch.setattr(journal.os, 'replace', replace)
    monkeypatch.setattr(journal.time, 'sleep', lambda _: pytest.fail('No delay on success'))
    journal.atomic(target, {'state': 'new', 'data': list(range(1000))})
    assert events == ['fsync', 'replace']
    assert not list(tmp_path.glob('*.tmp'))


@pytest.mark.parametrize('winerror', [None, 32, 112])
def test_other_replace_errors_fail_immediately(journal, tmp_path, monkeypatch, winerror):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old'})
    before = target.read_bytes()
    failure = PermissionError(errno.EACCES, 'other failure')
    if winerror is not None:
        failure.winerror = winerror
    calls = []

    def replace(*args):
        calls.append(args)
        raise failure

    monkeypatch.setattr(journal.os, 'replace', replace)
    monkeypatch.setattr(journal.time, 'sleep', lambda _: pytest.fail('Do not retry other errors'))
    with pytest.raises(PermissionError) as caught:
        journal.atomic(target, {'state': 'new'})
    assert caught.value is failure and len(calls) == 1
    assert target.read_bytes() == before
    assert not list(tmp_path.glob('*.tmp'))


def test_exclusive_record_arriving_during_backoff_is_preserved(journal, tmp_path, monkeypatch):
    target = tmp_path / '00000.json'
    existing = journal.canonical({'correct': False}) + b'\n'
    calls = []

    def replace(*args):
        calls.append(args)
        raise access_denied()

    def sleep(_):
        target.write_bytes(existing)

    monkeypatch.setattr(journal.os, 'replace', replace)
    monkeypatch.setattr(journal.time, 'sleep', sleep)
    with pytest.raises(FileExistsError):
        journal.atomic(target, {'correct': True}, exclusive=True)
    assert len(calls) == 1
    assert target.read_bytes() == existing
    assert not list(tmp_path.glob('*.tmp'))


def test_failed_serialization_never_replaces_target(journal, tmp_path, monkeypatch):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old'})
    before = target.read_bytes()
    monkeypatch.setattr(journal.os, 'replace', lambda *a: pytest.fail('Incomplete JSON must not be published'))
    with pytest.raises(ValueError):
        journal.atomic(target, {'bad': float('nan')})
    assert target.read_bytes() == before
    assert not list(tmp_path.glob('*.tmp'))


def test_access_denial_during_fsync_is_not_retried(journal, tmp_path, monkeypatch):
    target = tmp_path / 'status.json'
    journal.atomic(target, {'state': 'old'})
    before = target.read_bytes()
    failure = access_denied()

    def fsync(_):
        raise failure

    monkeypatch.setattr(journal.os, 'fsync', fsync)
    monkeypatch.setattr(journal.os, 'replace', lambda *a: pytest.fail('Unsynced JSON must not be published'))
    monkeypatch.setattr(journal.time, 'sleep', lambda _: pytest.fail('Only replace is retried'))
    with pytest.raises(PermissionError) as caught:
        journal.atomic(target, {'state': 'new'})
    assert caught.value is failure
    assert target.read_bytes() == before
    assert not list(tmp_path.glob('*.tmp'))
