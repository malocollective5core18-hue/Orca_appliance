# ORCA web and intended central service

This folder groups ORCA public web and dashboard prototypes. The owner intends the webserver project to become the central service for all ORCA software. **The current checked-in code is not that production service yet:** this folder contains static HTML prototypes and media, but no API server, backend package, database migrations, payment integration, or device service was found in the repository snapshot.

See the root [system architecture](../SYSTEM-ARCHITECTURE.md) for the complete target architecture and interactions with mobile and TV.

## Files currently present

- `index.html` — public ORCA marketing page.
- `indexb.html` — another public marketing-page variant. Which version is canonical for deployment is **UNVERIFIED**.
- `orca-dashboard-demo-1.html` — browser dashboard demonstration with overview, device, payment, alert, partner, and audit-style views. It generates sample records locally in JavaScript. The only observed use of `localStorage` is the dashboard theme preference; business data is not fetched from an API.
- `logo.png`, `orca-logo-B.png`, `orca-logo-w.png`, `bc2.png`, and `VID-20261015-WA0031.mp4` — visual/media assets. Their licensing, source-of-truth versions, and production use approval are **UNVERIFIED**.

The public pages' actual publishing host, form handling, analytics, canonical page, and production URLs are **UNVERIFIED**. The demo dashboard must not be represented as a live financial or device-control console.

## Intended production responsibility

The central ORCA Cloud service should own the API and data authority used by:

- `orca_mobile/` customer app for customer-specific profile, balances, appliances, payments, and TV linking.
- `orca_TVapp/` device client for secure activation, appliance status, health, and server-authorized state changes.
- Authorized staff/partner web interfaces for customer support, device and payment operations, alerts, audits, and approved administrative actions.
- Payment provider webhooks and approved device-message channels.

The central service must own authentication and authorization, customer/appliance relationships, financing ledger, provider reconciliation, activation-code lifecycle, device identity/status, audit trail, API versioning, backups, monitoring, and support controls. The database must not be exposed to browser, Flutter, or TV clients. Payment callbacks and device messages require independent signature/authentication and replay protection.

## Planned service boundaries

A future implementation should separate logical modules even if they are initially deployed together:

1. Identity/session and role authorization.
2. Customer profile, consent, and appliance ownership.
3. Financing agreements and immutable payment ledger.
4. Payment intent/provider adapter/webhook/reconciliation.
5. TV/device registry, secure provisioning, activation/link workflow, telemetry, desired state, and acknowledgement.
6. Staff dashboard API, audit, support actions, and safe reporting.
7. Versioned OpenAPI contract for web/mobile clients and a separate authenticated device protocol.

Actual backend framework, database, API hostname, payment provider, device broker/protocol, cloud account, and production environment are **UNVERIFIED**. Do not create client assumptions from this list; obtain the backend owner's approved design first.

## Required communication patterns

- Customer and staff web clients use HTTPS JSON APIs with session/token authentication and server-side object authorization.
- Payment providers call a dedicated signed webhook. Only reconciled server-side results update balances or entitlements.
- TV devices use per-device credentials over TLS through the selected device channel. Cloud commands carry IDs/version/expiry and require acknowledgement.
- TV linking and payment are mediated by the central service. The phone must not send payment success directly to a TV, and a TV must not accept an arbitrary browser command.
- Use stable IDs, idempotency keys for retried writes, UTC timestamps, explicit status enums, privacy-safe errors, and correlation IDs.

Detailed customer endpoint proposal and open questions are in [`../orca_mobile/docs/api-contract.md`](../orca_mobile/docs/api-contract.md); it is not yet approved or implemented.

## Implementation gates

Before this folder is called a live webserver, add and document the actual backend project, local/staging/production configuration, database and migration process, health/readiness endpoints, CI, auth, API schema, deployment/build/start commands, secrets management, backup/restore, monitoring, audit, and test fixtures. Keep marketing HTML static if appropriate, and keep demo fixtures clearly separated from real customer data. Never reuse dashboard demo sample values as production defaults.

Coordinate breaking API changes with Flutter and TV owners. For each release, document compatible client versions, staged rollout, schema migration order, rollback, and test evidence in the root architecture/release notes.
