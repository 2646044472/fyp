# Counter enrollment and palm payment

The PC runs Palm Merchant, customer registration, palm capture, and checkout. The phone runs Palm Wallet for balance, demo top-ups, and receipts. Pi 5 performs capture and recognition and stores palm images and templates locally. PalmPay stores opaque identity references.

## Start

Start the configured Pi service with `systemctl --user start fyp-fpn-c-e10-station.service`.
On Windows run `scripts/start-fpn.ps1 -TunnelOnly` in one terminal and `scripts/start-fpn.ps1` in another. The launcher prompts for the operator key. Its default threshold is the experimental 0.80 setting. Use `-Threshold` to change the trial value.

For public phone access, run Cloudflare Tunnel against port 8000, set `PALMPAY_SECURE_COOKIES=1` before starting the backend, and use the HTTPS address on both devices. A quick tunnel's URL changes when recreated. The computer, Pi, and tunnel need to stay running.

## Register a customer at the PC

1. Sign in to Merchant and select **Enroll customer**.
2. Choose **Create customer wallet** or **Existing wallet**. The customer enters their credentials at the counter, selects a hand and reviews the capture consent.
3. Continue to the embedded capture page. The selected identity and hand are assigned by the backend.
4. Select **Start capture** in that page. Hold the selected palm toward the Pi camera, capture for at least 60 seconds, then select 10 photos.
5. Review the photos and confirm and save. PalmPay confirms the saved template and links it to the wallet automatically. The PC displays **Palm registered**.
6. The customer signs in to Wallet on their phone using the same credentials. No pairing code is needed.

The embedded preview and review images are served to the authenticated operator browser. When using the public tunnel, this traffic travels through Cloudflare over HTTPS. Captures remain persisted on the station. The proxy permits enrollment actions for the selected identity and excludes the station's general library-management routes.

## Pay at the PC

Add products in **Checkout**, select **Pay with palm**, then **Start palm verification**. The customer holds the registered hand toward the Pi camera. A matching result can settle the simulated payment. The phone receives a receipt and updated balance while Wallet is open.

The POS checks station connectivity. Camera standby means the station responds while the camera is closed. Verification waits for fresh frames for up to 20 seconds and allows repositioning after a low score. Cancellation prevents settlement and releases the camera when the current request finishes.

## Recovery

The counter remembers the selected enrollment in that browser tab. Refresh restores the embedded capture session. Sign in again with the same customer to recover an unexpired preparation. Preparing enrollment is idempotent for the selected hand. If saving succeeds but the response is lost, status checks reconcile the saved template and link the wallet. Expired preparations require signing in again. Cancelling capture releases its pending link.

## Validation

Automated checks exercise counter credentials and consent, server-assigned capture identity and hand, route scoping, automatic binding, duplicate settlement and payment failures. The browser acceptance scenario creates a customer at the PC, simulates counter enrollment and payment, signs into the phone wallet, verifies receipt synchronization and refresh recovery, and adds demo funds from the phone.

Physical capture, recognition accuracy with the current camera, and phone-device connectivity require a live user session. The 0.80 threshold remains experimental. Restart recovery needs a separate device restart check.
