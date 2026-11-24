"""Opt-in OpenCV DNN CPU/Winograd backend for an unchanged FP32 PKLNet graph.

Experimental: floating-point accumulation differs; verify on the target CPU.
No production factory selects this class. Use only a verified isolated graph.
"""
import hashlib
import importlib.util
import json
import cv2
import numpy as np
from pklnet_roi import PKLNetROI, PKLNetUnavailable, MODEL_GEOMETRY_VERSION


class DNNSession:
    def __init__(self, path):
        self.net = cv2.dnn.readNetFromONNX(str(path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.net.enableWinograd(True)
        self.names = set(self.net.getUnconnectedOutLayersNames())
        if not {'keypoints', 'heatmap_keypoints', 'fc_keypoints'}.issubset(self.names):
            raise ValueError('Missing PKLNet diagnostic outputs')

    def run(self, names, inputs):
        value = inputs['image']
        if value.shape != (1, 3, 400, 300) or value.dtype != np.float32:
            raise ValueError('Expected original PKLNet FP32 input geometry')
        if not set(names).issubset(self.names):
            raise ValueError('Unknown diagnostic output')
        self.net.setInput(value)
        return self.net.forward(names)


class OpenCVDNNROI(PKLNetROI):
    def _ensure_loaded(self):
        if self._session is not None:
            return
        if self.policy == 'legacy':
            raise PKLNetUnavailable('Experimental DNN backend requires diagnostic geometry')
        with self._load_lock:
            if self._session is not None:
                return
            path = self.root/'pklnet-keypoints-diagnostics.onnx'
            metadata = json.loads(path.with_suffix('.json').read_text())
            if (metadata.get('roi_geometry') != MODEL_GEOMETRY_VERSION
                    or metadata.get('input_shape') != [1, 3, 400, 300]
                    or metadata.get('diagnostic_schema') != 'pklnet-branches-v1'):
                raise PKLNetUnavailable('Incompatible DNN model geometry/schema')
            for artifact, key in ((path, 'onnx_sha256'), (self.weights, 'weights_sha256')):
                if hashlib.sha256(artifact.read_bytes()).hexdigest() != metadata[key]:
                    raise PKLNetUnavailable('DNN model artifact checksum mismatch')
            session = DNNSession(path)
            spec = importlib.util.spec_from_file_location('pklnet_dnn_geometry', self.root/'roiExtractor.py')
            geometry = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(geometry)
            self._roi_extractor = geometry
            self._session = session
            self.backend_used = 'opencv-dnn-experimental'
