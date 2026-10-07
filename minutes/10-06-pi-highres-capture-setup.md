# Raspberry Pi full-resolution capture setup (2026-10-06)

## Decision investigated

Can the existing IMX219 NoIR camera deliver a full-resolution still through a dedicated collection page, resume the live preview, and retain enough information for a later palm focus check?

## Evidence

- [E] The Pi's running `palm-debug-ui.service` still previews at 480x360. A dedicated `/collect` page now lets the operator label participant code, hand, background, optional distance and notes before capture. It saves `full.jpg`, `preview.jpg` and `metadata.json` under `runtime/highres_capture/<sample_id>/`. The browser shows a click-to-inspect 512-pixel native crop and displays exposure and analogue gain.
- [E] A clearly labelled **empty-scene calibration** still produced a 3280x2464 JPEG and a paired 480x360 preview. Its sensor metadata recorded 59.999 ms exposure, 5.45 analogue gain, 60075 us frame duration and full-frame `ScalerCrop`. The service remained active and `/frame.jpg` returned HTTP 200 after the mode switch. The calibration sample was moved into `runtime/calibration_capture/` to keep palm samples separate.
- [E] The page rendered in the in-app browser with live preview and blank required labels. `GET /collect` returned HTTP 200 after deployment. The Pi's original repeatability collection controls were retained in the merged debug UI.
- [E] The Pi clock was about 20 days behind the PC after offline boot; it was reset from the PC's UTC time on 2026-10-06. Metadata also stores browser UTC time to make future clock drift visible.
- [E] The dedicated page was extended to one labelled batch of ten 3280x2464 stills. After each capture it waits for two distinct no-hand processed frames before accepting the next hand placement. The page shows capture progress, saved images and their original-pixel crops, and offers a ZIP once all ten are saved. Incomplete batches can be abandoned without deleting their files. The updated Pi service was active; `/collect` returned HTTP 200, `/api/status` reported an idle ten-image batch, and an attempted capture without a started batch returned HTTP 400.

## Limits and next gate

- [GAP] No new palm image was captured as of this note. The empty scene does not measure focus or palm-line visibility at the intended hand distance.
- [GAP] The ten-image palm flow has not been exercised with a hand yet; the user will operate the collection page. Once a labelled batch is available at fixed distance/light, compare native palm detail and a 128x128 normalized ROI with the paired 480x360 previews, recording exposure and gain. Do not infer recognition accuracy from an empty-scene calibration image.
