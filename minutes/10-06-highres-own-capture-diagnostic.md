# Own-camera high-resolution palm diagnostic (2026-10-06)

## Decision investigated

Do the newly collected full-sensor images rescue the current palm matcher, and what part of the capture-to-ROI pipeline fails first?

## Data and method

- [E] 38 stills were copied from the Pi's `runtime/highres_capture/`: 17 labelled left, 21 labelled right, all `subject=bankey`, `background=existing`, `distance_cm=30`. Each has a 3280x2464 full still, a 480x360 preview, and exposure/gain metadata. These were made through the older single-image endpoint; the only 10-image session manifest had zero samples.
- [E] The 38 photos were taken in two short runs over about four minutes, often 1-3 seconds apart. They are correlated frames, not 38 independent hand placements. Left and right are the only two labelled classes, from one person.
- [E] The running camera had selected a 640x480 sensor crop for the 480x360 preview and the full sensor for the 3280x2464 still. Directly scaling the preview ROI coordinates to the full photo produced invalid crops containing the whole hand and background. The corrected offline pipeline resizes each full still to 480x360, runs the project's `HandLandmarkTracker`, scales that ROI quadrilateral back to full sensor coordinates, perspective-warps the palm to 128x128, and applies `crop_and_normalize`. This found a hand in 38/38 photos.
- [E] For a diagnostic two-class trial, the first five images of each hand were the gallery; the remaining 12 left and 16 right images were probes. Match scores were the median of the five gallery comparisons. The primary matcher is the deployed `DoN`; `FastCC` is a secondary baseline. Lower scores mean a closer match. Results are in the ignored local `code/palm_demo/data/processed/pi-own-captures/highres-2026-10-06/algorithm-diagnostic/full-detected/` directory.

## Results

| Input and preprocessing | DoN correct-hand rank 1 | FastCC correct-hand rank 1 |
| --- | ---: | ---: |
| Full image downsampled before 128x128 ROI | 11/28 | 12/28 |
| Native full pixels before 128x128 ROI | 11/28 | 13/28 |
| Native ROI, central 80x80 recropped to 128x128 | 19/28 | 18/28 |
| Native ROI with CLAHE only | 13/28 | 13/28 |
| Native central 80x80 crop plus CLAHE | 18/28 | 15/28 |

- [E] On the ordinary native 128x128 ROIs, median DoN distance was 0.1115 to the labelled hand and 0.1066 to the other hand. The deployed enrollment threshold floor is 0.15: it would accept both the labelled and wrong hand in all 28 probe comparisons. The distributions overlap; a threshold change alone cannot separate this set.
- [E] The central 80x80 recrop improved the exploratory rank result, but median DoN distances were still 0.1155 to the labelled hand and 0.1187 to the other hand, both below 0.15. FastCC medians were 0.3532 and 0.3655. The improvement was selected after inspecting this same small set, so it is not held-out evidence.
- [E] The current runtime ROI uses width and height scales of 2.0 times the index-to-pinky MCP span, with its center 0.30 spans toward the wrist. The generated 128x128 crops visibly include finger bases and, in several images, palm boundaries and background. The exploratory center 80x80 recrop retains only about 39% of the original crop area. Its rank improvement is evidence that ROI content matters, but is not a validated parameter choice.
- [E] The DoN implementation convolves an inverted grayscale ROI with a line template, turns three responses into binary maps, and uses the minimum shifted weighted XOR distance. It therefore consumes the entire normalized 128x128 crop. The quality gate requires five consecutive frames, contrast >=12 and sharpness >=2, plus broad geometric stability; it does not assess palm-line distinctiveness. In the corrected offline full-still crops, contrast ranged from 20.0 upward and sharpness from 6.9 upward, so the broad numeric thresholds would not flag them. This is an explanatory comparison, not a replay of the live preview gate.
- [E] At native resolution the palm has more visible fine lines than the paired 480x360 preview, but its centre remains low contrast. A bright haze enters the lower part of many later frames. Three inspected central palm patches had no pixels at grayscale level 250 or above; the pale appearance is not simply hard digital clipping.
- [C] The central recrop result suggests the current ROI includes too much finger base, palm boundary, and background. Illumination/IR reflection and residual focus may also suppress fine lines. The 38 images cannot isolate those causes because illumination, pose, and hand placement were not independently controlled.

## Development action and limits

- [E] The Pi preview was changed to IMX219's 1640x1232 full-field binned sensor mode while retaining 480x360 output. The service restarted successfully and its log confirmed the selected 1640x1232 sensor format. This makes preview framing correspond to the full still's field of view. The previous 640x480 preview mode had a much narrower field.
- [E] The older single-image endpoint now rejects captures during an active 10-image session. A direct request returned HTTP 400, the session remained at zero captures, `/collect` returned HTTP 200, and the service remained active.
- [E] Templates created before the field-of-view change are rejected for verification and require re-enrollment. Existing template files and original captures were preserved.
- [E] The collection page now shows, for each new 10-image capture, a full-still-derived `roi_128.png` and a native `palm_detail_512.jpg`, and includes both in the ZIP. The former uses the last stable preview quadrilateral to crop the full still; it is a diagnostic approximation because the live verifier uses the preview frame and the hand can move before the still is recorded.
- [GAP] No hand image has yet been captured under the new full-field preview configuration, so its live READY behavior and 10-image removal flow still need an operator check.
- [GAP] The gallery/probe split shares one short capture period and one person. It does not measure biometric accuracy, cross-session performance, or security. The next gate is separate labelled 10-shot sessions with true remove-and-replace, fixed camera distance, and controlled illumination. Keep a later session fully held out before choosing preprocessing or a threshold.
- [E] At the user's request, the `/collect` implementation was later changed to allow immediate, continuous 10-shot capture without a stability or hand-removal gate. It keeps full stills when no recent ROI exists. These continuous shots can check focus, crop, and lighting; they should not be counted as independent re-placement trials or used alone for cross-session validation.
