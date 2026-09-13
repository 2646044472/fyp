from __future__ import annotations

import numpy as np

from gallery import Gallery
from templates import TemplateStore


class DistanceAlgorithm:
    def match(self, probe, candidate):
        return abs(float(probe[0]) - float(candidate[0]))


def make_gallery(tmp_path, threshold=0.28, min_margin=0.0):
    store = TemplateStore(tmp_path)
    store.save("stephen", np.array([[0.10], [0.12]]), {"capture_profile": "rgb"})
    store.save("bankey", np.array([[0.40], [0.42]]), {"capture_profile": "rgb"})
    store.save("infrared", np.array([[0.01]]), {"capture_profile": "noir-ir"})
    return Gallery(store, DistanceAlgorithm(), threshold=threshold, min_margin=min_margin)


def test_correct_person_wins(tmp_path):
    result = make_gallery(tmp_path).identify(np.array([0.11]), "rgb")

    assert result.status == "MATCH"
    assert result.user_id == "stephen"
    assert result.second_score is not None


def test_unknown_user_stays_unknown(tmp_path):
    result = make_gallery(tmp_path).identify(np.array([0.90]), "rgb")

    assert result.status == "UNKNOWN"
    assert result.user_id is None


def test_nearest_identity_is_not_automatically_accepted(tmp_path):
    store = TemplateStore(tmp_path)
    store.save("stephen", np.array([[0.34]]), {"capture_profile": "rgb"})
    store.save("bankey", np.array([[0.42]]), {"capture_profile": "rgb"})

    result = Gallery(store, DistanceAlgorithm(), threshold=0.28).identify(np.array([0.0]), "rgb")

    assert result.status == "UNKNOWN"
    assert result.user_id is None


def test_profile_isolation(tmp_path):
    store = TemplateStore(tmp_path)
    store.save("infrared", np.array([[0.01]]), {"capture_profile": "noir-ir"})
    result = Gallery(store, DistanceAlgorithm(), threshold=0.28).identify(np.array([0.01]), "rgb")

    assert result.status == "UNKNOWN"
    assert result.user_id is None


def test_close_candidates_trigger_retry_when_margin_is_configured(tmp_path):
    result = make_gallery(tmp_path, min_margin=0.05).identify(np.array([0.25]), "rgb")

    assert result.status == "RETRY"
    assert result.user_id is None
