# ORCA web and central service foundation

This folder contains the ORCA public web and dashboard prototypes plus the Django server foundation. The Django service is still not production-ready: Phase 2 adds offline domain models, local/fake ports and adapters, state transitions, and image validation, but no public API, live provider integration, or production credentials.

See the root [system architecture](../SYSTEM-ARCHITECTURE.md) for the complete target architecture and interactions with mobile and TV.
See [`docs/PHASE0_REPORT.md`](docs/PHASE0_REPORT.md), [`docs/DECISIONS.md`](docs/DECISIONS.md), and [`docs/PHASE1_REPORT.md`](docs/PHASE1_REPORT.md) for approved scope, decisions, and verification evidence.
Read [`docs/PHASE2_REPORT.md`](docs/PHASE2_REPORT.md), [`docs/PORTS_AND_ADAPTERS.md`](docs/PORTS_AND_ADAPTERS.md), and [`docs/IMAGE_STORAGE.md`](docs/IMAGE_STORAGE.md) before extending the Phase 2 foundation.

## Files currently present

- `index.html` — public ORCA marketing page.
- `indexb.html` — another public marketing-page variant. Which version is canonical for deployment is **UNVERIFIED**.
- `orca-dashboard-demo-1.html` — browser dashboard demonstration with overview, device, payment, alert, partner, and audit-style views. It generates sample records locally in JavaScript. The only observed use of `localStorage` is the dashboard theme preference; business data is not fetched from an API.
- `logo.png`, `orca-logo-B.png`, `orca-logo-w.png`, `bc2.png`, and `VID-20261015-WA0031.mp4` — visual/media assets. Their licensing, source-of-truth versions, and production use approval are **UNVERIFIED**.
- `manage.py`, `config/`, and `apps/accounts/` — Phase 1 Django project skeleton. Only the custom `accounts.User` model is implemented; SMS OTP, staff TOTP, device credentials, and API permissions are deferred.
- `render.yaml`, `requirements*.txt`, and `scripts/ci.sh` — Render draft, direct dependency pins, and local CI commands. The dependency set is not a complete hashed lock, the Render service was not created, and GitHub Actions cannot be placed under this folder-only write scope.
- `docs/DECISIONS.md`, `docs/DEPLOY_RENDER.md`, and `docs/SUPABASE_DATA_API_LOCKDOWN.md` — approved decisions and human-operated deployment/security drafts. No live provider/database actions were run.

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

The backend framework (Django), host (Render), and database provider (Supabase PostgreSQL, database only) are approved. Actual service URLs, Render/Supabase accounts, connection mode, credentials, plans, API hostname, payment merchant setup and production environment are **UNVERIFIED**. Do not create client assumptions from this list; read [`docs/DECISIONS.md`](docs/DECISIONS.md) and obtain the approved server contract in a later phase.

## Required communication patterns

- Customer and staff web clients use HTTPS JSON APIs with session/token authentication and server-side object authorization.
- Payment providers call a dedicated signed webhook. Only reconciled server-side results update balances or entitlements.
- TV devices use per-device credentials over TLS through the selected device channel. Cloud commands carry IDs/version/expiry and require acknowledgement.
- TV linking and payment are mediated by the central service. The phone must not send payment success directly to a TV, and a TV must not accept an arbitrary browser command.
- Use stable IDs, idempotency keys for retried writes, UTC timestamps, explicit status enums, privacy-safe errors, and correlation IDs.

Detailed customer endpoint proposal and open questions are in [`../orca_mobile/docs/api-contract.md`](../orca_mobile/docs/api-contract.md); it is not yet approved or implemented.

## Current implementation gates

Phase 1 added local/staging/production settings, initial custom-user migration, `/healthz`, `/readyz`, a server-side database URL parser, safe JSON request logs, a Render Blueprint draft, and local CI commands. Django tests use isolated SQLite; no Postgres or Supabase connection was tested. Before calling this a live webserver, add GitHub Actions after root-level scope approval, complete dependency audit/hash locking, select SMS vendor, implement approved auth/MFA and API/domain phases, verify Supabase lockdown/backups, and complete legal/security review. Keep marketing HTML static if appropriate, and keep demo fixtures separate from real customer data. Never reuse dashboard demo sample values as production defaults.

Coordinate breaking API changes with Flutter and TV owners. For each release, document compatible client versions, staged rollout, schema migration order, rollback, and test evidence in the root architecture/release notes.
