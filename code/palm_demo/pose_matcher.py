"""Versioned FastCC matcher with a fixed full-image query pose bank."""
from __future__ import annotations

import importlib.util
from typing import Any

import cv2
import numpy as np
from PIL import Image

from pklnet_roi import PKLNET_ROOT, normalize_roi

POSE_MATCHER_NAME = 'FastCCPoseNearest-v1'
POSES = ((0,1),(-12,1),(12,1),(0,.85),(0,1.15),(-12,.85),(-12,1.15),(12,.85),(12,1.15))


class FastCCPoseMatcher:
    """Each identity gets the same poses; gallery uses original enrollment ROIs.

    A feature is a 9x32x32 int8 bank. Invalid optional poses are -1, never zero
    codes. Slot zero is always the unmodified, normalized base ROI. Ranking uses
    the nearest of the five enrollment samples; there is no acceptance threshold.
    """
    name = POSE_MATCHER_NAME

    def __init__(self, base: Any):
        self.base = base
        spec=importlib.util.spec_from_file_location('pose_matcher_geometry',PKLNET_ROOT/'roiExtractor.py')
        self.geometry=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.geometry)

    def extract(self, roi: np.ndarray) -> np.ndarray:
        base=np.asarray(self.base.extract(roi),np.int8)
        bank=np.full((len(POSES),*base.shape),-1,np.int8)
        bank[0]=base
        return bank

    def extract_with_context(self, full: Image.Image, quad: np.ndarray, normalized_roi: np.ndarray) -> np.ndarray:
        bank=self.extract(normalized_roi)
        q=np.asarray(quad,np.float32)
        if q.shape!=(4,2) or not np.isfinite(q).all():raise ValueError('Invalid palm quadrilateral')
        bgr=cv2.cvtColor(np.asarray(full.convert('RGB')),cv2.COLOR_RGB2BGR)
        center=q.mean(0)
        for i,(angle,scale) in enumerate(POSES[1:],1):
            rad=np.deg2rad(angle)
            rotation=np.array([[np.cos(rad),-np.sin(rad)],[np.sin(rad),np.cos(rad)]])
            candidate=((q-center)@rotation.T*scale+center).astype(np.float32)
            if not ((candidate>=0).all() and (candidate[:,0]<full.width).all() and (candidate[:,1]<full.height).all()):continue
            raw=self.geometry.getROIimg(bgr,candidate)
            if raw is None:continue
            try:roi=normalize_roi(raw)[0]
            except ValueError:continue
            bank[i]=self.base.extract(roi)
        return bank

    @staticmethod
    def _validate(bank: np.ndarray) -> np.ndarray:
        bank=np.asarray(bank)
        if bank.shape!=(len(POSES),32,32):raise ValueError('Incompatible pose template shape')
        if not np.isin(bank,[-1,0,1]).all():raise ValueError('Invalid pose feature values')
        if (bank[0]<0).any():raise ValueError('Missing original ROI feature')
        for item in bank:
            if (item<0).any() and not (item==-1).all():raise ValueError('Partially invalid pose feature')
        return bank

    def match(self, probe: np.ndarray, candidate: np.ndarray) -> float:
        probe=self._validate(probe);candidate=self._validate(candidate)
        base=candidate[0].astype(bool)
        return min(float(self.base.match(p.astype(bool),base)) for p in probe if p[0,0]>=0)

    def score_enrollment(self, probe: np.ndarray, enrolled: np.ndarray) -> float:
        if not len(enrolled):raise ValueError('At least one enrollment feature is required')
        return min(self.match(probe,candidate) for candidate in enrolled)
