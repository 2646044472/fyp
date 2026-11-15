"""DoN gallery scorer that keeps the closest enrolled template as identity evidence."""

from __future__ import annotations

from typing import Any


class DoNMinimumTemplateMatcher:
    """Keep DoN extraction/pair scores, but aggregate a hand gallery by its minimum.

    This is a separately named experimental matcher. It deliberately does not
    change the default DoN median aggregation or carry a decision threshold.
    """

    name = "DoNMinTemplate-v1"
    # Fixed from run-007's gallery-only leave-one-hand-out calibration on the
    # exposed 17-hand development gallery; this is not an independent threshold.
    default_threshold = 0.0960693359375
    default_min_margin = 0.0052815755208333315

    def __init__(self, base: Any) -> None:
        self.base = base

    def __getattr__(self, name: str) -> Any:
        return getattr(self.base, name)

    def score_enrollment(self, probe: Any, enrolled_features: Any) -> float:
        scores = [float(self.base.match(probe, candidate)) for candidate in enrolled_features]
        if not scores:
            raise ValueError("at least one enrolled feature is required")
        return min(scores)
