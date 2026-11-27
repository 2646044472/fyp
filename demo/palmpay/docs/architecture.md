# Architecture and Phase 2 integration

React Router mounts the two applications under `/wallet` and `/merchant` at a shared origin. They share design tokens, UI components, and OpenAPI response types. TanStack Query owns server state and the POS XState machine renders states confirmed by FastAPI. The wallet service worker caches the shell and leaves API responses and WebSocket traffic online.

FastAPI exposes account registration, login and wallet activity under `/api/auth` and `/api/wallet`. `/api/palm` manages pairing codes and enrollment status. `/api/merchant` contains operator login, catalog management and order creation. `/api/payments` creates, reads and cancels payment intents. Customer and operator sessions use separate HTTP-only cookies. The operator key is supplied by the host.

The server snapshots product names, prices and quantities when creating the order. All money is recorded in integer MOP minor units. Order creation, intent creation and demo top-ups accept an `Idempotency-Key` header. Settlement also uses the immutable intent ID as the authorization key, and stores the receipt and paired ledger entries in the same SQLite transaction as the two balance changes. An immediate write transaction serializes competing attempts. A second approval returns the previous result. Retrying an expired or failed intent creates a fresh challenge for the same unpaid order.

The mock provider binds the intent, merchant, amount, currency and expiry to the identified enrollment. The simulation endpoints require an operator session, demo mode, and the mock provider. Revoking consent deletes the simulated enrollment. An authenticated WebSocket at `/ws/events?role=wallet|merchant` sends a refresh signal after the committed state changes. Clients refetch scoped data on that signal, after reconnecting, and periodically as a fallback. SQLite runs in WAL mode and Alembic manages its schema.

## FPN station integration

The [FPN + C E10 integration](fpn-station.md) uses the FYP station's loopback API over localhost or SSH. Customer registration and palm enrollment run at the PC counter. The customer authenticates and reviews capture consent there. The server assigns an opaque identity and binds all station requests to that identity and hand. The embedded station provides capture and review, and saving automatically links the template to the wallet. Status checks recover the link if a save reply is lost. The camera verification call runs outside the SQLite write transaction. Settlement then rechecks intent expiry and state, customer consent, and the linked hand. The station retains all captures and templates.

A future deployment with remotely managed stations would need per-terminal identity, authenticated one-time challenge exchange, and a calibrated acceptance policy. These are separate from the local research setup.

## Demo limitations

- The deployment models one café and register with a shared operator key. Production would require per-operator accounts, role and terminal scoping, rate limits, lifecycle controls, and operational monitoring.
- The open wallet receives WebSocket updates. Background push and offline payment are outside Phase 1.
- English is the default. The signed-in wallet’s main navigation, home, and profile support Traditional Chinese. Sign-in and registration, receipt item names, server errors, and the operator POS currently use English.
- Menu photographs represent the product categories. They are illustrative for recipe-specific drinks.
- SQLite and the refresh feed are suited to the local research demo. Orders and wallet activity are currently returned without pagination.
- Physical phone installation and QR scanning require a phone that can reach the HTTPS demo URL. The Cloudflare quick tunnel is temporary.

