"""Opt-in exact fallback reuse with query-local shared input snapshots.

Operation identity and complete input validation are unchanged. Equal inputs may
share one immutable validation snapshot across different operation entries;
output snapshots remain separate. All retained array bytes, including inputs
leased by concurrent operations, stay inside the original 256 MiB budget.
This changes storage only, and does not imply any measured Pi speed gain.
"""

from dataclasses import dataclass

import numpy as np

from lazy_cached_matcher import ExactQueryReuse, LazyCachedRetainedMatcher, _bytes, _clone


@dataclass(eq=False)
class _InputSnapshot:
    key: bytes
    array: np.ndarray
    references: int = 1


class SharedSnapshotQueryReuse(ExactQueryReuse):
    """Share exact immutable inputs without sharing operations or answers.

The pool and operation cache live for one exhaustive query only. Hashes select
candidate buckets; dtype, shape and complete array equality always validate a
hit. Reference counts include in-flight operations so concurrent misses cannot
evade the byte budget or delete a snapshot another operation still needs.
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._input_pool = {}
        self._input_bytes = self._output_bytes = 0
        self._snapshot_reuses = self._snapshot_copies = self._snapshot_collisions = 0

    @staticmethod
    def _same(arrays, snapshots):
        if not ExactQueryReuse._same(arrays, snapshots):
            return False
        # Numerical equality alone treats +0.0 and -0.0 as equal. If a digest
        # collides, retain exact byte equality even for sign-sensitive kernels.
        return all(np.array_equal(
            np.ascontiguousarray(array).view(np.uint8).reshape(-1),
            np.ascontiguousarray(snapshot).view(np.uint8).reshape(-1))
            for array, snapshot in zip(arrays, snapshots))

    def _release_inputs(self, snapshots):
        # The caller holds _lock. One reference belongs to each argument slot,
        # even when two argument slots point at the same immutable snapshot.
        for snapshot in snapshots:
            snapshot.references -= 1
            if snapshot.references == 0:
                bucket = self._input_pool[snapshot.key]
                bucket.remove(snapshot)
                if not bucket:
                    del self._input_pool[snapshot.key]
                self._input_bytes -= snapshot.array.nbytes
                self._stored_bytes -= snapshot.array.nbytes

    def _lease_inputs(self, arrays, keys):
        # The caller holds _lock. Partial leases are rolled back on every exit.
        leased = []
        try:
            for array, key in zip(arrays, keys):
                bucket = self._input_pool.get(key, ())
                existing = next((entry for entry in bucket
                                 if self._same((array,), (entry.array,))), None)
                if existing is not None:
                    existing.references += 1
                    self._snapshot_reuses += 1
                    leased.append(existing)
                    continue
                if bucket:
                    self._snapshot_collisions += 1
                if not self._reserve(array.nbytes):
                    self._release_inputs(leased)
                    return None
                try:
                    copied = array.copy()
                    copied.flags.writeable = False
                    snapshot = _InputSnapshot(key, copied)
                    self._input_pool.setdefault(key, []).append(snapshot)
                    leased.append(snapshot)
                    self._input_bytes += copied.nbytes
                    self._stored_bytes += copied.nbytes
                    self._snapshot_copies += 1
                finally:
                    self._reserved_bytes -= array.nbytes
            return tuple(leased)
        except BaseException:
            self._release_inputs(leased)
            raise

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
        # Hash every complete input once. These same content keys select both
        # the operation entry and the shared snapshot buckets; no second pass
        # over all descriptor bytes is needed for snapshot pooling.
        input_keys = tuple(self.fingerprint((array,)) for array in arrays)
        key = (label, id(function), input_keys)
        leases = None
        with self._lock:
            cached = self._entries.get(key)
            if cached is not None:
                if cached[0] is function and self._same(arrays, cached[1]):
                    self._counts[label]["hits"] += 1
                    return _clone(cached[2])
                self._collisions += 1
            self._counts[label]["misses"] += 1
            # A colliding result never replaces the existing operation entry.
            may_store = cached is None and not self._closed and self.limit_bytes > 0
        if may_store:
            with self._lock:
                if not self._closed and key not in self._entries:
                    leases = self._lease_inputs(arrays, input_keys)
                    if leases is None:
                        self._skipped_budget += 1
        elif cached is None and not self._closed:
            with self._lock:
                self._skipped_budget += 1
        try:
            result = function(*args, **kwargs)
            if leases is not None:
                snapshots = tuple(entry.array for entry in leases)
                if self._same(arrays, snapshots):
                    try:
                        result_bytes = _bytes(result)
                    except TypeError:
                        return result
                    with self._lock:
                        if key not in self._entries and self._reserve(result_bytes):
                            try:
                                copied = _clone(result)
                                self._entries[key] = (function, snapshots, copied, leases)
                                self._stored_bytes += result_bytes
                                self._output_bytes += result_bytes
                                # Transfer lease ownership to this cache entry.
                                leases = None
                            finally:
                                self._reserved_bytes -= result_bytes
            return result
        finally:
            if leases is not None:
                with self._lock:
                    self._release_inputs(leases)

    def close(self):
        with self._lock:
            self._closed = True
            for cached in self._entries.values():
                self._release_inputs(cached[3])
            self._entries.clear()
            self._stored_bytes -= self._output_bytes
            self._output_bytes = 0
            # Pending operations retain their accounted leases until their
            # finally blocks run. The matcher drains workers before close().

    def stats(self):
        with self._lock:
            return dict(super().stats(), shared_input_bytes=self._input_bytes,
                        cached_output_bytes=self._output_bytes,
                        input_snapshots=sum(map(len, self._input_pool.values())),
                        snapshot_reuses=self._snapshot_reuses,
                        snapshot_copies=self._snapshot_copies,
                        snapshot_hash_collisions=self._snapshot_collisions)


class SharedSnapshotLazyMatcher(LazyCachedRetainedMatcher):
    """V28 operations and gates, with a different bounded cache storage policy."""

    name = "FastCCSharedLazy-v30-experimental"
    magic = LazyCachedRetainedMatcher.magic
    query_reuse_factory = SharedSnapshotQueryReuse
