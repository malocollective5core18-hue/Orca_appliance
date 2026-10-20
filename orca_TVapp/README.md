# ORCA TV

TV-facing ORCA experience and device-client project. The current folder contains a browser-based **demo simulator**, not an installable production TV application or a connected hardware agent.

See the root [system architecture](../SYSTEM-ARCHITECTURE.md) for how TV, mobile, and the intended central ORCA Cloud service fit together.

## Current implementation

- `orca-tv-demo-1.html` is a self-contained HTML/CSS/JavaScript mock with a 1920×1080 visual stage scaled to the browser viewport.
- It simulates standby, boot/check, offline, activation-code, linked, home, restricted, and payment-result screens.
- The local state object and demo controls simulate Wi-Fi, activation, payment, restriction, and reset behavior.
- No network API, WebSocket, EventSource, local persistence, device identity, hardware SDK, or remote-control integration is present. The displayed activation code and device/account/payment details are sample demo state.
- Google Fonts is loaded externally; logo/media references and network behavior should be checked before using this in an offline or production TV environment.

Do not install this HTML simulator as production TV firmware. Its controls deliberately allow local state changes and do not enforce ORCA account, finance, customer-consent, or device-security rules.

## Intended production TV responsibilities

1. Boot into a customer-safe connection/activation experience.
2. Authenticate to ORCA Cloud using a provisioned per-device identity, never a customer bearer token embedded in the TV.
3. Request and display a short-lived, single-use activation code when authorized by the server.
4. Wait for the server to confirm a customer link; do not infer success because a code was typed or a button was pressed.
5. Receive authoritative appliance state and only server-authorized, policy-versioned commands.
6. Report connectivity, device health, command receipt/application/rejection, and sequence/version information with minimal telemetry.
7. Recover after network loss by reconnecting securely, fetching current server state, and discarding expired or stale commands.
8. Avoid displaying customer balances, payment credentials, phone numbers, or unnecessary identity details on a shared screen.

The TV must not accept payments, mark a payment confirmed, determine whether an account is overdue, decide restriction policy, or bypass customer-support recovery. The backend and hardware teams must approve what the TV can display/control and how a customer can recover from a lost connection or replaced device.

## Intended relationship with mobile and central service

- The mobile app authenticates the customer and submits their activation code to the central service.
- The central service verifies the customer, code, device, expiry, and ownership constraints; it stores the link and returns status to both clients.
- The TV receives link/status changes through a secure device channel selected for the actual hardware. HTTPS polling, WebSocket, or MQTT over TLS are options, not confirmed choices.
- Payment-provider webhooks update the central ledger. The service decides whether the device's approved state should change and sends a versioned command. Mobile and TV only display the result returned by the service.
- TV does not connect directly to the phone or payment gateway. The central service is the only coordination and authorization point.

## Production decisions still required

- TV hardware, operating system, application runtime, firmware/device agent, hardware identity source, secure storage, clock trust, and update mechanism: **UNVERIFIED**.
- Device registration and key provisioning/rotation/revocation process: **UNVERIFIED**.
- API/device message schema, transport, heartbeat cadence, offline grace period, command expiry, acknowledgement and replay handling: **UNVERIFIED**.
- Activation code format, issuance, expiry, attempt limit, and account/appliance scoping: **UNVERIFIED**.
- Financing restriction rules, customer legal notice, appeal, support override, and safe reactivation process: **UNVERIFIED**.
- TV platform build/test/deployment commands and CI: **UNVERIFIED**; no production TV package is present here.

Agree these with the backend, mobile, embedded hardware, payment, support, security, and legal owners before replacing the simulator with live behavior.
