"""Synthetic gate/decision parity checks; no images, model or real gallery."""
import dataclasses

import cv2
import numpy as np
import pytest

from biometric import score_probe
from gallery import Gallery
from registered_matcher import FastCCRegisteredMatcher, registration


def features(*, clustered=False):
    points = np.asarray([[50, 50], [140, 50], [250, 55], [60, 160],
                         [160, 170], [260, 180], [75, 260], [270, 270]], np.float32)
    if clustered:
        points = points/100 + 100
    return points, np.eye(8, 128, dtype=np.float32)


def compare_modes(left, right):
    before = [a.copy() for a in (*left, *right)]
    baseline = registration(left, right)
    trace = {'stale_previous_reason': 'must not survive'}
    observed = registration(left, right, diagnostics=trace)
    if baseline is None:
        assert observed is None
    else:
        np.testing.assert_array_equal(observed, baseline)
    for original, value in zip(before, (*left, *right)):
        np.testing.assert_array_equal(original, value)
    assert 'stale_previous_reason' not in trace
    return observed, trace


@pytest.mark.parametrize('short_side', ['query', 'enrollment'])
def test_descriptor_count_and_unmeasured_stages(short_side):
    left, right = features(), features()
    if short_side == 'query':
        left = tuple(a[:3] for a in left)
    else:
        right = tuple(a[:3] for a in right)
    result, trace = compare_modes(left, right)
    assert result is None
    assert (trace['stage'], trace['reason']) == ('descriptor_count', 'insufficient_descriptors')
    assert trace['outcome'] == 'rejected'
    assert trace['mutual_matches'] is None and trace['inliers'] is None
    assert trace['coverage'] is None and trace['failed_gates'] == []


def test_mutual_matching_failure_is_distinct_from_fitting():
    points, descriptors = features()
    descriptors[:] = 0  # nearest/second-nearest tie fails the unchanged ratio.
    result, trace = compare_modes((points, descriptors), (points, descriptors.copy()))
    assert result is None
    assert (trace['stage'], trace['reason']) == ('correspondence', 'insufficient_mutual_matches')
    assert trace['mutual_matches'] == 0
    assert trace['inliers'] is None and trace['scale'] is None


@pytest.mark.parametrize('bad_transform,reason', [
    (None, 'no_transform'),
    (np.full((2, 3), np.nan), 'nonfinite_transform'),
])
def test_fitting_failure_reasons_preserve_none(monkeypatch, bad_transform, reason):
    monkeypatch.setattr(cv2, 'estimateAffinePartial2D',
                        lambda *a, **k: (bad_transform, np.ones((8, 1), np.uint8)))
    result, trace = compare_modes(features(), features())
    assert result is None
    assert (trace['stage'], trace['reason']) == ('similarity_fit', reason)
    assert trace['mutual_matches'] == 8 and trace['inliers'] is None


def test_insufficient_inliers_is_distinct_from_geometry(monkeypatch):
    mask = np.asarray([1, 1, 1, 0, 0, 0, 0, 0], np.uint8)[:, None]
    monkeypatch.setattr(cv2, 'estimateAffinePartial2D',
                        lambda *a, **k: (np.eye(3)[:2], mask))
    result, trace = compare_modes(features(), features())
    assert result is None
    assert (trace['stage'], trace['reason'], trace['inliers']) == ('inlier_count', 'insufficient_inliers', 3)
    assert trace['coverage'] is None


@pytest.mark.parametrize('clustered,scale,angle,failed', [
    (True, 1., 0., ['coverage']),
    (False, .4, 0., ['scale']),
    (False, 2.1, 0., ['scale']),
    (False, 1., 41., ['angle']),
    (False, 1., -41., ['angle']),
    (True, .3, 50., ['coverage', 'scale', 'angle']),
])
def test_geometry_records_every_failed_gate_without_changing_result(monkeypatch, clustered, scale, angle, failed):
    radians = np.deg2rad(angle)
    matrix = np.asarray([[scale*np.cos(radians), -scale*np.sin(radians), 0.],
                         [scale*np.sin(radians), scale*np.cos(radians), 0.]])
    monkeypatch.setattr(cv2, 'estimateAffinePartial2D',
                        lambda *a, **k: (matrix, np.ones((8, 1), np.uint8)))
    result, trace = compare_modes(features(clustered=clustered), features(clustered=clustered))
    assert result is None
    assert (trace['stage'], trace['reason']) == ('geometry', 'geometry_limits')
    assert trace['failed_gates'] == failed
    assert trace['inliers'] == 8
    assert trace['scale'] == pytest.approx(scale)
    assert trace['angle_degrees'] == pytest.approx(angle)


def test_real_opencv_synthetic_fit_is_identical_with_and_without_trace():
    points, descriptors = features()
    result, trace = compare_modes((points, descriptors), (points+[10, -5], descriptors.copy()))
    np.testing.assert_allclose(result, [[1., 0., 10.], [0., 1., -5.], [0., 0., 1.]], atol=1e-5)
    assert (trace['stage'], trace['outcome'], trace['reason']) == ('complete', 'accepted', 'accepted')
    assert trace['failed_gates'] == [] and trace['inliers'] == 8


def test_exception_keeps_unknown_reason_and_propagates_same_error(monkeypatch):
    failure = RuntimeError('synthetic fitter failure')
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(cv2, 'estimateAffinePartial2D', fail)
    with pytest.raises(RuntimeError) as unobserved:
        registration(features(), features())
    trace = {}
    with pytest.raises(RuntimeError) as observed:
        registration(features(), features(), diagnostics=trace)
    assert unobserved.value is observed.value is failure
    assert trace['stage'] == 'similarity_fit' and trace['outcome'] == 'error'
    assert trace['reason'] is None and trace['coverage'] is None
    assert trace['error_type'] == 'RuntimeError'


@pytest.mark.parametrize('threshold,margin,status', [(1., 0., 'MATCH'), (.1, 0., 'UNKNOWN'), (1., .05, 'RETRY')])
def test_existing_match_scores_and_gallery_decisions_are_identical(threshold, margin, status):
    class BinaryBase:
        def extract(self, pixels):
            return cv2.resize(pixels, (32, 32), interpolation=cv2.INTER_NEAREST) > 127
        def match(self, left, right):
            return float(np.mean(left != right))

    matcher = object.__new__(FastCCRegisteredMatcher)
    matcher.base = BinaryBase()
    points, descriptors = features()
    context = np.tile(np.arange(768) % 256, (768, 1)).astype(np.uint8)
    source = np.asarray([[1., 0., -100.], [0., 1., -100.], [0., 0., 1.]])
    def packed(first):
        bank = np.full((9, 32, 32), -1, np.int8)
        bank[0] = first
        return matcher._pack(bank, context, source, (1000, 1000), points, descriptors)
    probe = packed(np.indices((32, 32)).sum(axis=0) % 2)
    enrolled = {'synthetic-a': [packed(0)]*5, 'synthetic-b': [packed(1)]*5}

    class Store:
        def list_users(self):
            return sorted(enrolled)
        def load(self, user):
            return enrolled[user], {'capture_profile':'rgb'}

    gallery = Gallery(Store(), matcher, threshold=threshold, min_margin=margin)
    normal_scores = {u: score_probe(matcher, probe, f) for u, f in enrolled.items()}
    normal = dataclasses.asdict(gallery.identify(probe))
    traces = []
    def traced(left, right):
        trace = {}
        result = registration(left, right, diagnostics=trace)
        traces.append(trace)
        return result
    matcher.registration = traced
    traced_scores = {u: score_probe(matcher, probe, f) for u, f in enrolled.items()}
    observed = dataclasses.asdict(gallery.identify(probe))
    normal.pop('search_ms'); observed.pop('search_ms')
    assert normal_scores == traced_scores
    assert normal == observed and observed['status'] == status
    assert traces and all(t['outcome'] == 'accepted' for t in traces)
