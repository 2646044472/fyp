# Single-device ROI and recognition pipeline (2026-10-28)

The defaults remain v5 localization and DoN matching. The optional `FastCCWindowUnion-v4` uses the existing frozen PKLNet model. Neither candidate localization nor matching receives identities, filenames or split assignments. The old and new devices are evaluated separately, with no cross-device matching. Nothing was deployed to the Pi and the network was not changed.

## 1. Localization candidates

- Run the existing aspect-based localizer separately on the original and gamma 0.6 images. Keep valid quadrilaterals from each.
- The primary ROI follows v5: use the gamma result if it is valid and has IoU of at least 0.5 with the original-image box. Otherwise apply the existing fallback rule. The primary ROI supplies the base template and enrollment texture region.
- If the image aspect ratio differs from 4:3 by more than 0.05, place the largest possible 4:3 window at three equally spaced positions. Run original/gamma heatmap localization in each window and map the results back to source coordinates, adding up to six candidates. Images close to 4:3 get no extra windows. This is a geometric rule, not routing by device or identity.
- Original/gamma candidates retain their existing validity checks. Window candidates must have finite coordinates, all four corners inside the original, and a keypoint span of at least 0.1 times its shorter side. Geometric validity does not establish that a candidate contains the correct palm region. Report model loading and inference exceptions rather than silently dropping candidates or test samples.

## 2. Search regions and descriptors

- Map each candidate to 384×384 coordinates. On the query side, search both the box itself and a region twice as wide and high with the same center (768×768, coordinate offset 192). This expands the correspondence search.
- Original/gamma candidates use four fixed descriptor views with sigma 0, 2, 4 and 8; window candidates use 0 and 2. Smoothing is only for finding RootSIFT correspondences, not for the final pixels scored by FastCC.
- Enrollment correspondences always come from the primary ROI: the original and sigma 2, 4 and 8 views. The box does not change with the query label.
- Retain the `expanded_strict` branch: extract original and sigma 2 query descriptors from the saved v2 768 context. Compute these separately from views generated directly from candidate quadrilaterals to preserve historical resampling differences.

## 3. Correspondence and alignment

Require mutual nearest neighbors with a ratio below 0.85. Fit a partial affine transform with RANSAC: 3 px threshold, at most 2000 iterations and a fixed random seed. Require at least four inliers, an inlier convex hull covering at least 2% of 384² at each end, scale in 0.5–2 and absolute rotation no greater than 40°.

After the geometric checks, use the transform to sample the saved **native grayscale pixels** directly to 128×128 in a single pass. Each output corner must leave at least one pixel of margin inside the original so black padding cannot affect recognition. Store the grayscale image in the template as a lossless PNG and check its dimensions when decoding. Do not use generative repair or manual reference boxes.

## 4. Scoring

Normalize the aligned ROI using the existing procedure, compute FastCC and compare it with the FastCC template of the primary enrollment ROI. For every image pair, use the smallest distance across all valid candidates and the original v2 fallback. Each identity has five enrollment templates; its score is the mean of the two smallest distances. There are no sample-specific exceptions, identity-specific thresholds or branches selected using the correct answer.

`base_full` is a separate historical control: only its base descriptor switched to native-pixel sampling. It is not a dependency of the offline union or the parent baseline of `expanded_strict`. It improved 210 directed pairs over v2. Five of those pairs were still better than the final offline union, with a maximum distance difference of 0.0009765625. These differences are recorded in `single-device/union-audit.json`; they are not silently incorporated into the runtime to improve its results.

## Versions and validation limits

- v2: original primary ROI, two descriptor types and local alignment.
- v3: multiple original/gamma candidates and single-pass native-pixel sampling; no complete union of window and coarse-scale candidates.
- v4: full implementation of the window, coarse-scale and baseline branches above. It has a separate template version and cannot mix old and new templates.
- Offline `window-coarse-union`: takes the minimum across the computed candidate distances; all development experiments scored 20. This does not establish that the v4 runtime entry point, a live camera or the Pi passed validation.

The runtime evaluation uses `audit_registered_runtime.py --matcher FastCCWindowUnion-v4`: compress and save 80 templates, reload them and score all directed same-device pairs under fixed forward/reverse splits, ten random splits and an additional 100 random splits.
`audit_union_fresh_features.py` reruns localization and checks the templates. `verify_union_runtime.py` checks original-image hashes, splits, baseline and distance consistency.
`replay_pi_pipeline.py --demo-matcher FastCCWindowUnion-v4 --policies illumination` replays historical original images through the actual local HTTP capture, enrollment, query and isolated simulated payment flow.

These photos were repeatedly used for algorithm selection and parameter development. Perfect scores on all fixed splits would still not demonstrate generalization to an independent new session, validate stranger rejection or guarantee Pi performance. Templates contain palmprint pixels and descriptors and must be protected as biometric templates.

## Subsequent v5 spatial checks and v6 demo speedups

`FastCCAnchoredUnion-v5` requires the candidate box to intersect the automatic primary ROI by more than 1 pixel² and applies the same check to the final aligned scoring box. This removes clearly disjoint candidates; it is not hand segmentation. An incorrectly located primary box can still exclude useful candidates. No new localizer has yet resolved why the primary box is too small. On the fixed 80 images, the check removed 48 descriptor views from 9 images without changing any of the 3120 pair scores.

`match_with_diagnostics` returns the winning branch, descriptor-view index, source_matrix and aligned_quad for each pair. An identity's best2 score may combine two different alignments, so there is no unique final candidate. If the legacy_v2 fallback wins, report the fallback only; do not invent an unrecorded alignment box. See the actual contribution plots in `runtime/roi-palmir-20261028/single-device/report-v5.html`.

`FastCCDemo-v6` retains v5 scoring and mainly changes computation and storage:

- Enrollment computes only the legacy base template and coarse-scale gallery descriptors. It neither computes query candidates nor saves a native query PNG.
- Queries still run the full candidate search, with up to two workers and deterministic output order and scores.
- Decode each query image only once. Keep only compact data needed for gallery matching, not unused query images or views.
- Cap the gallery cache at 64MiB. Check file inode, size, and nanosecond modification/creation times. Re-enrollment, metadata changes and deletion invalidate entries; use LRU eviction above the limit. Only templates with compatible metadata participate in recognition.
- v6 templates carry a distinct version identifier. The enrollment-only format cannot serve as a query template. Templates from the old algorithm require re-enrollment; existing accounts and balances are retained under the existing procedure.
- Recognition API results include `timing_ms`, broken down into capture/extraction, gallery matching and total time. The frontend displays a localization preview only; it does not label this thumbnail as the unique final scoring ROI.

Parallel extraction was byte-identical to the serial implementation on all 80 images except for the version identifier. Compact enrollment and parallel matching preserved all 3120 non-self, same-device pair scores exactly, leaving the original 224 fixed-split results unchanged. See the subsequent `report-v6.html` for the complete HTTP and timing records.

To enable the optional demo (no service was started on the Pi in this round):

```sh
python debug_ui.py --enable-recognition --roi-mode pklnet --demo-matcher FastCCDemo-v6
```

The default capture-only service and DoN parameters are unchanged. Local timings do not replace on-device validation with the Pi camera and CPU.
