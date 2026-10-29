"""Experimental fixed illumination/scale ensemble for the existing palm detector.

No per-person/sample parameters. This is not selected by the application.
Palm geometry uses the existing anatomical defaults; biometric pixels are raw.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from palm_roi import HandLandmarkTracker, landmarks_to_palm_quad, warp_palm_roi
from pklnet_roi import illumination_pixels


def unrotate(points, angle, original_size):
    points = np.asarray(points, np.float32)
    x, y = points[:, 0], points[:, 1]
    w, h = original_size
    if angle == 0:
        return points.copy()
    if angle == 90:
        return np.stack((w-1-y, x), axis=1)
    if angle == 180:
        return np.stack((w-1-x, h-1-y), axis=1)
    if angle == 270:
        return np.stack((y, h-1-x), axis=1)
    raise ValueError('Only right-angle rotations are supported')


class IlluminatedLandmarkROI:
    def __init__(self, root=None):
        root = Path(root) if root else Path(__file__).resolve().parent/'models'
        self.tracker = HandLandmarkTracker(root/'palm_detection_mediapipe_2023feb.onnx',
            root/'handpose_estimation_mediapipe_2023feb.onnx', input_size=(640, 360), refine_pose=True)

    def extract(self, image):
        attempts = []
        for angle in (0, 90, 180, 270):
            rotated = image.rotate(angle, expand=True)
            view = rotated.copy()
            view.thumbnail((640, 640))
            original = np.asarray(view.convert('RGB'))
            for gamma in (False, True):
                rgb = illumination_pixels(original) if gamma else original
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                for scale in (1., .65):
                    detection = self.tracker._infer(bgr, detector_scale=scale)
                    attempts.append((float(detection.score), angle, gamma, scale, rotated.size, view.size, bgr, detection))
        best = max(attempts, key=lambda x: x[0])
        score, angle, gamma, scale, rotated_size, view_size, bgr, detection = best
        if detection.points is None:
            raise ValueError(f'Palm detection failed at unchanged threshold: score={score}')
        hand = self.tracker._handpose.infer(bgr, np.r_[detection.box, detection.points.reshape(-1)])
        if hand is None:
            raise ValueError('Hand-pose confirmation failed at unchanged threshold')
        landmarks = hand[4:67].reshape(21, 3)[:, :2] / np.asarray(view_size)
        rotated_quad = landmarks_to_palm_quad(landmarks, rotated_size, min_span_px=24, fit_to_frame=False)
        quad = unrotate(rotated_quad, angle, image.size)
        raw = np.asarray(warp_palm_roi(image, quad))
        details = dict(roi_geometry_valid=True, roi_geometry_reason='ok', roi_quad_full=quad.tolist(),
                       experimental_localizer='illuminated-landmark-ensemble-v1',
                       detection_score=score, handpose_score=float(hand[-1]), rotation=angle,
                       gamma=gamma, detector_scale=scale, detector_passes=len(attempts),
                       pklnet_roi_candidates=[dict(quad=quad.tolist(), valid=True)])
        return raw, quad, details

    def close(self):
        self.tracker.close()
