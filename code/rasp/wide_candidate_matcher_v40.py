"""Candidate-first variant with query-local memo storage fully disabled."""

from wide_candidate_matcher_v39 import WideCandidateFirstV39


class WideCandidateFirstV40(WideCandidateFirstV39):
    name = "FastCCWideCandidateFirst-v40-experimental"
    exact_reuse_limit_bytes = 0
