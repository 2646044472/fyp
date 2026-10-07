# Palmprint project workspace

## Active application

`code/palm_demo/` is the Raspberry Pi camera demo. Start with its
[README](code/palm_demo/README.md).

- `debug_ui.py`: camera web UI, enrollment and verification.
- `palm_app/palm_roi.py`, `palm_app/roi_quality.py`, `palm_app/live_roi.py`: dynamic ROI, quality gate and preview tracking.
- `palm_app/biometric.py`: matcher loading and feature comparison.
- `palm_app/common.py`: shared normalization, paths, templates and logs.
- `models/` and local `vendor/`: runtime model and matcher dependencies.
- `deploy/palm-debug-ui.service`: Pi service configuration.
- `tools/`, `tests/`: collection, analysis and verification tools.

The checked-in service uses dynamic ROI and the web UI currently selects DoN.
The former Fast-CC CLI is archived in `archive/palm_demo_legacy/`. This describes repository configuration, not a
verified copy of the software currently running on the Pi.

## ROI experiments

`code/pklnet/` contains the PKLNet model and ROI extractor. It has been tested
offline but is not integrated into the camera web UI.

The local, Git-ignored `offline_tongji_roi_audit/` contains comparison runners,
downloaded dependencies, extracted datasets and results. Its PKLNet runners are
`run_pklnet_tongji.py` and `run_pklnet_debug_capture.py`. Keep this directory when
reproducing those experiments; it is not a Pi runtime dependency.

`external/` holds local third-party comparison implementations.

## Data and reports

- `code/data/debug_capture/`: local captured originals, ROIs, metadata and results.
- `code/palm_demo/runtime/`: local runtime captures, templates and logs.
- `docs/`: experiment reports, including the two-hand pilot analysis.
- `research/`, `.research/`, `minutes/`: research notes and project records.

Preserve capture originals, model weights, experiment manifests and results.
The actual September capture directory is
`code/data/debug_capture/20260916T152121Z/`.

## Separate work and generated files

`archive/prf_tr/` is an archived physical-target research workflow, not a dependency
of the palm demo. `.worktrees/` contains isolated working checkouts and should
be managed separately rather than deleted as cache.

Python `__pycache__/`, `.pytest_cache/` and compiler `.obj` files are generated
and can be rebuilt. Large ignored directories remain local even though they do
not appear in Git changes.
