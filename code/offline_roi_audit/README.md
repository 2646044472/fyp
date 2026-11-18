# Offline ROI geometry diagnostics

The reusable dark-background foreground proxy and crop metrics from the historical Tongji audit are in `geometry_metrics.py`. They estimate apparent coverage, an upper-region intrusion proxy and area or optional mask correlation. They do not detect identity, provide segmentation ground truth or reconstruct the old local dataset layout. Use NumPy, OpenCV and Pillow; run the synthetic check from this directory with `python -m unittest discover`. The earlier platform-specific launchers and private-data reports are not runtime dependencies.
