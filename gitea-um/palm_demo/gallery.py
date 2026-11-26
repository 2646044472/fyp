from __future__ import annotations

import json
import time
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
    def __init__(self, store: TemplateStore, algorithm: Any, threshold: float | dict[str, Any] = 0.28, min_margin: float = 0.0) -> None:
        if isinstance(threshold, dict):
            policy = threshold
            threshold = float(policy.get("threshold", 0.28))
            min_margin = float(policy.get("min_margin", 0.0))
        self.store = store
        self.algorithm = algorithm
        self.threshold = float(threshold)
        self.min_margin = float(min_margin)

    @property
    def size(self) -> int:
        return len(self.store.list_users())

    def identify(self, probe_feature: np.ndarray, capture_profile: str = "rgb") -> IdentificationResult:
        started = time.perf_counter()
        ranked: list[tuple[float, str]] = []
        for user_id in self.store.list_users():
            try:
                features, metadata = self.store.load(user_id)
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                continue
            if metadata.get("capture_profile") != capture_profile:
                continue
            ranked.append((score_probe(self.algorithm, probe_feature, features), user_id))
        ranked.sort(key=lambda item: item[0])
        elapsed = (time.perf_counter() - started) * 1000
        if not ranked:
            return IdentificationResult("UNKNOWN", None, None, None, elapsed, "NO_ENROLLED_USERS")
        best, user_id = ranked[0]
        second = ranked[1][0] if len(ranked) > 1 else None
        if best > self.threshold:
            return IdentificationResult("UNKNOWN", None, best, second, elapsed, "SCORE_ABOVE_THRESHOLD")
        if second is not None and self.min_margin > 0 and second - best < self.min_margin:
            return IdentificationResult("RETRY", None, best, second, elapsed, "AMBIGUOUS_MARGIN")
        return IdentificationResult("MATCH", user_id, best, second, elapsed)
