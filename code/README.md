# Code workspace

| Directory | Purpose |
| --- | --- |
| [palm_demo](palm_demo/README.md) | Raspberry Pi camera application, enrollment and verification |
| [pklnet](pklnet/README.md) | Third-party ROI model for deferred extraction and offline benchmark |
| [offline_roi_audit](offline_roi_audit/README.md) | Reusable crop coverage and geometry diagnostics |
| [experiment_registry](experiment_registry/README.md) | Experiment dependency validation and synthetic tests |
| data/debug_capture | Local original captures, metadata and derived results; Git-ignored |

Start with `palm_demo/README.md`. Its `docs/` directory contains setup and
connection instructions. Installation, connection and packaging tools live in
`palm_demo/deploy/`; run them from the application root using `./deploy/...`.

Keep `palm_demo/models/`, `palm_demo/vendor/` and PKLNet weights: they are model
or algorithm dependencies, not disposable caches. Captures and experiment
results should be preserved separately from source cleanup.

School-facing research code and results are indexed in [gitea-um](../gitea-um/README.md). Retired launchers and workstation-only reports are not part of the active code tree.
