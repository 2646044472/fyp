# 22 September | Fast-CC two-participant pilot (public abridgment)

**Question.** With a single reference image held fixed, did repeated placements of the same hand match it, and were placements of the other hand rejected? The original analysis used a Pi 5 and NoIR Camera v2, 128 × 128 palm crops and the demo's provisional distance threshold of 0.28. The threshold was not fitted or validated on an independent set.

| Probe group | Planned comparisons | Accepted | Rejected |
| --- | ---: | ---: | ---: |
| Same hand | 9 | 4 | 5 |
| Different hand | 9 | 1 | 8 |

The average distances were 0.2822 and 0.3403 respectively; lower means more similar. Although the groups differed on average, their scores overlapped. Producing crops of the same pixel dimensions did not guarantee that they covered the same palm area. Placement, scale and centering varied. The different-hand error also passed the minimum contrast and sharpness checks: those checks alone could not make a match reliable.

**Interpretation.** This was an engineering diagnostic based on two people, not a population accuracy, FAR, FRR, EER, liveness or payment-security evaluation. It does not establish that the matcher is unsuitable, that geometry is the only problem, or that 0.28 should be retained. The separate short note's rough rejection figure had no documented denominator; do not substitute it for this pilot's counts.

**Proposed, not completed:** collect independent remove-and-replace placements, measure position, scale and rotation, and compare multiple enrollment templates only after checking crop stability. Choose thresholds on separate development data; reserve new participants and sessions for final testing.

**What was omitted:** The original school Word report includes names linked to individual comparisons, original palm photographs, ROI images, scores and session records. That document is preserved unchanged in the source school archive and in the local school folder. This public abridgment retains the protocol, aggregate outcomes, interpretation and proposed experiments without disclosing individual biometric records.
