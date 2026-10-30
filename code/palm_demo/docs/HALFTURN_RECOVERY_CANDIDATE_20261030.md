# Out-of-bounds half-turn ROI recovery — isolated candidate

Prospective candidate fixed before its original-device audit. Standard remains tag `standard-device-20261030`; no standard/core source, model, acceptance threshold or runtime policy is changed. New implementation lives only in `tools/halfturn_roi_recovery.py` on the experiment branch, is never imported by production and has no identity/filename/score input.

Motivation: development SMPD 008 F03 visibly includes the reference finger valleys but the original crop is just outside image bounds. Mapping a 180-degree input's prediction back produces an in-bounds, substantially overlapping crop. The matched 008 F00 control is already valid. This is a localization observation, not a recognition correction. Missing-valley side views are not required repair targets.

Fixed mechanism:

1. Call the standard illumination PKLNet localizer once. Return every valid result verbatim, preserving its arrays and diagnostics; perform no extra inference.
2. Only a primary `roi_out_of_bounds` result permits one exact 180-degree retry using the same model and policy. Other errors keep their original outcome.
3. Require the retry's existing geometry guards to pass, map all coordinates back, require original-image bounds and overlap with the primary prediction at least the **existing** illumination consistency IoU of 0.5. Do not search a threshold or a rotation set by identity score.
4. Resample original RGB/gray pixels using the mapped quadrilateral; do not use generated pixels or the rotated raster as a restored source. Map primary/alternate/branch/crop diagnostics consistently. Store the candidate provenance separately in its isolated runtime.

This is not an independent finger-valley visibility detector. Multiple model views can agree on the wrong region. Geometry-only recovery never counts as correct identity, and any full recognition test must retain wrong accepts and processing failures. A fixed rotation for every image was already rejected; this candidate has a narrower failure-only route and cannot inherit a recognition-success claim from that prior experiment.

First audit all 169 unchanged original-device photos and the fixed development control/failure pair. Record exact primary/recovered ROI equality for every original valid case, retry counts, geometric recoveries, new geometry failures and original integrity. If any valid original changes, stop the candidate as a regression. No per-person exceptions follow failure. Then perform the [mandatory full original-device regression](protocols/CANDIDATE_DEVICE_REGRESSION_REQUIREMENTS_20261030.json), including all 168 queries and actual isolated HTTP storage/payment handlers. Computer comparisons are not Pi timings; promotion remains subject to Pi regression and user authorization.

The full public baseline continues on its separately locked source. Any overlapping local audit load must be disclosed alongside its Windows timing record. No exclusivity or measured acceleration is assumed.
