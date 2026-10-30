"""Durable version-bound records for the isolated public evaluation (stdlib only)."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import time
import uuid


_REPLACE_RETRY_DELAYS = (.05, .1, .2, .4, .8)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def atomic(path, value, *, exclusive=False):
    """Publish complete JSON; bound retries for Windows access-denied replaces."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive and path.exists():
        raise FileExistsError(path)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('xb') as stream:
            stream.write(canonical(value) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(len(_REPLACE_RETRY_DELAYS) + 1):
            if exclusive and path.exists():
                raise FileExistsError(path)
            try:
                os.replace(temp, path)
                break
            except OSError as error:
                # Access denial can be transient, but is not assumed to be so.
                # Keep the same flushed file and never fall back to in-place writes.
                if getattr(error, 'winerror', None) != 5:
                    raise
                if attempt == len(_REPLACE_RETRY_DELAYS):
                    raise
                time.sleep(_REPLACE_RETRY_DELAYS[attempt])
    finally:
        temp.unlink(missing_ok=True)


def inside(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Artifact path outside candidate root: ' + str(path))
    return path


@contextmanager
def run_lock(root):
    """Kernel-held lock; a stale PID/file never prevents a legitimate restart."""
    path = Path(root) / 'runner.lock'
    with path.open('a+b') as stream:
        stream.seek(0, 2)
        if stream.tell() == 0:
            stream.write(b'0'); stream.flush()
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == 'nt':
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


class Journal:
    def __init__(self, root, stage, fingerprint, samples):
        self.root = Path(root)
        self.folder = self.root / 'records' / stage
        self.folder.mkdir(parents=True, exist_ok=True)
        self.fingerprint, self.stage, self.samples = fingerprint, stage, list(samples)
        if len(self.samples) != len(set(self.samples)):
            raise ValueError('Duplicate expected sample')
        self.records = []
        for index, path in enumerate(sorted(self.folder.glob('*.json'))):
            if index >= len(self.samples) or path.name != f'{index:05d}.json':
                raise ValueError('Record sequence gap/extra record')
            record = load(path)
            unsigned = {k: v for k, v in record.items() if k != 'record_sha256'}
            if record.get('record_sha256') != digest(unsigned):
                raise ValueError('Record digest mismatch')
            expected = dict(sequence=index, stage=stage, run_fingerprint=fingerprint,
                            previous_record_sha256=self.previous, sample=self.samples[index])
            if any(record.get(k) != v for k, v in expected.items()):
                raise ValueError('Not an exact same-version ordered prefix')
            self.records.append(record)

    @property
    def previous(self):
        return self.records[-1]['record_sha256'] if self.records else None

    def append(self, sample, payload):
        index = len(self.records)
        if index >= len(self.samples) or sample != self.samples[index]:
            raise ValueError('Append must be next fixed sample')
        record = dict(sequence=index, stage=self.stage, run_fingerprint=self.fingerprint,
                      previous_record_sha256=self.previous, sample=sample, payload=payload)
        record['record_sha256'] = digest(record)
        atomic(self.folder / f'{index:05d}.json', record, exclusive=True)
        self.records.append(record)
        return record


def recover_inflight(root, journals):
    """Keep interrupted attempts, including commit-before-marker-clear crashes."""
    root = Path(root)
    marker = root / 'inflight.json'
    if not marker.exists():
        return
    value = load(marker)
    journal = journals[value['stage']]
    if value['run_fingerprint'] != journal.fingerprint:
        raise ValueError('Inflight version mismatch')
    index = value['sequence']
    if index >= len(journal.samples) or journal.samples[index] != value['sample']:
        raise ValueError('Inflight sample mismatch')
    committed = index < len(journal.records)
    if index > len(journal.records) or (committed and index != len(journal.records)-1):
        raise ValueError('Inflight marker is not at journal boundary')
    receipt = dict(value, recovered_unix=time.time(), already_committed=committed,
                   action='preserve committed record' if committed else 'retry only this uncommitted attempt')
    target = root / 'interruptions' / (value['attempt_id'] + '.json')
    if not target.exists():
        atomic(target, receipt, exclusive=True)
    marker.unlink()


def begin_attempt(root, journal, epoch):
    index = len(journal.records)
    value = dict(stage=journal.stage, run_fingerprint=journal.fingerprint, sequence=index,
                 sample=journal.samples[index], epoch=epoch, started_unix=time.time(),
                 attempt_id=uuid.uuid4().hex)
    atomic(Path(root) / 'inflight.json', value, exclusive=True)
    return value
