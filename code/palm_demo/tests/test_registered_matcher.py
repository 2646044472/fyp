from pathlib import Path

import numpy as np
import pytest

from biometric import score_probe
from palm_app.biometric import load_algorithm
from registered_matcher import FastCCRegisteredMatcher, HEADER, MAGIC, MAX_POINTS, registration
from templates import TemplateStore


@pytest.fixture
def matcher():
    return load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python',
                          'FastCCRegisteredBest2-v1')


def test_packed_template_roundtrip_and_base_only_fallback(matcher, tmp_path):
    rng = np.random.default_rng(40)
    roi = rng.integers(0, 256, (128, 128), dtype=np.uint8)
    feature = matcher.extract(roi)
    store = TemplateStore(tmp_path)
    store.save('test', np.stack([feature]*5), {'algorithm': matcher.name})
    restored, _ = store.load('test')
    np.testing.assert_array_equal(restored[0], feature)
    assert matcher.match(feature, restored[0]) == 0.
    assert score_probe(matcher, feature, restored) == 0.


def test_rejects_legacy_and_corrupt_packed_features(matcher):
    with pytest.raises(ValueError, match='shape'):
        matcher._unpack(np.zeros((9, 32, 32), np.int8))
    feature = matcher.extract(np.arange(128*128, dtype=np.uint8).reshape(128, 128))
    feature[:HEADER] = np.asarray([MAGIC, MAX_POINTS+1, 100, 100], '<i4').view(np.uint8)
    with pytest.raises(ValueError, match='header'):
        matcher._unpack(feature)


def test_geometric_registration_requires_distributed_consistent_matches():
    rng = np.random.default_rng(42)
    points = np.asarray([[50, 50], [140, 50], [250, 55], [60, 160],
                         [160, 170], [260, 180], [75, 260], [270, 270]], np.float32)
    desc = rng.random((8, 128), dtype=np.float32)
    transform = registration((points, desc), (points + [10, -5], desc.copy()))
    assert transform is not None
    np.testing.assert_allclose(transform, [[1, 0, 10], [0, 1, -5], [0, 0, 1]], atol=1e-5)
    clustered = points/100 + 100
    assert registration((clustered, desc), (clustered+[10, -5], desc.copy())) is None
    assert registration((points[:3], desc[:3]), (points[:3], desc[:3])) is None


def test_registered_outside_original_image_falls_back_without_border_match(matcher, monkeypatch):
    from PIL import Image
    rng = np.random.default_rng(44)
    image = Image.fromarray(rng.integers(0, 256, (256, 256, 3), dtype=np.uint8))
    roi = rng.integers(0, 256, (128, 128), dtype=np.uint8)
    q = np.asarray([[50, 50], [200, 50], [200, 200], [50, 200]], np.float32)
    probe = matcher.extract_with_context(image, q, roi)
    target = matcher.extract(np.flipud(roi))
    from pose_matcher import FastCCPoseMatcher
    expected = FastCCPoseMatcher.match(matcher, matcher._unpack(probe)[0], matcher._unpack(target)[0])
    monkeypatch.setattr('registered_matcher.registration', lambda *args: np.asarray([[1., 0., 900.], [0., 1., 0.], [0., 0., 1.]]))
    assert matcher.match(probe, target) == expected


def test_two_template_support_is_used_through_score_probe(matcher, monkeypatch):
    monkeypatch.setattr(matcher, 'match', lambda probe, candidate: float(candidate))
    # A single attractive outlier cannot determine the enrolled identity's score.
    assert score_probe(matcher, None, [0., .4, .5, .6, .7]) == pytest.approx(.2)


def test_dual_views_roundtrip_and_version_isolation(matcher, tmp_path):
    from PIL import Image
    from registered_matcher import FEATURE_SIZE
    dual = load_algorithm(Path(__file__).resolve().parents[1]/'vendor/palmprint-recognition-python',
                          'FastCCRegisteredBest2-v2')
    rng = np.random.default_rng(49)
    image = Image.fromarray(rng.integers(0, 256, (256, 256, 3), dtype=np.uint8))
    roi = rng.integers(0, 256, (128, 128), dtype=np.uint8)
    quad = np.asarray([[50, 50], [200, 50], [200, 200], [50, 200]], np.float32)
    feature = dual.extract_with_context(image, quad, roi)
    np.testing.assert_array_equal(feature, dual.extract_with_context(image, quad, roi))
    store = TemplateStore(tmp_path)
    store.save('dual', np.stack([feature]*5), {'algorithm': dual.name})
    restored, _ = store.load('dual')
    assert score_probe(dual, feature, restored) == 0.
    with pytest.raises(ValueError, match='shape'):
        matcher.match(feature, feature)
    with pytest.raises(ValueError, match='shape'):
        dual.match(feature[:FEATURE_SIZE], feature)
    corrupted = feature.copy()
    corrupted[FEATURE_SIZE:FEATURE_SIZE+4] = 0
    with pytest.raises(ValueError, match='header'):
        dual.match(corrupted, feature)
