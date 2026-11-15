# Experiment and protocol catalogue

This index groups the records without renaming or moving them. The flat file
layout is retained because local scripts and experiment notes may refer to
these paths. For a study, read its protocol/configuration before interpreting
the result, and check whether the referenced inputs and tools are available in
a clean checkout.

## Dataset validation and analysis

- [Frozen public validation protocol](FROZEN_PUBLIC_VALIDATION_20261030.json)
- [Aggregate public validation results](FROZEN_PUBLIC_VALIDATION_20261030_AGGREGATE.json)
- [Prospective SMPD optimization split](SMPD_PROSPECTIVE_OPTIMIZATION_SPLIT_20261030.json)
- [Accuracy diagnostics](ACCURACY_DIAGNOSTICS_20261030.json)
- [Anatomical-oracle analysis](ANATOMICAL_ORACLE_20261030.json)
- [Unregistered-pseudonym analysis](PSEUDO_UNREGISTERED_20261030.json)
- [Full-score reconciliation](V26_FULL_SCORE_RECONCILIATION_20261030.json)

These records do not make the original datasets or per-sample evidence
redistributable. Keep raw palm images, ROIs, templates, feature caches and
identity-linked records out of Git.

## Device behavior and resource limits

- [Device demo optimization](DEVICE_DEMO_OPTIMIZATION_20261103.json)
- [Retained-evidence pilot](RETAINED_EVIDENCE_PILOT_20261030.json)
- [Shared-localizer session pilot](SHARED_LOCALIZER_SESSION_PILOT_20261030.json)
- [Index-capacity preflight](INDEX_CAPACITY_PREFLIGHT_20261103.json)
- [Operation-cost oracle](OPERATION_COST_ORACLE_20261030.json)
- [Pi 5 exclusive timing tree](PI5_EXCLUSIVE_TIMING_TREE_20261030.json)
- [Pi 5 oracle candidate cost](PI5_ORACLE_CANDIDATE_COST_20261030.json)

These are separate from independent-dataset validation and live-camera
performance claims.

## Rejection-policy evidence

- [Development rejection policy](DEVELOPMENT_REJECTION_POLICY_20261030.json)
- [Rejection-policy audit](REJECTION_POLICY_AUDIT_20261030.json)
- [HTTP rejection-policy checks](REJECTION_POLICY_HTTP_20261030.json)

## Enrollment and preview behavior

- [Preview strict-quality gate](DEMO_PREVIEW_STRICT_QUALITY_GATE_20261109.md)
- [Enrollment candidate selection](ENROLLMENT_CANDIDATE_SELECTION_20261109.md)
- [Enrollment capture feedback](ENROLLMENT_CAPTURE_FEEDBACK_20261109.md)
- [Enrollment capture-server gate](ENROLLMENT_CAPTURE_SERVER_GATE_20261109.md)
- [Enrollment camera recovery pause](ENROLLMENT_CAMERA_RECOVERY_PAUSE_20261109.md)
- [Enrollment refresh recovery](ENROLLMENT_REFRESH_RECOVERY_20261109.md)
- [Enrollment refresh network recovery](ENROLLMENT_REFRESH_NETWORK_RECOVERY_20261109.md)
- [Enrollment step-error resume](ENROLLMENT_STEP_ERROR_RESUME_20261109.md)

## Reading and reproducing records

The `tools/` directory contains analysis and experiment scripts, but some
historical tools depend on ignored files in `runtime/` or on local datasets
and model artifacts. Review each script's inputs before running it. Do not
move or clean `data/` or `runtime/` as part of source organization; these paths
may be referenced by active work. Keep checkpoints out of Git until their
provenance and redistribution rights are established.
