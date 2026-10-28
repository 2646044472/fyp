"""Optional, lazy CPU restoration of a manually selected camera ROI."""
import base64
import hashlib
import io
import json
import math
from pathlib import Path
import threading
import time
import uuid

import numpy as np
from PIL import Image

MODEL = Path(__file__).resolve().parents[1] / "models/local-palmir-ria.onnx"


def crop_roi(image, payload):
    """Normalized center plus square side relative to shorter image dimension."""
    values = [float(payload.get(k, default)) for k, default in
              (("x", .5), ("y", .5), ("size", .5))]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("ROI coordinates must be finite")
    x, y, size = values
    if not (0 <= x <= 1 and 0 <= y <= 1 and .1 <= size <= 1):
        raise ValueError("Invalid ROI coordinates")
    width, height = image.size
    side = max(1, round(min(width, height) * size))
    left = min(width - side, max(0, round(x * width - side / 2)))
    top = min(height - side, max(0, round(y * height - side / 2)))
    box = (left, top, left + side, top + side)
    return image.crop(box).convert("RGB"), box


def png_url(image):
    output = io.BytesIO()
    image.save(output, format="PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


class Restorer:
    def __init__(self, model=MODEL):
        self.model = Path(model)
        self.lock = threading.Lock()
        self.session = None
        self.snapshot_lock = threading.Lock()
        self.snapshot = None
        self.matcher = None
        self.reference = None
        self.don = None

    def _don_feature(self, image):
        from palm_app.biometric import load_algorithm
        from pklnet_roi import normalize_roi
        if self.don is None:
            self.don = load_algorithm(self.model.parents[1] / "vendor/palmprint-recognition-python", "DoN")
        normalized, _ = normalize_roi(np.asarray(image.convert("L")))
        return self.don.extract(normalized)

    def capture(self, camera):
        with self.snapshot_lock:
            _, image, _ = camera.capture_highres()
            token = uuid.uuid4().hex
            self.snapshot = (token, image.copy())
            return dict(snapshot_id=token, source=png_url(image), source_size=image.size)

    def restore_snapshot(self, payload):
        with self.snapshot_lock:
            if self.snapshot is None or payload.get("snapshot_id") != self.snapshot[0]:
                raise ValueError("Snapshot expired; capture a new image")
            image = self.snapshot[1]
        result = self.run(image, payload)
        result["same_as_reference"] = bool(self.reference and payload.get("snapshot_id") == self.reference[0])
        return result

    def _load_matcher(self):
        if self.matcher is not None:
            return
        import onnxruntime as ort
        self._load()
        path = self.model.with_name("local-palmir-matcher.onnx")
        manifest = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["onnx_sha256"]:
            raise RuntimeError("Matcher checksum mismatch")
        if manifest["checkpoint_sha256"] != self.manifest.get("training_matcher_checkpoint_sha256"):
            raise RuntimeError("Matcher differs from the restoration training matcher")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.matcher = ort.InferenceSession(str(path), sess_options=options,
                                           providers=["CPUExecutionProvider"])

    def enroll_reference(self, payload):
        with self.snapshot_lock:
            if self.snapshot is None or payload.get("snapshot_id") != self.snapshot[0]:
                raise ValueError("Snapshot expired; capture a new image")
            token, image = self.snapshot
        with self.lock:
            self._load_matcher()
            roi, _ = crop_roi(image, payload)
            roi = roi.resize((128, 128), Image.Resampling.BILINEAR)
            tensor = np.asarray(roi, dtype=np.float32).transpose(2, 0, 1)[None] / 255
            self.reference = (token, self.matcher.run(None, {"image": tensor})[0][0], self._don_feature(roi))
            return dict(reference_ready=True, message="Reference set; capture a different image to compare")

    def _load(self):
        if self.session is not None:
            return
        import onnxruntime as ort
        self.manifest = json.loads(self.model.with_suffix(".json").read_text(encoding="utf-8"))
        if hashlib.sha256(self.model.read_bytes()).hexdigest() != self.manifest["onnx_sha256"]:
            raise RuntimeError("Restoration model checksum mismatch")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(self.model), sess_options=options,
                                           providers=["CPUExecutionProvider"])

    def run(self, image, payload):
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Restoration is busy; wait for the previous result")
        try:
            self._load()
            roi, box = crop_roi(image, payload)
            size = self.manifest["input_size"]
            original = roi.resize((size, size), Image.Resampling.BILINEAR)
            from pklnet_roi import normalize_roi
            _, quality = normalize_roi(np.asarray(original.convert("L")))
            quality["low_contrast_warning"] = quality["contrast"] < 12
            quality["interpretation"] = "Engineering warning only; does not detect a palm or prove eligibility"
            tensor = np.asarray(original, dtype=np.float32).transpose(2, 0, 1)[None] / 255
            start = time.perf_counter()
            result = self.session.run(None, {"image": tensor})[0]
            elapsed = (time.perf_counter() - start) * 1000
            if result.shape != tensor.shape or not np.isfinite(result).all():
                raise RuntimeError("Invalid restoration output")
            restored = Image.fromarray(np.rint(result[0].transpose(1, 2, 0).clip(0, 1) * 255).astype(np.uint8))
            comparison = None
            don_comparison = None
            if self.reference is not None:
                self._load_matcher()
                reference = self.reference[1]
                raw_feature = self.matcher.run(None, {"image": tensor})[0][0]
                restored_feature = self.matcher.run(None, {"image": result})[0][0]
                def cosine(feature):
                    return float(np.clip(np.dot(feature, reference) /
                                         (np.linalg.norm(feature) * np.linalg.norm(reference)), -1, 1))
                raw_score, restored_score = cosine(raw_feature), cosine(restored_feature)
                comparison = dict(raw_score=raw_score, restored_score=restored_score,
                                  delta=restored_score - raw_score, threshold=None,
                                  interpretation="Cosine similarity only; no camera-calibrated acceptance threshold")
                reference_don = self.reference[2]
                raw_distance = float(self.don.match(self._don_feature(original), reference_don))
                restored_distance = float(self.don.match(self._don_feature(restored), reference_don))
                don_comparison = dict(raw_distance=raw_distance, restored_distance=restored_distance,
                                      improvement=raw_distance-restored_distance, lower_is_better=True,
                                      threshold=None, matcher="DoN")
            return dict(original=png_url(original), restored=png_url(restored), comparison=comparison,
                        don_comparison=don_comparison,
                        source=png_url(image), roi_box=box, source_size=image.size,
                        inference_ms=round(elapsed, 1), model=self.manifest["label"],
                        checkpoint_epoch=self.manifest["checkpoint_epoch"],
                        checkpoint_sha256=self.manifest["checkpoint_sha256"],
                        roi_method="manual_square", input_size=size, input_quality=quality,
                        runtime_warning="Low-contrast blur may be numerically sensitive; no acceptance threshold is deployed")
        finally:
            self.lock.release()


RESTORER = Restorer()
