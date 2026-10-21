# ORCA Cloud Phase 2 implementation report

**Date:** 21 October 2026

**Branch:** `codex/orca-cloud-foundation`
**Scope:** Phase 2 offline foundation in `orca_webserver/` only. No root files, Phase 3 API, external provider, production system, or production data were accessed. Changes remain local, uncommitted, and unpushed.

## Result

Phase 2 implementation is present, with the boundaries and remaining verification gaps below. This is not deployment or production approval. Phase 3 has not started.

## A. Domain model and lifecycle

Added `apps/domain/` with partner, customer, product, agreement, installment, device, pairing, payment, webhook-event, command, status-history, notification, idempotency, audit, and image metadata models. Monetary values use integer TZS. Constraints, indexes, partner references, and protected deletion behavior are in migration `0001_initial.py`.

Payment, pairing-code, and device-command transitions are centralized in `services.py`. Cross-partner relationships are guarded by model validation and database triggers in `0002_partner_scope_triggers.py` for PostgreSQL and SQLite. Audit events reject mutation through ORM APIs and database triggers. SQLite suite coverage passes; PostgreSQL trigger and concurrency behavior remains **UNVERIFIED** until run against PostgreSQL.

## B. Ports and adapters

Added protocols under `apps/ports/` for payment, storage, SMS, device transport, and clock. Deterministic fake/local adapters live under `apps/adapters/`. No ClickPesa, Supabase, object-storage, SMS vendor, or MQTT client is installed or contacted. Backend selectors reject unknown values; demo/local selection is explicit and production settings reject it unless `ALLOW_DEMO_BACKENDS=true` is deliberately set. That opt-in is for controlled staging only, not production readiness.

## C. Image handling

Added byte-based image validation and metadata-free WebP variant generation in `apps/domain/images.py`. It checks format, dimensions, pixel/byte limits and strips EXIF by rebuilding pixels. `ImageAsset` stores metadata and a storage key, not image bytes. No upload endpoint, public file serving route, or cloud storage integration was added. Details: `IMAGE_STORAGE.md`.

## D. Database and tests

SQLite verification completed:

- `manage.py check --settings=config.settings.test`: passed.
- `manage.py makemigrations --check --dry-run --settings=config.settings.test`: no changes detected.
- Django suite: **40 passed, 4 skipped**. The 4 skips are PostgreSQL-only tests.
- SQLite migration apply and reverse/reapply commands completed successfully.
- Cross-partner direct ORM create and direct SQL audit mutation tests passed through SQLite triggers.

PostgreSQL server was unavailable (`pg_isready` reported no response). PostgreSQL migration behavior, row-lock races, duplicate-webhook races, partner trigger behavior, and concurrency repeats are **UNVERIFIED**. The skipped tests are not counted as passes.

## E. Dependencies and CI

Pillow is pinned in runtime input for image processing. Runtime and development `.in` inputs are present. Hashed `requirements.lock` files were intentionally not generated; the repository owner must run the documented pip-tools commands and review hashes. `docs/ci/` contains drafts only. GitHub will not execute those nested drafts as Actions, and CODEOWNERS is not active there. Root-level workflow and CODEOWNERS files were outside the authorized scope. GitHub Actions, Ruff, pytest, pip-audit, pre-commit, and local runserver smoke checks are **UNVERIFIED**; the owner will run these tools and provide results.

## F. Documentation and Render setup

Updated `README.md`, `DECISIONS.md`, `DEPENDENCY_REVIEW.md`, `DEPLOY_RENDER.md`, `PORTS_AND_ADAPTERS.md`, `IMAGE_STORAGE.md`, and `CI_SCOPE.md`. Render configuration remains nested at `orca_webserver/render.yaml`; set Blueprint Path to that file and service Root Directory to `orca_webserver` when the owner chooses to connect it. No Blueprint import, Render settings, deploy, or live health check was performed.

## Verification and boundaries

| Check | Result |
|---|---|
| Django test settings check | Pass |
| Migration drift check | Pass |
| SQLite Django suite | Pass: 40; 4 PostgreSQL-only skips |
| SQLite migration apply/reverse/reapply | Pass |
| Python `compileall` / `git diff --check` | Pass |
| Production `check --deploy` with synthetic settings | Pass; no connection attempted |
| PostgreSQL migration/concurrency tests | **UNVERIFIED**; no local PostgreSQL server |
| Ruff, pytest, pip-audit, pre-commit, local server | **UNVERIFIED**; owner-run checks pending |
| Hashed dependency locks | Not generated; owner action pending |
| GitHub Actions / CODEOWNERS | Draft only, not active |
| Live integrations, Render deploy, Phase 3 API | Not run / out of scope |

No lock file generation, push, commit, merge, deployment, or production-data access occurred. Do not start Phase 3 until the owner reviews this report and supplies their verification results.
