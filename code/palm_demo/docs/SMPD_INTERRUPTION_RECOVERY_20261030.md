# Full SMPD operational interruption and prefix-preserving recovery

The original inference process and its reporting process were found absent while `evaluation/results.json` and the flushed `queries.jsonl` both contained **exactly the same 130 completed queries**. The unified execution tool returned `Unknown process id 7360`, so no process traceback was recoverable. The termination cause is **unknown**; it is not established as a memory, power, model or network failure. No complete 3,217-query result is claimed.

Preserved prefix JSONL SHA256: `289c2c94185b00dc303c0104145a98bd85b005d853ec86f0ff9f36fb0f12c99c`.

`tools/resume_raw_smpd.py` is an operational adapter for the source-locked evaluator, not a new algorithm or a retest selected for better outcomes. Before restart it:

- Verifies the original evaluator/core/dependency/model locks and complete archive/preparation flags.
- Requires exact equality between the report and JSONL, complete newline framing, unique query names, and an exact fixed-order prefix. It refuses inconsistent or partial lines rather than truncating them.
- Snapshots the report and exact prefix bytes before writing anything new.
- Loads and verifies every already registered identity against all five original prepared feature arrays, original metadata, account and unchanged balance. It keeps the same complete 76-identity gallery and all 16 failed enrollments.
- Adapts only registration loading, existing-directory handling, report loading, append mode and iteration over the remaining ordered originals. The actual capture/ROI/features/scoring/HTTP result loop is kept verbatim and checked by a test.

The remaining **3,087 queries** reread and hash their originals, recompute ROI/features, and use the same staged matching, thresholds and full gallery. Already completed failures remain in the first 130 records; no result is replaced or removed. Each new epoch records its separately measured model/gallery startup and source hashes. Final completeness requires all 3,217 outcomes plus original-integrity and transaction invariance. The final JSONL must still start with the exact previously captured bytes.

This is now a sequential multi-epoch experiment following an operational interruption, not one uninterrupted process. Per-query times retain their actual observed host conditions; existing concurrent-load intervals remain disclosed. The standard tag/branch and original frozen evaluator sources are unchanged.

The continued current experiment is launched as a hidden background Windows process with stdout/stderr saved under the private runtime. This preserves future diagnostics independently of a tool session handle. It is not an hourly automation, a recurring experiment or evidence that the original termination cause is fixed. A reporting dependency writes a completed scalar report only when the strict completion checks pass.
