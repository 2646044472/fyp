"""Candidate-first FastCC with a frozen-policy acceptance early stop."""

from wide_candidate_matcher_v43 import WideCandidateFirstV43


class WideCandidateFirstV44(WideCandidateFirstV43):
    """Stop after candidate refinement only when the loaded policy accepts."""

    name = "FastCCWideCandidateFirst-v44-experimental"

    def _policy_candidate_decision(self, scores, route):
        policy = getattr(self, "candidate_early_policy", None)
        if policy is None:
            return {"configured": False, "status": None, "reason": "POLICY_NOT_ATTACHED",
                    "would_accept": False}
        ordered = sorted(scores.values())
        if len(ordered) < 2:
            return {"configured": True, "status": "RETRY", "reason": "INSUFFICIENT_CANDIDATES",
                    "would_accept": False}
        decision = policy.rejection(ordered[0], ordered[1], route)
        if decision is None:
            return {"configured": True, "status": "MATCH", "reason": None, "would_accept": True}
        return {"configured": True, "status": decision[0], "reason": decision[1],
                "would_accept": False}

    def _candidate_early_stop_decision(self, scores, route):
        return self._policy_candidate_decision(scores, route)

