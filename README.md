# ORCA Appliance

ORCA Appliance is intended to connect customers, financed appliances, financing partners, payments, and device status through a central cloud service. The repository keeps the customer app, central web/server project, and TV experience in separate folders so teams can work independently. A shared product contract is a target; the mobile API draft is not approved or implemented.

**Baseline reviewed:** branch `codex/orca-cloud-foundation`, starting commit `3f5e4b8` (21 October 2026). The Flutter and TV clients are demos. The Django project now contains a Phase 1/2 foundation, including models and local/fake adapters, but it has no product API and is not production-ready. See [AI review trace](orca_webserver/docs/AI_REVIEW_TRACE.md) and [roadmap](docs/roadmap.md).

## What the product is intended to do

The target product helps a customer apply for or manage an appliance-financing agreement, understand installments, submit payment intent, link an appliance/TV, and see authoritative payment and device status. Financing partners and authorized staff need tools to manage agreements, customer support, payment reconciliation, device activation, and audited operations. The TV should present safe activation/status information. ORCA Cloud is intended to be the authority for customer identity, agreement and ledger state, payment confirmation, device identity, linking, and device state.

This is the intended business problem, not proof these production workflows work today. Sample balances, payment screens, activation codes, restrictions, dashboard metrics, and connectivity are simulations.

## Repository map

```text
SYSTEM-ARCHITECTURE.md                 Current-state and target architecture
docs/decisions/                        Canonical decision index and detailed ADRs
docs/testing.md                        Commands, test evidence, and limits
docs/HUMAN_VERIFICATION.md             Human Flutter/browser/PostgreSQL checks and blank results
docs/roadmap.md                        Evidence-based next milestones
docs/reports/                           Mission reports and claim audit
orca_mobile/                           Flutter customer-app demo and API proposal
  lib/main.dart                        Flutter's default package entry point
  orca_mobile/main.dart                Separate, older/different unselected copy
  docs/api-contract.md                 Draft proposal; no matching API exists yet
  docs/server-data-migration.md        Draft migration guidance
orca_webserver/                        Static prototypes plus Django cloud foundation
  index.html, indexb.html              Two marketing-page variants; canonical choice open
  orca-dashboard-demo-1.html           Browser-only dashboard demo
  manage.py, config/, apps/            Django service foundation
  docs/                                Phase, security, deployment, and adapter records
orca_TVapp/                            Browser TV simulator, not production TV software
  orca-tv-demo-1.html                  Simulator entry point
```

## How the projects relate

| Project | Current implementation | Intended responsibility |
|---|---|---|
| `orca_mobile/` | Flutter demo with in-memory sample values and simulated actions. | Customer-authenticated app. It should submit intent and display server-authoritative account, payment, appliance, and TV-link state. |
| `orca_webserver/` | Marketing HTML, a sample dashboard, and Django Phase 1/2 foundation. Django currently exposes health/readiness and admin routes only; there is no versioned customer/staff API. | ORCA Cloud: API, authorization, database, finance/ledger, payment-provider boundary, device registry, activation, audit, staff workflows, and operations. |
| `orca_TVapp/` | Single browser HTML simulator with local state and developer controls. | TV/device client authenticated as a provisioned device, receiving server-approved status and commands. |

Target communication is mobile ↔ Cloud, TV ↔ Cloud, staff dashboard ↔ Cloud, and payment provider ↔ Cloud webhook. Mobile and TV must not trust one another for account/payment decisions. The database must never be exposed to browser or device clients. This topology is proposed; no client-to-cloud product integration is implemented.

## Status vocabulary

- **IMPLEMENTED** means present in the inspected source. It does not automatically mean tested or production-ready.
- **PROTOTYPE / DEMO** means sample or simulated behavior that must not be treated as real customer, payment, or device state.
- **PROPOSED** means documented design not yet approved or implemented.
- **UNVERIFIED** means evidence is missing or a check could not be run.
- **BLOCKED** means a decision, dependency, or implementation is required before proceeding.

See [System architecture](SYSTEM-ARCHITECTURE.md), [decision index](docs/decisions/README.md), and the [AI review trace](orca_webserver/docs/AI_REVIEW_TRACE.md) before making integration assumptions.

## Prerequisites and local commands

### Flutter customer demo

Requirements: Flutter SDK with a Dart SDK satisfying `^3.13.5`; dependencies are declared in `orca_mobile/pubspec.yaml` and `pubspec.lock`. The actual Flutter SDK/runtime tested for this repository is **UNVERIFIED** here.

```sh
cd orca_mobile
flutter pub get
flutter analyze
flutter test
flutter run
```

`lib/main.dart` is Flutter's default package entry point; `pubspec.yaml` does not set a custom entry point. Do not delete or edit the separate `orca_mobile/main.dart` copy without a dedicated source-change review.

### Django cloud foundation

Requirements: Python 3.14-compatible runtime and packages from `orca_webserver/requirements.txt` or `requirements-dev.txt`. `render.yaml` pins the proposed Render runtime to Python 3.14.8. These requirements are direct pins, not a complete generated hash lock. The project does not load `.env` automatically; export variables or use a local environment tool without committing secrets.

```sh
cd orca_webserver
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py check --settings=config.settings.test
python manage.py makemigrations --check --dry-run --settings=config.settings.test
python manage.py test --settings=config.settings.test
python manage.py migrate
python manage.py runserver
```

The local command set does not make the service production-ready. For PostgreSQL-only behavior, configure a disposable local PostgreSQL database and `DATABASE_URL`, then use `DJANGO_SETTINGS_MODULE=config.settings.postgres_test`. Never point tests at production.

### Static marketing/dashboard pages and TV simulator

They have no Node package manifest or build step. From the relevant directory, serve files locally with Python's standard library:

```sh
python3 -m http.server 8000
```

Open the desired HTML file in a browser at `http://localhost:8000/`. This only serves static files. It does not start Django or create API connectivity. Fonts load from Google Fonts when the browser has internet access.

More commands and the checks actually run are in [docs/testing.md](docs/testing.md).

## Data and security rules

- Never commit passwords, access tokens, ClickPesa keys, database URLs, device keys, production API origins that reveal private infrastructure, or customer data.
- Never put database credentials or provider secrets into Flutter builds, TV HTML, public marketing HTML, screenshots, or logs.
- Treat all demo values as fictitious. Do not load real customer records into demos or CI.
- Do not call ClickPesa for a test: its documented API has no sandbox and may move real funds. Use the local fake adapter.
- Do not accept a client statement as payment confirmation, device ownership, or authorization. The future server must verify every state change.
- Do not expose Supabase directly to mobile, TV, or browser clients. The intended flow is through a server API and least-privilege database roles.
- Do not enable live mode or deploy the current foundation as a customer service. Authentication, object-level authorization, API, ledger behavior, PostgreSQL verification, monitoring, backup/restore, legal review, and operating procedures remain incomplete.

## Known limitations and next milestones

1. Stabilize/review demo behavior and run Flutter analysis/tests on an installed compatible SDK.
2. Approve identity, partner scope, ledger/payment semantics, hardware identity, TV transport, staff roles, privacy, and operations decisions.
3. Approve a versioned API and separate device protocol before adding client calls.
4. Implement authenticated APIs and integrations using staged environments, contract tests, audit, and rollback evidence.
5. Prove PostgreSQL migrations/concurrency, dependency audit, CI, backup/restore, monitoring, and legal/security readiness before production.

See [roadmap](docs/roadmap.md) for deliverables and acceptance evidence. Current server reports and verification limits are in `orca_webserver/docs/PHASE0_REPORT.md`, `PHASE1_REPORT.md`, and `PHASE2_REPORT.md`.
