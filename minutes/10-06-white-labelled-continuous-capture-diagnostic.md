# Continuous high-resolution palm capture diagnostic (2026-10-06)

## Decision investigated

Whether the new left/right 10-shot batches fix the capture and matching failures seen in the earlier Pi batch.

## Inputs and protocol

- [E] Pi manifests `20261006T035537011048Z-05a19b1d` (left) and `20261006T040847950968Z-c9b9f00a` (right) each contain ten 3280x2464 full stills, paired 480x360 previews and metadata. Both say `subject=bankey`, `background=white`, `distance_cm=30`. They were taken continuously, without a required hand removal between shots.
- [E] The full stills visibly show a dark desk and a green region behind the hand. The `white` metadata label is inconsistent with these image backgrounds; this capture cannot estimate the effect of white paper.
- [E] For diagnosis, each full still was downsampled to 480x360, independently processed with the project's `HandLandmarkTracker`, then its quadrilateral was mapped back to the full still. The existing `crop_and_normalize` generated a 128x128 ROI. The deployed DoN algorithm was evaluated with first five captures of each hand as gallery and last five as probes, using median distance to five gallery features. This is an exploratory two-class, one-person, same-day comparison, not a biometric accuracy estimate. The ignored local report and images are in `code/palm_demo/data/processed/pi-own-captures/highres-2026-10-06/white-continuous-2026-10-06/`.

## Findings

- [E] The old collection-page path saved an automatic ROI for 9/10 left stills and 7/10 right stills. Independent detection on the saved full stills found a palm in 20/20, including all four missed by the page. The missing crops therefore do not mean the full images lack a detectable hand.
- [E] For the 16 images with both ROIs, the median difference between the preview-based ROI center and a full-still redetection was 51.5 full-sensor pixels for left and 86.2 for right. One right sample differed by about 638 pixels. Using a pre-still preview location to crop the later still can visibly misplace the palm.
- [E] The saved and redetected 128x128 crops often include finger bases and palm edges. The native 512x512 patches show major creases, but many fine lines are faint; some right-hand patches are especially low in local detail. The images do not isolate focus, exposure, illumination, and hand motion as causes.
- [E] With full-still redetection, DoN ranked the labelled hand first in 7/10 probes. Median genuine and wrong-hand distances were 0.1243 and 0.1251; 7/10 rank margins were smaller than 0.003 in absolute value. All ten genuine and all ten wrong-hand distances were below the deployed threshold floor of 0.15, so this threshold accepts both hands in all ten comparisons. On the seven probes with saved live ROIs, rank was 7/7, but wrong-hand acceptance was likewise 7/7. These results are not directly comparable because the missing saved ROIs remove the three harder right-hand probes.
- [E] Re-cropping the central 80x80 of the full-still ROI reduced DoN rank to 5/10 on this batch. The earlier apparent benefit of this change did not generalize to this exploratory split; it must not be deployed as a matcher fix.
- [E] The full-still detector took about 0.24 seconds for one existing right-hand still on the Pi. The collection code was updated to redetect on the captured full still before producing the 128x128 and 512x512 diagnostics. Existing capture files were preserved.

## Interpretation and next gate

- [C] Three separable failures remain: pre-still preview coordinates can drift relative to the saved still; the present broad ROI includes irrelevant anatomy/background; and DoN plus its genuine-only threshold floor has too little separation for the two hands in this batch. Direct still redetection addresses the first issue for future captures but does not fix the matcher.
- [GAP] The two ten-shot series are temporally correlated and contain one person's two hands. There is no real white-paper condition, independent return visit, additional participant, or known ground-truth focus/illumination manipulation. Do not infer cross-session reliability, false-acceptance rate, or a camera-purchase decision from these twenty images.
