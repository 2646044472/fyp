"""Approximate the upstream PeakValleyDetector decision on saved contours."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
CAPTURE = ROOT.parent / "code" / "data" / "debug_capture" / "20260916T152121Z"
TONGJI = ROOT / "raw_extract" / "session1"


def get_contour(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    image = cv2.resize(image, (512, 384))
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.int32)
    image = cv2.filter2D(image, 0, kernel)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    _, binary = cv2.threshold(ycrcb[:, :, 1], 0, 255, cv2.THRESH_OTSU)
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, element)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return max(contours, key=cv2.contourArea).reshape(-1, 2)


def next_inflection(points: np.ndarray, start: int, stop: int, step: int, maximum: bool) -> int:
    reverse = 1 if step > 0 else -1
    sign = 1 if maximum else -1
    cur = start + step
    while reverse * cur < reverse * stop:
        if sign * int(points[cur, 1]) <= sign * int(points[cur - step, 1]) and reverse * int(points[cur, 0]) < reverse * int(points[cur - step, 0]):
            datum = -2**31 if maximum else 2**31 - 1
            index = cur
            i = cur - step
            while reverse * i <= reverse * cur:
                if sign * int(points[i, 1]) > sign * datum:
                    datum = int(points[i, 1])
                    index = i
                i += reverse
            return index
        cur += step
    return 0


def detect(points: np.ndarray, step_size: int) -> dict[str, object]:
    peaks = [tuple(points[0])]
    valleys: list[tuple[int, int]] = []
    for side in (1, -1):
        step = step_size * side
        start = 0 if side == 1 else len(points) - 1
        stop = len(points) // 2
        founded = 0
        is_peak = False
        start += 2 * step
        while side * start < side * stop:
            start = next_inflection(points, start, stop, step, not is_peak)
            if start == 0:
                break
            point = tuple(int(v) for v in points[start])
            if side == 1:
                (peaks.insert(0, point) if is_peak else valleys.insert(0, point))
            else:
                (peaks.append(point) if is_peak else valleys.append(point))
            founded += 1
            start += 2 * step
            is_peak = not is_peak
            if founded >= 4:
                break
    monotonic_peaks = all(peaks[i][0] <= peaks[i + 1][0] for i in range(len(peaks) - 1))
    monotonic_valleys = all(valleys[i][0] <= valleys[i + 1][0] for i in range(len(valleys) - 1))
    shape_ok = len(peaks) >= 5 and len(peaks) > 3 and (peaks[2][1] < peaks[1][1] and peaks[2][1] < peaks[3][1] and peaks[1][1] < peaks[0][1] and peaks[3][1] < peaks[4][1])
    return {"step": step_size, "peaks": len(peaks), "valleys": len(valleys), "total": len(peaks) + len(valleys), "peak_x_monotonic": monotonic_peaks, "valley_x_monotonic": monotonic_valleys, "shape_check": shape_ok, "peaks_xy": peaks, "valleys_xy": valleys}


for name, path in [("capture_001", CAPTURE / "sample_001" / "raw.png"), ("tongji_00001", TONGJI / "00001.tiff")]:
    contour = get_contour(path)
    print(name, "contour_points", len(contour))
    for step in (5, 8, 10):
        print(detect(contour, step))
