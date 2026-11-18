"""Dark-background ROI geometry diagnostics (not segmentation ground truth)."""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image

def make_hand_mask(image: Image.Image) -> np.ndarray:
    """Approximate hand foreground against Tongji's dark background."""
    rgb = np.asarray(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # The Tongji originals use a dark display background.  Otsu plus a low
    # floor is intentionally conservative; this is a diagnostic proxy, not GT.
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = np.where(gray > max(12, int(_)), 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = np.where(labels == keep, 255, 0).astype(np.uint8)
    return mask

def geometry_metrics(mask_warp: np.ndarray, quad: np.ndarray, raw_size: tuple[int, int], *, reference: np.ndarray | None = None) -> dict[str, float | None]:
    fg = mask_warp > 0
    total = int(fg.sum())
    upper = int(fg[:24, :].sum())
    # Diagnostic proxies: occupancy of the normalized ROI, and occupancy in
    # its finger-side top band.  They do not replace a hand/palm segmentation GT.
    metrics: dict[str, float | None] = {
        "roi_foreground_coverage_pct": 100.0 * total / fg.size,
        "finger_intrusion_proxy_pct": 100.0 * upper / max(total, 1),
        "roi_quad_area_pct_of_image": 100.0 * abs(cv2.contourArea(quad.astype(np.float32))) / (raw_size[0] * raw_size[1]),
    }
    if reference is not None:
        a = cv2.resize(mask_warp.astype(np.float32), (128, 128)).ravel()
        b = np.asarray(reference, dtype=np.float32).ravel()
        if np.std(a) > 1e-6 and np.std(b) > 1e-6:
            metrics["mask_correlation_to_reference"] = float(np.corrcoef(a, b)[0, 1])
        else:
            metrics["mask_correlation_to_reference"] = None
    return metrics
