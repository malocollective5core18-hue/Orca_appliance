# ORCA Cloud Phase 1 report

**Date:** 20 October 2026
**Branch:** `codex/orca-cloud-foundation`
**Base:** `codex/orca-architecture-docs` at `32b8c91`
**Scope:** Django foundation only, written under `orca_webserver/`. No push, commit, merge, deployment,
command against a production environment, ClickPesa request, Supabase request, or live credential access occurred.

## A. What was done and why

- Added a Django 5.2 project with base/local/production/test settings and a custom `accounts.User`
  model in its initial migration. `AUTH_USER_MODEL` is set before any domain migrations exist.
- Added role labels for customer, support, finance, admin, and partner viewer. These labels do not
  implement authentication flows or permissions yet.
- Added empty-body `/healthz` (process only) and `/readyz` (database connection only), plus a
  server-generated request ID and JSON logging with an allow-list that omits arbitrary messages,
  paths, query strings, and payloads.
- Added a development-only console SMS adapter. It masks phone numbers and refuses to send unless
  `DEBUG=True`. OTP generation and a real SMS provider remain unimplemented.
- Added PostgreSQL `DATABASE_URL` parsing, required production SSL, a guard rejecting pooler port
  6543, Render session-pooler settings, HTTPS/security settings, WhiteNoise, Gunicorn, and a Render
  Blueprint draft.
- Added direct dependency pins, test/lint tooling declarations, a local `scripts/ci.sh`, a fake-value
  `.env.example`, `.gitignore`, and Phase 1 deployment, decision, dependency, Supabase lockdown, and
  ClickPesa live-test documents.
- Did not create payment, partner, customer, agreement, ledger, API, pairing, or device code. No
  ClickPesa fake provider exists yet because the payment domain is outside this skeleton. No payment
  endpoint or provider call path exists; production rejects `PAYMENTS_LIVE_ENABLED=true`.

## B. Files created or changed

All files are inside `orca_webserver/`; no files were written outside it.

- Changed `README.md`.
- Added `.env.example`, `.gitignore`, `.pre-commit-config.yaml`, `requirements.txt`,
  `requirements-dev.txt`, `pyproject.toml`, `render.yaml`, `manage.py`, and `scripts/ci.sh`.
- Added `config/` settings, URL, health, middleware, logging, WSGI, and ASGI modules.
- Added `apps/accounts/` custom user, admin, console SMS adapter, tests, and
  `migrations/0001_initial.py`.
- Added `apps/README.md` and `docs/DECISIONS.md`, `docs/CI_SCOPE.md`,
  `docs/DEPENDENCY_REVIEW.md`, `docs/DEPLOY_RENDER.md`, `docs/LIVE_SMOKE_TEST.md`,
  `docs/SUPABASE_DATA_API_LOCKDOWN.md`, and this report. The Phase 0 reports remain available.

GitHub Actions and CODEOWNERS were not added. They must reside at repository-root locations for
GitHub to recognize them; the owner selected “Keep scope inside orca_webserver.” See `docs/CI_SCOPE.md`
for the local command and owner action needed to add real path-filtered CI and code ownership.

## C. Commands and results

The environment reused an existing Python 3.14.4 virtual environment from the B&U workspace; Django
was 5.2.18. This is not a fresh install of `requirements-dev.txt`.

| Check | Result | Output/evidence |
|---|---|---|
| `manage.py makemigrations --check --dry-run --settings=config.settings.test` | Pass | `No changes detected`. |
| `manage.py check --settings=config.settings.test` | Pass | `System check identified no issues (0 silenced).` |
| `manage.py test --settings=config.settings.test` | Pass | 12 tests passed; SQLite test DB created and destroyed. |
| `manage.py check --deploy` with non-secret placeholder values | Pass | `System check identified no issues (0 silenced).` |
| `collectstatic --dry-run --noinput --settings=config.settings.test` | Pass | 127 Django admin static files were discovered; dry-run wrote no assets. |
| Python AST parse | Pass | All project Python files parsed successfully. |
| `bash -n scripts/ci.sh` | Pass | `scripts/ci.sh: valid Bash syntax`. |
| TOML parse | Pass | `pyproject.toml: valid TOML`. |
| `git diff --check` and whitespace scan | Pass | No whitespace errors found. |
| `ruff`, `pytest`, `pre-commit`, `pip-audit` | Not run | These executables are absent. Network package installation was not attempted. |
| Complete locked install | Not run | `requirements-dev.txt` was not installed. Declared versions are direct pins, not a complete hashed/transitive lock. |
| Actual `pytest` runner | Not run | `pytest` and `pytest-django` are declared but unavailable; the Django test runner executed the tests. |
| PostgreSQL migration/integration | Not run | No local PostgreSQL test server was used. Test migrations ran against isolated SQLite only. |
| Render YAML parser | Not run | PyYAML is absent. The small YAML file was reviewed manually. |
| Local `runserver` HTTP smoke | Blocked | The sandbox refused loopback socket access (`curl: (7) failed to open socket: Operation not permitted`; Django runserver returned `Errno 1`). Django test-client endpoint checks passed instead. |
| GitHub Actions, Render, Supabase, ClickPesa | Not run | No account-level access, secret, or live operation was used. |

The first `check --deploy` attempt used a placeholder containing the word `fake`, which the
production secret guard correctly rejected. It was rerun with a clearly named, non-secret CI value
long enough to validate settings; the rerun passed without warnings. An initial test command used the
repository parent as its working directory and could not find `manage.py`; it was rerun from
`orca_webserver/` and passed.

## D. Verified facts and UNVERIFIED items

- **Verified locally:** Django 5.2.18 ran on Python 3.14.4; current test suite passes with SQLite;
  migration state matches models; deployment settings pass Django's deploy check with placeholder
  settings. These tests do not prove compatibility with the Render image or Supabase.
- **UNVERIFIED:** Render discovers `orca_webserver/render.yaml` when nested, the actual service Root
  Directory, paid plan/cost, deployed Python patch, HTTPS behavior, and environment-variable setup.
- **UNVERIFIED:** Supabase session-pooler hostname, SSL certificate behavior, Render connectivity,
  role privileges, Data API exposure, backups, PITR, and restore procedure. The code rejects port
  6543 and requires SSL; this is a guard, not evidence of a live connection.
- **UNVERIFIED:** dependency vulnerabilities, because `pip-audit` was not run; transitive dependency
  versions are not locked by hash.
- **UNVERIFIED:** ClickPesa schemas, merchant account, phone wallet, fees, minimum amount, KYC, and
  live transaction behavior. No request was made. Official docs say there is no sandbox and calls
  can move funds; the human procedure is deferred to a later approved phase in `LIVE_SMOKE_TEST.md`.
- **UNVERIFIED:** SMS provider, Tanzania delivery, sender-ID rules, pricing, and delivery terms. The
  console adapter is local-only and no message was sent to a provider.
- **UNVERIFIED:** hardware serial format and hardware provisioning list; ADR-006 uses a server-issued
  device ID and nullable serial until hardware confirmation.
- **UNVERIFIED:** exact staging/production Render and Supabase plans, regions, budget, backup RPO/RTO,
  retention, privacy/legal approvals, support and incident ownership.

Current official sources consulted on 20 October 2026:

- Django 5.2.18 package metadata: <https://pypi.org/project/Django/5.2.18/>.
- Supabase connection modes: <https://supabase.com/docs/guides/database/connecting-to-postgres>.
- Supabase row-level security: <https://supabase.com/docs/guides/database/postgres/row-level-security>.
- Render Python version and Blueprint references: <https://render.com/docs/python-version>,
  <https://render.com/docs/blueprint-spec>.
- ClickPesa no-sandbox and live-call notice: <https://docs.clickpesa.com/home/sandbox-and-testing-environment>.
- Package pins, maintainers, licenses, and release data: see `DEPENDENCY_REVIEW.md` and its PyPI
  links.

## E. Risks, open decisions, and owner actions

1. Approve root-level writes before adding working GitHub Actions and CODEOWNERS. Until then CI is a
   local shell script only; this does not create GitHub branch protection or required checks.
2. Confirm Render nested Blueprint discovery, Root Directory, plan price/budget, and separate
   staging/production service settings before creating services.
3. Confirm the Supabase session-pooler connection in a non-production project and apply the documented
   Data API lockdown there before any customer schema exists.
4. Generate a complete hash-locked dependency file, install it cleanly on Python 3.14.8, run Ruff,
   pytest, pre-commit, `pip-audit`, and PostgreSQL tests in CI.
5. Select an SMS provider and delivery/security policy before implementing customer OTP. Do not enable
   console SMS in staging/production.
6. Do not add payments until the separate phase. Then add `FakeClickPesa` tests before any live
   adapter. Never use ClickPesa as a sandbox.
7. Custom-user role values are labels only. Implement authentication, MFA, role enforcement, account
   recovery, and per-device revocation only in their approved phases with tests.
8. Confirm TOTP recovery owner, legal/privacy notices, location of customer data, retention, and
   Tanzanian counsel review before go-live.

No Phase 2 work was started. No deployment, push, merge, or commit was made.

## F. Contract changes

- API contract version before: **none** (no OpenAPI contract existed).
- API contract version after: **none** (Phase 1 adds no API endpoints).
- No contract files or client folders changed; nothing was written outside `orca_webserver/`.
- Mobile and TV agents should continue treating all current screens/data as demos. They must not call
  these Django health endpoints as product APIs or infer an auth/payment/device contract from the
  custom user model. Wait for an approved Phase 3 OpenAPI contract and device protocol.
