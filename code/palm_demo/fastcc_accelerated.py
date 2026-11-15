"""FastCC kernels with the original binary codes and shifted-overlap scores."""
import cv2
import numpy as np
from scipy.signal import convolve2d
from palmprint.algorithms.fastcc import FastCCAlgorithm
import threading


class AcceleratedFastCC:
    def __init__(self, reference, *, track_dispatch=False):
        self.reference = reference
        self.name = reference.name
        self.kernels = reference.kernels
        self.track_dispatch = bool(track_dispatch)
        self.instance_override_dispatches = 0
        self._dispatch_lock = threading.Lock()
        self._difference = np.ascontiguousarray((self.kernels[0] - self.kernels[3])[::-1, ::-1])
        dy, dx = np.meshgrid(np.arange(-4, 5), np.arange(-4, 5), indexing='ij')
        self._dy, self._dx = dy, dx
        self._area = (32 - abs(dy)) * (32 - abs(dx))

    def extract(self, image):
        image = np.asarray(image)
        if image.shape != (128, 128) or image.dtype != np.uint8:
            return self.reference.extract(image)
        values = image.astype(np.float64)
        response = cv2.filter2D(values, cv2.CV_64F, self._difference,
                                borderType=cv2.BORDER_CONSTANT)[::4, ::4]
        result = response > 0
        # FFT/direct filter accumulation can disagree at numerical ties. Re-run
        # only those 17x17 patches using the exact reference convolution order.
        tied = np.argwhere(np.abs(response) <= 1e-8)
        if len(tied):
            padded = np.pad(values, 8)
            for y, x in tied:
                patch = padded[y*4:y*4+17, x*4:x*4+17]
                first = convolve2d(patch, self.kernels[0], mode='valid')[0, 0]
                second = convolve2d(patch, self.kernels[3], mode='valid')[0, 0]
                result[y, x] = first > second
        return result

    def match(self, left, right):
        # Instance-level replacements are used by gallery-adaptive matchers.
        # Checking only the class method silently bypasses those replacements.
        instance_match = getattr(self.reference, "__dict__", {}).get("match")
        if instance_match is not None:
            if self.track_dispatch:
                with self._dispatch_lock:
                    self.instance_override_dispatches += 1
            return instance_match(left, right)
        # The vectorized kernel below is a faithful FastCC implementation,
        # but must not replace an opt-in FastCC subclass's distinct metric.
        if type(self.reference).match is not FastCCAlgorithm.match:
            return self.reference.match(left, right)
        left, right = np.asarray(left), np.asarray(right)
        if left.shape != (32, 32) or right.shape != (32, 32):
            return self.reference.match(left, right)
        left, right = left.astype(bool).astype(np.float32), right.astype(bool).astype(np.float32)
        correlation = np.rint(cv2.matchTemplate(np.pad(left, 4), right, cv2.TM_CCORR))[::-1, ::-1]
        def sums(array, dy, dx):
            integral = cv2.integral(array)
            y0, y1 = np.maximum(-dy, 0), 32-np.maximum(dy, 0)
            x0, x1 = np.maximum(-dx, 0), 32-np.maximum(dx, 0)
            return integral[y1, x1]-integral[y0, x1]-integral[y1, x0]+integral[y0, x0]
        mismatch = sums(left, self._dy, self._dx) + sums(right, -self._dy, -self._dx) - 2*correlation
        return float(np.min(mismatch/self._area))
