# Five-frame anatomical ROI counterfactual — 2026-10-30

All four frozen wrong queries were compared with all five enrollment frames of their true and returned wrong identities. The fixed manual landmark rule was unchanged: interdigital valleys A/B and wrist direction W, square side 1.05 AB, center at midpoint plus 0.65 AB toward the wrist. Corner orientation/chirality follows the nearest original ordering. This examines position/scale and does not repair a possible orientation error.

Existing 11 annotations were reused; 28 additional frame annotations were locked before the resulting matcher scores were examined. The annotator had development exposure; this is score-independent locked annotation, not independent blind validation. No labels, templates, thresholds or images were changed. No frame was dropped based on score. Full-gallery recognition and HTTP timing are not measured by these pairwise counterfactuals.

The experiment completed **160 pair cells** (four queries, two identities, five enrollment frames, two query ROIs, two enrollment ROIs). All 40 original/original frame scores exactly match frozen diagnostics. All 160 winning branches were fixed-pose `legacy_v2`; no accepted legacy alignment improved its fallback. Source templates were unchanged and all Pi power samples were zero.

OO = original query/original enrollment; AO = manual query/original enrollment; OA = original query/manual enrollment; AA = manual query/manual enrollment. Each cell shows true / wrong distance, with the unchanged mean of the best two frames (lower wins).

| Query suffix | OO | AO | OA | AA |
|---|---|---|---|---|
| a4677ec5 | .387695 / .383600 | **.369546 / .373866** | .386987 / .380371 | **.372972 / .385951** |
| 61f30739 | .389959 / .374023 | **.378848 / .389617** | .389160 / .375488 | **.376852 / .394941** |
| 8d6441d2 | .405874 / .374721 | .398816 / .373992 | **.375716 / .376953** | **.380162 / .383984** |
| 37d0c433 | .375324 / .345703 | **.387527 / .389614** | .387522 / .378841 | .395650 / .388310 |

Bold means the true identity beats only the selected wrong identity. It does **not** establish correct full-gallery recognition or confidence. In particular, correcting both query and enrollment ROIs loses again for the fourth case. Earlier first-frame flips do not establish that full enrollment aggregation is fixed.

Original/original best-two frame indices (zero based):

| Query suffix | True frames | Wrong frames | Mechanism limit |
|---|---|---|---|
| a4677ec5 | 0, 3 | 4, 0 | One strong true frame is insufficient once the second frame is averaged |
| 61f30739 | 0, 3 | 0, 1 | Wrong frames 0, 1 and 4 tie at .374023; not a single bad-frame outlier |
| 8d6441d2 | 2, 3 | 4, 1 | A low wrong-frame distance contributes; that alone does not prove deletion would fix ranking |
| 37d0c433 | 4, 0 | 3, 4 | Two wrong frames score strongly; rejecting one outlier does not explain the error |

Only two union candidates were accepted across the 160 cells. Both belong to query `61f30739`, wrong identity enrollment frame 3, view 11 / sigma 2. Original query: final fixed-pose .389648 versus union .411133; manual query: final .386089 versus union .411133. Neither union wins. The mapped quadrilateral is fully inside the source image (visible fraction approximately 1.0); overlap as a fraction of that quadrilateral is 23.73% with the original anchor and 40.25% with the manual anchor. Their actual accepted source matrix and quadrilateral, visible area and overlap with the respective query anchor are preserved in the scalar artifact. Passing geometric overlap does not prove anatomical correspondence.

The evidence supports investigating query localization and low-information fixed-pose collisions, but does not justify adopting manual ROIs, frame deletion, a custom per-person rule or a new rejection threshold. Reproducible per-mode five-frame arrays, exact selected frame IDs/indices and geometric diagnostics: [ACCURACY_DIAGNOSTICS_20261030.json](protocols/ACCURACY_DIAGNOSTICS_20261030.json), generated from frozen results by `tools/report_accuracy_diagnostics.py`.
