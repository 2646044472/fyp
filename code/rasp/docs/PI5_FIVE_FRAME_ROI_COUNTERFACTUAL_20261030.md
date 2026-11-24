# Five-frame anatomical ROI counterfactual — 2026-10-30

All four frozen wrong queries were compared with all five enrollment frames of their true and returned wrong identities. The fixed manual landmark rule was unchanged: interdigital valleys A/B and wrist direction W, square side 1.05 AB, center at midpoint plus 0.65 AB toward the wrist. Corner orientation/chirality follows the nearest original ordering. This examines position/scale and does not repair a possible orientation error.

Existing 11 annotations were reused; 28 additional frame annotations were locked before the resulting matcher scores were examined. The annotator had development exposure; this is score-independent locked annotation, not independent blind validation. No labels, templates, thresholds or images were changed. No frame was dropped based on score. Full-gallery recognition and HTTP timing are not measured by these pairwise counterfactuals.

The experiment completed **160 pair cells** (four queries, two identities, five enrollment frames, two query ROIs, two enrollment ROIs). All 40 original/original frame scores exactly match frozen diagnostics. All 160 winning branches were fixed-pose `legacy_v2`; no accepted legacy alignment improved its fallback. Source templates were unchanged and all Pi power samples were zero.

OO = original query/original enrollment; AO = manual query/original enrollment; OA = original query/manual enrollment; AA = manual query/manual enrollment. Each cell shows true / wrong distance, with the unchanged mean of the best two frames (lower wins).

*The participant-linked evidence for this section is retained locally.*

Bold means the true identity beats only the selected wrong identity. It does **not** establish correct full-gallery recognition or confidence. In particular, correcting both query and enrollment ROIs loses again for the fourth case. Earlier first-frame flips do not establish that full enrollment aggregation is fixed.

Original/original best-two frame indices (zero based):

*The participant-linked evidence for this section is retained locally.*

The evidence supports investigating query localization and low-information fixed-pose collisions, but does not justify adopting manual ROIs, frame deletion, a custom per-person rule or a new rejection threshold. Reproducible per-mode five-frame arrays, exact selected frame IDs/indices and geometric diagnostics: local study record, generated from frozen results by `tools/report_accuracy_diagnostics.py`.
