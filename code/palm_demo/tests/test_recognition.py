from __future__ import annotations

import numpy as np

from gallery import Gallery, ScoreDirection
from recognition import RecognitionEngine


class FeatureAlgorithm:
    def extract(self, roi):
        return np.array([float(np.asarray(roi).mean())])

    def match(self, query, template):
        return abs(float(query[0]) - float(template[0]))


def test_recognize_extracts_feature_before_searching_gallery():
    algorithm = FeatureAlgorithm()
    gallery = Gallery(
        {"P001": [np.array([101.0])]},
        algorithm,
        threshold=0.28,
        direction=ScoreDirection.DISTANCE,
    )
    engine = RecognitionEngine(algorithm, gallery)

    result = engine.recognize(np.full((2, 2), 101.0))

    assert result.status == "ACCEPT"
    assert result.user_id == "P001"


def test_recognize_returns_retry_before_feature_extraction_when_roi_not_ready():
    class FailingAlgorithm(FeatureAlgorithm):
        def extract(self, roi):
            raise AssertionError("invalid ROI must not reach the matcher")

    algorithm = FailingAlgorithm()
    gallery = Gallery({}, algorithm, threshold=0.28, direction=ScoreDirection.DISTANCE)
    engine = RecognitionEngine(algorithm, gallery)

    result = engine.recognize(np.zeros((2, 2)), roi_status="LOW_QUALITY")

    assert result.status == "RETRY"
    assert result.user_id is None
