# Terminal-RF SMPD frozen full evaluation — 2026-10-31

This is a new candidate run, not continuation of the old ordinary-score241.
Standard branch/tag remain at `9d9bb43e909e992765bf586da13a3b881e3dc481`.
Production and Pi deployment are outside this experiment.

## Fixed execution

- Candidate: device-qualified `original-confident-paths-terminal-rf-v1`, v26 + retained ordinary FastCC, terminal-only supported-response RF. Models and gates `.32/.08/1.0/0` frozen; rejection off. No fitting or threshold sweeps.
- Inputs: all3677 published originals /92 right-palm identities; fixed F0–F4 (460 files), every remaining3217 query. Existing raw JPEG paths and byte-hash metadata reused; no old ROI/feature/template/score cache. Verify raw bytes inside each capture.
- Fresh registration uses actual `capture_demo_feature(enrollment=True)` once per selected file. Save success/failure durably; no replacement. Offline five-frame bulk enrollment is separately timed; it is not live enrollment latency.
- All eligible identities, including protected people, share one gallery. Failed-registration queries remain in primary3217 denominator. Windows index/cache guards remain2GiB/6GiB; no gallery partitioning or scoring change to fit memory.
- Each query freshly performs the actual loopback HTTP identification pipeline: raw read/hash, PIL EXIF transpose/RGB, PKLNet illumination3 threads, feature extraction, staged matching, response. OpenCV1 thread; CompNet1 thread. No duplicate full-query preprocessing pass. Capture observes actual ROI diagnostics without rerunning localization. `ReplayCamera.select`'s redundant untimed header decode is avoided; input decoding is entirely inside timed capture.
- Query latency excludes camera/external upload, checkpoint/report/integrity-boundary I/O and token cancellation. Cancellation is separately timed; account balances/transaction count must remain unchanged. Cold model/gallery readiness and each resume epoch are separate costs. Environment/source checking and ledger operations contribute to wall throughput, not timed HTTP latency.
- Fixed order is the old stable `(subject,index)` sort, with frozen ZIP-inventory ordinal breaking ties. No outcome/geometry-based selection. Two initial formal queries form an operational preflight; retain them and resume at query3, with no candidate choice from their scores.

## Isolation and recovery

`tools/run_terminal_smpd.py init` seals the explicit sample list, prospective split, exact model/source hashes, relevant package file hashes, package versions, interpreter/environment, source commit and old-checkpoint digests in a new sibling root. The runner cannot load a feature outside its own `features` directory; templates include run fingerprint and individual frame-record hashes. Old results are never imported into the candidate journal. The old checkpoint files are hashed only as preservation evidence.

`tools/smpd_run_journal.py` stores each enrollment/query record in its own atomically replaced, fsynced JSON. Records bind run fingerprint, stage, sequence, sample, previous-record digest and payload digest. Only an exact unique same-version prefix can resume. A kernel file lock prevents two workers writing one run. Existing completed failures are never rerun/overwritten. Temporary/uncommitted files remain for inspection and are never imported as completed features. Per-identity gallery seals permit restart after a completed template commit; a partial data/metadata pair fails closed for explicit recovery.

Before a request, an inflight marker identifies its attempt/epoch. Resume preserves an interruption receipt. If the record already committed before a crash, skip it; otherwise retry only that uncommitted sample and disclose the earlier attempt. No silent JSON truncation, result repair or repeat-until-pass selection. `STOP` requests a boundary pause; remove it only under a later continuation instruction. HTTP timeout1800 seconds is an infrastructure interruption, not an algorithm deadline or successful rejection. Exceptions preserve prefix and marker.

Startup requires10GiB available memory; each new frame/query requires1GiB. These are operational guards, not evidence of actual peak capacity. Source/model/old metadata locks are checked at boundaries; installed inference package content hashes are checked at epoch start/end. Code changes require a new run rather than adapting a partially completed one. Accuracy does not stop or modify the fixed run. Resource/provenance/gallery/payment violations stop it.

## Reporting and limits

`tools/report_terminal_smpd.py` creates scalar-only snapshots without inference. Incomplete snapshots are prominently labeled. Primary outcomes are disjoint: unique-correct, wrong identity accepted, true-ID nonunique/tied, rejected, processing failure. Report natural unregistered truth and registration/ROI failure as separate axes; rejection/retry is not correct. Include all-query/correct-query P50/P95/max, correctly≤2.5s, gallery readiness, enrollment costs, memory, interruptions and wall throughput.

Report overall, capture views F/RF/P/RP, development74 people/2588 queries, protected18/629, actual truth-registered/unregistered groups, and predefined byte-content diagnostics. Keep all files primary. Secondary duplicate selection is lexicographically first query per SHA256, with enrollment overlap separately disclosed. No outcome-selected deduplication. Geometry checks are not anatomical ROI labels, and no release-wide finger-valley visibility annotation exists.

SMPD is **seen public development data**, including known001/002/008 exposure. The protected split is prospective protection against later fitting, not a blind never-evaluated independent test. Pretraining exposure is unknown. Closed-set identification and naturally failed registrations do not establish stranger FAR. Existing local-device person-removal diagnostics do not authorize inventing a new SMPD unknown cohort. No repeated CASIA/PalmBig protocols.

Historical resource evidence: each v26 feature is16MiB;460 arrays alone represent7.1875GiB, before additional indexes/cache/model/temporary storage. Old241 requests total6837.379 seconds (~28.371 seconds/request); naive3217-query scaling is~25.35 hours, excluding fresh enrollment/startup. This is a partial-prefix arithmetic illustration, **not an ETA or a paired candidate speed estimate**. New full-run peak and remaining time must be measured and remain uncertain as poses/routes change.

Private runtime: `runtime/smpd-terminal-rf-20261031/`. Original images, ROI pictures, features, templates and weights stay private. Only owned tools/tests/protocol and scalar checkpoint summaries may be pushed. No new public evaluation is called complete until all460 enrollment attempts, all3217 query records and final integrity/accounting checks pass.
