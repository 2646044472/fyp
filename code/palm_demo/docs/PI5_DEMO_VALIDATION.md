# Pi 5 demo deployment — 2026-10-28

V6 is deployed to `rasp5:/home/fyp5/palm_demo`. The service now uses the optional
`deploy/demo-v6.conf` systemd drop-in: FastCCDemo-v6, OpenCV 4 threads and PKLNet
ONNX 2 threads. It is active and waiting for a camera; live camera acquisition
and the browser/live-preview end-to-end path were not tested in this session.

## Actual Pi replay measurements

All processing ran on the Pi 5 (aarch64, OpenCV 4.10.0, ONNX Runtime 1.28.0).
Only acquisition was replaced with historical images. Each device has 40 unchanged
images, four identities, indices 1–5 for enrollment and 6–10 for queries. Runs
were sequential. No queries, identities, or ROI candidates were dropped.

| Dataset | Correct | Five-frame enrollment median, before → after | Identify median, before → after | Final identify p95 | Final process peak RSS |
| --- | --- | --- | --- | --- | --- |
| New camera | 20/20 | 12.15 → 11.42 s | 14.86 → 14.46 s | 18.39 s | 1115 MiB |
| Old camera | 20/20 | 13.70 → 11.51 s | 6.01 → 5.59 s | 6.11 s | 997 MiB |

These are single-run comparisons on repeatedly inspected development images,
not an independent accuracy study or proof of stable latency across environments.
First identification follows enrollment and is not a cold-model query.
No throttling or undervoltage was observed (`get_throttled=0x0`).

## Changes and validation

- Replace full-image floating-point gamma computation with a 256-entry LUT;
  all byte values are exactly equal to the original formula.
- Skip unused contrast/sharpness diagnostics inside matching. Camera and UI
  callers retain their diagnostics; normalized matcher pixels are unchanged.
- Add explicit OpenCV/ONNX thread options. A 2-thread OpenCV trial made new-image
  median identification slower (16.17 s), so deployment retains 4 threads.
- Prevent duplicate UI requests and disable retry/inputs while busy; display
  elapsed seconds and describe unconfirmed payment responses as uncertain.
- Both Pi cohorts passed enrollment, 20 queries, four isolated simulated payments,
  cancellation, cancelled-confirmation rejection, and duplicate-confirmation rejection.
- Pi before/after: all 40 identities, winner/runner-up scores and statuses are
  identical; all eight five-frame enrollment archives have equal feature arrays.
- Windows numerical regression: 80 enrollment representations and all 3,120 directed
  non-self same-device pair distances remain exactly equal to the saved v5 reference.
  This preserves the previous 224 split results; those splits are not new independent data.
- Python regression: 144 passed, 2 skipped (the Windows environment lacks ORT).
  `tests/test_existing_pipeline.py` is explicitly excluded because it imports an
  obsolete module; this is not a claim that the entire unexcluded suite passes.
- `node tests/test_demo_page.cjs` passes interaction checks for duplicate actions,
  waiting state, uncertain confirmation, cancellation and enrollment.
- Actual Pi PalmIR HTTP tests pass snapshot/reference/restore and stale-snapshot
  rejection. The two fixed examples did not improve matching scores; PalmIR is
  not inserted into the recognition pipeline.

## Deployment and rollback

42 installed source files match local SHA-256 values. All 526 pre-existing runtime
files remain byte-identical after deployment; replay templates/accounts stay under
`/home/fyp5/demo-v6-20261028`, outside production runtime. The matcher and ONNX model
load successfully from the installed directory. No benchmark processes remain.

Backup: `/home/fyp5/maintenance-20261028/pre-demo-v6-192340/`.
The backup contains original source files, `original-service.txt`, and
`deployment.json` (installed file hashes and whether each file previously existed).
The installed override is
`/etc/systemd/system/palm-debug-ui.service.d/demo-v6.conf`.
To return to capture-only, move that override outside the `.conf` suffix, reload
systemd, and restart `palm-debug-ui`; restoring code additionally requires restoring
previously existing files listed in the backup manifest while leaving runtime intact.
Do not copy simulated replay accounts into the production runtime.

Local evidence: `runtime/pi5-v6-20261028/report.html`, `comparison.json`,
`pi-parity.json`, `deployment.json`, and `parity/prepared-parity-parallel.json`.
Pi evidence: `/home/fyp5/demo-v6-20261028/{baseline-new-r2,baseline-old,final-new,final-old}`.

Reproduce a cohort using a manifest whose original paths exist on the target host:

```sh
python tools/replay_demo_manifest.py inputs/new.json fresh-output --opencv-threads 4 --onnx-threads 2 --restoration
```

Output must be a new directory. This exercises real HTTP handlers with independent
simulated storage. A camera is unnecessary. Dataset enrollment is still required
for a live demo; templates from older algorithm versions need reenrollment using
the original IDs to retain balances.
