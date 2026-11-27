# PalmPay

The FYP payment demo lives in `demo/palmpay/`. Run all commands below from this directory, not from the FYP root. The Pi recognition station remains in [`../../code/rasp/`](../../code/rasp/README.md).

See [repository integration and local data](docs/repository-integration.md) and the [offline pipeline presentation](docs/palmpay-pipeline.html).

Palm Wallet is a mobile-first PWA. Palm Merchant is a café POS for CKLC Coffee. Both use the same FastAPI service and SQLite ledger. All balances and purchases are simulated. Use either the simulated provider or the local FPN + C E10 station for authorization.

## Run the demo

Install Python 3.12 or newer, Node 22 or newer, and pnpm 12. Run these commands from the project root. Change `.venv\Scripts\python.exe` to `.venv/bin/python` on macOS or Linux and set the environment variables using your shell.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
pnpm install --frozen-lockfile
pnpm build

$env:PALMPAY_DEMO = '1'
$env:PALMPAY_OPERATOR_KEY = 'replace-with-your-own-demo-key'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open [Palm Merchant](http://localhost:8000/merchant) and sign in with your operator key. For a physical-phone demo, open the POS using the host computer’s LAN address and allow inbound traffic on port 8000 on the local network. Keep both devices on the same network.

1. On the PC, open **Enroll customer** and choose **Create customer wallet** or **Existing wallet**.
2. Enter the customer's credentials, choose a hand and review capture consent.
3. In FPN mode, capture and review the palm within the embedded station page. Save to link the wallet automatically. In mock mode, use the clearly labeled **Simulate enrollment** control.
4. On the phone, open Wallet and sign in with the same account. The initial simulated balance is MOP 500.00.
5. At the PC checkout, add one Iced Latte and select **Pay with palm**.
6. In mock mode, enter the enrolled email and simulate approval. In FPN mode, start verification and hold the registered hand above the camera.
7. Compare the receipt references and verify that Wallet updates to MOP 475.00.
8. Refresh both applications. Repeating the approval must preserve the original balance and receipt.
9. Add MOP 100.00 from Wallet to test the demo top-up.

For installability on a separate phone, serve the built app from a trusted HTTPS origin. Under HTTPS, set `PALMPAY_SECURE_COOKIES=1` and configure the reverse proxy to preserve the public Host and forward WebSocket upgrades. Localhost can use HTTP. Plain LAN HTTP supports the browser demo without service-worker installation.

During frontend development, run `pnpm dev` with FastAPI running at `127.0.0.1:8000`. Vite proxies the API and WebSocket and serves both app routes. Alternatively set the two demo variables and run `docker compose -p palmpay up --build` from this directory. The explicit project name keeps the `palmpay_palm-data` volume identity stable.

For camera-backed authorization, follow the [FPN + C E10 station integration guide](docs/fpn-station.md).

After dependency installation, Windows users can also run `./scripts/start-mock.ps1` from this directory. It prompts for an operator key, selects mock mode explicitly, migrates the local database, builds the UI, and starts the server.

## Verify locally

```powershell
pnpm build
pnpm test
.\.venv\Scripts\python.exe -m pytest tests/backend
pnpm exec playwright install chromium
pnpm e2e
```

Playwright starts a dedicated server and a separate database under `test-results`. The test opens independent Chromium wallet and register contexts, verifies matching receipts, retries an authorization, and checks recovery after network loss. It also captures the mobile, tablet, and desktop views in `docs/screenshots`.

## Architecture and API

- [Architecture and Phase 2 integration](docs/architecture.md)
- [FastAPI OpenAPI schema](openapi.json) and [generated TypeScript definitions](packages/shared-types/openapi.ts)
- [Menu photo credits](docs/photo-credits.md)

FastAPI also serves interactive API documentation at `/docs`. Regenerate API types after changing a response model with `python -m scripts.openapi` followed by `pnpm exec openapi-typescript openapi.json -o packages/shared-types/openapi.ts`.


## Screenshots

- [Wallet home](docs/screenshots/wallet-mobile.png) and [live payment notification](docs/screenshots/wallet-payment.png)
- [Desktop checkout](docs/screenshots/merchant-desktop.png) and [tablet checkout](docs/screenshots/merchant-tablet.png)
- [Merchant receipt](docs/screenshots/merchant-receipt.png)
