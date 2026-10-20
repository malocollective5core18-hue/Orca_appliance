# ORCA Cloud Phase 0 report — learn before building

**Date:** 20 October 2026
**Branch:** `codex/orca-cloud-phase0`
**Starting point:** `codex/orca-architecture-docs` at `32b8c91` (the branch created for the earlier family architecture documentation).
**Status:** Phase 0 only. No Django application code or cross-folder client files were written. No push, merge, deployment, production command, payment call, or database access occurred.

## Executive summary

`orca_webserver/` is a static marketing/dashboard prototype, not a Django webserver. Mobile and TV are also demos and do not call it. The intended architecture is sensible at the boundary level—Cloud is authoritative and both clients communicate through it—but there is no implemented API or OpenAPI contract to synchronize. Do not begin payment, financing, pairing or device-control code until the decisions in §6 are approved and a staging plan exists.

Most significant external constraint: ClickPesa's current official documentation says there is no sandbox and all API requests can affect production and move real funds. Use fake provider fixtures for automated tests. No live API test should happen without a specific written owner authorization and a test transaction plan.

## 1. Lessons and references

See [LESSONS_AND_REFERENCES.md](LESSONS_AND_REFERENCES.md) for the detailed source inventory, owner-shared project failures, eighteen testable “Do not repeat” rules, reference repositories/licenses, official documentation notes and exact verification limits.

### Prior Django project observations

The owner-shared history for B&U Mega Map/Mauzosheet includes Render deployment and dependency drift, redirecting root health checks, staff MFA/role 403 confusion, a Leaflet `markers.getBounds is not a function` error, updates hidden by creation-time ordering, a hard-coded 30 m duplicate threshold, a PostgreSQL row-lock issue, DNS-blocked dependency installs, and sensitive-data URL/log concerns. Some source fixes were made, but several live causes and deployed SHAs remained **UNVERIFIED**. Do not treat the whole history as production-confirmed incidents.

Uni-COT history shows repeated user-reported responsive group-management issues (search/filter, group filtering, modal positioning and compact table fit); deployed source/root causes were **UNVERIFIED**. The available history does not substantiate a specific Aiven or tenant-provisioning incident.

## 2. Existing architecture decisions and unresolved items

The following unresolved decisions are carried from `SYSTEM-ARCHITECTURE.md`, `orca_webserver/README.md`, `orca_mobile/docs/api-contract.md`, `orca_mobile/docs/server-data-migration.md`, and `orca_TVapp/README.md`. Statements marked “target” are design intentions, not code facts.

### Explicitly selected by owner in the mission

- Django web/backend in `orca_webserver/`.
- Render for the application service.
- Supabase PostgreSQL as a database only (not Supabase Auth, Storage, Realtime or Data API as the client-facing app backend).
- ClickPesa as payment provider.

These are requirements for future design, not evidence that accounts/services are configured.

### Still unresolved

1. Canonical public marketing page: `index.html` or `indexb.html`; publishing host, domain, form handling and analytics.
2. Django service repository layout, owner, environment URLs and support/incident owner; no backend currently exists.
3. Customer authentication/sign-in, token lifecycle, reset/recovery, consent, session revocation and customer support verification.
4. Staff authentication, staff roles, admin security/MFA and partner-viewer boundaries.
5. Financing partner tenancy model and whether data is shared or strictly tenant-isolated.
6. Product/appliance catalog, customer/appliance ownership cardinality, contract/agreement semantics, currencies, installment schedules and ledger definitions.
7. Meaning of balances, amount due, ownership progress, part-payment/overpayment, allocation order, refunds/reversals and when finance counts a payment as received versus settled.
8. ClickPesa collection rail(s), payment method availability, fees, minimum/maximum values, production merchant setup and any outbound IP allowlist/static-egress requirement.
9. ClickPesa webhook retry schedule, timeout, ordering, duplicate delivery and final status reconciliation cadence; current docs did not state retry schedule.
10. Whether BillPay, hosted checkout, USSD push or cards are enabled/allowed for ORCA; no client or server payment flow is built.
11. TV hardware/VIDAA version, app runtime, embedded board relationship, device identity source, secure key storage/rotation/revocation, trusted clock and update process.
12. Pairing code format, TV-side request flow, expiry, attempts, throttling, customer selection behavior, reassignment and lost/replaced TV handling.
13. Device transport and hosting: HTTPS polling versus WebSockets versus MQTT; MQTT vendor/broker, network connectivity, command delivery, acknowledgement, expiry, replay/version protection and heartbeat interval.
14. What the TV may display/control, actual command semantics, physical “applied” proof, offline/unknown state, safe fallback, grace stages, restrictions, appeals, staff override and reactivation.
15. SMS provider for login/alerts, delivery and cost limits, data-processing terms, fraud/recovery requirements and Swahili wording review.
16. Render plan, database plan, region, connection mode, scaling/concurrency, release command, cron/workers and budget. Free Render is unsuitable for production payment webhooks due spin-down/ephemeral limitations.
17. Supabase PostgreSQL schema exposure/RLS configuration, DB roles, SSL verification, pooler mode, backup retention, RPO/RTO and actual restore drill.
18. Error monitoring/log aggregation, alert rules, retention, redaction, request IDs, on-call and incident ownership. Sentry is not approved.
19. Availability/latency goals, expected traffic/payment volume, polling load, offline cache/freshness and rate-limit policy.
20. English/Swahili parity, native-language review, privacy notice/retention/legal obligations, financing lock terms, user consent, customer support and regulator/legal review.
21. API error schema, pagination, idempotency scope/retention, exact enum values, currency/time-zone conventions, backward compatibility and minimum client versions.
22. API contract/version and device protocol are not present or approved; the mobile API draft is a proposal only.

## 3. Current official documentation facts and unknowns

Read on 20 October 2026. Full source links and details are in [LESSONS_AND_REFERENCES.md](LESSONS_AND_REFERENCES.md).

| Area | Verified from current official docs | Still unverified for ORCA |
|---|---|---|
| ClickPesa auth and references | Token generated using client ID/API key; token includes `Bearer`, lasts one hour. Example base URL `https://api.clickpesa.com/third-parties`. Order reference example rule: alphanumeric and max 20 chars. | Merchant API access, current endpoint schemas, key setup, enabled collection methods and minimum amounts. |
| ClickPesa testing and confirmation | No sandbox; all calls use production and can move funds. USSD API has preview, initiate and status query. Hosted Checkout can use webhook/callback/status query. Statuses distinguish received (`SUCCESS`) from settled (`SETTLED`). | Webhook retries/order/timeout; complete current fee/minimum schedules; safe authorized live-test procedure. |
| ClickPesa signature/checksum | Recursive alphabetic key sorting, compact JSON, HMAC-SHA256, excluding `checksum` and `checksumMethod`. Webhook docs require 2xx receipt acknowledgment. | Confirm exact canonical bytes and supported types using official vectors before code; retry schedule not specified. |
| Supabase connections | Direct connection IPv6 by default; shared session/transaction poolers support IPv4; transaction mode lacks prepared statements. RLS without policies denies Data API requests. Daily backups are documented for paid plans; PITR is a paid add-on. | Render egress/IP support, actual project plan, hidden/disabled Data API configuration, pooler/driver behavior, capacity, backup retention and restore evidence. |
| Render | Django/Python web services supported. Python `3.14.8` was current default for newly created services from 2026-10-12; explicit version pin available. Pre-deploy migration command is available only on paid web services/private services/background workers. Health check GET accepts 2xx/3xx. Free web services spin down after 15 idle minutes and have ephemeral filesystem/no shell/no scaling/no one-off jobs. | Actual account service plan/settings, outbound static IP, configured environment group, worker/cron entitlements, rollback history, domain/TLS and build overrides. |
| Django / Python | Django 5.2 is LTS and supports Python 3.10–3.14 in current docs. Deployment checklist requires `check --deploy` and secure production settings. | Exact patch versions to pin at Phase 1, compatibility with locked dependencies and Render runtime. Re-check at implementation time. |

ClickPesa minimum payment amounts and full collection fee details were not confirmed. Do not hard-code them. Query preview endpoints in a properly authorized environment and get business approval before display or collection.

## 4. Proposed ORCA Cloud architecture (proposal, not implementation)

### Runtime and folder boundaries

- Keep the public marketing pages static if desired; serve Django as a separate Render Web Service rooted at `orca_webserver/`.
- Use a Django project package such as `config/` with `settings/base.py`, `local.py`, `test.py`, `production.py`, root URL/ASGI/WSGI modules and a top-level `manage.py`.
- Put domain apps under `apps/`; use services for transactional state changes and selectors for read/query logic. Views/serializers validate and translate HTTP, not own payment or device state machines.
- PostgreSQL is reachable only from Django through `DATABASE_URL`; mobile, TV, browser HTML and static pages never hold DB credentials or Supabase service-role keys.
- Use `/api/v1/` for client JSON and keep staff API authorization separate. Keep the device transport's authentication and message schema separately specified even if it shares the Django service/database.

### Candidate apps and ownership

| App | Candidate records / responsibility |
|---|---|
| `accounts` | Custom user from first migration, customer/staff identity, sessions/revocation, role grants; do not decide auth method until owner approval. |
| `partners` | Financing partner/tenant boundaries and scoped staff membership. |
| `customers` | Customer profile/consent and verified contact points; customer IDs are never authorization input. |
| `catalog` | Appliance/product model and serial/device inventory. |
| `agreements` | Agreement terms and immutable snapshots; product owner must define schedule and amounts. |
| `ledger` | Append-only financial entries, installment allocations, corrections/refunds/reversals with audit references. Never represent money as float. |
| `payments` | Payment intent/attempt, provider reference, webhook inbox event, status history, reconciliation/outbox. Unique provider event/reference and idempotency constraints. |
| `devices` | Device identity/credential lifecycle, observed telemetry, link state, reported status. |
| `commands` | Server desired-state command, signature/key version, expiry, delivery attempts, acknowledgment/application result, manual override audit. |
| `notifications` | Provider adapter, durable outbox, message templates, localized status and delivery metadata; SMS provider TBD. |
| `audit` | Append-only actor/action/object/request correlation and privacy-minimized metadata. |
| `api` | Versioned DRF schemas, authentication/permissions, throttling, pagination, stable errors and generated OpenAPI. |

Candidate tables are proposals, not approved schema. Add explicit database constraints/indexes from tested invariants. Do not create migrations until the model/cardinality and tenancy decisions are approved.

### Proposed flows

1. Mobile authenticates and reads only its authorized account/agreement; submits payment intent with an idempotency key.
2. Cloud stores intent before external provider call; sends provider request outside a long DB transaction via durable outbox/worker; exposes `PENDING` until verified provider status.
3. Webhook verifies ClickPesa checksum, stores event once, returns 2xx after durable storage, then idempotent worker validates merchant/reference/amount/currency and queries payment status before ledger transition.
4. Scheduled reconciliation queries old pending payments and compares provider totals with ORCA ledger. Use management commands/cron only if Render plan and failure/retry design are approved.
5. TV identifies with a per-device revocable credential and requests pairing; signed-in mobile submits code; server links device to an approved customer/agreement. TV receives server state and acknowledgments over the selected authenticated protocol.
6. Cloud emits commands with unique IDs, version, expiry and signature/key version; devices report received/applied/rejected status. The application must distinguish desired state from physically acknowledged state.

No endpoint names, response payloads, webhook retry interval, device command format or status enum are approved by this proposal.

### Environments and operations

- Local: synthetic fixture data, local PostgreSQL for integration tests, fake ClickPesa adapter, no real provider secrets.
- CI: locked Python/dependency versions; PostgreSQL service; formatting/lint, Django `check`, migration drift, unit/API/contract tests, dependency audit and secret scan.
- Staging: separate Render service and Supabase project/database, synthetic accounts, deterministic fake payment provider by default. ClickPesa has no official sandbox, so do not point staging automation at ClickPesa production.
- Production: human-configured Render secrets, separate Supabase project/roles, paid always-on plan, tested backup and restore, monitoring/alerting, verified webhook URL/IP policy, runbooks and approved legal/customer terms.

## 5. Reference repos and licenses

Repositories and visible license metadata are listed in [LESSONS_AND_REFERENCES.md](LESSONS_AND_REFERENCES.md). Exact latest commit SHAs and shallow-clone review are **UNVERIFIED** because GitHub DNS failed. No third-party code or package was added.

## 6. Human decisions — recommendation and approval required

| Decision | Recommendation for review | Why / what must be approved |
|---|---|---|
| Customer sign-in | Phone OTP can fit the customer context, with strict rate limiting, device/session revocation and recovery controls. | SMS account takeover/SIM swap and provider costs require security and support approval. SMS provider remains TBD. |
| TV pairing | TV asks Cloud for a short-lived one-time code; authenticated mobile submits it after the customer selects the appliance/agreement; server links and independently notifies TV. | Approve code lifetime/attempt limits, who can relink, consent, lost/replaced device recovery and TV identity hardware. |
| Device channel / MQTT | Start with HTTPS polling for minimum infrastructure if VIDAA constraints and latency permit; do not select MQTT broker until fleet/latency/command requirements justify one. | Render does not host an MQTT broker. If MQTT is chosen, pick a managed broker with TLS, per-device ACL/identity, key rotation, audit, availability, data region and costs. |
| SMS provider | Compare at least two locally available providers on delivery, sender-ID approval, retry receipts, DPA, cost, API idempotency and support. | No vendor or test credentials selected. |
| Render plan | Paid always-on Web Service at a region chosen for service/latency; use paid pre-deploy if it is the approved migration gate. Add a worker only after queue/reconciliation needs are specified. | Choose plan from load, webhook availability/SLO, static egress requirement and budget. Do not use Free for production payments. |
| Supabase plan | Paid plan sized after data/concurrency estimate; prove SSL, pooler mode and migrations. Require documented restore drill and agreed RPO/RTO; evaluate PITR cost. | Confirm project feature/pricing with owner. Free is not a production backup strategy. |
| Monitoring | Start with structured logs/metrics, health/readiness and alerts for webhook backlog, reconciliation mismatch, failed commands and auth abuse. Add an approved error tracker such as Sentry only after PII redaction/retention review. | Name on-call owner, retention, alert channels and vendor/data residency. |
| Multi-tenancy | Include explicit financing `Partner` from the first schema; enforce tenant scoping in service/query layer and database uniqueness; evaluate PostgreSQL RLS only with a tested threat model. | Decide shared database/schema versus separate database/project per partner, support cross-tenant workflows and exports. |

## 7. Phased implementation plan with rough estimates

Estimates are engineering effort for one experienced backend engineer, not calendar promises; assume owners respond promptly. Provider KYC, legal review, hardware integration and third-party account setup may add unbounded elapsed time.

| Phase | Scope / exit evidence | Rough effort |
|---|---|---:|
| 0. Learn and approve | Current report, product/payment/device decisions, service owners, sandbox/test strategy, RPO/RTO. | Completed in this phase |
| 1. Skeleton and operations | Django settings split, custom user, Render/Supabase staging, CI, health/readiness, secrets, logs, migration process. | 4–7 engineer-days |
| 2. Domain model and tenancy | Partner/customer/product/agreement/ledger/device schema, constraints, admin, PostgreSQL migrations/tests. | 7–12 engineer-days |
| 3. Auth and customer API | Customer/staff/device auth boundary, API v1, OpenAPI, permissions, errors, throttles, contract tests. | 8–14 engineer-days |
| 4. Payments | ClickPesa adapter, preview/initiate, durable webhook inbox, query reconciliation, ledger, idempotency, audit and failure tests. | 8–15 engineer-days after ClickPesa access/policy; no sandbox raises test planning risk |
| 5. Pairing and devices | Provisioning/security model, activation, protocol, status, command delivery/ack/recovery and simulator fixtures. | 10–20 engineer-days after hardware protocol decisions |
| 6. Staff operations and notifications | Staff APIs/dashboard integration, support/audit, reporting, SMS adapter and localized templates. | 7–12 engineer-days |
| 7. Security/reliability/staging rehearsal | Threat review, load/concurrency, backup restore, observability, privacy/legal review, mobile/TV contract integration and rollback drill. | 8–15 engineer-days |

Parallel mobile/TV work and provider/legal lead time are excluded. Re-estimate after scope, volume and client/hardware teams are known.

## 8. Contract and client-folder status

- Server contract before: **none** (no `orca_webserver/docs/contracts/openapi.yaml` or `CONTRACT_VERSION` exists).
- Server contract after: **none**; no API schema was invented in Phase 0.
- Mobile `orca_mobile/docs/api-contract.md` remains a draft proposal and was not copied or relabeled as an API.
- TV and mobile `docs/cloud-contract/` files were not generated. Writing placeholder `openapi.yaml` copies would falsely imply a server contract. Generate the template documents only after server endpoints are implemented and approved; then sync read-only copies and enforce checksum/version in CI.
- Files written outside `orca_webserver/`: **none**.

## 9. Manual work and human approval gates

Before Phase 1, provide written decisions for the auth, tenancy, finance/ledger, ClickPesa flow and no-sandbox testing approach, pairing/hardware, device channel and restriction/legal policy, Render/Supabase plans/RPO/RTO, SMS vendor, monitoring/on-call, and client language/legal/privacy constraints in §6. Also confirm whether to make the ORCA Cloud backend in this repository or provide a separate backend repository; current `orca_webserver/` is a static prototype folder.

No ClickPesa production calls, client implementation, or database changes should be made pending these approvals. After written Phase 0 approval, proceed one phase at a time.

## 10. Checks and files

| Check | Result |
|---|---|
| Repository status before edits | Clean on `codex/orca-architecture-docs` at `32b8c91`. |
| Branch creation | Created local `codex/orca-cloud-phase0` from `32b8c91`. |
| Reference shallow clones | **Not run successfully**: GitHub DNS failure, `Could not resolve host: github.com`. |
| Official docs research | Reviewed source pages listed in `LESSONS_AND_REFERENCES.md` on 20 October 2026. |
| Application/test commands | Not run: no application code changed and no Django project exists. |
| `git diff --check` | Pending final report check. |

Files created:

- `orca_webserver/docs/LESSONS_AND_REFERENCES.md`
- `orca_webserver/docs/PHASE0_REPORT.md`

## 11. Stop gate

This completes Phase 0 only. **Stop here and wait for the owner's written approval.** Do not scaffold Django, write a contract/version, create client contract copies, commit, push, merge, or deploy until approval and missing policy decisions are supplied.
