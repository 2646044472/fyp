"""Opt-in query-only geometric repair; no identity or score selects an ROI.

Run only after the unchanged terminal scorer and a conflicting, valid primary.
The original five-frame gallery, acceptance gates and scoring code are reused.
This module never installs itself in the service.
"""
import copy
import itertools
import time

import cv2
import numpy as np
from PIL import Image

from halfturn_roi_recovery import quad_iou
from pklnet_roi import MIN_ILLUMINATION_IOU, normalize_roi_pixels

POLICY = 'terminal-four-view-geometric-quorum-v1'
TERMINAL_ROUTE = 'exhaustive_terminal_rf_evidence'
TURNS = (0, 1, 2, 3)


def unrotate(points, size, turns):
    """Inverse of PIL's exact counterclockwise right-angle pixel transforms."""
    p = np.asarray(points, np.float32)
    if p.size % 2 or not np.isfinite(p).all() or turns not in TURNS:
        raise ValueError('Expected finite xy coordinates and a right-angle turn')
    xy = p.reshape(-1, 2); x, y = xy[:, 0], xy[:, 1]
    w, h = size
    mapped = ((x, y), (w-1-y, x), (w-1-x, h-1-y), (y, h-1-x))[turns]
    return np.stack(mapped, axis=1).reshape(p.shape).astype(np.float32)


def valid_quad(quad, size):
    q = np.asarray(quad, np.float32)
    return bool(q.shape == (4, 2) and np.isfinite(q).all() and (q >= 0).all()
                and (q[:, 0] < size[0]).all() and (q[:, 1] < size[1]).all()
                and cv2.isContourConvex(q) and abs(cv2.contourArea(q)) > 1)


def choose_quorum(views):
    """Unique largest clique of >=3 distinct views, then geometric medoid.

    Hull ordering is used for spatial overlap only. Sampling retains the chosen
    detector's anatomical corner order; sorting those corners would rotate ROI
    texture independently of the predicted finger-valley coordinate convention.
    """
    eligible = [v for v in views if v['valid']]
    if len({v['turns'] for v in views}) != len(views):
        raise ValueError('One observation per rotation required')
    overlap = {(a['turns'], b['turns']): quad_iou(
        cv2.convexHull(np.asarray(a['quad'], np.float32)).reshape(4, 2),
        cv2.convexHull(np.asarray(b['quad'], np.float32)).reshape(4, 2))
        for a in eligible for b in eligible}
    cliques = [c for n in range(3, len(eligible)+1) for c in itertools.combinations(eligible, n)
               if all(overlap[a['turns'], b['turns']] >= MIN_ILLUMINATION_IOU
                      for a, b in itertools.combinations(c, 2))]
    trace = dict(pairwise_iou=[dict(left=a, right=b, iou=value) for (a, b), value in overlap.items()],
                 min_iou=MIN_ILLUMINATION_IOU, minimum_views=3)
    if not cliques:
        return None, dict(trace, reason='no_three_view_quorum')
    largest = [c for c in cliques if len(c) == max(map(len, cliques))]
    if len(largest) != 1:
        return None, dict(trace, reason='ambiguous_maximum_quorum')
    group = largest[0]
    selected = min(group, key=lambda a: (-sum(overlap[a['turns'], b['turns']] for b in group), a['turns']))
    return selected['turns'], dict(trace, reason='unique_geometric_quorum',
                                  quorum=[v['turns'] for v in group], selected_turns=selected['turns'])


def mapped_details(details, size, turns):
    d = copy.deepcopy(details)
    keys = ('pklnet_keypoints', 'pklnet_heatmap_keypoints', 'pklnet_fc_keypoints',
            'pklnet_full_frame_keypoints', 'roi_quad_full', 'pklnet_heatmap_quad',
            'pklnet_fc_quad', 'pklnet_full_frame_quad')
    for key in keys:
        if key in d:
            d[key] = unrotate(d[key], size, turns).tolist()
    for view in d.get('pklnet_roi_candidates', []):
        view['quad'] = unrotate(view['quad'], size, turns).tolist()
    if 'pklnet_retry_box' in d:
        l, t, r, b = d['pklnet_retry_box']
        points = unrotate([[l, t], [r-1, b-1]], size, turns)
        d['pklnet_retry_box'] = [*points.min(axis=0).tolist(), *(points.max(axis=0)+1).tolist()]
    return d


class RotationConsensus:
    def __init__(self, localizer, boundary=lambda: None):
        self.localizer, self.boundary = localizer, boundary
        self.trace = None

    def repair(self, image, primary):
        views = []; results = {0: primary}; started = time.perf_counter()
        for turns in TURNS:
            if turns:
                self.boundary()
                rotated = image.transpose((None, Image.Transpose.ROTATE_90,
                                           Image.Transpose.ROTATE_180, Image.Transpose.ROTATE_270)[turns])
                tick = time.perf_counter()
                result = self.localizer.extract(rotated, side=primary[0].shape[0])
                results[turns] = result
                ms = (time.perf_counter()-tick)*1000
            else:
                result = primary; ms = 0.
            quad = unrotate(result[1], image.size, turns)
            views.append(dict(turns=turns, quad=quad.tolist(), ms=ms,
                              valid=bool(result[2]['roi_geometry_valid']) and valid_quad(quad, image.size),
                              detector_details=copy.deepcopy(result[2])))
        selected, trace = choose_quorum(views)
        self.trace = dict(trace, policy=POLICY, views=views, changed=False,
                          localization_ms=(time.perf_counter()-started)*1000)
        if selected is None or selected == 0:
            return primary
        chosen = views[selected]; quad = np.asarray(chosen['quad'], np.float32)
        if np.array_equal(quad, primary[1]):
            return primary
        # No interpolated/averaged or label-selected coordinates are introduced.
        bgr = cv2.cvtColor(np.asarray(image.convert('RGB')), cv2.COLOR_RGB2BGR)
        side = primary[0].shape[0]
        raw = self.localizer._roi_extractor.getROIimg(bgr, quad, side=side, ratio=1.)
        if raw is None or raw.shape != (side, side):
            raise ValueError('Consensus perspective sampling failed')
        d = mapped_details(results[selected][2], image.size, selected)
        d.update(roi_quad_full=quad.tolist(), roi_in_bounds=True, roi_geometry_valid=True,
                 roi_geometry_reason=None, rotation_consensus_policy=POLICY,
                 rotation_consensus_turns=selected, pklnet_roi_pixels='original')
        self.trace.update(changed=True, effective_quad=quad.tolist())
        return raw.astype(np.uint8), quad, d


class TerminalRepair:
    """Attach only to an isolated matcher after terminal RF is installed."""
    def __init__(self, algorithm, localizer, boundary=lambda: None):
        if not getattr(algorithm, '_terminal_rf_installed', False):
            raise ValueError('Frozen terminal RF must be installed first')
        self.algorithm = algorithm
        self.geometry = RotationConsensus(localizer, boundary)
        self.localizer, self.boundary = localizer, boundary
        self.context = None; self.trace = None
        self.original = algorithm.score_gallery
        algorithm.score_gallery = self.score

    def observe(self, image, primary):
        self.context = (image, primary)

    def score(self, probe, groups):
        values = self.original(probe, groups)
        original_trace = copy.deepcopy(self.algorithm._terminal_rf_trace)
        self.trace = dict(policy=POLICY, attempted=False, rescored=False,
                          original_route=probe.route, original_scores=dict(values),
                          original_terminal_rf=original_trace)
        if self.context is None:
            raise ValueError('Missing current-query localization context')
        image, primary = self.context
        d = primary[2]
        if (probe.route != TERMINAL_ROUTE or not d['roi_geometry_valid']
                or d.get('pklnet_consensus_valid') is not False):
            self.trace['reason'] = 'outside_terminal_geometry_scope'
            return values
        self.trace['attempted'] = True
        revised = self.geometry.repair(image, primary)
        self.trace['geometry'] = copy.deepcopy(self.geometry.trace)
        if revised is primary:
            self.trace['reason'] = 'geometry_preserved_primary'
            return values
        self.boundary(); tick = time.perf_counter()
        raw, quad, details = revised
        roi = normalize_roi_pixels(raw)
        new_probe = self.algorithm.extract_probe_with_context(image, quad, roi)
        candidates = details.get('pklnet_roi_candidates') or [dict(quad=quad.tolist(), valid=True)]
        new_probe.localization_candidates = candidates
        def exhaustive():
            hypotheses = self.algorithm.complete_hypotheses(image, candidates, self.localizer)
            return self.algorithm.extract_with_hypotheses(image, quad, roi, hypotheses)
        new_probe.exhaustive = exhaustive
        # Call the saved frozen scorer, never this wrapper (no recursive repair).
        repaired = self.original(new_probe, groups)
        probe.route = new_probe.route
        self.trace.update(rescored=True, reason='geometric_repair_rescored_once',
                          effective_route=new_probe.route, effective_scores=dict(repaired),
                          effective_terminal_rf=copy.deepcopy(self.algorithm._terminal_rf_trace),
                          rescore_ms=(time.perf_counter()-tick)*1000,
                          effective_roi_sha256=__import__('hashlib').sha256(raw.tobytes()).hexdigest())
        return repaired
