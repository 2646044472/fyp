# Enrollment refresh after a transient status-query failure — 2026-11-09

## Change

A refresh-time network/API failure no longer deletes the browser's only enrollment token or claims the session cannot be found. The page preserves the token, exposes a status retry and cancellation, and does not offer capture resume until the server confirms the session state. A confirmed `EXPIRED` response still clears the token. A successful retry restores identity, hand, progress and selected previews before exposing the existing resume/commit controls.

## Verification

- The Node page harness simulated a failed first status request, confirmed token retention and no premature resume, retried with the same token, restored a partial session, and cancelled it. The existing explicit-expiry test still confirms that `EXPIRED` clears the token.
- `node --test tests/test_demo_page.cjs`: passed.
- No live API, camera, real person, or Pi was used.
