# Legacy Raspberry Pi Station: 60-Second Palm Enrollment

- Open `/enroll` on the Raspberry Pi's legacy station and click **Start capture**. The server collects frames for at most 59 seconds from that point, leaving about one second for the page to poll. Camera, network, or browser problems can delay the page. Late results are not added to the current session.
- The current legacy implementation distinguishes a successfully cropped palm ROI from an ROI that qualifies as an enrollment candidate. A crop may still fail the old absolute sharpness or contrast checks. Enrollment now ranks geometrically valid, nonempty, fresh crops from their original exposure. Verification camera and quality requirements are unchanged.
- The station usually picks from roughly a dozen usable candidates and may stop once it has enough high-quality, complementary shots. You do not have to wait out the timer. Present only one hand throughout; slight changes in distance or angle are fine. If fewer than five distinct usable photos are available, the station keeps what it captured instead of filling the set with duplicates.
- Each review pair shows the original image and ROI from the same exposure. Click either to enlarge it. Remove and recapture a pair or fill only the remaining slots during the current session. Click **Confirm and save** only after reviewing five photos of the same palm. The station does not record the full video or submit unselected images.
- The old failure mode can be reproduced with synthetic inputs. That does not establish that all 21 candidates in a particular live run were rejected for the same reason. The repository includes the code and simulated regression checks; the field Pi was not connected for this revision. Use the next hardware trial to check the first candidate, the final selection, and timing. This revision updates both the base camera module and the capture station files, so do not replace only the old station script.

```sh
python verify_best_frame.py
python verify_ranked_window.py
python verify_review.py
python verify_adapter.py
python verify_render.py  # Requires Node.js
```
