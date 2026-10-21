# ORCA decision records

**Status:** proposals and implemented-source records; no production integration approval is implied. **Owner:** product and engineering decision owners. **Last reviewed:** 21 October 2026. **Baseline:** codex/orca-cloud-foundation at 3f5e4b8.

This file is the detailed history for the index in [README.md](README.md). The previous server-local file is now a pointer. Historical ADR labels are not sufficient approval evidence. The following recommendations must remain PROPOSED unless the owner confirms them in writing: same repository placement, customer phone plus SMS sign-in, staff two-factor authentication, one schema with partner rows, polling before MQTT, fake ClickPesa until separate live approval, and a later S3-compatible storage choice.

## ADR-001 — Server location and repository scope

- **Date/status:** 20 October 2026 — PROPOSED; prior Accepted label retained in historical reports only.
- Build Django in this repository under `orca_webserver/`.
- Keep all files created in this phase under `orca_webserver/`.
- Root `.github/workflows/` and GitHub `CODEOWNERS` files are outside the approved write boundary. `docs/CI_SCOPE.md` records the owner action required; no nested pretend-workflow or pretend-CODEOWNERS file is added.
- Set the Render service Root Directory to `orca_webserver` and confirm dashboard values match `render.yaml` before importing/deploying.

## ADR-002 — Payment provider safety

- **Date/status:** 20 October 2026 — PROPOSED; prior Accepted label retained in historical reports only.
- USSD Push is primary. Use M-Pesa, Mixx by Yas, Airtel Money, and Halopesa as provider-supported wallet labels.
- Keep a thin provider interface and `FakeClickPesa` for all development and CI. CI must never call ClickPesa.
- `PAYMENTS_LIVE_ENABLED` defaults to false. Phase 1 production settings reject `true` because live payment code is not implemented.
- Hosted Checkout/cards and BillPay require separate approval.
- ClickPesa has no sandbox; each API call is live and may move funds. Reuse access tokens. Do not perform calls in Phase 1. See `LIVE_SMOKE_TEST.md` for a later human-only procedure.

## ADR-003 — Identity methods

- **Date/status:** 20 October 2026 — PROPOSED; prior Accepted label retained in historical reports only.
- Customers sign in with phone number plus one-time SMS code.
- Staff sign in with email, password, and TOTP two-factor authentication.
- Devices use a per-device credential issued during provisioning and revocable by staff.
- Phase 1 creates only the custom identity model. OTP, SMS delivery, staff MFA, and device credentials are not implemented.

## ADR-004 — Partner tenancy

- **Date/status:** 20 October 2026 — PROPOSED; core schema is IMPLEMENTED FOUNDATION, but tenancy policy approval remains open.
- Use one PostgreSQL schema and partner rows. Every partner-scoped domain table must have a `Partner` foreign key.
- Never provision tenants through process memory, a redeploy, or a process restart. Provisioning must be one retry-safe database transaction.
- Phase 1 created no `Partner` model. Phase 2 adds `Partner` and partner-scoped records. No API or
  production tenant provisioning exists yet.

## ADR-005 — Ledger and restrictions

- **Date/status:** 20 October 2026 — PROPOSED; prior Accepted label retained in historical reports only.
- Allocate payments to the oldest unpaid installment first. Allow partial payment; hold overpayment as credit for the next installment.
- Require a reason, second approver, and audit event for manual refunds/reversals.
- Store ledger and grace-policy rules as configuration. Do not implement automatic device restrictions before the business approves grace policy.
- Phase 2 adds only the Payment/Installment records and lifecycle foundation; no ledger allocation,
  automatic charge/refund, payment adapter, or device restriction business policy is implemented.

## ADR-006 — TV identity and pairing

- **Date/status:** 20 October 2026 — PROPOSED with hardware dependency; prior Accepted label retained in historical reports only.
- The TV requests a six-digit, single-use pairing code; the customer enters it in the mobile app.
- Control-board serial as hardware identity is **UNVERIFIED** with the hardware team. Until confirmed, use a server-issued device ID provisioned server-side; store the serial as nullable.
- Phase 2 adds Device/PairingCode records and a tested state-transition service. Provisioning,
  device authentication, pairing endpoints, and client-folder edits remain out of scope.

## ADR-007 — Device transport

- **Date/status:** 20 October 2026 — PROPOSED for first release; prior Accepted label retained in historical reports only.
- Start with authenticated HTTPS heartbeat and status polling.
- MQTT requires a separate ADR and owner approval of the broker.
- Phase 2 adds DeviceCommand metadata and an offline database polling adapter. Authenticated
  heartbeat/poll endpoints remain Phase 3 work; MQTT still requires a separate ADR.

## ADR-008 — SMS vendor

- **Date/status:** 20 October 2026 — Open.
- Provider is not selected. Development may use a console adapter only; never send SMS from CI.
- Phase 1 provides `apps.accounts.sms.ConsoleSMSBackend`; it refuses to send unless `DEBUG=True`
  and masks the phone in console output. It is an adapter only, not OTP generation or a vendor link.
- Owner must compare Tanzania delivery, price, sender-ID rules, support, privacy terms, and failure reporting before Phase 3.
- No OTP generation or real SMS provider is implemented in Phase 1.

## ADR-009 — Hosting and database environments

- **Date/status:** 20 October 2026 — PROPOSED architecture; exact plans and budget open.
- Keep staging and production as separate Render services and separate Supabase projects.
- Production Render must be paid and always on. Production Supabase must have backups and point-in-time recovery.
- Plan names, region, price, budget, retention, RPO/RTO, and restore proof are **UNVERIFIED**. The Blueprint's `starter` is only a draft minimum paid choice; do not import it until the owner checks price and capacity.
- Use Supabase session pooler from Render with SSL, and run migrations over a direct or session connection; never use transaction pooler port 6543. This is based on official documentation, not a successful connection test. Actual Render-to-Supabase connectivity is **UNVERIFIED**.

## ADR-010 — Health checks and monitoring

- **Date/status:** 20 October 2026 — PROPOSED; prior Accepted label retained in historical reports only.
- Provide empty `/healthz` and database-checking `/readyz`; Phase 2 `/readyz` returns only the
  server-selected `server_mode` after a successful database check.
- Do not add Sentry until the owner approves it. Logs use server-generated request IDs and redact arbitrary messages, URL paths, query strings, and payloads.

## ADR-011 — Privacy and legal gates

- **Date/status:** 20 October 2026 — PROPOSED go-live gate; legal owner approval remains required.
- Store the minimum personal data. Mask phone numbers and never log payment data.
- Tanzanian legal review of data protection, customer terms, and device restriction on non-payment is required before go-live. This phase does not provide legal approval.

## ADR-012 — Reference repositories

- **Date/status:** 20 October 2026 — PROPOSED research boundary; prior Accepted label retained in historical reports only.
- Keep reference URLs and visible licenses in `LESSONS_AND_REFERENCES.md`.
- Exact latest GitHub commits remain **UNVERIFIED** because clone/network access failed. Do not copy reference code.

## ADR-013 — Offline ports and demo mode

- **Date/status:** 21 October 2026 — IMPLEMENTED FOUNDATION; approval of production behavior remains open.
- Provider operations go through ports in `apps/ports/`; the only implementations are fake/local
  adapters. No ClickPesa, Supabase, object storage, SMS vendor, or MQTT connection exists.
- Unknown backend environment values fail at Django startup. Demo/local selection sets
  `SERVER_MODE=demo`; production refuses it unless `ALLOW_DEMO_BACKENDS=true` is explicitly set.
- `/healthz` remains empty. `/readyz` returns only `server_mode` after checking DB connectivity. A
  client status API remains Phase 3 work.

## ADR-014 — Product image visibility and object storage

- **Date/status:** 21 October 2026 — PROPOSED; owner approval pending.
- Images are files in object storage. PostgreSQL stores `ImageAsset` metadata and storage keys only.
- Keep incoming files private until validation/processing. Publish only staff-approved `READY`
  product images. Keep customer/payment/device documents private.
- First upload endpoint should be an authenticated staff server upload to private quarantine. Direct
  signed uploads remain an alternative after bucket policy and finalize validation are designed.
- Use an S3-compatible backend through `django-storages` only after separate approval. No cloud
  backend is installed or enabled in Phase 2.

## ADR-015 — Domain records and lifecycle

- **Date/status:** 21 October 2026 — IMPLEMENTED FOUNDATION; production API and authorization remain absent.
- Add a single-schema Partner tenancy model; tenant-owned tables expose partner references and use
  `PROTECT` deletes for business/audit history. Monetary amounts use integer TZS.
- Define persisted statuses once in `apps/domain/statuses.py`; move payment, device command, and
  pairing transitions through `apps/domain/services.py` and test allowed/rejected transitions.
- Keep webhook payloads out of the database; persist provider/event id, hash, validity, status and
  timestamps. Enforce event and idempotency uniqueness at the database layer.
- Cross-partner relationship agreement is checked by PostgreSQL and SQLite triggers in migration
  `0002_partner_scope_triggers.py`, with model `clean()` methods as an additional application-level
  check. Tests cover ORM writes that bypass `full_clean()`. Public write services must still call
  `full_clean()` and derive the partner identifier from the authorized principal.
