"""Recognition boundary between ROI capture and the 1:N gallery."""

from __future__ import annotations

from typing import Any

import numpy as np

from gallery import Gallery, IdentificationResult


class RecognitionEngine:
    def __init__(self, algorithm: Any, gallery: Gallery) -> None:
        self.algorithm = algorithm
        self.gallery = gallery

    def recognize(self, roi: np.ndarray, *, roi_status: str = "READY") -> IdentificationResult:
        if roi_status != "READY":
            return IdentificationResult("RETRY", None, None, None)
        feature = np.asarray(self.algorithm.extract(np.asarray(roi)))
        return self.gallery.identify(feature)

