# Code workspace

| Directory | Purpose |
| --- | --- |
| [palm_demo](palm_demo/README.md) | Raspberry Pi camera application, enrollment and verification |
| [pklnet](pklnet/README.md) | Third-party ROI model, currently tested offline |
| data/debug_capture | Local original captures, metadata and derived results; Git-ignored |

Start with `palm_demo/README.md`. Its `docs/` directory contains setup and
connection instructions. Installation, connection and packaging tools live in
`palm_demo/deploy/`; run them from the application root using `./deploy/...`.

Keep `palm_demo/models/`, `palm_demo/vendor/` and PKLNet weights: they are model
or algorithm dependencies, not disposable caches. Captures and experiment
results should be preserved separately from source cleanup.

The unrelated physical-target workflow is archived at `../archive/prf_tr/`.
