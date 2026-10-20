# Lessons and references for ORCA Cloud

**Phase:** 0, report before code
**Reviewed:** 20 October 2026
**Repository branch:** `codex/orca-cloud-phase0`
**Scope:** Read-only review of ORCA repository and owner-shared prior work; no application code, service, payment API, database, or production account was accessed.

## 1. What exists today

The ORCA repository currently contains three prototypes, not a functioning three-client production system:

| Area | Observed files and behavior | Confidence |
|---|---|---|
| Mobile | `orca_mobile/lib/main.dart` is the Flutter entry point declared by `pubspec.yaml`. Its `AppState` seeds demo customer, appliance, balance, payment history, simulated payment/restriction/link actions in memory. There is no configured HTTP API client. `orca_mobile/orca_mobile/main.dart` is a second differing copy; its intended status is **UNVERIFIED**. | Verified by source review. |
| Web / intended Cloud | `orca_webserver/index.html`, `indexb.html`, `orca-dashboard-demo-1.html`, and media assets. Dashboard records are sample JavaScript data; observed `localStorage` use is theme only. No Django project, API, migrations, database, payment adapter, device service, or deployment configuration exists in this snapshot. Which landing page is canonical and where the pages are hosted are **UNVERIFIED**. | Verified by source review. |
| TV | `orca_TVapp/orca-tv-demo-1.html` is an HTML/JS simulator with in-memory states and developer controls. No device identity, network API, hardware control, persistence, or production package was found. The target VIDAA version/device/firmware is **UNVERIFIED**. | Verified by source review. |

`orca_mobile/docs/api-contract.md` and `server-data-migration.md` are proposals/guides, not approved or implemented contracts. The root `SYSTEM-ARCHITECTURE.md` explicitly separates those target plans from what is checked in.

## 2. Prior project lessons available from owner-shared work

These are observations from the B&U Mega Map/Mauzosheet Django and Render work in this conversation and its local release reports. They are not claims about ORCA or a currently deployed system. Where a live root cause was never verified, that is stated.

| Observed failure or decision | Root cause / resolution | Evidence limit |
|---|---|---|
| Render log installed DRF 3.17.2 while an earlier local report said 3.16.1. | `requirements.lock` and the active local environment were different sources of truth. Align all installers to the committed lock and run tests from that exact lock. | The owner supplied Render logs; the deployed branch/SHA was not established. |
| Render log showed `HEAD /` → `301` during a health probe. | The probe used `/`, which redirects to HTTPS. A dedicated redirect-exempt `/healthz` was added in source and configured in `render.yaml`. | Actual live Render health-check configuration was **UNVERIFIED**. |
| Admin sign-in unexpectedly showed “Set up two-step verification.” | Staff MFA enrolment was enforced by the current source. The owner said admin login should not require it; later source introduced a configured superuser-email exemption. | The deployed branch and live environment-variable configuration were **UNVERIFIED**. Do not copy the exemption into ORCA without an explicit security decision. |
| Staff dashboard customer list/detail returned 403. | Source has distinct MFA and role denials (`mfa_required`, role-required errors); a key or verified phone is not a submitted customer business. The exact live cause was not established. Dashboard messaging and source diagnostics were improved. | Live response body, deployed SHA, role and database were not verified. |
| Customer directory displayed `markers.getBounds is not a function`. | The frontend assumed the wrong Leaflet object type; code must use a layer/group that implements `getBounds`, and the browser console/list flow must be exercised. | Owner supplied the error; deployed build was not reproduced in a browser in the diagnosis report. |
| Returning customer location updates were hard to find. | Updates modified an existing row while list ordering used `created_at` and the open screen did not poll. Source was changed to updated-first ordering and displayed update time. | This was a source-level cause; live deployment was not checked. |
| A configured duplicate-location radius still behaved like 30 m. | Candidate query bounds were configurable, but final distance comparison/advisory-lock cell logic retained literal 30 m. A regression was proposed; the source defect remained open in Mission 11 readiness notes. | Regression execution/fix is **UNVERIFIED**. ORCA must use one named radius for query, lock and final comparison, with boundary tests. |
| PostgreSQL staff edit hit a related-row lock problem. | Lock only the intended business row (`select_for_update(of=("self",))`); add a PostgreSQL-backed regression rather than relying on SQLite. | Prior report records the PostgreSQL test passed in its temporary environment; it was not rerun in this phase. |
| Installing Python dependencies failed with `Could not resolve host: github.com` / PyPI DNS errors. | Network/DNS was unavailable; this is an environment failure, not proof that package pins are wrong. Use committed locks and report the exact blocked command; do not quietly substitute system packages. | Reproduced in this ORCA Phase 0 when attempting `git ls-remote`. |
| A migration log said “No migrations to apply,” but did not identify the deployed source. | Migration output only describes the code/database pair that ran; it does not establish branch/SHA, which database web requests use, or whether a customer row exists. Record deployment SHA and migration state separately. | Owner-shared Render log, no live inspection. |
| Request logs and URLs can expose personal data. | Keep names, phone/key, payment data and coordinates out of query strings and logs; use request bodies for writes/search, opaque IDs in paths, and explicit redaction. | B&U source review found most sensitive requests used bodies, but the Photon area-search query was sent to a third party. No ORCA API exists yet. |
| Customer delete / notes-save complaints were raised. | No verified implementation root cause was established in the supplied history. Add regression tests for write, permission, CSRF, response parsing and persistence before claiming a fix. | **UNVERIFIED**; do not invent a root cause. |
| Uni-COT group-management UI needed repeated refinements. | User-reported issues included search/filter placement, a missing group filter, modal positioning/scroll boundaries, responsive spacing and readability. Keep compact lists and detail dialogs usable at real viewport sizes; derive filters from persisted rows and test the actual screen. | Source-level causes and deployed build identity were not established in the available history. |

The owner mentioned Render, Supabase, and in an earlier brief Aiven PostgreSQL/tenant provisioning. Specific Aiven incidents or a tenant-provisioning bug/fix are **UNVERIFIED** in the available evidence; do not attribute an incident to them.

## 3. Do not repeat — concrete, testable rules

1. **Never run `migrate` in the image/build command.** Run migrations as a controlled release/pre-deploy action; test that deploy and running service target the same database. Render pre-deploy support is plan-dependent.
2. **Never keep provisioning state in process memory.** Persist one-time setup/seed idempotency in the database and test after a process restart without redeploying.
3. **Never use a free-spinning-down instance as the sole webhook processor.** Test cold starts, delivery latency, webhook retry/reconciliation, and choose an always-on plan for production payment callbacks.
4. **Never assume a transaction pooler behaves like a persistent PostgreSQL session.** Confirm Supabase pooler mode; if transaction mode is chosen, disable prepared statements and Django server-side cursors and test migrations separately on a direct/session connection.
5. **Never trust `ALLOWED_HOSTS` or CSRF from local tests alone.** Configure the exact production host and HTTPS origins, trust Render's forwarded HTTPS header only as documented, and test a real CSRF-protected POST behind the proxy.
6. **Never serve Django static files from an ephemeral upload path.** Use WhiteNoise or approved static hosting, run `collectstatic` in build, and check the built manifest/static URL in a deployed smoke test.
7. **Never mix local, test and production settings by accidental defaults.** Split settings, make `DEBUG=False` by default, require production secrets via environment, and test `manage.py check --deploy` with non-secret dummy settings.
8. **Never use local timezone-naive payment/device timestamps.** Store aware UTC timestamps, convert only for display, and test DST/UTC boundaries and delayed webhooks.
9. **Never serialize relations in a loop without a query-count test.** Use `select_related`/`prefetch_related` or batched selectors and assert query growth remains bounded at representative page sizes.
10. **Never rely on application validation for data invariants.** Put unique/check constraints and indexes in PostgreSQL for idempotency, provider event IDs, references, amounts, foreign keys and common list filters; test migrations on PostgreSQL.
11. **Never process a payment webhook as a one-shot side effect.** Verify checksum/signature and expected reference/amount/currency, store an inbox event uniquely, acknowledge only after durable receipt, process idempotently, then reconcile by provider status query.
12. **Never store API keys, tokens, DB URLs or signing keys in source, HTML, tests, logs, client bundles or screenshots.** Read server secrets from environment/secrets manager; test log redaction with sentinel values.
13. **Never call a phone/TV/client result “paid” or “restricted” from local state.** Wait for authoritative Cloud state; test client disconnect, duplicate taps, replay and out-of-order events.
14. **Never test an irreversible payment against an unverified sandbox.** ClickPesa's current official documentation says no sandbox exists and API calls can move real funds. Use mocked HTTP/provider fixtures until the owner explicitly authorizes a small live-money test.
15. **Never assume an HTTP 403 is “no data.”** Return stable error codes, distinguish auth/MFA/role/CSRF errors in UI and tests, and never render a permission failure as an empty customer list.
16. **Never assume a deployed app is the branch you intended.** Before diagnosing or releasing, capture Render branch, commit SHA, build file, dependency lock and database target identity without exposing credentials.
17. **Never implement a configurable threshold with one remaining literal.** Use the same setting in candidate query, lock scope, and final comparison; test below/at/above the configured boundary.
18. **Never treat a demo dashboard as a server or rely on instance files for correctness.** Keep demo fixtures explicit; test against a durable test database and process restart.

## 4. Reference repository review

Official GitHub pages were checked on 20 October 2026. The exact HEAD commit was not captured because `git ls-remote` failed: `Could not resolve host: github.com`. Thus repository existence and visible license labels were checked, but no shallow clone, code checkout, or exact latest commit was verified.

| Repository | Existence / visible license | Exact latest commit | Pattern to study after network access returns |
|---|---|---|---|
| [cookiecutter/cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django) | Exists; Apache-2.0 shown in its template choices | **UNVERIFIED** (clone blocked) | Split local/production settings, environment configuration, deployment/security defaults, custom user model, static pipeline. Do not import its entire template blindly. |
| [HackSoftware/Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide) | Exists; MIT | **UNVERIFIED** (clone blocked) | Keep writes in services and reads in selectors; views/serializers handle transport, not payment/domain transitions. It is opinionated, not Django law. |
| [encode/django-rest-framework](https://github.com/encode/django-rest-framework) | Exists; BSD-3-Clause | **UNVERIFIED** (clone blocked) | DRF permissions, serializers, throttling, pagination, API testing. Official DRF docs remain authoritative. |
| [tfranzel/drf-spectacular](https://github.com/tfranzel/drf-spectacular) | Exists; 3-Clause BSD | **UNVERIFIED** (clone blocked) | Generate OpenAPI from explicit serializers/views; pin and test schema generation against supported Django/DRF versions. Its pre-1.0 versioning warrants careful upgrades. |
| [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries) | Exists; CC-BY-SA-4.0 | **UNVERIFIED** (clone blocked) | Use published guidance on REST, authentication, secrets, logging, webhook verification/replay and authorization; cite, do not copy large passages. |
| [django/django](https://github.com/django/django) | Exists; BSD-3-Clause | **UNVERIFIED** (clone blocked) | Official framework behavior, supported versions, security and deployment documentation. |
| [JAXPARROW/clickpesa-python-sdk](https://github.com/JAXPARROW/clickpesa-python-sdk) | Public repository appears in GitHub topic listing; license **UNVERIFIED** | **UNVERIFIED** (clone blocked) | Do not install. At most compare token/checksum/retry behavior against official ClickPesa documentation and review history, license, package provenance and tests first. |
| [ClickPesa official checksum demo](https://github.com/ClickPesa/clickpesa-api-checksum-demo) | Official organization repository exists; license **UNVERIFIED** from accessible page | **UNVERIFIED** (clone blocked) | Compare checksum test vectors to official docs before adapting; no code copied. |

No code was copied and no dependency was added.

## 5. Official documentation reviewed (20 October 2026)

### ClickPesa

- [Quickstart](https://docs.clickpesa.com/home/introduction): API base URL shown as `https://api.clickpesa.com/third-parties`; token generation uses `client-id` and `api-key`; the returned token is already prefixed `Bearer`; order references shown as alphanumeric, at most 20 characters; token lasts one hour. Most importantly, the page states there is no sandbox and test calls run against production.
- [Sandbox and Testing Environment](https://docs.clickpesa.com/home/sandbox-and-testing-environment): explicitly says all calls, including API Explorer, are live and move real funds; pre-KYC limits documented there are TZS 100,000 cumulative and 100 API calls/day. Do not use these limits as a safe test budget.
- [USSD-PUSH overview](https://docs.clickpesa.com/payment-api/mobile-money-payment-api/mobile-money-payment-api-overview): preview validates mobile number, amount, order reference and availability; initiate sends a wallet prompt; query reads status by order reference.
- [Payment status API](https://docs.clickpesa.com/api-reference/collection/querying-for-payments/querying-for-payments): documented status query is `GET /third-parties/payments/{orderReference}`. Provider statuses include `SUCCESS`, `SETTLED`, `PROCESSING`, `PENDING`, `FAILED`, `ON-HOLD`, `REFUNDED`, and `REVERSED`; map these to ORCA states only after finance approval.
- [Payment status descriptions](https://docs.clickpesa.com/home/payment-status): `SUCCESS` means received but not yet settled; `SETTLED` means settled. Do not collapse settlement and receipt without an agreed ledger policy.
- [Checksum](https://docs.clickpesa.com/home/checksum): recursively sort object keys alphabetically, serialize compact JSON, compute HMAC-SHA256 with secret, output a 64-character hex digest. Exclude `checksum` and `checksumMethod`. Official docs say webhook payloads use this scheme. Use constant-time comparison and confirm exact bytes/types through vectors before coding.
- [Webhooks](https://docs.clickpesa.com/home/webhooks): HTTP POST callbacks; configure application-level webhooks for application API transactions; return 2xx to acknowledge receipt, which means receipt, not processing success. Retry schedule, timeout, delivery order and maximum retry period were not found in the page: **UNVERIFIED**. Build idempotent ingestion and reconciliation regardless.
- [IP whitelist](https://docs.clickpesa.com/home/whitelisted-ip-address): ClickPesa can restrict API calls by source IP; once configured, all other request IPs are blocked and API Explorer no longer works. Render outbound IP stability for the chosen plan must be verified before enabling it: **UNVERIFIED**.
- [Hosted Checkout overview](https://docs.clickpesa.com/checkout/checkout-overview): checkout link flow; payment notifications can use application webhook, optional callback URL, or status query. A browser return URL is not proof of success.
- [BillPay overview](https://docs.clickpesa.com/bill-pay/bill-pay-overview): merchant static, order-specific, and customer-specific control numbers exist; API can support full/partial/over modes and optional collection ceilings. Whether this suits installment allocation is an owner/payment-provider decision.
- Wallet examples/docs identify M-Pesa, Mixx by Yas, Airtel Money and Halopesa. Minimum collection amount and an authoritative complete fee schedule were not established in this pass: **UNVERIFIED**. Preview endpoint must be used and customer-visible fees approved before initiation.

### Supabase PostgreSQL

- [Connect to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres): direct connections are IPv6 by default on current plans; shared session and transaction poolers provide IPv4. Transaction mode does not support prepared statements. Choose connection mode based on Render egress and Django connection lifecycle; copy the exact connection string from Supabase rather than deriving the hostname.
- [Pooling and limits](https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits): poolers share connections; app-side and server-side pools stack, so size Django worker/thread connections against database limits. Recheck when scaling.
- [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security): Data API access relies on RLS/policies; RLS with no policies denies requests. ORCA should use Django with a server-only DB role and no client Supabase keys. Exact project-level steps to disable/hide auto-generated Data API access for all ORCA schemas/roles must be validated in the Supabase dashboard: **UNVERIFIED**.
- [Database backups](https://supabase.com/docs/guides/platform/backups): current docs list daily backups on Pro/Team/Enterprise; retention varies by plan; free-tier projects should make off-site exports. PITR is an add-on, with a Small compute add-on minimum stated by the docs. A restore makes the project unavailable during the procedure. Select a plan only after RPO/RTO and restore-drill requirements are agreed.
- [IPv4 add-on](https://supabase.com/docs/guides/platform/ipv4-address): documents IPv4 availability for direct connections via add-on and shared pooler IPv4 paths. Render-specific connectivity was not exercised here.
- SSL: use TLS for every remote DB connection and verify certificates where supported; exact SSL verification option must be tested with the chosen Supabase URL and psycopg/Django settings: **UNVERIFIED**.

### Render

- [Python version](https://render.com/docs/python-version): documentation reviewed 20 October 2026 showed default Python `3.14.8` for services created 12 October 2026 onward and version selection through `PYTHON_VERSION` or `.python-version`. Django 5.2 supports Python 3.10–3.14; pin a compatible fully qualified Python version rather than inheriting a moving default.
- [Deploys](https://render.com/docs/deploys): build installs dependencies; pre-deploy can run migrations but is available only for paid web services, private services and background workers; it runs in a separate instance. It is therefore not a universal free-plan release hook.
- [Blueprint spec](https://render.com/docs/blueprint-spec): `buildCommand`, `startCommand`, `preDeployCommand`, `healthCheckPath`, `branch`, and auto-deploy behavior are explicit Blueprint fields. Check whether service dashboard overrides match `render.yaml`.
- [Health checks](https://render.com/docs/health-checks): HTTP checks use GET; a 2xx or 3xx within five seconds passes. Health should not expose account/payment/customer data.
- [Free plan limits](https://render.com/docs/free): free web services spin down after 15 minutes idle, can take about a minute to spin up, have ephemeral filesystems, no SSH/shell, one instance/no scaling, no persistent disk, and no one-off jobs. The docs say not to use free instances for production applications.
- [Web services](https://render.com/docs/web-services): Django belongs on a Web Service; custom domains and TLS are available; service-level configuration and health-check settings may differ from repository Blueprint.
- Exact plan pricing, outbound static IP availability, the chosen account's worker/cron limits, rollback retention, domain and TLS state were not inspected in Render: **UNVERIFIED**. The project has no Render account access in this Phase 0 run.

### Django and Python

- [Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/): Django 5.2 is an LTS release with Python 3.10–3.14 compatibility (5.2.8+); LTS receives security support for at least three years from release. It is the current LTS referenced by the official version pages checked for this report. Pin the latest supported patch at implementation time; do not pin an old patch solely because this report says 5.2.
- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/): use `check --deploy`, protect secrets, set `DEBUG=False`, configure host/HTTPS/cookies/static/media, and use a production server rather than `runserver`.
- Python is selected by Render configuration; validate its exact patch against Django, psycopg and all locked dependencies in CI.

## 6. Known limits of this review

- GitHub shallow clones were attempted and blocked by DNS; source-level reference patterns are summarized from official repository pages and official documentation, not from a checked-out revision.
- ClickPesa official docs are dynamic. Re-read them immediately before implementation and capture API schema/page versions. No ClickPesa transaction, API Explorer call, or credential was used.
- Render, Supabase and ClickPesa merchant dashboards were not accessed. Billing, account capabilities, IP egress, payment method enablement, backup configuration and production settings are **UNVERIFIED**.
- No real ORCA customer, lender/financing partner, hardware supplier, ClickPesa merchant account, SMS provider, Render service, Supabase project or legal agreement was inspected.
