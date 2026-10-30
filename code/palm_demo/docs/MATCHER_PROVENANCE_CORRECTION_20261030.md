# Windows half-turn replay matcher provenance correction

The contour pilot's first fresh-standard comparison returned `INCOMPATIBLE_TEMPLATES`. Investigation found that the historical half-turn Windows evaluator labeled its outer report `FastCCCompNetAlternateROI-v26-experimental`, but `frozen.run_case` passed `source['matcher']` from `active169-baseline-20261029/protocol.json` to initialization. That unchanged split protocol names `FastCCQualityEvidence-v24-experimental`. The saved enrollment metadata also consistently names v24. The defect is in experimental orchestration, not evidence of an algorithm accuracy change.

The historical 336 query outcomes and timing observations are preserved. Their 165/168 per variant, three wrong and zero rejection are **v24 + retained FastCC** results, not proof of v26 regression. The independently measured Pi v26 retained-evidence result (165 correct, three wrong, zero rejection /168; 145 correct within 2.5 seconds) used its own explicit v26 baseline and is not reclassified by this finding. SMPD's evaluator explicitly uses v26; its incomplete 241-query checkpoint and frozen dependency sources are unchanged.

The 169-frame geometry audit still establishes that half-turn recovery did not modify valid primary device ROIs. The public 008 v26 registration recovery pilot remains a single-person development observation, but its prerequisite was a mislabeled v26 regression; no promotion/complete v26 qualification is justified. Original images, labels, thresholds, standard branch/tag and production services are unchanged.

Corrections:

- Pass the requested matcher into a copied in-memory split protocol. Require the instantiated matcher name and class to match before any HTTP evaluation, and record each startup's actual matcher.
- The half-turn reporter refuses historical data without verified executed-matcher provenance, rather than regenerate its erroneous v26 qualification.
- A fresh contour paired pilot uses the existing Pi evaluator's lossless v24-to-v26 envelope migration in isolated writable destinations: validate five original v24 frames, change only the four-byte magic and algorithm metadata, verify every remaining payload byte by hashes, and load all identities. This is reuse of enrollment, not a fresh registration or registration latency claim.
- Keep the 19-query contour selection fixed as declared before candidate scoring. The historical Windows v24 run supplies selection only. Compare actual fresh v26 standard/candidate decisions; its historical v24 scores cannot be required to equal v26.
- Preserve the two aborted contour runs and their errors. The second records the actual `UNKNOWN / INCOMPATIBLE_TEMPLATES` response; no recognition improvement is claimed from either. No scoring or geometric parameter was changed to fit these runs.

A full v26 fresh-enrollment four-case regression is required before a candidate can be qualified on that pipeline. A bounded unsuccessful contour pilot is rejected without a parameter scan. Windows results cannot establish Pi latency or unseen-person accuracy.

The separate [verified v26 reference](V26_DEVICE_REFERENCE_20261030.md) has now completed fresh 34 five-frame enrollments and all168 queries: 165 correct, three wrong, zero rejection/processing failure, and all isolated payment guards passed. This confirms the actual v26 baseline; it does not retroactively qualify the historical half-turn candidate. The fixed contour pilot completed without a genuine correction and was rejected.
