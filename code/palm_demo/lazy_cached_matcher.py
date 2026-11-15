"""Instance-local exact reuse, enabled only inside the full-query fallback.

This integrates the historical exact-input reuse idea without installing a
global profiler or hashing confident queries. It changes no ROI, candidate,
distance, gate or enrollment aggregation. Pi speed gains require validation.
"""

from __future__ import annotations

import hashlib
import threading
import time
from concurrent.futures import wait

import numpy as np

from retained_evidence_matcher import RetainedCompNetAlternateROIMatcher


DEFAULT_REUSE_BYTES = 256 * 1024 * 1024
_MISSING = object()


def _clone(value):
    if isinstance(value, np.ndarray):
        return value.copy()
    if isinstance(value, tuple):
        return tuple(_clone(item) for item in value)
    if isinstance(value, list):
        return [_clone(item) for item in value]
    if value is None or np.isscalar(value):
        return value
    raise TypeError("Unsupported exact-reuse output")


def _bytes(value):
    if isinstance(value, np.ndarray):
        return value.nbytes
    if isinstance(value, (tuple, list)):
        return sum(_bytes(item) for item in value)
    if value is None or np.isscalar(value):
        return 0
    raise TypeError("Unsupported exact-reuse output")


class ExactQueryReuse:
    """A bounded cache of pure operations, never query identities or answers."""

    def __init__(self, limit_bytes=DEFAULT_REUSE_BYTES):
        if type(limit_bytes) is not int or limit_bytes < 0:
            raise ValueError("Expected a non-negative exact-reuse byte budget")
        self.limit_bytes = limit_bytes
        self._lock = threading.RLock()
        self._entries = {}
        self._stored_bytes = self._reserved_bytes = self._peak_bytes = 0
        self._closed = False
        self._counts = {label: dict(calls=0, hits=0, misses=0)
                        for label in ("sift", "registration")}
        self._skipped_budget = self._collisions = 0

    @staticmethod
    def fingerprint(arrays):
        digest = hashlib.sha256()
        for array in arrays:
            header = repr((array.shape, array.dtype.str)).encode("ascii")
            digest.update(len(header).to_bytes(8, "little"))
            digest.update(header)
            contiguous = np.ascontiguousarray(array)
            if contiguous.nbytes:
                digest.update(memoryview(contiguous).cast("B"))
        return digest.digest()

    @staticmethod
    def _same(arrays, snapshots):
        return len(arrays) == len(snapshots) and all(
            a.shape == b.shape and a.dtype == b.dtype and np.array_equal(a, b)
            for a, b in zip(arrays, snapshots))

    def _reserve(self, count):
        if self._closed or self._stored_bytes + self._reserved_bytes + count > self.limit_bytes:
            return False
        self._reserved_bytes += count
        self._peak_bytes = max(self._peak_bytes, self._stored_bytes + self._reserved_bytes)
        return True

    def call(self, label, function, arrays, args, kwargs=None):
        kwargs = kwargs or {}
        with self._lock:
            closed = self._closed
            if not closed:
                self._counts[label]["calls"] += 1
        if closed:
            return function(*args, **kwargs)
        arrays = tuple(np.asarray(array) for array in arrays)
        if any(array.dtype.hasobject for array in arrays):
            return function(*args, **kwargs)
        key = (label, id(function), self.fingerprint(arrays))
        snapshots = None
        reserved = 0
        snapshot_allowed = False
        with self._lock:
            cached = self._entries.get(key)
            if cached is not None:
                if cached[0] is function and self._same(arrays, cached[1]):
                    self._counts[label]["hits"] += 1
                    return _clone(cached[2])
                self._collisions += 1
            self._counts[label]["misses"] += 1
            count = sum(array.nbytes for array in arrays)
            if cached is None and self.limit_bytes > 0 and self._reserve(count):
                reserved = count
                snapshot_allowed = True
            else:
                self._skipped_budget += cached is None
        try:
            if snapshot_allowed:
                snapshots = tuple(array.copy() for array in arrays)
            # Expensive SIFT/native/RANSAC operations run outside the cache lock.
            result = function(*args, **kwargs)
            if snapshots is not None and self._same(arrays, snapshots):
                try:
                    result_bytes = _bytes(result)
                except TypeError:
                    return result
                with self._lock:
                    if key not in self._entries and self._reserve(result_bytes):
                        reserved += result_bytes
                        # Cloning under the lock is a memory copy, not a kernel.
                        copied = _clone(result)
                        # Keep the callable alive, so an object-ID cannot be
                        # reused for a different operation in this query.
                        self._entries[key] = (function, snapshots, copied)
                        self._reserved_bytes -= reserved
                        self._stored_bytes += reserved
                        reserved = 0
            return result
        finally:
            with self._lock:
                self._reserved_bytes -= reserved

    def close(self):
        with self._lock:
            self._closed = True
            self._entries.clear()
            self._stored_bytes = 0

    def stats(self):
        with self._lock:
            return dict(activated=True, limit_bytes=self.limit_bytes,
                        peak_bytes=self._peak_bytes, stored_bytes=self._stored_bytes,
                        entries=len(self._entries),
                        **{label: dict(value) for label, value in self._counts.items()},
                        skipped_budget=self._skipped_budget, collisions=self._collisions)


class _TrackedExecutor:
    """Drain fallback jobs before restoring attributes, including on failure."""

    def __init__(self, executor):
        self.executor = executor
        self.futures = []
        self.lock = threading.Lock()

    def submit(self, function, *args, **kwargs):
        future = self.executor.submit(function, *args, **kwargs)
        with self.lock:
            self.futures.append(future)
        return future

    def map(self, function, *iterables, timeout=None, chunksize=1):
        deadline = None if timeout is None else time.monotonic() + timeout
        futures = [self.submit(function, *args) for args in zip(*iterables)]
        def results():
            try:
                for future in futures:
                    yield future.result(None if deadline is None else max(0, deadline-time.monotonic()))
            finally:
                for future in futures:
                    future.cancel()
        return results()

    def drain(self, cancel=False):
        with self.lock:
            futures = list(self.futures)
        if cancel:
            for future in futures:
                future.cancel()
        # wait does not replace the original failure with a later worker error.
        wait(futures)

    def __getattr__(self, name):
        return getattr(self.executor, name)


class _RegistrationReuse:
    def __init__(self, memo, function):
        self.memo, self.function = memo, function

    def __call__(self, left, right):
        return self.memo.call("registration", self.function, (*left, *right), (left, right))

    def __getattr__(self, name):
        return getattr(self.function, name)


class LazyCachedRetainedMatcher(RetainedCompNetAlternateROIMatcher):
    """Opt-in lazy reuse; its packed byte format remains v26/v27-compatible."""

    name = "FastCCLazyRetained-v28-experimental"
    magic = RetainedCompNetAlternateROIMatcher.magic
    exact_reuse_limit_bytes = DEFAULT_REUSE_BYTES
    query_reuse_factory = ExactQueryReuse

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lazy_query_lock = threading.RLock()
        self._lazy_query_active = False

    def score_gallery(self, probe, groups):
        with self._lazy_query_lock:
            if self._lazy_query_active:
                raise RuntimeError("Recursive scoring cannot share a fallback reuse scope")
            self._lazy_query_active = True
            original_callback = getattr(probe, "exhaustive", None)
            own_callback = vars(probe).get("exhaustive", _MISSING)
            saved = []
            memo = tracker = None
            succeeded = False

            def replace(owner, name, value):
                saved.append((owner, name, vars(owner).get(name, _MISSING)))
                setattr(owner, name, value)

            def exhaustive():
                nonlocal memo, tracker
                if memo is None:
                    memo = self.query_reuse_factory(self.exact_reuse_limit_bytes)
                    tracker = _TrackedExecutor(self._workers)
                    replace(self, "_workers", tracker)
                    for owner in (self, self.legacy):
                        function = owner.local_features
                        def features(pixels, _function=function):
                            return memo.call("sift", _function, (pixels,), (pixels,))
                        replace(owner, "local_features", features)
                        replace(owner, "registration", _RegistrationReuse(memo, owner.registration))
                return original_callback()

            if callable(original_callback):
                probe.exhaustive = exhaustive
            try:
                result = super().score_gallery(probe, groups)
                succeeded = True
                return result
            finally:
                try:
                    if tracker is not None:
                        tracker.drain(cancel=not succeeded)
                finally:
                    for owner, name, value in reversed(saved):
                        if value is _MISSING:
                            delattr(owner, name)
                        else:
                            setattr(owner, name, value)
                    if own_callback is _MISSING:
                        if callable(original_callback):
                            delattr(probe, "exhaustive")
                    else:
                        probe.exhaustive = own_callback
                    if memo is not None:
                        memo.close()
                        probe.exhaustive_reuse_stats = memo.stats()
                    else:
                        probe.exhaustive_reuse_stats = dict(activated=False,
                            limit_bytes=self.exact_reuse_limit_bytes, peak_bytes=0,
                            stored_bytes=0, entries=0,
                            sift=dict(calls=0, hits=0, misses=0),
                            registration=dict(calls=0, hits=0, misses=0),
                            skipped_budget=0, collisions=0)
                    self._lazy_query_active = False


class BlockConsensusLazyRetainedMatcher(LazyCachedRetainedMatcher):
    """Opt-in v31 pipeline using the same stages with block-consensus FastCC."""

    name = "FastCCBlockConsensus-v31-experimental"


class Top3ConsensusLazyRetainedMatcher(LazyCachedRetainedMatcher):
    """Opt-in v32 pipeline requiring support from three enrollment frames."""

    name = "FastCCTop3Consensus-v32-experimental"

    @staticmethod
    def _aggregate(pair_scores):
        """Average up to the three best frame scores, not only the best two."""
        scores = sorted(float(value) for value in pair_scores)
        if not scores:
            raise ValueError("Cannot aggregate an empty frame score set")
        return float(np.mean(scores[:3]))
