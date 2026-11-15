"""Candidate-first FastCC refinement over the complete sharded descriptor index.

The matcher keeps the original full-gallery pose scores for every enrolled
hand. It refines only high-vote enrollment frames first, then uses the existing
full-gallery path whenever that broader score set remains uncertain.
"""

from __future__ import annotations

import cv2
import numpy as np

from pklnet_roi import normalize_roi_pixels
from proposed_index_matcher import proposed_registration
from wide_sharded_matcher import WideCapacityShardedMatcher


class WideCandidateFirstMatcher(WideCapacityShardedMatcher):
    """v37 experiment: shortlist enrollment frames before expensive alignment."""

    name = "FastCCWideCandidateFirst-v37-experimental"
    candidate_pair_limit = 20
    wide_candidate_pair_limit = 32

    def _rank_candidate_pairs(self, views):
        """Collect complete-index votes and return ranked frame keys and proposals."""
        group_votes = {}
        proposals = []
        with self._index_lock:
            index = self._index
            if index is None:
                return [], [], {}
            for source, points, descriptors in views:
                found = {}
                rows = index.knnMatch(descriptors, k=16) if len(descriptors) else []
                for query_index, matches in enumerate(rows):
                    if not matches:
                        continue
                    cutoff = matches[0].distance * 1.25 + 0.02
                    for match in matches:
                        if match.distance > cutoff:
                            continue
                        group = int(self._labels[match.trainIdx])
                        found.setdefault(group, set()).add(query_index)
                        group_votes[group] = group_votes.get(group, 0.0) + 1.0 / (match.distance + 0.1)
                proposals.append(found)

        pair_votes = {}
        for group, vote in group_votes.items():
            user, sample_index, _ = self._mapping[group]
            key = (user, sample_index)
            pair_votes[key] = pair_votes.get(key, 0.0) + vote
        ranked = sorted(pair_votes, key=lambda key: (-pair_votes[key], key))
        return ranked, proposals, pair_votes

    def _refine_candidates(self, probe, groups, pairs, views, proposals, selected):
        selected = [key for key in selected if key in pairs]
        if not selected:
            return 0

        corners = np.asarray([[0, 0, 1], [128, 0, 1], [128, 128, 1], [0, 128, 1]])

        def refine(key):
            user, sample_index = key
            best = pairs[key]
            sample = groups[user][sample_index]
            for (source, points, descriptors), found in zip(views, proposals):
                for group in self._positions[key]:
                    indices = found.get(group, ())
                    if len(indices) < 4:
                        continue
                    _, _, view_index = self._mapping[group]
                    target = sample[1][view_index]
                    transform = proposed_registration(
                        (points, descriptors), (target[2], target[3]), indices)
                    if transform is None:
                        continue
                    warp = np.diag([1 / 3, 1 / 3, 1]) @ transform @ source
                    mapped = corners @ np.linalg.inv(warp).T
                    mapped = mapped[:, :2] / mapped[:, 2:]
                    if (not np.isfinite(mapped).all() or (mapped < 1).any()
                            or (mapped[:, 0] >= probe.native.shape[1] - 1).any()
                            or (mapped[:, 1] >= probe.native.shape[0] - 1).any()
                            or not self._accept_alignment((None, None, probe.source), mapped)):
                        continue
                    pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native, warp, (128, 128)))
                    best = min(best, self.base.match(self.base.extract(pixels), target[4]))
            return key, best

        pairs.update(self._workers.map(refine, selected))
        return len(selected)

    def _aggregate_gallery(self, groups, pairs):
        return {user: self._aggregate([pairs[(user, j)] for j in range(len(samples))])
                for user, samples in groups.items()}

    def score_gallery(self, probe, groups):
        # This pose score is a cheap, complete-gallery guard. It remains present
        # for unselected identities so the shortlist cannot manufacture a gap.
        pairs = {
            (user, j): min(self.base.match(p.astype(bool), sample[0])
                           for p in probe.bank if p[0, 0] >= 0)
            for user, samples in groups.items() for j, sample in enumerate(samples)
        }
        scores = self._aggregate_gallery(groups, pairs)
        trace = {
            "initial_gallery_frames": len(pairs),
            "initial_pose_confident": bool(self.confident(scores)),
            "candidate_pair_limit": self.candidate_pair_limit,
            "normal_candidates": [],
            "normal_candidate_pairs_refined": 0,
            "wide_candidates": [],
            "wide_candidate_pairs_refined": 0,
            "full_gallery_fallback": False,
            "policy_early_stop": False,
        }
        probe.candidate_first_trace = trace
        if trace["initial_pose_confident"]:
            probe.route = "pose_confident"
            trace["terminal_route"] = probe.route
            return scores

        auxiliary = getattr(self, "_auxiliary_scores", None)
        if auxiliary is not None:
            candidate = auxiliary(probe, groups)
            if candidate is not None and self.confident(candidate):
                probe.route = getattr(probe, "auxiliary_route", "compnet_evidence_confident")
                trace["terminal_route"] = probe.route
                return candidate

        self.prepare_gallery(groups)
        if self._index is not None:
            for wide, limit, stage_name in (
                    (False, self.candidate_pair_limit, "normal"),
                    (True, self.wide_candidate_pair_limit, "wide")):
                views = self._stage_views(probe, wide)
                ranked, proposals, pair_votes = self._rank_candidate_pairs(views)
                selected = ranked[:limit]
                if stage_name == "normal":
                    trace["normal_candidates"] = [
                        {"user": user, "sample_index": int(sample), "vote": float(pair_votes[(user, sample)])}
                        for user, sample in selected]
                    trace["normal_candidate_pairs_refined"] = self._refine_candidates(
                        probe, groups, pairs, views, proposals, selected)
                else:
                    trace["wide_candidates"] = [
                        {"user": user, "sample_index": int(sample), "vote": float(pair_votes[(user, sample)])}
                        for user, sample in selected]
                    trace["wide_candidate_pairs_refined"] = self._refine_candidates(
                        probe, groups, pairs, views, proposals, selected)
                scores = self._aggregate_gallery(groups, pairs)
                if self.confident(scores):
                    probe.route = f"candidate_first_{stage_name}_index_confident"
                    trace["terminal_route"] = probe.route
                    return scores
                early_stop = getattr(self, "_candidate_early_stop_decision", None)
                if callable(early_stop):
                    route = f"candidate_first_{stage_name}_index_confident"
                    decision = early_stop(scores, route)
                    trace["candidate_policy_decision"] = decision
                    if decision.get("would_accept"):
                        probe.route = route
                        trace["terminal_route"] = probe.route
                        trace["policy_early_stop"] = True
                        return scores

        # Keep the established registration, linked-enrollment and exhaustive
        # behavior for every unresolved query; the shortlist never rejects.
        trace["full_gallery_fallback"] = True
        scores = super().score_gallery(probe, groups)
        trace["terminal_route"] = getattr(probe, "route", None)
        return scores
