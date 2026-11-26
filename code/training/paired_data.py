"""Local-only crop and step contract shared by portable recognizer trainers."""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from private_paths import outside_git


def _require(flag, message):
    if not flag:
        raise ValueError(message)


def _ids(values, length=None):
    a = np.asarray(values)
    _require(a.ndim == 1 and a.dtype.kind in "iuU", "expected 1-D integer or Unicode labels")
    _require(length is None or len(a) == length, "unaligned metadata")
    if a.dtype.kind == "U":
        _require(np.all(np.char.str_len(np.char.strip(a)) > 0), "empty identity or source label")
    return a


def _ints(values, name, dims):
    a = np.asarray(values)
    _require(a.ndim == dims and a.dtype.kind in "iu", "invalid integer scheduling array: " + name)
    if a.dtype.kind == "u":
        _require(a.size == 0 or a.max() <= np.iinfo(np.int64).max, "integer overflow")
    return a.astype(np.int64, copy=False)


@dataclass(frozen=True)
class PairedStep:
    source: int
    rows: np.ndarray
    valid: np.ndarray
    labels: np.ndarray


class PairedData:
    def __init__(self, gray, source, person, palm, capture, batches, pair_count, epoch_start,
                 holdout_person=None, holdout_capture=None):
        gray = np.asarray(gray)
        _require(gray.dtype == np.uint8 and gray.ndim == 3 and gray.shape[1:] == (128, 128)
                 and len(gray) > 0, "gray must be uint8[N,128,128]")
        n = len(gray)
        source, person, palm, capture = (_ids(x, n) for x in (source, person, palm, capture))
        _require(len(np.unique(capture)) == n, "reuse of one physical capture")
        fields = (person, capture)
        for current, holdout in zip(fields, (holdout_person, holdout_capture)):
            if holdout is not None:
                _require(not set(current.astype(str)) & set(_ids(holdout).astype(str)),
                         "overlap between FIT and holdout metadata")
        # Each input must be a real useful crop; no fabricated valid placeholders.
        _require(np.all(gray.max(axis=(1, 2)) > gray.min(axis=(1, 2))), "invalid constant crop")
        self.gray = gray
        _, self._source = np.unique(source, return_inverse=True)
        self._label = np.empty(n, dtype=np.int64)
        class_sizes = []
        for d in np.unique(self._source):
            ix = np.flatnonzero(self._source == d)
            owners = {}
            labels = {}
            for i in ix:
                key = palm[i].item()
                who = person[i].item()
                _require(owners.setdefault(key, who) == who, "one source-local palm has two owners")
                self._label[i] = labels.setdefault(key, len(labels))
            _require(len(labels) > 1, "a source needs at least two enrolled palms for its proxies")
            class_sizes.append(len(labels))
        self.class_counts = tuple(class_sizes)
        self._person = person
        self.batches = _ints(batches, "batches", 3)
        self.pair_count = _ints(pair_count, "pair_count", 1)
        self.epoch_start = _ints(epoch_start, "epoch_start", 1)
        e, two, maxp = self.batches.shape
        _require(e > 0 and two == 2 and 1 <= maxp <= 12 and len(self.pair_count) == e
                 and np.all((1 <= self.pair_count) & (self.pair_count <= maxp)), "invalid pair width")
        _require(len(self.epoch_start) >= 2 and self.epoch_start[0] == 0
                 and self.epoch_start[-1] == e and np.all(np.diff(self.epoch_start) > 0),
                 "epoch_start must divide all steps into nonempty epochs")
        # Validate each planned step before starting any work; no quiet resampling.
        for i in range(e):
            self.step(i)

    def step(self, i):
        p = int(self.pair_count[i])
        slots = self.batches[i, :, :p]
        _require(np.all(self.batches[i, :, p:] == -1)
                 and np.all((slots >= -1) & (slots < len(self.gray)))
                 and np.all(slots[0] >= 0), "invalid slot or padding")
        valid = slots >= 0
        rows = slots[valid]
        _require(len(np.unique(rows)) == len(rows), "duplicate capture rows within a step")
        s = int(self._source[rows[0]])
        _require(np.all(self._source[rows] == s), "cross-source supervision within a step")
        _require(len(np.unique(self._person[slots[0]])) == p, "two anchors share a person")
        labels = np.full(slots.shape, -1, dtype=np.int64)
        labels[valid] = self._label[rows]
        positive = valid[1]
        _require(np.all(labels[0, positive] == labels[1, positive]), "positive is not the same palm")
        return PairedStep(s, rows, valid, labels)


def load_paired(path):
    """Open one caller-owned local NPZ; object arrays and unknown fields are rejected."""
    p = Path(path)
    _require(p.suffix.casefold() == ".npz" and p.is_file() and outside_git(p), "expected local .npz FIT input")
    required = {"gray", "source", "person", "palm", "capture", "batches", "pair_count", "epoch_start"}
    optional = {"holdout_person", "holdout_capture"}
    with np.load(p, allow_pickle=False) as a:
        _require(required <= set(a.files) <= required | optional and len(set(a.files)) == len(a.files),
                 "wrong or duplicate NPZ training fields")
        return PairedData(**{k: a[k] for k in a.files})


def synthetic_paired():
    """One full optimizer step per epoch, two epochs to test the thaw gate."""
    rng = np.random.default_rng(3)
    noise = rng.integers(0, 256, (4, 128, 128), dtype=np.uint8)
    return PairedData(noise, np.zeros(4, dtype=int),
                      np.array([0, 0, 1, 1]), np.array([0, 0, 1, 1]), np.arange(4),
                      np.array([[[0, 2], [1, 3]], [[1, 3], [0, 2]]]),
                      np.array([2, 2]), np.array([0, 1, 2]))
