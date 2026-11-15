import numpy as np
import pytest
from templates import TemplateStore


def test_legacy_refresh_atomic_and_preserves_original(tmp_path, monkeypatch):
    old = tmp_path / 'alice.npz'; side = tmp_path / 'alice.json'
    np.savez_compressed(old, features=np.array([1]))
    side.write_text('{"version": 1}')
    original = old.read_bytes(), side.read_bytes()
    store = TemplateStore(tmp_path)
    import templates
    replace = templates.os.replace
    monkeypatch.setattr(templates.os, 'replace', lambda *args: (_ for _ in ()).throw(OSError('injected')))
    with pytest.raises(OSError): store.save('alice', np.array([2]), {'version': 2})
    assert store.load('alice')[1]['version'] == 1
    monkeypatch.setattr(templates.os, 'replace', replace)
    store.save('alice', np.array([2]), {'version': 2})
    values, meta = TemplateStore(tmp_path).load('alice')
    assert values.tolist() == [2] and meta['version'] == 2
    assert (old.read_bytes(), side.read_bytes()) == original
    assert store.list_template_ids() == ['alice']


def test_corrupt_new_does_not_fallback_and_partial_old_not_overwritten(tmp_path):
    store = TemplateStore(tmp_path)
    (tmp_path / 'a.json').write_text('{}')
    with pytest.raises(ValueError): store.save('a', np.array([1]), {})
    np.savez_compressed(tmp_path / 'a.npz', features=np.array([1]))
    (tmp_path / 'a.atomic.npz').write_bytes(b'broken')
    with pytest.raises(Exception): store.load('a')


def test_explicit_delete_removes_new_and_historical_files(tmp_path):
    store = TemplateStore(tmp_path)
    store.save('new', np.array([1]), {'version': 1})
    assert store.list_users() == ['new']
    store.delete('new')
    assert not store.list_template_ids()
    np.savez_compressed(tmp_path / 'old.npz', features=np.array([1]))
    (tmp_path / 'old.json').write_text('{"version":1}')
    store.save('old', np.array([2]), {'version':2})
    store.delete('old')
    assert store.list_template_ids() == []
    assert not any(tmp_path.iterdir())


def test_union_conflict_is_not_overwritten(tmp_path):
    from lossless_template_store import LosslessTemplateStore
    store = TemplateStore(tmp_path)
    union = tmp_path / 'a.union2.npz'
    union.write_bytes(b'historical')
    assert store.list_template_ids() == ['a']
    with pytest.raises(ValueError): store.save('a', np.array([1]), {})
    with pytest.raises(ValueError): store.load('a')
    assert union.read_bytes() == b'historical'
    store.save('b', np.array([1]), {})
    with pytest.raises(ValueError): LosslessTemplateStore(tmp_path).load('b')


def test_replacement_failure_preserves_new_archive(tmp_path, monkeypatch):
    import templates
    store = TemplateStore(tmp_path)
    store.save('a', np.array([1]), {'version': 1})
    monkeypatch.setattr(templates.os, 'replace', lambda *args: (_ for _ in ()).throw(OSError('injected')))
    with pytest.raises(OSError): store.save('a', np.array([2]), {'version': 2})
    values, meta = TemplateStore(tmp_path).load('a')
    assert values.tolist() == [1] and meta['version'] == 1


@pytest.mark.parametrize('legacy', [True, False])
@pytest.mark.parametrize('point', ['before', 'after'])
def test_killed_writer_reopens_one_complete_generation(tmp_path, legacy, point):
    import os
    import subprocess
    import sys
    store = TemplateStore(tmp_path)
    if legacy:
        np.savez_compressed(tmp_path / 'a.npz', features=np.array([1]))
        (tmp_path / 'a.json').write_text('{"version":1}')
    else:
        store.save('a', np.array([1]), {'version': 1})
    script = '''
import os, signal, sys
import numpy as np
import templates
original = templates.os.replace
def stop(source, dest):
    if sys.argv[2] == 'after': original(source, dest)
    os.kill(os.getpid(), signal.SIGKILL)
templates.os.replace = stop
templates.TemplateStore(sys.argv[1]).save('a', np.array([2]), {'version':2})
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path), point], env=os.environ.copy())
    assert result.returncode < 0
    values, metadata = TemplateStore(tmp_path).load('a')
    expected = 1 if point == 'before' else 2
    assert values.tolist() == [expected] and metadata['version'] == expected
    assert TemplateStore(tmp_path).list_template_ids() == ['a']


@pytest.mark.parametrize('point', ['before', 'after'])
def test_killed_new_registration_is_absent_or_complete(tmp_path, point):
    import os
    import subprocess
    import sys
    script = '''
import os, signal, sys
import numpy as np
import templates
original = templates.os.replace
def stop(source, dest):
    if sys.argv[2] == 'after': original(source, dest)
    os.kill(os.getpid(), signal.SIGKILL)
templates.os.replace = stop
templates.TemplateStore(sys.argv[1]).save('new', np.array([2]), {'version':2})
'''
    result = subprocess.run([sys.executable, '-c', script, str(tmp_path), point], env=os.environ.copy())
    assert result.returncode < 0
    store = TemplateStore(tmp_path)
    if point == 'before':
        assert store.list_template_ids() == []
    else:
        values, metadata = store.load('new')
        assert values.tolist() == [2] and metadata['version'] == 2
        assert store.list_template_ids() == ['new']


@pytest.mark.parametrize('method', ['load', 'read_metadata'])
def test_archive_check_and_read_share_open_file(tmp_path, monkeypatch, method):
    import os
    import zipfile
    first = TemplateStore(tmp_path / 'first')
    second = TemplateStore(tmp_path / 'second')
    first.save('a', np.array([1]), {'version': 1})
    second.save('a', np.array([2]), {'version': 2})
    original = zipfile.ZipFile.infolist
    changed = False
    def replace_after_inspection(archive):
        nonlocal changed
        result = original(archive)
        if not changed:
            changed = True
            os.replace(second._atomic_path('a'), first._atomic_path('a'))
        return result
    monkeypatch.setattr(zipfile.ZipFile, 'infolist', replace_after_inspection)
    result = getattr(first, method)('a')
    if method == 'load':
        values, metadata = result
        assert values.tolist() == [1]
    else:
        metadata = result
    assert metadata['version'] == 1


def test_cross_format_delete_conflicts_leave_all_files_untouched(tmp_path):
    from lossless_template_store import LosslessTemplateStore
    store = TemplateStore(tmp_path)
    store.save('a', np.array([1]), {'version': 1})
    union = tmp_path / 'a.union2.npz'
    union.write_bytes(b'union-history')
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    with pytest.raises(ValueError): store.delete('a')
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    with pytest.raises(ValueError): LosslessTemplateStore(tmp_path).delete('a')
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before


def test_union_deletion_failure_preserves_archive(tmp_path, monkeypatch):
    from pathlib import Path
    from lossless_template_store import LosslessTemplateStore
    union = tmp_path / 'a.union2.npz'
    union.write_bytes(b'union-history')
    original = Path.unlink
    def fail_union(path, *args, **kwargs):
        if path == union: raise OSError('injected')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'unlink', fail_union)
    with pytest.raises(OSError): LosslessTemplateStore(tmp_path).delete('a')
    assert union.read_bytes() == b'union-history'
