"""Opt-in post-ranking rejection; score families are never interchanged.

No threshold is estimated here. Runtime profiles must be evaluated separately
for correct accepts, wrong accepts and lost correct decisions.
"""
from dataclasses import dataclass
import json
import math
from pathlib import Path


ROUTE_FAMILIES = {
    **dict.fromkeys(("pose_confident", "legacy_confident", "enrollment_link_confident",
        "affine_confident", "pooled_enrollment_confident", "normal_index_confident",
        "wide_index_confident", "exhaustive_fallback", "exhaustive_retained_fastcc_pilot"), "fastcc"),
    "compnet_evidence_confident": "compnet",
    "compnet_alternate_roi_confident": "compnet",
    "quality_evidence_confident": "quality",
}


def unit_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Acceptance limits must be finite numbers in [0, 1]")
    return float(value)


@dataclass(frozen=True)
class ScoreGate:
    max_distance: float
    min_margin: float


class AcceptancePolicy:
    def __init__(self, document):
        if not isinstance(document, dict) or set(document) != {"version", "name", "profiles"}:
            raise ValueError("Acceptance policy requires version, name and profiles")
        if type(document['version']) is not int or document['version'] != 1:
            raise ValueError("Unsupported acceptance policy version")
        if not isinstance(document['name'], str) or not 1 <= len(document['name']) <= 80:
            raise ValueError("Invalid acceptance policy name")
        profiles = document['profiles']
        if not isinstance(profiles, dict) or not profiles or set(profiles) - {"fastcc", "compnet", "quality"}:
            raise ValueError("Unknown or missing acceptance score families")
        self.name = document['name']
        self.profiles = {}
        for family, values in profiles.items():
            if not isinstance(values, dict) or set(values) != {"max_distance", "min_margin"}:
                raise ValueError("Each score family requires max_distance and min_margin")
            self.profiles[family] = ScoreGate(unit_number(values['max_distance']), unit_number(values['min_margin']))

    def rejection(self, best, second, route):
        """Return (status, reason), or None to keep an otherwise valid MATCH."""
        family = ROUTE_FAMILIES.get(route)
        if family not in self.profiles:
            return "RETRY", "UNCONFIGURED_SCORE_FAMILY"
        try:
            best = unit_number(best)
            if second is not None: second = unit_number(second)
        except ValueError:
            return "RETRY", "INVALID_MATCH_SCORES"
        gate = self.profiles[family]
        if best > gate.max_distance:
            return "UNKNOWN", "POLICY_SCORE_ABOVE_THRESHOLD"
        if second is None:
            return "RETRY", "INSUFFICIENT_CANDIDATES"
        if second <= best or second - best < gate.min_margin:
            return "RETRY", "POLICY_AMBIGUOUS_MARGIN"
        return None


def load_acceptance_policy(path: Path):
    if not path.exists(): return None
    return AcceptancePolicy(json.loads(path.read_text(encoding="utf-8")))
