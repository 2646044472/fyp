# Independent silhouette/valley evidence — fixed development pilot

Standard stays frozen and the ongoing SMPD full baseline source is unchanged. This is a new isolated candidate, not an adopted ROI replacement. Its purpose is to test whether anatomical geometry can supply useful early evidence for the three remaining exposed device errors, without more PKLNet windows or relaxed matching gates.

Read-only screen: all 169 original-device frames, raw grayscale Otsu foreground and background polarities, largest external contour, convexity defects with fixed angle <90° and depth >=2% of frame side. Candidate counts are not anatomical accuracy. Old-camera bright polarity has at least three candidates in 103/110 frames; new-camera bright polarity in 29/59. Manual review of the three frozen errors finds usable-looking finger gaps; the two fixed correct controls show that background and contrast can make the method fail. Both polarities and all failures remain recorded. No segmentation/identity threshold is fitted to remove these failures.

Fixed candidate rule, before recognition scores:

- Exactly four valley-like defects and at most two touched frame edges for a polarity. Pick the unique minimum normalized-residual three-point row; require its middle direction cosine >=0.8. Equal minima abstain.
- The outer row points plus the silhouette distance-transform center define the existing PalmKit ROI (unchanged alpha/beta). Require existing minimum keypoint span, full image bounds, all ROI corners inside the silhouette, and the existing >1px² anchor-overlap check. If neither or both polarities qualify, abstain.
- For each of all five gallery frames, use the contour embedding when a unique geometric candidate exists; otherwise retain that frame's original CompNet embedding. No frame, person or competing identity is removed. This remains a complete-gallery best-two-of-five angular CompNet calculation.
- Existing confident pose/base/gamma evidence takes precedence. Only an uncertain query tries one contour proposal and one additional frozen CompNet embedding. It returns early only under the same .32 distance / .08 margin gate; otherwise the original scoring/fallback continues. Ordinary FastCC and angular CompNet metrics are not merged.

The implementation accepts image/geometry only, no identity, query filename or correct-score selection. It is installed in one isolated process before preparing the same frozen enrollment templates. Original stored feature bytes, primary ROI and production files remain unchanged. The new tuple field is an in-memory experimental embedding, not a production template migration.

Mechanism pilot selection is all exhaustive Windows-standard queries from the completed half-turn paired regression, union all three incorrect queries and one lexicographic first timely correct control per case. Fixed selection before new candidate recognition. All enrolled identities/five frames remain in each ranking. Pass requires a genuine wrong-to-correct improvement and no loss of a previously correct selected query; otherwise reject this candidate without another parameter/threshold scan. Only a passing pilot proceeds to the mandatory whole168 device regression. New confident wrong answers, enrollment fallback rates and all unchanged errors must be disclosed.

This is exposed development testing. No independent generalization, unseen-person rejection, new-device Pi timing or long-tail solution is established by the contour observations or this protocol.

## Completed fixed pilot: rejected

The 19-query selection was fixed before candidate recognition. Both **actual v26 + retained FastCC** variants completed all 19 real HTTP queries: **16 correct, three wrong MATCH, zero rejection, zero processing failure**. Identity, best/second score and recognition route were identical on **19/19**. No correct result was lost, but no remaining error was genuinely corrected, so the candidate fails its fixed pass criterion. Do not tune the geometry or confidence gates on these outcomes. No full168 candidate regression or deployment followed this unsuccessful pilot.

The two new-camera cases are 2/2 and 6/6 correct; old-camera original is 4/7, reverse 4/4, in both variants. Correct within 2.5 seconds was 9/19 standard and 8/19 candidate. Windows P50/P95/max were 2.767/6.189/8.657 seconds and 2.639/6.073/8.001 seconds. These small, noncontrolled timing differences do not establish acceleration; in particular, the timely-correct count did not improve. Full-gallery ready time and offline enrollment copy costs are reported separately. Five-frame enrollments were reused through the previously used lossless v24-to-v26 version-envelope migration, with all non-header payload bytes verified unchanged; there were no fresh registration requests in this pilot.

The three mistakes give different evidence:

| Error suffix | New contour proposal | Independent CompNet evidence |
|---|---|---|
| 37d0c433 | Geometrically accepted | Wrong identity still first at .386678; true second at .439704. Geometry success is not identity success. |
| 61f30739 | Geometrically accepted | True identity becomes first at .415251, second .479488; both the unchanged .32 distance and .08 margin gates fail. Do not turn this one exposed ranking into a threshold fit. |
| 8d6441d2 | Rejected by existing minimum keypoint span | No extra embedding; original scoring remains unchanged. |

The initial runner uncovered a separate historical matcher-label defect; two aborted setup runs are preserved. The final pilot validates actual v26 name/class, every five-frame format and a fully prepared gallery in both arms. It uses the historical Windows run only to fix its query selection, never as a v26 score reference. See [provenance correction](MATCHER_PROVENANCE_CORRECTION_20261030.md).

All 169 original bytes and source templates remained unchanged, and isolated cancellation left transaction counts unchanged. This bounded pilot does not replace the complete enrollment/payment regression. Scalar report and query ledger: [summary](experiments/contour-compnet-pilot-20261030/summary.json), [decisions](experiments/contour-compnet-pilot-20261030/decisions.csv). The candidate remains experiment-only and must not be enabled in production.
