# Repository agent guidance

- Keep palmprint originals, ROI crops, templates, embeddings/feature caches, per-sample identity or score mappings, participant-linked capture archives, and generated runtime results out of Git remotes. Do not force-add the ignored `code/palm_demo/runtime/` tree or replace/stage local `code/data/` capture symlinks and deletions.
- Stage exact reviewed paths only; do not use `git add .` in this checkout. Exclude local caches such as `code/palm_demo/var/`.
- Before sharing experiment scripts or reports, inspect added content for real participant identifiers, sample-level biometric records, private absolute paths, and dependencies on ignored runtime-only helpers. Prefer synthetic tests and aggregate, non-identifying summaries.
- Model/checkpoint redistribution requires verified provenance and an explicit license that permits it. The local PalmSet projection candidate is marked “no redistribution”; leave it and other unverified weights local. Do not assume a weight is safe merely because it is small or excludes raw images.
- Distinguish local or synthetic experiment results from independent generalization and Pi hardware validation. Do not describe a candidate as production-ready or Pi-tested without a fresh Pi 5 validation.
- Read project run instructions and relevant dependency manifests before running tests; avoid tests that read actual captured biometric data.
