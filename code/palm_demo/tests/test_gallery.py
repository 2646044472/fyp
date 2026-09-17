from __future__ import annotations

import numpy as np

from gallery import Gallery, ScoreDirection
from templates import TemplateStore


class DistanceMatcher:
    def match(self, query, template):
        return abs(float(query[0]) - float(template[0]))


class SimilarityMatcher:
    def match(self, query, template):
        return 1.0 - abs(float(query[0]) - float(template[0]))


def test_distance_gallery_returns_best_user_and_second_score(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    store.save("P001", np.array([[0.10], [0.12]]), {"capture_profile": "rgb"})
    store.save("P002", np.array([[0.40], [0.42]]), {"capture_profile": "rgb"})
    gallery = Gallery.from_store(
        store,
        DistanceMatcher(),
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
        capture_profile="rgb",
    )

    result = gallery.identify(np.array([0.11]))

    assert result.status == "ACCEPT"
    assert result.user_id == "P001"
    assert result.score == 0.01
    assert result.second_score == 0.29


def test_nearest_user_is_unknown_when_threshold_is_not_met(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    store.save("P001", np.array([[0.34]]), {"capture_profile": "rgb"})
    store.save("P002", np.array([[0.42]]), {"capture_profile": "rgb"})
    gallery = Gallery.from_store(
        store,
        DistanceMatcher(),
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
        capture_profile="rgb",
    )

    result = gallery.identify(np.array([0.0]))

    assert result.status == "UNKNOWN"
    assert result.user_id is None
    assert result.score == 0.34


def test_similarity_gallery_accepts_when_score_reaches_threshold(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    store.save("P001", np.array([[0.10]]), {"capture_profile": "rgb"})
    gallery = Gallery.from_store(
        store,
        SimilarityMatcher(),
        threshold=0.85,
        direction=ScoreDirection.SIMILARITY,
        capture_profile="rgb",
    )

    result = gallery.identify(np.array([0.20]))

    assert result.status == "ACCEPT"
    assert result.user_id == "P001"
    assert result.score == 0.9


def test_gallery_does_not_mix_capture_profiles(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    store.save("P001", np.array([[0.10]]), {"capture_profile": "noir-ir"})
    gallery = Gallery.from_store(
        store,
        DistanceMatcher(),
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
        capture_profile="rgb",
    )

    result = gallery.identify(np.array([0.10]))

    assert result.status == "UNKNOWN"
    assert result.user_id is None
    assert result.score is None


def test_gallery_does_not_mix_template_algorithms(tmp_path):
    store = TemplateStore(tmp_path / "templates")
    store.save("P001", np.array([[0.10]]), {"capture_profile": "rgb", "algorithm": "FastCC"})
    store.save("P002", np.array([[0.40]]), {"capture_profile": "rgb", "algorithm": "OtherMatcher"})
    gallery = Gallery.from_store(
        store,
        DistanceMatcher(),
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
        capture_profile="rgb",
        algorithm_name="FastCC",
    )

    result = gallery.identify(np.array([0.40]))

    assert result.status == "UNKNOWN"
    assert result.user_id is None


def test_empty_gallery_returns_unknown(tmp_path):
    gallery = Gallery({}, DistanceMatcher(), threshold=0.28, direction=ScoreDirection.DISTANCE)

    result = gallery.identify(np.array([0.10]))

    assert result.status == "UNKNOWN"
    assert result.user_id is None
    assert result.score is None
