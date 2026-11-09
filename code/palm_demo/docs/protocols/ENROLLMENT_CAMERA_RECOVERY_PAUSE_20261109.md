# Enrollment pause on camera interruption — 2026-11-09

## Change

When the enrollment step API returns `capture_failure=CAMERA_UNAVAILABLE`, the browser now stops the automatic step loop and preserves the existing server session, token, selected previews, and candidate-pool progress. The page exposes the existing manual resume/cancel controls. Automatic continuation uses the existing readiness transition: a not-ready status must be observed, then camera and ROI status must become fresh and READY. If the capture call fails while the preview still reports READY, the session stays paused and requires manual resume rather than immediately retrying in a loop.

Other failures, including `CAPTURE_TIMEOUT`, retain their current retry behavior. `NO_HAND` keeps its existing pause semantics.

## Verification

- `node --test tests/test_demo_page.cjs`: passed, including a mocked camera-unavailable response, no repeated step requests across a simulated 2-second pause, retained candidate-pool progress/token, exactly one automatic resume after not-ready→READY, and no parallel loop on subsequent READY polls.
- No camera, real hand, Pi, recognition cohort, or matcher was used in this check.
