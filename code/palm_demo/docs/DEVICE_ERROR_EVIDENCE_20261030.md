# Three remaining device errors: complete five-frame evidence

The baseline is the verified Windows v26 + retained FastCC full168 run: 165 correct, three wrong, zero rejection. These are previously exposed development samples. This review does not claim independent generalization. No original, enrollment, label or threshold is changed, and the failed contour candidate is not revisited.

## Images and anatomical correspondence

Each error page includes its original query and actual primary ROI, followed by every one of the five true-identity and five returned-wrong-identity enrollment originals and ROIs in protocol order. The unchanged PKLNet sampler is rerun; all **30 displayed enrollment instances** exactly reproduce their stored FastCC base codes. A preliminary gray-before-warp reconstruction failed that check and is preserved but excluded from pixel evidence: color-warp/grayscale order and coordinate precision matter. The final atlas uses the actual runtime sampling path. Raw photos/ROIs remain private.

- Both xyt query crops center toward wrist/forearm, while all five true enrollment crops mainly cover the palm. At least one query includes background. Geometry passes do not establish semantic/anatomical correspondence. Small hand scale alone cannot explain the issue, since several true enrollment hands are also small but localized to the palm.
- The cyw query and its five enrollments all approximately cover the palm; their exact sampled regions, scale and appearance still differ. The returned kss-left frames share broad crease/illumination structure. This error cannot be explained solely by a wrist-versus-palm mismatch.
- The normalized views amplify weak contrast and noise. Normalization cannot supply missing discriminative texture. No image or enrollment frame is removed based on these observations.

## Exact observational replay

Seven original-image HTTP queries were mechanically selected before new scoring: all three errors, global slowest correct, the formerly wrong query corrected by retained evidence, first correct exhaustive query and first timely correct in the errors' case. All identities/five frames stay in each gallery. Every full-gallery score, status, returned identity and route matches the immutable Windows baseline exactly.

Complete instrumentation records **8,081 ordinary FastCC calls**: 8,055 fixed-pose calls and 26 actual geometric-warp calls, zero unknown query/target calls and no missing source records. An independent all-one source plane is propagated through actual raster warp chains, then eroded by the 17×17 filter footprint before stride-four sampling. All observed masks equal the same 28×28 valid response region; there is no additional unsupported crop interior. Black source-image pixels remain valid; this is not a foreground/skin mask.

The initial observer missed source records compiled under the retained-evidence helper's synthetic filename. Its exact original source and results are preserved in runtime. Adding that filename to tracing coverage captures the missing calls without changing recognition. The corrected seven-query replay again has exact baseline parity. Instrumented durations are not a performance control.

For all **30 error true/wrong frame pairs**, the exhaustive frame score equals the minimum of the existing fixed poses. No accepted union alignment wins. Only one of these pairs has an accepted union-scoring attempt at all (xyt `61f30739`, wrong stephen-left frame 3), and its score is worse than the pose fallback. Full before/after/merged frame evidence and independent CompNet primary/alternate frame distances are retained separately; metrics are never mixed.

## Boundary agreement mechanism and bounded ablation

For cyw `37d0c433`, returned kss-left frames 3/4 score .344727/.345703 in the pose search; using only fully supported responses gives .384921/.398860. True cyw frames 4/0 are .364204/.384067 originally and .367627/.372800 with supported responses. The old wrong ranking benefits more from artificial-boundary agreements. These pose-only numbers are mechanism diagnostics, not full-pipeline recognition results.

The two xyt errors also show boundary sensitivity, but their actual crops lack the same anatomical content as true enrollment. Independent primary CompNet ranks true xyt seventh and ninth. One available alternate crop raises true xyt to first for `61f30739`, but distance .426356 and gap .015090 fail both unchanged confidence conditions. For cyw, both primary/alternate CompNet rank the wrong kss-left first and true cyw second, also without confidence. Thus neither arbitrary metric mixing nor simply choosing one representation's best rank is justified.

This evidence supports one uniform [receptive-field distance ablation](DEVICE_RF_ABLATION_20261030.md), fixed before its recognition outcomes: exclude responses relying on artificial filter padding, use actual overlap denominators for all existing shifts, and apply this distance through the shared ordinary FastCC base in every stage. Do not change ROI, features, poses, five-frame aggregation, gallery, registration bounds, CompNet, quality scoring or thresholds.

The fixed seven-query pilot completed **5 correct / 2 wrong / 0 rejected / 0 processing failure**, versus 4 correct / 3 wrong originally: `37d0c433` genuinely becomes correct, with zero loss of the four original correct controls. The two xyt queries still misidentify and return different wrong competitors. This passes the predeclared small-pilot gate but is not a complete accuracy or speed result. Full168 fresh-enrollment validation is required before retaining the candidate; any original correct result lost disqualifies it. No scan follows a failure.

Owned scalar artifacts: [summary](experiments/device-error-evidence-20261030/summary.json), [all-gallery frame/pose ledger](experiments/device-error-evidence-20261030/frame-ledger.csv). Private illustrated report: `runtime/device-error-evidence-20261030-r2/report.html`; actual image atlas: `runtime/device-error-evidence-20261030-r1/atlas-actual/`. No public evaluation images, templates, feature arrays or weights are included in Git.
