import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from palm_app.palmir_restore import Restorer, crop_roi


def test_manual_square_matches_display_bounds():
    image = Image.new("RGB", (1920, 1080))
    for x, y, expected in [(0, 0, (0, 0, 540, 540)),
                            (1, 1, (1380, 540, 1920, 1080)),
                            (.5, .5, (690, 270, 1230, 810))]:
        roi, box = crop_roi(image, dict(x=x, y=y, size=.5))
        assert box == expected
        assert roi.size == (540, 540)


@pytest.mark.parametrize("payload", [{"x": float("nan")}, {"size": 0},
                                     {"y": 2}, {"size": float("inf")}])
def test_invalid_selection_rejected(payload):
    with pytest.raises(ValueError):
        crop_roi(Image.new("RGB", (1920, 1080)), payload)


def test_snapshot_replacement_never_restores_wrong_frame():
    class Camera:
        def capture_highres(self):
            return None, Image.new("RGB", (1920, 1080)), {}
    restorer = Restorer()
    old = restorer.capture(Camera())
    new = restorer.capture(Camera())
    assert old["snapshot_id"] != new["snapshot_id"]
    with pytest.raises(ValueError, match="expired"):
        restorer.restore_snapshot(old)


def test_exported_model_runs_and_preserves_input():
    pytest.importorskip("onnxruntime")
    restorer = Restorer()
    if not restorer.model.exists():
        pytest.skip("Exported local model not present")
    image = Image.fromarray(np.random.default_rng(8).integers(0, 256, (180, 240, 3), dtype=np.uint8))
    before = image.tobytes()
    result = restorer.run(image, {})
    import base64
    restored = Image.open(io.BytesIO(base64.b64decode(result["restored"].split(",")[1])))
    assert restored.size == (128, 128)
    assert restored.mode == "RGB"
    assert image.tobytes() == before
    assert result["roi_method"] == "manual_square"


def test_reference_compares_same_input_and_has_no_acceptance_claim():
    pytest.importorskip("onnxruntime")
    restorer = Restorer()
    if not restorer.model.with_name("local-palmir-matcher.onnx").exists():
        pytest.skip("Exported matcher not present")
    image = Image.fromarray(np.random.default_rng(9).integers(0, 256, (180, 240, 3), dtype=np.uint8))
    restorer.snapshot = ("reference", image)
    restorer.enroll_reference({"snapshot_id": "reference"})
    result = restorer.restore_snapshot({"snapshot_id": "reference"})
    assert result["same_as_reference"]
    assert abs(result["comparison"]["raw_score"] - 1) < 1e-5
    assert result["comparison"]["threshold"] is None
