import json
import sys
from pathlib import Path

import numpy as np


APP_DIR = Path(__file__).parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from palm_roi import (  # noqa: E402
    PalmROIError,
    ROIStatus,
    frame_diagnostics_match,
    landmarks_to_palm_quad_diagnostics,
)


def normalized_landmarks():
    points = np.zeros((21, 2), dtype=np.float32)
    points[0] = (0.50, 0.10)  # wrist
    points[5] = (0.35, 0.55)  # index MCP
    points[9] = (0.50, 0.58)  # middle MCP
    points[13] = (0.62, 0.57)  # ring MCP
    points[17] = (0.70, 0.54)  # pinky MCP
    return points


def test_quad_diagnostics_reports_raw_final_and_boundary_factor():
    result = landmarks_to_palm_quad_diagnostics(
        normalized_landmarks(),
        image_size=(100, 80),
        width_scale=2.0,
        height_scale=2.0,
        center_offset=0.30,
        min_span_px=10.0,
        fit_to_frame=True,
    )

    assert result.raw_quad.shape == (4, 2)
    assert result.final_quad.shape == (4, 2)
    assert result.out_of_frame is True
    assert 0.0 < result.fit_factor < 1.0
    assert np.all(result.final_quad >= 0.0)
    assert np.all(result.final_quad[:, 0] < 100.0)
    assert np.all(result.final_quad[:, 1] < 80.0)
    assert result.final_width_px < result.raw_width_px

    try:
        landmarks_to_palm_quad_diagnostics(
            normalized_landmarks(),
            image_size=(100, 80),
            width_scale=2.0,
            height_scale=2.0,
            center_offset=0.30,
            min_span_px=10.0,
            fit_to_frame=False,
        )
    except PalmROIError as error:
        assert "outside the frame" in str(error)
    else:
        raise AssertionError("out-of-frame ROI must be rejected when fitting is disabled")


def test_quad_diagnostics_can_be_serialized_without_numpy_values():
    result = landmarks_to_palm_quad_diagnostics(
        normalized_landmarks(),
        image_size=(400, 300),
        width_scale=1.0,
        height_scale=1.0,
        min_span_px=10.0,
        fit_to_frame=True,
    )

    payload = result.as_dict()
    encoded = json.dumps(payload)

    assert encoded
    assert payload["raw_quad"] != payload["final_quad"] or payload["fit_factor"] == 1.0


def test_roi_status_serializes_geometry_diagnostics():
    result = landmarks_to_palm_quad_diagnostics(
        normalized_landmarks(),
        image_size=(400, 300),
        width_scale=1.0,
        height_scale=1.0,
        min_span_px=10.0,
        fit_to_frame=True,
    )
    status = ROIStatus(
        result.final_quad,
        "tracking",
        geometry_diagnostics=result.as_dict(),
    )

    payload = status.as_dict()

    assert payload["roi_geometry_diagnostics"]["fit_factor"] == result.fit_factor
    assert payload["roi_geometry_diagnostics"]["final_quad"] == result.as_dict()["final_quad"]


def test_frame_diagnostics_match_requires_accepted_same_timestamp():
    diagnostics = {"frame_timestamp_ms": 1234, "reason": "accepted"}

    assert frame_diagnostics_match(diagnostics, 1234) is True
    assert frame_diagnostics_match(diagnostics, 1235) is False
    assert frame_diagnostics_match({"frame_timestamp_ms": 1234, "reason": "no_candidate"}, 1234) is False
