"""Read-only parent trees and explicitly linked journal segments (no inference)."""
import ctypes
import os
from pathlib import Path
import sys

from smpd_run_journal import atomic, digest, file_sha, load


_protected = []
_installed = False


def _deny_parent_write(event, args):
    if not _protected:
        return
    paths = []
    if event == 'open':
        path, mode, flags = args
        if isinstance(path, int):
            return  # Existing descriptors are also restricted by Windows handles.
        if any(c in (mode or '') for c in 'wax+') or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            paths = [path]
    elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.chown', 'os.utime', 'os.truncate'):
        paths = [args[0]]
    elif event in ('os.rename', 'os.link', 'os.symlink'):
        paths = list(args[:2])
    for path in paths:
        if isinstance(path, (str, bytes, os.PathLike)):
            resolved = Path(os.fsdecode(path)).resolve()
            if any(resolved == root or resolved.is_relative_to(root) for root in _protected):
                raise PermissionError('Immutable parent write blocked: ' + str(resolved))


def tree_paths(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Read-only tree missing')
    paths = [root] + sorted(root.rglob('*'))
    for path in paths:
        if path.is_symlink() or getattr(path.stat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('Reparse/symlink not allowed in immutable tree: ' + str(path))
    return paths


def tree_stamps(root):
    result = {}
    for path in tree_paths(root):
        stat = path.stat()
        result[path.relative_to(root).as_posix()] = [stat.st_dev, stat.st_ino, stat.st_size,
                                                   stat.st_mtime_ns, stat.st_ctime_ns]
    return result


class ReadOnlyTree:
    """Windows deny-write/delete handles plus a Python mutation audit guard.

    No ACL or file attributes are changed. Existing file contents and directory
    generations are checked; a new/missing entry also invalidates the tree.
    """
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.handles = []
        self.stamps = None

    def __enter__(self):
        global _installed
        if os.name != 'nt':
            raise RuntimeError('This frozen Windows continuation requires Windows deny-write handles')
        from ctypes import wintypes
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        self.kernel.CreateFileW.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        paths = tree_paths(self.root)
        before = tree_stamps(self.root)
        try:
            for path in paths:
                handle = self.kernel.CreateFileW(str(path), 0x80000000, 1, None, 3,
                    0x02000000 if path.is_dir() else 0x80, None)
                if handle == ctypes.c_void_p(-1).value:
                    raise ctypes.WinError(ctypes.get_last_error())
                self.handles.append(handle)
            if not _installed:
                sys.addaudithook(_deny_parent_write)
                _installed = True
            _protected.append(self.root)
            self.stamps = before
            self.verify()
            return self
        except BaseException:
            self.close()
            raise

    def verify(self):
        if tree_stamps(self.root) != self.stamps:
            raise ValueError('Immutable tree entries/file identity changed: ' + str(self.root))

    def inventory(self):
        self.verify()
        value = {p.relative_to(self.root).as_posix(): {'bytes': p.stat().st_size, 'sha256': file_sha(p)}
                 for p in tree_paths(self.root) if p.is_file()}
        self.verify()
        return value

    def close(self):
        if self.root in _protected:
            _protected.remove(self.root)
        for handle in reversed(self.handles):
            self.kernel.CloseHandle(handle)
        self.handles.clear()

    def __exit__(self, *args):
        try:
            self.verify()
        finally:
            self.close()


def read_chain(folder, stage, fingerprint, rows, *, start=0, previous=None):
    """Validate original schemas and global ordinals without mkdir or writes."""
    samples = [row['sample'] for row in rows]
    if len(samples) != len(set(samples)):
        raise ValueError('Duplicate sample in frozen rows')
    records = []
    for sequence, path in enumerate(sorted(Path(folder).glob('*.json')), start):
        if sequence >= len(rows) or path.name != f'{sequence:05d}.json':
            raise ValueError('Journal gap, overlap or extra record')
        record = load(path)
        expected = dict(sequence=sequence, stage=stage, run_fingerprint=fingerprint,
                        previous_record_sha256=previous, sample=samples[sequence])
        if any(record.get(k) != v for k, v in expected.items()):
            raise ValueError('Journal fingerprint/order/sample/chain mismatch')
        if record.get('record_sha256') != digest({k:v for k,v in record.items() if k != 'record_sha256'}):
            raise ValueError('Journal record digest mismatch')
        validate_input(record['payload'], rows[sequence])
        records.append(record)
        previous = record['record_sha256']
    return records


def validate_input(payload, row):
    if (payload.get('source_sha256') != row['sha256']
            or payload.get('capture', {}).get('input_sha256') != row['sha256']):
        raise ValueError('Journal source/captured input hash mismatch')


class SegmentJournal:
    """Parent bytes keep their fingerprint; only the new segment gets a new one."""
    def __init__(self, root, stage, fingerprint, rows, parent_records):
        self.root, self.stage, self.fingerprint = Path(root), stage, fingerprint
        self.rows, self.samples = rows, [r['sample'] for r in rows]
        if len(self.samples) != len(set(self.samples)):
            raise ValueError('Duplicate expected sample')
        self.folder = self.root / 'records' / stage
        self.parent_count = len(parent_records)
        if stage == 'enrollment':
            if self.parent_count != len(rows) or list(self.folder.glob('*.json')):
                raise ValueError('Registration must be inherited exactly once')
            self.records = list(parent_records)
        else:
            previous = parent_records[-1]['record_sha256'] if parent_records else None
            suffix = read_chain(self.folder, stage, fingerprint, rows,
                                start=self.parent_count, previous=previous)
            self.records = list(parent_records) + suffix

    @property
    def previous(self):
        return self.records[-1]['record_sha256'] if self.records else None

    def append(self, sample, payload):
        index = len(self.records)
        if self.stage != 'query' or index >= len(self.rows) or sample != self.samples[index]:
            raise ValueError('Append must be next uncommitted global query')
        validate_input(payload, self.rows[index])
        record = dict(sequence=index, stage=self.stage, run_fingerprint=self.fingerprint,
                      previous_record_sha256=self.previous, sample=sample, payload=payload)
        record['record_sha256'] = digest(record)
        atomic(self.folder / f'{index:05d}.json', record, exclusive=True)
        self.records.append(record)
        return record


def verify_inventory(root, expected):
    actual = {p.relative_to(root).as_posix(): {'bytes':p.stat().st_size, 'sha256':file_sha(p)}
              for p in tree_paths(root) if p.is_file()}
    if actual != expected:
        raise ValueError('Immutable parent byte inventory mismatch')
    return digest(actual)
