# ORCA Cloud decisions

**Updated:** 20 October 2026. These ADRs record the owner's Phase 0 approval and Phase 1 scope.
Phase 1 is a skeleton only. Decisions about payments, tenancy, and devices are not implementations.

## ADR-001 — Server location and repository scope

- **Date/status:** 20 October 2026 — Accepted.
- Build Django in this repository under `orca_webserver/`.
- Keep all files created in this phase under `orca_webserver/`.
- Root `.github/workflows/` and GitHub `CODEOWNERS` files are outside the approved write boundary. `docs/CI_SCOPE.md` records the owner action required; no nested pretend-workflow or pretend-CODEOWNERS file is added.
- Set the Render service Root Directory to `orca_webserver` and confirm dashboard values match `render.yaml` before importing/deploying.

## ADR-002 — Payment provider safety

- **Date/status:** 20 October 2026 — Accepted for future payment phase.
- USSD Push is primary. Use M-Pesa, Mixx by Yas, Airtel Money, and Halopesa as provider-supported wallet labels.
- Keep a thin provider interface and `FakeClickPesa` for all development and CI. CI must never call ClickPesa.
- `PAYMENTS_LIVE_ENABLED` defaults to false. Phase 1 production settings reject `true` because live payment code is not implemented.
- Hosted Checkout/cards and BillPay require separate approval.
- ClickPesa has no sandbox; each API call is live and may move funds. Reuse access tokens. Do not perform calls in Phase 1. See `LIVE_SMOKE_TEST.md` for a later human-only procedure.

## ADR-003 — Identity methods

- **Date/status:** 20 October 2026 — Accepted design; implementation deferred.
- Customers sign in with phone number plus one-time SMS code.
- Staff sign in with email, password, and TOTP two-factor authentication.
- Devices use a per-device credential issued during provisioning and revocable by staff.
- Phase 1 creates only the custom identity model. OTP, SMS delivery, staff MFA, and device credentials are not implemented.

## ADR-004 — Partner tenancy

- **Date/status:** 20 October 2026 — Accepted design; implementation deferred to Phase 2.
- Use one PostgreSQL schema and partner rows. Every partner-scoped domain table must have a `Partner` foreign key.
- Never provision tenants through process memory, a redeploy, or a process restart. Provisioning must be one retry-safe database transaction.
- Phase 1 creates no `Partner` model and makes no tenancy claims.

## ADR-005 — Ledger and restrictions

- **Date/status:** 20 October 2026 — Accepted design; implementation deferred.
- Allocate payments to the oldest unpaid installment first. Allow partial payment; hold overpayment as credit for the next installment.
- Require a reason, second approver, and audit event for manual refunds/reversals.
- Store ledger and grace-policy rules as configuration. Do not implement automatic device restrictions before the business approves grace policy.
- No ledger, payment, installment, or restriction code is part of Phase 1.

## ADR-006 — TV identity and pairing

- **Date/status:** 20 October 2026 — Accepted with hardware dependency.
- The TV requests a six-digit, single-use pairing code; the customer enters it in the mobile app.
- Control-board serial as hardware identity is **UNVERIFIED** with the hardware team. Until confirmed, use a server-issued device ID provisioned server-side; store the serial as nullable.
- Pairing and device records are deferred. No client-folder edits are authorized.

## ADR-007 — Device transport

- **Date/status:** 20 October 2026 — Accepted for first release; implementation deferred.
- Start with authenticated HTTPS heartbeat and status polling.
- MQTT requires a separate ADR and owner approval of the broker.
- Device commands and transport are out of Phase 1.

## ADR-008 — SMS vendor

- **Date/status:** 20 October 2026 — Open.
- Provider is not selected. Development may use a console adapter only; never send SMS from CI.
- Phase 1 provides `apps.accounts.sms.ConsoleSMSBackend`; it refuses to send unless `DEBUG=True`
  and masks the phone in console output. It is an adapter only, not OTP generation or a vendor link.
- Owner must compare Tanzania delivery, price, sender-ID rules, support, privacy terms, and failure reporting before Phase 3.
- No OTP generation or real SMS provider is implemented in Phase 1.

## ADR-009 — Hosting and database environments

- **Date/status:** 20 October 2026 — Accepted architecture; exact plans and budget open.
- Keep staging and production as separate Render services and separate Supabase projects.
- Production Render must be paid and always on. Production Supabase must have backups and point-in-time recovery.
- Plan names, region, price, budget, retention, RPO/RTO, and restore proof are **UNVERIFIED**. The Blueprint's `starter` is only a draft minimum paid choice; do not import it until the owner checks price and capacity.
- Use Supabase session pooler from Render with SSL, and run migrations over a direct or session connection; never use transaction pooler port 6543. This is based on official documentation, not a successful connection test. Actual Render-to-Supabase connectivity is **UNVERIFIED**.

## ADR-010 — Health checks and monitoring

- **Date/status:** 20 October 2026 — Accepted.
- Provide data-free `/healthz` and database-checking `/readyz` now.
- Do not add Sentry until the owner approves it. Logs use server-generated request IDs and redact arbitrary messages, URL paths, query strings, and payloads.

## ADR-011 — Privacy and legal gates

- **Date/status:** 20 October 2026 — Accepted go-live gate.
- Store the minimum personal data. Mask phone numbers and never log payment data.
- Tanzanian legal review of data protection, customer terms, and device restriction on non-payment is required before go-live. This phase does not provide legal approval.

## ADR-012 — Reference repositories

- **Date/status:** 20 October 2026 — Accepted research boundary.
- Keep reference URLs and visible licenses in `LESSONS_AND_REFERENCES.md`.
- Exact latest GitHub commits remain **UNVERIFIED** because clone/network access failed. Do not copy reference code.
