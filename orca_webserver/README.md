# ORCA Web and Cloud foundation

This folder combines two static website prototypes, a browser-only staff dashboard demo, and the Django ORCA Cloud foundation. The Django project is real source code, but it is not a production service: no customer/staff product API, implemented login flow, live payment/SMS/device integration, or verified deployment exists.

Cross-project architecture is in [`../SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md). For current implementation boundaries read [`docs/AI_REVIEW_TRACE.md`](docs/AI_REVIEW_TRACE.md), the phase reports, and [`../docs/decisions/README.md`](../docs/decisions/README.md).

## Component inventory

| Component | Entry point | Current behavior and data | Status |
|---|---|---|---|
| Public marketing variant A | `index.html` | Standalone HTML/CSS. No form, fetch/XHR, or customer data persistence. Links/fonts may navigate/load externally. | Prototype; canonical page and hosting are **UNVERIFIED**. |
| Public marketing variant B | `indexb.html` | A second standalone public page with a similar title but a different implementation. No form or API request observed. | Prototype; relationship to variant A is **UNVERIFIED**. Do not delete either file in a docs-only change. |
| Staff dashboard | `orca-dashboard-demo-1.html` | Browser JavaScript generates sample devices/payments/alerts/partners/audit-like records. `localStorage` stores the theme preference; business records are not read from an API or persisted as server data. | Demo only; not authenticated or operational. |
| Django ORCA Cloud | `manage.py`, `config/`, `apps/` | Phase 1 custom user and Phase 2 domain models, migrations, service helpers, local/fake adapters, health/readiness, and Django admin. | Implemented foundation; no product APIs or production proof. |

Assets include `logo.png`, `orca-logo-B.png`, `orca-logo-w.png`, `bc2.png`, and `VID-20261015-WA0031.mp4`. Asset provenance/license, canonical variants, and production use approval are **UNVERIFIED**.

## Django routes and data boundary

`config/urls.py` currently registers:

- `GET /healthz` — empty process health response.
- `GET /readyz` — checks database availability and returns server mode.
- `/admin/` — Django admin site; this is not the planned staff operations dashboard.

There are no customer, mobile, TV device, payment webhook, or staff product API routes. The Phase 2 domain models do not themselves expose data over HTTP. Browser HTML, Flutter and TV clients must never connect to the database directly.

The backend configuration reads environment variables; Django does not load `.env.example`. Settings split into `config/settings/base.py`, `local.py`, `test.py`, `postgres_test.py`, and `production.py`. Production requires shaped environment values and explicit database connection mode. `render.yaml` is a draft Blueprint nested in this subfolder. It has not been imported or deployed; see [`docs/DEPLOY_RENDER.md`](docs/DEPLOY_RENDER.md).

## Run the static pages

The static pages have no npm package or build step. With Python 3:

```sh
cd orca_webserver
python3 -m http.server 8000
```

Open `/index.html`, `/indexb.html`, or `/orca-dashboard-demo-1.html` under `http://127.0.0.1:8000/`. This serves static files only; it does not start Django, enable authentication, or connect a database. The dashboard's local-storage theme is a browser preference, not customer-data persistence.

## Run the Django foundation locally

From this folder, create a virtual environment and install declared direct dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py check --settings=config.settings.test
python manage.py makemigrations --check --dry-run --settings=config.settings.test
python manage.py test --settings=config.settings.test
python manage.py migrate
python manage.py runserver
```

`requirements.txt` and `requirements-dev.txt` are not generated hash-locked transitive requirements. Run tests against a disposable local database. PostgreSQL-only tests need a PostgreSQL server and `DJANGO_SETTINGS_MODULE=config.settings.postgres_test`; do not use production data. See [`../docs/testing.md`](../docs/testing.md) for recorded outcomes and limits.

## Before production use

Implement the approved API and object-level authorization; establish identity/session and staff roles; finish finance ledger semantics and provider reconciliation; provision and secure devices; add background work and monitoring; review privacy/legal obligations; create staging/production separately; prove PostgreSQL behavior and backup/restore; and establish support/incident ownership. Do not claim demo metrics or current Django models as live financial/device data.

Related guides: [`docs/PORTS_AND_ADAPTERS.md`](docs/PORTS_AND_ADAPTERS.md), [`docs/IMAGE_STORAGE.md`](docs/IMAGE_STORAGE.md), [`docs/CI_SCOPE.md`](docs/CI_SCOPE.md), and [`docs/PHASE2_REPORT.md`](docs/PHASE2_REPORT.md).
