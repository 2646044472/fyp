# Repository integration and local data

## Boundaries

- `demo/palmpay/` owns the PC register, phone wallet, payment API, tests, and demo documentation.
- `code/rasp/` owns the existing Pi camera and FPN + C E10 station. PalmPay uses its HTTP API over localhost or SSH forwarding; it does not import its Python environment or models.
- The two applications keep separate dependency environments and run instructions. No FYP-root Node workspace is required.
- `docs/palmpay-pipeline.html` is a standalone, editable HTML presentation with embedded assets. Its existing presentation language is preserved.

## Start from a fresh checkout

From the FYP root, change directory to `demo/palmpay`, then follow this folder's README to install dependencies and build. On Windows, `./scripts/start-mock.ps1` starts the synthetic demo. For hardware mode, follow [station integration](fpn-station.md) and the [station instructions](../../../code/rasp/README.md). No launcher starts the Pi or a public tunnel automatically.

The browser paths remain `/merchant` and `/wallet`. Moving source files does not add `/demo/palmpay` to their URLs. The standalone HTML presentation can be opened directly from disk.

## Existing local state

The original sibling PalmPay folder is retained as a fallback. It is not the continuing development location. Its database, installed dependencies, environment settings, and test results were not copied into this repository.

The default SQLite URL is relative to the process working directory. Starting this copy creates a separate local `palmpay.db`; existing accounts and balances are not automatically transferred. If existing state is needed, stop the old backend first and use `PALMPAY_DATABASE_URL` with an absolute SQLite path to the intended database. Do not run both copies against the same database. Never copy a live SQLite database without accounting for its WAL state.

Create a new `.venv` and install Node dependencies here; do not relocate the old virtual environment. Only one backend should use port 8000 at a time. For Docker, run `docker compose -p palmpay up --build` here; do not remove volumes when switching directories. Confirm any custom project name before reusing existing Docker data.

## Verification scope

Use synthetic accounts and the mock provider for automated acceptance. Tests use a separate database under `test-results/`. The end-to-end scenario covers PC account creation and enrollment, phone sign-in, payment and matching receipts, reload recovery, offline reconnection, repeated approval, and demo top-up.

Passing these checks does not establish real-camera payment, calibrated recognition accuracy, Pi restart recovery, or physical-phone connectivity. Hardware acceptance remains separate. Captures, templates, model weights, credentials, and local wallet databases remain outside Git.

Python dependency versions are recorded in `requirements.lock.txt` from the original demo environment. Install that file to reproduce the verified environment; `requirements.txt` retains the declared dependency ranges. Node dependencies continue to use the unchanged pnpm lockfile.

## Integration verification (2026-11-27)

- Production frontend build: passed.
- Frontend state-machine test: 1 passed.
- Synthetic backend tests: 11 passed.
- Full browser scenario: 1 passed, including counter enrollment, wallet synchronization, receipt recovery, offline reconnect, duplicate approval, and top-up.
- Mock launcher: started from outside the demo directory with a separate synthetic database; both application routes returned HTTP 200. The smoke-test process was stopped afterward.
- Standalone presentation: all 8 slides, embedded images, keyboard/overview navigation, and mobile scaling passed from the new location.
- Docker Compose configuration: validated. The container image was not built or started.
- Core source hashes and both dependency sets were checked against the original demo. No application behavior was changed for the integration.

A third-party TestClient deprecation warning remains in the existing Python stack; it did not fail the tests. Pi hardware and Cloudflare were not started for these checks. These checks cover the local integration; publication is recorded in Git history.
