import numpy as np
import pytest
from affine_enrollment_matcher import affine_registration, bounded_affine, AffineEnrollmentMatcher
from linked_enrollment_matcher import LinkedEnrollmentMatcher
from types import SimpleNamespace


@pytest.mark.parametrize('matrix', [np.diag([-1., 1., 1.]), np.diag([3., 3., 1.]),
    np.diag([1.8, .6, 1.]), np.asarray([[1., 0, 0], [0, 1, 0], [.01, 0, 1]]),
    np.full((3, 3), np.nan)])
def test_affine_guard_rejects_reflection_extreme_scale_shear_and_projective(matrix):
    assert not bounded_affine(matrix)


def test_affine_recovers_bounded_tilt_from_six_spread_correspondences():
    points = np.asarray([[40, 40], [300, 40], [300, 300], [40, 300], [90, 160], [240, 180]], np.float32)
    expected = np.asarray([[1.1, .12, 9], [.04, .95, -7], [0, 0, 1.]])
    target = np.c_[points, np.ones(len(points))] @ expected.T
    descriptors = np.zeros((6, 128), np.float32)
    transform = affine_registration((points, descriptors), (target[:, :2], descriptors),
                                    lambda a, b: [(i, i) for i in range(6)])
    np.testing.assert_allclose(transform, expected, atol=1e-4)
    np.testing.assert_allclose(np.c_[target[:, :2], np.ones(6)] @ np.linalg.inv(transform).T,
                               np.c_[points, np.ones(6)], atol=1e-4)


def test_affine_rejects_clustered_matches_and_too_few_inliers():
    points = np.asarray([[1, 1], [3, 1], [3, 3], [1, 3], [2, 1], [2, 3]], np.float32)
    descriptors = np.zeros((6, 128), np.float32)
    assert affine_registration((points, descriptors), (points, descriptors),
                               lambda a, b: [(i, i) for i in range(6)]) is None
    assert affine_registration((points[:5], descriptors[:5]), (points, descriptors)) is None


def test_existing_confidence_threshold_is_unchanged():
    assert not AffineEnrollmentMatcher.confident({'a': .33, 'b': .5})
    assert not AffineEnrollmentMatcher.confident({'a': .30, 'b': .37})
    assert AffineEnrollmentMatcher.confident({'a': .30, 'b': .40})


def test_query_correspondences_are_cleared_after_failure(monkeypatch):
    algorithm = object.__new__(AffineEnrollmentMatcher)
    probe = SimpleNamespace(affine_pairs={'stale': ['old-image']})
    def fail(self, current, groups):
        assert current.affine_pairs == {}
        current.affine_pairs['new'] = [1, 2]
        raise RuntimeError('injected failure')
    monkeypatch.setattr(LinkedEnrollmentMatcher, 'score_gallery', fail)
    with pytest.raises(RuntimeError, match='injected failure'):
        algorithm.score_gallery(probe, {})
    assert probe.affine_pairs == {}


def test_affine_uses_supplied_correspondences_without_descriptor_search(monkeypatch):
    points = np.asarray([[40, 40], [300, 40], [300, 300], [40, 300], [90, 160], [240, 180]], np.float32)
    descriptors = np.zeros((6, 128), np.float32)
    def forbidden(*args):
        raise AssertionError('Descriptor search was repeated')
    monkeypatch.setattr('affine_enrollment_matcher.cv2.BFMatcher', forbidden)
    result = affine_registration((points, descriptors), (points, descriptors),
                                 lambda a, b: [(i, i) for i in range(6)])
    np.testing.assert_allclose(result, np.eye(3), atol=1e-6)
