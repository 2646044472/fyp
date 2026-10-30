# SMPD checkpoint / terminal-RF version boundary — read-only audit

**Decision: preserve the old241, but do not use them as the new candidate's prefix. No public evaluation has been launched.** The terminal-RF device experiment was committed and its remote SHA verified as `83b7b01cde6d46f8df064c72ac249d343a0a61d0` before this audit. Standard branch/tag remain `9d9bb43e909e992765bf586da13a3b881e3dc481`.

This audit only reads existing checkpoint, source/model locks, manifests and prepared-feature container metadata. It writes a separate scalar report; it does not modify source data, inspect public query correctness for tuning, decode/reuse feature arrays, or run recognition. The protocol review was also read-only. No model switch or actual chat-model identity is inferred from dispatch parameters.

## Verified evidence

| Item | Verified state |
|---|---|
| Historical evaluation | 241/3217 complete query records; JSON and newline-framed JSONL exactly equal |
| Fixed order | Unique exact original-query prefix, validated by the pinned `remaining()` implementation |
| Last / next old-baseline query | `smpd-007-RP-36` / `smpd-007-RP-37`; 2976 remaining for that old version |
| Results SHA256 | `19dbd849fc65b09c2a42045975e5a2ccf267e07352a9450b0a467153efdc48fa` |
| JSONL SHA256 | `a9d967c51197f471f2cdde02d428d26131358304741bf552af389291abbf9eaf` |
| Protocol/model binding | Checkpoint protocol/archive digests match the unchanged protocol/download records; all original source/dependency/model locks pass |
| Cohort/registration | All3677 declared members match the prepared manifest; all92 fixed five-frame registration selections match the checkpoint; 76 registered,16 failed |
| Feature integrity/schema | All417 successful old enrollment feature containers match their stored byte SHA256; each header is 1-D `uint8`, shape16777216, C order, NPY1.0, v26 magic2801066 |
| ROI/source representation | `pklnet-illumination-consistent-v5`; original extraction sources/models and prepared-manifest hashes unchanged; candidate's34 local enrollment arrays were previously verified equal |
| Feature protocol fingerprint | `b86ed5e207da2bafc41c6ec0938beebf0bee940caeca33e11d39050aac86e352` |
| Current candidate fingerprint | `a09904ff41d14698f420f598f92e767a3df4b8302d50362ac50dd4685ba60c1d` (candidate helpers + original sources + exact models + frozen thresholds) |
| Prospective split | Same inventory/manifest binding; 74 development people/2588 queries,18 protected people/629 queries, disjoint full coverage |
| Exact-byte duplicate metadata | 3591 unique contents/3677 files,86 redundant files in62 groups, no cross-identity byte conflict; two queries overlap enrollment bytes;3137 unique query contents |

The historical full-archive CRC completion flag is preserved and tied to its unchanged download record. This audit did **not** redo the whole archive CRC or scan every original image's bytes. Future inference must verify each original before processing. Duplicate counts use existing byte hashes, not a new perceptual/pixel-duplicate inspection. The report lists record fields, current/historical environment, source hashes and all protocol fingerprints explicitly.

## Why scores cannot be appended

The old prefix used v26 + retained ordinary FastCC terminal scores. The new candidate preserves original confident paths but replaces the terminal whole-gallery vector with an independent supported-response RF vector. Same models and feature representation do not turn old scores, identities or durations into a new-version execution. The changed behavior is the **terminal score definition**; it does not imply that the155 confident early paths were altered.

The old run may only be resumed as its original frozen version, preserving its exact241-record prefix. It cannot be relabeled as terminal-RF, concatenated with terminal-RF outcomes or extrapolated into a complete candidate baseline. Side-by-side descriptive comparisons on identical inputs can be version-labeled, but a partial fixed prefix is not a full-release baseline or generalization estimate.

Per the user's prohibition on cross-version feature reuse, a future candidate evaluation must use a separate run directory and regenerate fixed enrollment/query features from original images. Do not import the old `prepared/features`, old templates or query caches, even though their container format is compatible. Source-image paths and immutable byte-hash metadata may identify the same raw dataset. `candidate_feature_reuse=False` in this audit describes what this audit did and what future policy requires; no future runner isolation has yet been implemented or certified.

## Future once-only frozen evaluation plan — not started

1. Keep the published3677 original files/92 identities, fixed F0–F4 (460 selected enrollment images) and every remaining3217 query in a frozen explicit order. No replacement, geometry-based deletion or outcome-selected subset. Register all eligible identities together, including protected subjects. Record every registration failure; their queries remain in the primary3217 denominator. Do not advertise the historical76-person eligible gallery as92 successful registrations or assume a future success count before running it.
2. Regenerate candidate-version enrollment features from original images into a new isolated root. Enforce that every imported template/feature belongs to that root and its frozen run manifest; reject paths pointing into old feature/template directories. Query ROI/features must also be freshly recomputed. This enforcement is a future execution requirement, not an achieved property of this metadata audit.
3. Preserve all release files in primary accounting. Predetermine duplicate disclosures/secondary unique-byte views before scores, including enrollment/query byte overlap; never remove failures or duplicates after seeing recognition. Do not perform new failure-image review to tune this candidate.
4. Treat SMPD as **seen public data**. Known development exposure includes001 original views,002 partial scalar outcomes and008 source/half-turn development pilot. Report overall3217, development2588 and protected629 using the **same complete gallery and unchanged candidate**. The protected split is prospective protection from further fitting, not a never-evaluated blind test. Original pretraining exposure is not fully established. Public closed-set identification cannot establish stranger rejection.
5. Before the first candidate query, finalize and hash the actual evaluation/resume programs, all inference dependencies, exact models, candidate/kernel/retained helpers, decoding/ROI/features, thresholds`.32/.08/1.0/0`, rejection-off policy, sample/order/split, registration/gallery/duplicate rules, environment/resource allowances and timing scope. The current candidate fingerprint alone is **not** that complete future execution lock. Windows memory allowances must be explicit and must not partition/reduce the gallery; no Pi capacity claim follows.
6. Report correct, wrong accepted, rejected, processing failure, registration failure, every denominator, correct within2.5s and P50/P95/max. Keep feature preparation, enrollment, model/gallery ready and query times separate. Retry/rejection never counts as correct. Do not infer full baseline improvements from the old241. CASIA/PalmBig completed same-version protocols are not repeated for parameter selection.
7. Predetermine graceful stopping at complete-record boundaries, exact JSON/JSONL/order/source/model/protocol checks, snapshots and interrupted-query retry rules. Resume only the same frozen run/version without overwriting prior failures or repeating completed records. Any scoring/feature/threshold/protocol change creates a new version. No public result may trigger hidden tuning/repeated attempts presented as one frozen evaluation.

No public runner was created or launched in this turn, no old checkpoint was resumed and no dataset/model/raw palm data was uploaded. Device candidate evidence remains **166/168 correct,2 wrong,0 rejected;157/168 correct within2.5s; PC P95 4.094s/max8.933s**, with155 original fast paths preserved. This is not Pi timing, an independent generalization result or a deployment qualification. Standard and production stay untouched.

Machine-readable evidence: [boundary summary](experiments/terminal-rf-smpd-boundary-20261030/summary.json). Reproducible audit utility: `tools/audit_smpd_terminal_boundary.py`; it reads only container headers/four-byte format tags after hashing, never loads feature arrays. Its new schema tests and the existing strict resume-prefix tests pass. Broader execution isolation and frozen public-run readiness remain future work.
