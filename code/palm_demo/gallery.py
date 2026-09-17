"""1:N palm identification over stored feature templates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

import numpy as np

from templates import TemplateStore


class ScoreDirection(str, Enum):
    """How a matcher score ranks similarity."""

    SIMILARITY = "similarity"  # larger is better
    DISTANCE = "distance"  # smaller is better


@dataclass(frozen=True)
class IdentificationResult:
    status: str
    user_id: str | None
    score: float | None
    second_score: float | None = None


def _score(matcher: Any, query: np.ndarray, template: np.ndarray) -> float:
    match = matcher.match if hasattr(matcher, "match") else matcher
    value = float(match(query, template))
    if not math.isfinite(value):
        raise ValueError("matcher returned a non-finite score")
    # Stable display/serialization without changing the matcher ordering.
    return float(round(value, 12))


def identify(
    query: np.ndarray,
    gallery: Mapping[str, Sequence[np.ndarray]],
    matcher: Any,
    threshold: float,
    *,
    direction: ScoreDirection = ScoreDirection.DISTANCE,
) -> IdentificationResult:
    """Search every enrolled identity and reject the gallery winner if needed.

    The best template per identity is used: min for a distance matcher and max
    for a similarity matcher. The threshold is deliberately supplied by the
    caller because a 1:1 threshold is not automatically a valid 1:N threshold.
    """

    if not math.isfinite(float(threshold)):
        raise ValueError("threshold must be finite")
    if not isinstance(direction, ScoreDirection):
        direction = ScoreDirection(direction)

    per_user: dict[str, float] = {}
    for user_id, templates in gallery.items():
        scores = [_score(matcher, np.asarray(query), np.asarray(template)) for template in templates]
        if not scores:
            continue
        per_user[user_id] = (
            max(scores) if direction is ScoreDirection.SIMILARITY else min(scores)
        )

    if not per_user:
        return IdentificationResult("UNKNOWN", None, None, None)

    ordered = sorted(
        per_user.items(),
        key=lambda item: item[1],
        reverse=direction is ScoreDirection.SIMILARITY,
    )
    best_user, best_score = ordered[0]
    second_score = ordered[1][1] if len(ordered) > 1 else None
    accepted = (
        best_score >= threshold
        if direction is ScoreDirection.SIMILARITY
        else best_score <= threshold
    )
    if not accepted:
        return IdentificationResult("UNKNOWN", None, best_score, second_score)
    return IdentificationResult("ACCEPT", best_user, best_score, second_score)


class Gallery:
    def __init__(
        self,
        templates: Mapping[str, Sequence[np.ndarray]],
        matcher: Any,
        *,
        threshold: float,
        direction: ScoreDirection = ScoreDirection.DISTANCE,
    ) -> None:
        self.templates = {
            str(user_id): tuple(np.asarray(template) for template in user_templates)
            for user_id, user_templates in templates.items()
        }
        self.matcher = matcher
        self.threshold = float(threshold)
        self.direction = ScoreDirection(direction)

    @classmethod
    def from_store(
        cls,
        store: TemplateStore,
        matcher: Any,
        *,
        threshold: float,
        direction: ScoreDirection = ScoreDirection.DISTANCE,
        capture_profile: str | None = None,
        algorithm_name: str | None = None,
    ) -> "Gallery":
        templates: dict[str, Sequence[np.ndarray]] = {}
        for user_id, (features, metadata) in store.load_all().items():
            if capture_profile is not None and metadata.get("capture_profile") != capture_profile:
                continue
            if algorithm_name is not None and metadata.get("algorithm") != algorithm_name:
                continue
            templates[user_id] = tuple(np.asarray(feature) for feature in features)
        return cls(templates, matcher, threshold=threshold, direction=direction)

    def identify(self, query: np.ndarray) -> IdentificationResult:
        return identify(
            query,
            self.templates,
            self.matcher,
            self.threshold,
            direction=self.direction,
        )
