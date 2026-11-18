# FYP: Palmprint recognition

This repository combines an active Raspberry Pi demo with dataset and model experiments, research notes, and archived work. Directory paths are intentionally left in place because scripts and experiment records may depend on them.

## Start here

- [School project handoff](gitea-um/README.md): original meeting notes and demo code, plus dated weekly progress and offline evaluation findings.

- [`current.md`](current.md): latest handoff and project status.
- [`AGENTS.md`](AGENTS.md): repository guardrails for data handling, experiments, and Pi validation.
- [`code/README.md`](code/README.md): code-workspace map.
- [`code/palm_demo/README.md`](code/palm_demo/README.md): active camera demo, matcher options, experiment summaries, setup, tests, and deployment notes.
- [`code/pklnet/README.md`](code/pklnet/README.md): PKLNet ROI model and extractor.

## Dataset experiments

For dataset work, start with `code/palm_demo/docs/protocols/`, then follow each protocol to its relevant script under `code/palm_demo/tools/`. Check the protocol's data source, split, and limitations before interpreting a result. The `code/palm_demo/runtime/` directory holds local experiment runs, checkpoints, caches, and outputs; some scripts use those exact paths.

- `code/data/`: capture and evaluation datasets. Preserve the current files and local links; do not move or publish raw palm images, ROIs, templates, feature caches, or per-sample identity/score records without provenance review and explicit approval.
- `code/palm_demo/runtime/`: local generated results and model artifacts. Keep out of Git; do not force-add or relocate it.
- `offline_tongji_roi_audit/`: separate offline comparison workspace, not a Pi runtime dependency.

## Repository map

| Path | Purpose |
| --- | --- |
| `code/palm_demo/` | Active Raspberry Pi camera demo, application code, tests, tools, and experiment protocols. |
| `code/pklnet/` | PKLNet ROI model and extractor. |
| `docs/meeting minutes/`, `minutes/`, `minutes_note/` | Dated meeting and project notes. |
| `research/`, `.research/`, `idea/` | Research notes, reconciliation, and proposed directions. |
| `archive/` | Historical workflows. These are not the active deployment path. |

## Working safely

Keep captures, model weights, experiment manifests, and results in their established locations. Avoid broad staging commands: this checkout may contain local dataset links, uncommitted experiments, and generated files. Stage only reviewed source or aggregate documentation. Treat local replay results as distinct from independent generalization or fresh Pi 5 validation.
