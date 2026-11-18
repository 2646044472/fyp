# Resuming automatic enrollment after a step fails — 2026-11-09, X

## Failure mode

After the page obtained a token from `/api/demo/enroll/start`, a failure on the first or any later `/api/demo/enroll/step` request only displayed an error. The page still held `enrollmentToken`, but `enrollmentPaused` was false, hiding the option to resume capture. The user could only cancel the session and discard the cached candidates. The same state occurred if a manual resume failed after a pause.

## Change

Both capture-error branches now preserve the paused state while the page holds a token and prompt the user to resume manually once preview is ready, or cancel. Resuming uses the same token. The existing `resumeEnrollment` checks camera and ROI readiness and guards against concurrent actions. Server sessions, selection of five out of eight candidates and quality thresholds are unchanged.

## Verification

`node tests/test_demo_page.cjs` passed. A new interaction test simulates a transport failure on the first step, another failure on the first manual resume, and a successful response of NO_HAND on the second manual resume. Each resume uses the same token; canceling hides the resume button. `git diff --check -- demo_page.py tests/test_demo_page.cjs` passed.

## Limits

This was a simulated page test without a camera or a human participant. Resume will still fail if the server session has expired after 120 seconds or the token has been revoked. The change only restores the page's recovery path after a temporary step-request error.
