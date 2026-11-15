# Palmprint demo evaluation handoff (2026-11-15)

## Decision

No ROI/recognizer pair is validated for a live cross-device demonstration. Keep the deployed Raspberry Pi configuration unchanged until a fresh on-device session. Current X results are offline development evidence only; no Pi speed, live-camera, human acceptance, retry-loop, or end-to-end 2.5-second result has been measured.

D127 21-point ROI is not promoted as the default. It has good coverage on some development sets but is inconsistent against reference ROIs and can lose substantial Rank-1 accuracy. On PalmSet b16d, D127 vs author-formula reference Rank-1 on the same 625 known queries was PB 370/625 vs 615/625 and SF2 304/625 vs 625/625. On X-Palm test, D127 vs reference was PB 42/55 vs 52/55 and SF2 40/55 vs 47/55. On 11KHands common support, Rank-1 was tied (PB 119/120, SF2 120/120), while EER increased by 0.02452 and 0.04409 respectively. These cohorts were exposed during development; PalmSet has direct image overlap with recognizer training, and X-Palm has prior development exposure.

## What is measured

- **PalmSet b16d, 1,600 planned rows:** D127 ROI 1,572 success / 28 failure; strict reference/D127 support 625 known, 779 stranger, and 18/20 complete galleries. D127 rank and EER are substantially worse than reference. D136 training/dev image overlap is 1,360/1,600.
- **PalmSet cbe42, 1,600 planned rows:** PKLNet-v5 ROI 1,546 success / 54 failure; 98/100 gallery images and 680/700 registered queries localized. Only 18/20 galleries are complete; 768 localized stranger rows are unscorable for full-gallery decisions. On 614 rankable known rows, PB Rank-1 514 and EER .09475; SF2 Rank-1 529 and EER .10586. Three-ROI paired results have narrower model-specific common support: PB 13 hands / 389 known, SF2 16 hands / 542 known. D136 train/dev overlap is 1,440/1,600. Treat as training-exposed pipeline diagnosis.
- **11KHands development20:** reference8, PKLNet-v5, and D127 results are available. On 120-query strict common support, PB Rank-1 119/120 and SF2 120/120 for reference8 and D127; EER worsened with D127 by .02452 (PB) and .04409 (SF2). No verified physical-device grouping or independent holdout remains.
- **X-Palm:** official/reference, PKLNet-v5, RTM, MCP-v2 and D127 ROI comparisons are available for the existing dev/test role rows. D127 test Rank-1 is PB 42/55 and SF2 40/55 versus reference PB 52/55 and SF2 47/55. Historical development exposure and incomplete galleries prevent independent open-set claims.
- **Axon:** D127 and PKLNet-v5 ROI arms use frozen PB170/SF2e20 weights. No reference ROI exists. Only 10 stranger queries per arm have complete galleries in the available fold; other stranger rows are unscorable. This is not a FAR estimate.
- **Self-capture:** 196 frozen rows compare existing RTM and D127 ROIs. On strict common support (11 recorded identity/hand proxies, 54 gallery images, 59 known queries), PB Rank-1 RTM/D127 is 53/59 vs 49/59 and EER .13559/.12881; SF2 is 46/59 vs 51/59 and EER .22034/.11864. Most labels are recorded proxies, not individually verified. Forty-eight stranger images are not used for an FAR claim because real-person linkage to the gallery is uncertain.
- **TCD/Tongji:** D127, RTM and PKLNet fixed-ROI recognition results exist on the available 12,000-row release; there are no stranger rows or reference ROI, and person/hand/device identity mapping is inadequate for cross-device claims.
- **BJTU_PalmV2:** existing fixed pre-cropped ROI recognition result only. No raw image or matching reference/D127 ROI arm is available; the reserved cohort must not be retested.

Full denominators, per-sample records, protocols and source hashes remain in the local-only runtime ledger at `code/palm_demo/runtime/palm-full-evaluation-ledger-X-20261115-001/REPORT.md`. Runtime artifacts and biometric records are intentionally excluded from this document and from Git.

## Recommended next validation

1. Keep D127 and PKLNet-v5 as comparison candidates, not approved production ROI. The reconstruction reference is an upper-bound diagnostic and is not an available live detector.
2. Before changing the Pi, freeze a genuinely unseen person cohort with verified left/right hand labels, gallery/query roles, and camera/session metadata. Preserve all ROI failures and incomplete galleries in the denominator.
3. On the Pi, measure ROI, embedding, gallery matching and full request latency separately. Test one enrolled hand and one unfamiliar hand with all retries, rejects, false accepts, tracking losses and processing failures logged. Report human acceptance and power-stability results separately.
4. Keep all results from exposed development data marked as development diagnostics. Current samples do not support a FAR=10^-6 claim.

## Data and sharing boundary

This note contains aggregate metrics only. Do not publish or push images, ROI crops, embeddings, templates, per-sample scores, identity/hand maps, capture archives, runtime caches, or weights whose redistribution license has not been verified. No dataset was newly searched for or downloaded for these experiments; THUPALMLAB was not accessed.
