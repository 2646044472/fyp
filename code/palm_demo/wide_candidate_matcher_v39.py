"""Lower-memory candidate-first variant; unresolved queries use exact fallback."""

from wide_candidate_matcher_v38 import WideCandidateFirstV38


class WideCandidateFirstV39(WideCandidateFirstV38):
    """Avoid duplicate wide alignment and bound query-local reuse memory."""

    name = "FastCCWideCandidateFirst-v39-experimental"
    wide_candidate_pair_limit = 0
    exact_reuse_limit_bytes = 64 * 1024 * 1024

    def _stage_views(self, probe, wide):
        if wide:
            # An unresolved normal shortlist goes directly to the established
            # complete-gallery fallback, which already performs wide search.
            self._candidate_profile.stage = "wide"
            return []
        return super()._stage_views(probe, wide)
