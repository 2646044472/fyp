"""Review the whole retained candidate pool when the operator selects photos."""
from base64 import b64decode
from io import BytesIO
from statistics import median

from ranked_window import refine_set, select_set


def image_quality(photo, candidate):
    import cv2
    import numpy as np
    from PIL import Image

    roi = np.asarray(photo.payload["roi"])
    if roi.shape != (128, 128):
        return candidate.sharpness, candidate.contrast, 1.0
    smoothed = cv2.GaussianBlur(roi, (3, 3), 0)
    laplacian = np.abs(cv2.Laplacian(smoothed, cv2.CV_32F))[8:-8, 8:-8]
    # Use the median of 16 palm patches so a single strong edge, reflection
    # or isolated noisy patch cannot win on its own.
    patch_energy = laplacian.reshape(4, 28, 4, 28).mean(axis=(1, 3))
    detail = float(np.median(patch_energy))
    low, high = np.percentile(roi, (10, 90))
    contrast = float(high - low)
    gray = float(np.median(roi))
    # Keep the operating range soft so different skin tones or lighting can
    # still produce a complete set. Penalize washed-out or very dark regions.
    offset = max(0., 110. - gray, gray - 185.)
    dark = float(np.mean(roi <= 5))
    bright = float(np.mean(roi >= 250))
    preview = photo.payload.get("station_review_rgb")
    if preview:
        try:
            with Image.open(BytesIO(b64decode(preview))) as image:
                rgb = np.asarray(image.convert("RGB"))
            mask = np.zeros(rgb.shape[:2], np.uint8)
            cv2.fillConvexPoly(mask, np.rint(photo.roi_quad).astype(np.int32), 1)
            pixels = rgb[mask != 0]
            if pixels.size:
                bright = max(bright, float(np.mean(np.any(pixels >= 250, axis=1))))
        except (OSError, ValueError):
            pass  # Grayscale metrics remain available on older candidates.
    exposure = max(0., 1. - offset / 90. - 2. * (bright + dark))
    return detail, contrast, exposure


def rank_final(window, picked, payloads):
    candidates = tuple(window.pool) + tuple(window.retained)
    measured = {c.frame_id: image_quality(payloads[c.frame_id], c) for c in candidates}
    ref_detail = max(1e-6, median(values[0] for values in measured.values()))
    ref_contrast = max(1e-6, median(values[1] for values in measured.values()))
    quality = {}
    for c in candidates:
        detail, contrast, exposure = measured[c.frame_id]
        detail = min(1., detail / (1.5 * ref_detail))
        contrast = min(1., contrast / (1.5 * ref_contrast))
        quality[c.frame_id] = .55 * detail + .20 * contrast + .25 * exposure
    alternative = select_set(window.pool, retained=window.retained, count=window.target_count, frame_quality=quality)
    return refine_set(picked, candidates, quality, retained=window.retained, alternative=alternative)
