"""Candidate-first FastCC with one high-recall shortlist expansion."""

from wide_candidate_matcher_v41 import WideCandidateFirstV41


class WideCandidateFirstV43(WideCandidateFirstV41):
    """Refine 16 normal-index frame candidates before the unchanged fallback."""

    name = "FastCCWideCandidateFirst-v43-experimental"
    candidate_pair_limit = 16

