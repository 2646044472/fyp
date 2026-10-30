from __future__ import annotations

import json
import math
import time
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any

import numpy as np

from biometric import score_probe
from models import IdentificationResult
from templates import TemplateStore


DEFAULT_POLICY = {"algorithm": "FastCC", "capture_profile": "rgb", "threshold": 0.28, "min_margin": 0.0, "frozen": False}


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_POLICY)
    policy_path = Path(path)
    if not policy_path.exists():
        return dict(DEFAULT_POLICY)
    policy = dict(DEFAULT_POLICY)
    policy.update(json.loads(policy_path.read_text(encoding="utf-8")))
    return policy


class Gallery:
    def __init__(self, store: TemplateStore, algorithm: Any, threshold: float | dict[str, Any] = 0.28, min_margin: float = 0.0, *, required_metadata: dict[str, Any] | None = None, acceptance_policy=None) -> None:
        if isinstance(threshold, dict):
            policy = threshold
            threshold = float(policy.get("threshold", 0.28))
            min_margin = float(policy.get("min_margin", 0.0))
        self.store = store
        self.algorithm = algorithm
        self.threshold = float(threshold)
        self.min_margin = float(min_margin)
        self.required_metadata = dict(required_metadata or {})
        self.acceptance_policy = acceptance_policy
        self._prepared_cache = OrderedDict()
        self._prepared_cache_bytes = 0
        self.prepared_cache_limit_bytes = getattr(algorithm, 'prepared_cache_limit_bytes', 64 * 1024 * 1024)
        self._prepared_cache_lock = threading.RLock()

    def _signature(self,user_id):
        return tuple((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
                     for s in (p.stat() for p in self.store.paths(user_id)))

    def _load_prepared(self,user_id):
        with self._prepared_cache_lock:
            return self._load_prepared_locked(user_id)

    def _load_prepared_locked(self,user_id):
        signature=self._signature(user_id)
        cached=self._prepared_cache.pop(user_id,None)
        if cached is not None:
            self._prepared_cache_bytes-=cached[3]
            if cached[0]==signature:
                self._prepared_cache[user_id]=cached
                self._prepared_cache_bytes+=cached[3]
                return cached[1],cached[2]
        features,metadata=self.store.load(user_id)
        # Validate metadata before preparing a potentially incompatible format.
        if any(metadata.get(k)!=v for k,v in self.required_metadata.items()):return None,metadata
        prepared=self.algorithm.prepare_enrollment(features)
        size=self.algorithm.prepared_bytes(prepared)
        if size<=self.prepared_cache_limit_bytes and signature==self._signature(user_id):
            while self._prepared_cache and self._prepared_cache_bytes+size>self.prepared_cache_limit_bytes:
                _,entry=self._prepared_cache.popitem(last=False);self._prepared_cache_bytes-=entry[3]
            self._prepared_cache[user_id]=(signature,prepared,metadata,size)
            self._prepared_cache_bytes+=size
        return prepared,metadata

    @property
    def size(self) -> int:
        return len(self.store.list_users())

    def warm_up(self, capture_profile="noir-ir"):
        """Build optional cross-user search indexes before accepting queries."""
        if not hasattr(self.algorithm, 'prepare_gallery'):
            return
        groups = {}
        for user_id in self.store.list_users():
            features, metadata = self._load_prepared(user_id)
            if metadata.get('capture_profile') != capture_profile:
                continue
            if any(metadata.get(k) != v for k,v in self.required_metadata.items()):
                continue
            groups[user_id] = features
        self.algorithm.prepare_gallery(groups)

    def identify(self, probe_feature: np.ndarray, capture_profile: str = "rgb") -> IdentificationResult:
        started = time.perf_counter()
        ranked: list[tuple[float, str]] = []
        incompatible = False
        users=self.store.list_users()
        with self._prepared_cache_lock:
            for stale in set(self._prepared_cache)-set(users):
                self._prepared_cache_bytes-=self._prepared_cache.pop(stale)[3]
        prepared_mode=all(hasattr(self.algorithm,k) for k in ('prepare_probe','prepare_enrollment','prepared_bytes','score_prepared'))
        prepared_probe=self.algorithm.prepare_probe(probe_feature) if prepared_mode else None
        global_mode = prepared_mode and hasattr(self.algorithm, 'score_gallery')
        groups = {}
        for user_id in users:
            try:
                features, metadata = self._load_prepared(user_id) if prepared_mode else self.store.load(user_id)
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                continue
            if metadata.get("capture_profile") != capture_profile:
                continue
            if any(metadata.get(key) != value for key, value in self.required_metadata.items()):
                incompatible = True
                continue
            if global_mode:
                groups[user_id] = features
                continue
            score=self.algorithm.score_prepared(prepared_probe,features) if prepared_mode else score_probe(self.algorithm, probe_feature, features)
            ranked.append((float(score), user_id))
        if global_mode and groups:
            ranked.extend((float(score),user_id) for user_id,score in self.algorithm.score_gallery(prepared_probe,groups).items())
        if any(not math.isfinite(score) for score, user_id in ranked):
            return IdentificationResult("RETRY", None, None, None, (time.perf_counter() - started) * 1000, "INVALID_MATCH_SCORES")
        ranked.sort(key=lambda item: item[0])
        elapsed = (time.perf_counter() - started) * 1000
        if not ranked:
            return IdentificationResult("UNKNOWN", None, None, None, elapsed, "INCOMPATIBLE_TEMPLATES" if incompatible else "NO_ENROLLED_USERS")
        best, user_id = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else None
        if best > self.threshold:
            return IdentificationResult("UNKNOWN", None, best, second, elapsed, "SCORE_ABOVE_THRESHOLD")
        if second is not None and self.min_margin > 0 and second - best < self.min_margin:
            return IdentificationResult("RETRY", None, best, second, elapsed, "AMBIGUOUS_MARGIN")
        if self.acceptance_policy is not None:
            rejection = self.acceptance_policy.rejection(best, second, getattr(prepared_probe, 'route', None))
            if rejection is not None:
                status, reason = rejection
                return IdentificationResult(status, None, best, second, elapsed, reason)
        return IdentificationResult("MATCH", user_id, best, second, elapsed)
