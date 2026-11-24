# Automatic enrollment candidate selection — 2026-11-09

## Change

Enrollment now collects eight quality-passing candidate frames before selecting the five templates saved to the gallery. The existing quality gate remains `sharpness >= 2` and `contrast >= 12`. Frames with mean absolute ROI difference below `2.5` are treated as repeats; a repeat replaces the buffered frame only when its sharpness is more than 10% higher. Repeats do not consume the quality-failure budget. The existing 15 quality-failure limit, 120-second timeout, explicit hand confirmation, and cancel-before-save behavior remain in force.

The selector greedily balances normalized image quality (75%) and diversity from the nearest selected sample (25%). Before selection, all selected candidates must meet the first-five baseline minimum sharpness and contrast, so the candidate set cannot lower the baseline minimum on either metric. Diversity combines normalized ROI-quadrilateral pose descriptors (center, scale, aspect ratio, orientation) and cosine distance between 16×16 samples from the normalized ROI. Ties are deterministic by capture frame ID. Selection occurs only when the eight-frame candidate buffer is full. `DemoFlow` then replaces the temporary candidate pool with the selected five; commit still persists exactly five features. The capture callback passes the full-frame ROI quad and dimensions. The UI reports pool progress and shows the selected five crops before confirmation.

## Development screen

The initial 50/50 selector without a quality floor was screened on 2,165 previously exposed source70 ROI records from 139 hands. It improved the pose+texture diversity descriptor on all 95 hands with ten eligible candidates, but selected minimum sharpness fell below the first-five baseline on 49/95 hands. That variant was rejected. The ten-candidate screen with the quality floor increased mean diversity on 61/95 hands, tied 28, decreased 6; it raised mean sharpness but still needed ten captures. The live pool was reduced to eight. Its screen covered 112/139 hands with enough candidates and improved diversity on 64, tied 39, decreased 9; minimum diversity improved on 62, tied 47, decreased 3. Mean sharpness increased 1.46; worst-photo sharpness increased 1.59 on average and fell below baseline on 0/112. See `runtime/enrollment-selector-detailed-source70-X-20261109/run-006/REPORT.md`. These are development records, not independent identities; no recognition accuracy was used to select parameters.

## Verification

- Synthetic burst tests cover quality rejection, repeated-frame handling, clearer duplicate replacement, eight-frame collection, selected-feature alignment, cancel, hand confirmation, exact five-template commit, and gallery warmup metadata.
- Python: 40 relevant tests passed (`test_union_lossless_capacity.py`, `test_demo_enrollment_burst.py`, `test_enrollment_photo_selection_prototype.py`) with the project vendor path configured.
- Browser interaction test: `node tests/test_demo_page.cjs` passed.
- No live hand was present. The selector screen used previously exposed static development ROIs and measured image descriptors only; the mock tests use synthetic frames. Neither verifies real enrollment accuracy, user effort, or camera capture timing.

## Follow-up

Use a consenting person's repeated enrollment captures to verify that selected views are genuinely different, keep the correct hand, and improve or preserve recognition. Report the complete capture-attempt denominator and do not tune against the sealed Axon validation cohort.
