"""Lower-resident-memory FLANN configuration for candidate-first scoring."""

from wide_candidate_matcher_v40 import WideCandidateFirstV40


class WideCandidateFirstV41(WideCandidateFirstV40):
    name = "FastCCWideCandidateFirst-v41-experimental"
    shard_trees = 2
    search_checks = 64
