"""Synchronous, in-memory primary-view RTM localization; no camera or persistence."""
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import threading

import cv2
import numpy as np
from PIL import Image

from palm_app.palm_roi import landmarks_to_palm_quad
from palm_app.common import crop_and_normalize

_ROOT = Path(__file__).resolve().parents[1] / 'runtime'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_locator = _load('rtm_same_frame_locator', _ROOT / 'rtmpose-hand-baseline-X-20261107/locator.py')
_choose = _load('rtm_same_frame_dedup', _ROOT / 'rtmpose-anatomical-dedup-X-20261107/dedup.py').choose


@dataclass(frozen=True)
class Frame:
    """RGB uint8 pixels are copied on construction to isolate the capture buffer."""
    frame_id: object
    timestamp: float
    pixels: np.ndarray

    def __post_init__(self):
        pixels = np.array(self.pixels, copy=True)
        if pixels.dtype != np.uint8 or pixels.ndim != 3 or pixels.shape[2] != 3 or min(pixels.shape[:2]) == 0:
            raise ValueError('pixels must be a nonempty RGB uint8 image')
        pixels.setflags(write=False)
        object.__setattr__(self, 'pixels', pixels)


class Localizer:
    def __init__(self, detector, pose):
        self.detector, self.pose = detector, pose
        self._lock = threading.Lock()

    @classmethod
    def from_models(cls, detector_path, pose_path):
        import onnxruntime as ort
        cv2.setNumThreads(1)
        options = ort.SessionOptions()
        options.intra_op_num_threads = options.inter_op_num_threads = 1
        options.add_session_config_entry('session.intra_op.allow_spinning', '0')
        options.add_session_config_entry('session.inter_op.allow_spinning', '0')
        def session(path):
            return ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
        return cls(session(detector_path), session(pose_path))

    def process(self, frame, cancelled=lambda: False):
        """Process each call independently, including repeated IDs. Cancellation is cooperative.

        Calls on one instance cannot overlap; inference already in progress cannot be interrupted.
        """
        if not self._lock.acquire(blocking=False):
            raise RuntimeError('localizer busy')
        try:
            return self._process(frame, cancelled)
        finally:
            self._lock.release()

    def _process(self, frame, cancelled):
        def result(status, **kwargs):
            return dict(frame_id=frame.frame_id, timestamp=frame.timestamp, status=status, **kwargs)
        if cancelled(): return result('cancelled')
        view = Image.fromarray(frame.pixels, 'RGB')
        bgr = cv2.cvtColor(frame.pixels, cv2.COLOR_RGB2BGR)
        blob, ratio = _locator.detector_input(bgr)
        outputs = self.detector.run(None, {self.detector.get_inputs()[0].name: blob})
        if cancelled(): return result('cancelled')
        if len(outputs) != 2 or outputs[0].ndim != 3 or outputs[0].shape[0] != 1 or outputs[0].shape[-1] != 5 or outputs[1].shape != outputs[0].shape[:2] or not all(np.isfinite(x).all() for x in outputs):
            raise ValueError('invalid detector output')
        indices = np.flatnonzero((outputs[0][0, :, 4] > .3) & (outputs[1][0] == 0))
        entry = {'qualified': {}, 'cap_exceeded': len(indices) > 10}
        proposals = []
        if not entry['cap_exceeded']:
            for k in indices:
                if cancelled(): return result('cancelled')
                box = outputs[0][0, k, :4] / ratio
                rec = {'index': int(k), 'detector_score': float(outputs[0][0, k, 4]), 'status': 'rejected'}
                if not (box[2:] > box[:2]).all():
                    rec['reason'] = 'invalid box'; proposals.append(rec); continue
                pb, center, scale, _ = _locator.pose_input(bgr, box)
                po = self.pose.run(None, {self.pose.get_inputs()[0].name: pb})
                if cancelled(): return result('cancelled')
                if len(po) != 2 or any(x.shape != (1, 21, 512) or not np.isfinite(x).all() for x in po):
                    raise ValueError('invalid pose output')
                points, scores = _locator.decode_pose(po, center, scale)
                try:
                    if not (scores[[0, 5, 9, 17]] >= .3).all(): raise ValueError('required_ROI_keypoint_score_below_0.3')
                    lm = points / np.array(view.size)
                    landmarks_to_palm_quad(lm, (320, 240), width_scale=2., height_scale=2., min_span_px=32, fit_to_frame=True)
                    quad = landmarks_to_palm_quad(lm, (640, 480), width_scale=1.3, height_scale=1.3, min_span_px=32, fit_to_frame=True) * np.array(view.size) / np.array((640, 480))
                    crop_and_normalize(view, roi_quad=quad)
                    rec.update(status='qualified', points_view=points, landmarks=lm, quad_view=quad)
                    entry['qualified'][str(k)] = rec
                except (ValueError, RuntimeError, AssertionError) as exc:
                    rec['reason'] = str(exc)
                proposals.append(rec)
        status, winner, pairs = _choose(entry)
        if winner is None: return result(status, proposals=proposals, pairs=pairs)
        try:
            quad = landmarks_to_palm_quad(winner['landmarks'], view.size, width_scale=1.3, height_scale=1.3, min_span_px=32, fit_to_frame=True)
            pixels, quality = crop_and_normalize(view, roi_quad=quad)
        except (ValueError, RuntimeError, AssertionError) as exc:
            return result('processing_failure', reason=str(exc), proposals=proposals, pairs=pairs)
        if cancelled(): return result('cancelled')
        return result(status, roi=pixels, quad=quad, quality=quality, proposals=proposals, pairs=pairs)
