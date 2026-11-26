"""Replay two already-scored crop routes. No image, vector or model input."""
from collections import Counter
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Match:
    hand: str
    score: float

    def __post_init__(self):
        if not self.hand or not isfinite(self.score):
            raise ValueError("Expected a hand class and a finite score")


def audit(attempts, threshold):
    """Rows: (enrolled true hand or None for stranger, upright match, direct match).

    Each route has its own gallery of the same enrolled hand classes. A missing
    route is None; this example assumes a valid crop always yields a score.
    Use a threshold selected on a different development set for this policy.
    """
    if not isfinite(threshold):
        raise ValueError("Expected a finite threshold")
    counts = Counter()
    for truth, upright, direct in attempts:
        group = "unknown" if truth is None else "known"
        counts[group + "_planned"] += 1
        route = "upright" if upright is not None else "direct"
        match = upright if upright is not None else direct
        if match is None:
            counts[group + "_missing"] += 1
            continue
        counts["used_" + route] += 1
        if truth is not None:
            correct = match.hand == truth
            counts["rank1_correct" if correct else "rank1_wrong"] += 1
            outcome = ("correct_accept" if correct else "wrong_accept")
        else:
            outcome = "false_accept"
        if match.score < threshold:
            outcome = "reject"
        counts[group + "_" + outcome] += 1
    return dict(counts)


if __name__ == "__main__":
    # Invented hand labels and scores; the threshold is illustrative.
    print(audit([
        ("A-L", Match("A-L", .4), Match("A-R", .95)),
        ("A-R", None, Match("A-R", .8)),
        (None, None, Match("A-L", .9)),
        (None, None, None),
    ], threshold=.7))
