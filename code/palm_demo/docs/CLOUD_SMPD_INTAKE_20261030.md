# Cloud SMPD intake audit, 2026-10-30

The user authorized private Codex cloud transfer and optimization of the palm data, confirmed the data can be used, and authorized stopping the original local task. Local tasks must remain stopped and production services unchanged. This records user authorization; dataset/model licensing has not been independently verified. No biometric originals or model binaries belong in this experiment's Git commits.

## Observed cloud state

- `/workspace/fyp` initially checked out `work` at `797bb47cb67ddf75620861166a487ec6bfddc87c`; remote main independently returned that same SHA.
- Fetched experiment commit `255d9186b0721073567a6a25b57b83973294735e` successfully and created `experiment/cloud-smpd-audit-20261030` from it. There are 21 changed paths between main and that experiment commit. No AGENTS.md was found under `/workspace`.
- Existing untracked `code/palm_demo/.venv/` is preserved. Its Python is 3.12.14, NumPy 2.3.5, OpenCV 5.0.0, Pillow 12.3.0, psutil 7.2.2 and pytest 9.2.0. The prior Windows interpreter was 3.13.9. These are different environments; source hashes alone do not establish numerical equivalence.
- Host exposes five AMD EPYC 9V74 logical CPUs, but cgroup CPU quota is 400000/100000 (four cores). Memory limit is 17179869184 bytes (16 GiB), no swap. Workspace filesystem reports about 30 GiB available.
- HTTP policy is enforced/restricted; no VPN, runtime secret or outbound identity is configured. No network/proxy/security settings were changed.
- No SMPD originals/parts, target CompNet/PKLNet ONNX, prepared manifest or 241-query checkpoint were found in the inspected workspace. Existing unrelated Pi capture archives were left alone. The small bundled palm detection/PalmIR models are different models.

## Minimum private intake

Use the platform's private file attachment/Library transfer capability, retaining filenames and directory structure. The Library connector is available to resolve/materialize an attached private file. For a 6.37 GB archive, platform size limits have not been verified; retain the existing 95 parts and transfer bounded bundles if necessary. Do not substitute a public URL, GitHub release, ordinary Git commit, third-party storage, or chat-pasted credential. A private attachment must actually become materializable before transfer is considered complete. No inbound public upload endpoint has been created.

Place intake outside the repository, for example `/workspace/private/smpd-intake/`:

1. Frozen run metadata: `protocol.json`, `dependency-lock.json`, `source-inventory.json`, `zip-inventory.json`, `SMPD.download.json`, `prepared/progress.json`, `prepared/manifest.json`, all available raw preparation logs and duplicate audits.
2. Exact 241-record `evaluation/results.json` and `evaluation/queries.jsonl`, plus corresponding query ROI images and any stage/numeric logs for representative parity queries. Preserve runtime registration/payment state if an operational resume will later be considered; no current cross-host resume is approved by this audit.
3. All 3677 unchanged originals referenced in the manifest and successful five-frame enrollment feature files, or the complete original 95-part archive plus frozen preparation artifacts. For immediate parity work, first transfer metadata, the two ONNX files, metadata.json, complete gallery feature files and a few preselected representative query originals/logs. Full evaluation still requires every original, including failures.
4. `compnet-tongji.onnx` (20036926 bytes; SHA256 `b513e614a8b1a4448ef58c1b7f288f760fc991ce31d0a35079b4f9226146d1ea`) and its `metadata.json`.
5. `pklnet-keypoints-diagnostics.onnx` (67688734 bytes; SHA256 `bf477f1778f03ccc203b64dd0c84d418c9bb22839a23ba923f479ab991aa067f`). Existing repo `code/pklnet/roiExtractor.py` must match the frozen dependency digest. PTH files are not required for ONNX inference.
6. Uncommitted local code/config needed by dependency hashes, as a separate reviewed patch/file bundle. Do not assume fetched commit includes them. Capture exact Python/package versions and effective runtime thread/provider settings separately; dependency-lock.json locks sources, not Python packages.

Known results SHA256: `19dbd849fc65b09c2a42045975e5a2ccf267e07352a9450b0a467153efdc48fa`.
Known ledger SHA256: `a9d967c51197f471f2cdde02d428d26131358304741bf552af389291abbf9eaf`.
Expected frozen counts: 3677 originals, 460 enrollment frames, 3217 queries, 92 people. The current prefix ends at `smpd-007-RP-36`. Its 86 correct / 120 wrong / 35 processing failures are partial development observations, not an independent test or Pi benchmark.

## Gates and code observations

`tools/audit_cloud_checkpoint.py` verifies the known checkpoint hashes, ledger equality/framing/order/truth, frozen split, source/model/dependency locks, inventory/manifest locks, and original/enrollment feature bytes. Explicit `--map OLD_ROOT=NEW_ROOT` performs lexical Windows-to-Linux path resolution for auditing without editing original metadata. A successful audit authorizes only a separate parity pilot; the old prefix remains unchanged. Portable launch/runtime configuration and numerical parity are still required.

Code inspection found the identity score aggregates the lowest two of five pair distances. Staged routing can return pose/FastCC evidence or CompNet angular distances using the same numerical confidence gate. This is a diagnostic lead, not proof of the source of errors. Inspect ROI anatomy, selected ROI/alignment validity, effective pixel support, per-frame distances, true identity rank and route separately before changing a gate. Never tune the final threshold to make rejection count as correctness.

After intake: freeze exact inputs and configuration; run a small declared set spanning successes, wrong matches, processing failures and expensive routes against the complete gallery. Record cross-host outputs and score differences, peak RSS, startup and stage timings. Any changed protocol/code gets a separate run, never a mixed Windows/cloud result ledger. Preserve all failure outcomes. CASIA/PalmBig frozen evaluations and private Pi168 remain separate.

No inference query has started in this cloud audit. Once queries start, persist UTC start time, fixed total/completed counts, batch wall time, rolling throughput and long-tail bounds. Report transfer, setup and gallery startup separately. Estimate remaining duration as an interval from representative route/condition costs, with uncertainty; do not multiply median latency by query count. Cloud latency is not Pi end-to-end latency; final candidates require real Pi validation.
