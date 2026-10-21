# ORCA Cloud implementation and verification trace for AI reviewers

**Last reviewed:** 21 October 2026

**Repository:** `malocollective5core18-hue/Orca_appliance`

**Current branch:** `codex/orca-cloud-foundation`

**Mission 02 starting commit:** `3f5e4b8` — `Document ORCA Cloud implementation trace`

**Phase 2 implementation commit:** `adcc4e1` — `Build ORCA Cloud Phase 2 offline foundation`

**Phase 1 parent:** `849ef54` — `Add ORCA Cloud Phase 1 foundation`

**Status at Mission 02 start:** Phase 2 was pushed. Phase 3 had not started. This trace records source and test evidence; it is not production approval. Mission 02 documentation changes are being prepared on top of `3f5e4b8`.

## How to use this document

1. Read the root README.md, this trace, the [canonical decision index](../../docs/decisions/README.md), then the phase reports before changing code.
2. Treat “implemented” as source-level unless this document names a passing check. Treat “UNVERIFIED” literally.
3. Preserve the repository boundary: backend work is under `orca_webserver/`; mobile and TV client folders were not changed by Phases 0–2.
4. Update this trace and the phase-specific report whenever an implementation, decision, or verification result changes.
5. Do not infer a client API, external integration, deployment, or production capability from the domain schema or adapters.

## Timeline and Git trace

| Point | Commit / branch | What it records |
|---|---|---|
| Initial repository | `28235bd` on `main` | Initial ORCA appliance upload. |
| Architecture documentation | `32b8c91` on `codex/orca-architecture-docs`; also base of `codex/orca-cloud-phase0` | Relationship of `orca_mobile`, `orca_webserver`, and `orca_TVapp`; no backend implementation. |
| Phase 1 foundation | `849ef54` on `codex/orca-cloud-foundation` | Django foundation, custom user, settings, health endpoints, logging, local SMS adapter, Render/dependency/docs groundwork. |
| Phase 2 offline foundation | `adcc4e1` on `codex/orca-cloud-foundation` | Domain schema/state transitions, ports/adapters, local image processing, SQLite/PostgreSQL trigger migration, docs and CI drafts. |

The Phase 2 branch was pushed to `origin/codex/orca-cloud-foundation`; the remote pointed to `adcc4e1` after push. No merge to `main`, tag, or deployment was performed. Recheck `git log --oneline --decorate` and `git status --short --branch` before continuing because later work may have changed this state.

Mission 02 begins at the later documentation commit `3f5e4b8`. The repository was verified clean on the required branch before this documentation pass. Keep these SHAs as chronology; do not replace them with a guess about the branch's eventual HEAD.

## Phase 0 — architecture and risk review

See `docs/PHASE0_REPORT.md` and `docs/LESSONS_AND_REFERENCES.md`.

- Reviewed the existing three-project family and concluded that the webserver folder was a prototype, not a working Django API. Mobile and TV did not yet communicate with it.
- Recorded architecture, integration risks, owner decisions, external documentation and lessons from earlier projects.
- No Django application implementation, client contract, production command, integration call, or database operation was performed in Phase 0.
- Recommendations in the Phase 0 report are proposals unless separately confirmed by the owner in writing and recorded in the canonical root decision index.

## Phase 1 — Django foundation

See `docs/PHASE1_REPORT.md`; source is in `config/`, `apps/accounts/`, `manage.py`, `scripts/`, and the project-level files inside this folder.

- Created Django 5.2 settings split into base/local/production/test, a custom `accounts.User`, and the initial user migration.
- Added `/healthz` (empty process health) and `/readyz` (database readiness), request IDs and privacy-minimized structured request logging.
- Added a development-only console SMS adapter that masks the destination and refuses operation unless `DEBUG=True`; it does not implement OTP or send real SMS.
- Added PostgreSQL URL validation, SSL requirement, rejection of Supabase transaction-pooler port 6543, production security settings, WhiteNoise/Gunicorn configuration and a nested Render Blueprint draft.
- Added dependency declarations and local CI tooling documentation. Phase 1 did not contain payment, tenant, customer, agreement, ledger, API, pairing or device domain code.

Phase 1 evidence is historical and its environment details are in its report. Do not substitute its 12-test result for the current Phase 2 result.

## Phase 2 — implemented source

See docs/PHASE2_REPORT.md, root docs/decisions/ADRS.md ADR-013–015, docs/PORTS_AND_ADAPTERS.md, and docs/IMAGE_STORAGE.md.

### Domain and persistence

`apps/domain/models.py` and migration `apps/domain/migrations/0001_initial.py` add:

- `Partner`, `Customer`, `Product`, and `Agreement`;
- `Installment`, `Payment`, `PaymentAttempt`, and `ProviderWebhookEvent`;
- `Device`, `PairingCode`, `DeviceCommand`, and `DeviceStatusHistory`;
- `Notification`, `IdempotencyRecord`, `AuditEvent`, and `ImageAsset`.

Amounts are integer TZS fields. The schema includes partner references, uniqueness/check constraints, indexes, protected deletion rules, and a one-primary-ready-image constraint. `apps/domain/statuses.py` defines persisted status constants; `apps/domain/services.py` contains payment, pairing, command transition helpers, idempotent payment creation and webhook event de-duplication. These are model/service foundations, not customer-facing HTTP workflows or a completed accounting ledger.

`apps/domain/migrations/0002_partner_scope_triggers.py` enforces cross-partner references for inserts and updates on PostgreSQL and SQLite. It also makes audit rows append-only at the database layer. Model validation and ORM protections are additional safeguards, not replacements for authorization at future API boundaries.

### Ports and adapters

Protocols are in `apps/ports/` for payment, storage, SMS, device transport and time. Deterministic fake/local implementations are in `apps/adapters/`; the accounts SMS adapter also has a recording test implementation. Backend settings are validated at startup. Demo/local selection reports `SERVER_MODE=demo`; production refuses demo mode unless explicitly opted in, and live payment mode is rejected.

There is no ClickPesa HTTP client, Supabase client, cloud object storage, production SMS vendor, MQTT broker connection, or live device transport. The database queue adapter is local application infrastructure, not an authenticated device API.

### Images

`apps/domain/images.py` validates image bytes and dimensions, enforces configured limits, rebuilds pixels to strip EXIF, and produces thumbnail/medium/large WebP variants. `ImageAsset` stores metadata and a storage key. There is no upload endpoint, private media authorization route, public CDN, or cloud storage adapter.

### Health and environment

`config/health.py` preserves empty `/healthz` and returns a small server-mode response from database-checking `/readyz`. `config/settings/postgres_test.py` supports a PostgreSQL test URL. Production requires explicit database, session-pooler mode, host and CSRF configuration and SSL. A synthetic `check --deploy` tests settings validation only; it does not connect to Render or Supabase.

## What is deliberately not implemented

The following are Phase 3 or owner-gated work; do not claim they exist because related database models or fake adapters exist:

- Versioned `/api/v1/` routes, serializers, OpenAPI document, client contract copies or mobile/TV integration.
- Customer OTP, token issuance/revocation, staff login/MFA, role/partner authorization, device credentials or pairing endpoints.
- Payment initiation endpoints, ClickPesa calls, webhook HTTP handling/signature verification against real provider vectors, reconciliation, ledger allocation, refunds or financial reporting.
- Product/customer/agreement CRUD, installment generation, tenant provisioning workflow, billing policy or device restriction policy.
- Device heartbeat, polling API, MQTT, remote commands, proof that a command was physically applied, offline sync or firmware update.
- SMS OTP delivery, production notification dispatch, background workers, retries, monitoring/alerting or incident runbooks.
- Image upload, file serving, moderation/approval workflow, object storage or CDN.
- Root `.github/workflows/` CI, active root CODEOWNERS, branch protection, required checks, generated hash-locked dependency files, or active GitHub CI. Files under `docs/ci/` are samples only.
- Render Blueprint import, service/environment configuration, Supabase provisioning, database migration on a hosted service, backup/restore drill, domain/TLS proof or live deployment.
- Production legal/privacy approval, retention plan, support ownership, RPO/RTO, budget or live smoke test.

## Verification ledger

Results observed for the Phase 2 commit:

| Check | Result | Limits |
|---|---|---|
| `manage.py check --settings=config.settings.test` | Pass | SQLite/test settings only. |
| `manage.py makemigrations --check --dry-run --settings=config.settings.test` | Pass; no changes detected | Does not validate a hosted DB. |
| `manage.py test apps.domain apps.accounts --settings=config.settings.test` | **40 passed, 4 skipped** | Four PostgreSQL-only tests skipped; suite used Django test runner. |
| SQLite migration apply, reverse domain migrations, and reapply | Pass | PostgreSQL DDL and data-volume behavior remain unverified. |
| Cross-partner ORM insert and direct SQL audit mutation guards | Pass | Observed on SQLite. PostgreSQL trigger test was skipped. |
| `python -m compileall -q apps config scripts` | Pass | Syntax compilation only. |
| `git diff --check` | Pass | Whitespace check only. |
| `manage.py check --deploy --settings=config.settings.production` with synthetic values and `ALLOW_DEMO_BACKENDS=true` | Pass | No database connection or live secret was used. |

Mission 02 documentation-review checks on 21 October 2026:

- Django test settings check and migration drift check passed.
- The Django suite rerun did **not** complete: test import failed with `ModuleNotFoundError: No module named 'PIL'` in the shared environment. 13 tests ran before the module import error. The earlier 40-pass/4-skip result above came from a temporary Pillow-enabled Phase 2 environment; do not represent it as reproduced here.
- `node --check` passed on five inline scripts across the two marketing pages, dashboard demo, and TV simulator. This proves syntax only.
- Local relative Markdown file-link scan passed. External URLs, anchors, Flutter analysis/tests, and browser visual behavior remain unverified.
- `git diff --check` passed after avoiding carriage-return whitespace on new lines in existing CRLF mobile docs.

Still **UNVERIFIED**: PostgreSQL migration and all PostgreSQL-only race/trigger tests; repeated concurrency run; fresh install from generated hashes; Ruff; pytest runner and coverage; `pip-audit`; pre-commit; local `runserver` socket smoke; root GitHub Actions; actual Render/Supabase behavior; all external integrations; client interoperability; security review and production approval. Owner-requested Ruff, pytest, pip-audit, pre-commit and local server checks remain owner-run gates.

## Decisions and dependencies to preserve

Use the root docs/decisions/README.md as the canonical decision index. Detailed ADRs are in docs/decisions/ADRS.md.

- ADR-001: implementation boundary is `orca_webserver/`; root CI/CODEOWNERS changes require owner action.
- ADR-002/003/004/005/006/007/008: payment, identity, tenant, ledger, hardware, device transport and SMS boundaries must not be guessed during Phase 3.
- ADR-009/010/011: hosted plans/connectivity, operational proof, privacy/legal review and incident responsibility remain release gates.
- ADR-013/014/015: fake/local adapters only, image publishing policy pending, domain invariants and trigger protections.
- Review `DEPENDENCY_REVIEW.md` before changing pins. Lock generation is an owner action; never label `.in` inputs or current pins a hashed reproducible lock.
- Review `DEPLOY_RENDER.md` before connecting Render. Nested Blueprint path and service Root Directory are separate settings and have not been validated in the owner account.

## Recommended continuation sequence

1. Owner runs the requested local checks and supplies complete output/errors without secrets.
2. Generate and review hashed runtime/development locks using the documented pip-tools process; install cleanly in a fresh Python 3.14 environment.
3. Run PostgreSQL migrations and the PostgreSQL-only test set against a disposable database; repeat the concurrency test as directed by the mission, then record the exact command and count.
4. Resolve open product/security decisions in the canonical decision index, especially tenancy, auth, ledger semantics, ClickPesa behavior, device identity/control, SMS, retention, backups, and operations.
5. Obtain explicit authorization for Phase 3. Design/version the OpenAPI and device protocol before exposing endpoints or editing client folders.
6. Add active GitHub Actions and CODEOWNERS only after the owner authorizes writes at recognized repository-root paths. Treat `docs/ci/` as documentation until then.
7. Import/configure Render and provision a separate non-production Supabase project only with explicit owner approval. Prove backup and restore before production.

Do not perform a live ClickPesa request as a test: the provider has no sandbox and requests may move real funds. Do not use production data in tests. Stop before an action that crosses an owner-approval boundary.

## Related documents

- `README.md` — local project entry point and commands.
- `docs/PHASE0_REPORT.md` — architecture and discovery.
- `docs/PHASE1_REPORT.md` — initial Django foundation and historical checks.
- `docs/PHASE2_REPORT.md` — Phase 2 implementation and verification results.
- Root docs/decisions/README.md and docs/decisions/ADRS.md — the sole current decision index and detailed records.
- `docs/PORTS_AND_ADAPTERS.md`, `docs/IMAGE_STORAGE.md` — implementation detail and safety boundaries.
- `docs/DEPENDENCY_REVIEW.md`, `docs/CI_SCOPE.md`, `docs/DEPLOY_RENDER.md` — dependency, CI, and hosting instructions.
- `docs/LIVE_SMOKE_TEST.md` — later human-only integration procedure; not evidence that it was run.
- Root `README.md`, `docs/testing.md`, `docs/roadmap.md`, `../../docs/decisions/README.md` — repository-wide developer entry point, checks, milestones and open decisions added in Mission 02.


## Mission 03 — baseline stabilization and documentation audit

Mission 03 began with HEAD 3f5e4b8 on codex/orca-cloud-foundation. The worktree already contained the uncommitted Mission 02 documentation changes; those files were inventoried and preserved. Mission 03 added documentation, an additive ignore-rule update, and inactive root documentation drafts only. No application source, dependency declaration, test configuration, active workflow, commit, or push was changed.

Dependency review confirmed Pillow 13.0.0 is declared in both requirements.in and requirements.txt; it was absent from the shared virtualenv. pyproject.toml already configures pytest, Django test settings, and the requires_postgres marker. No declaration or test-configuration fix was needed.

Observed rerun with DEBUG=False: Django check passed and makemigrations check returned “No changes detected”. The Django test command found 13 tests and errored importing apps.domain.tests because PIL was unavailable; 12 test cases executed successfully, one import-error placeholder failed, so the full suite did not pass. pytest, Flutter, Docker, pip-tools, Ruff, pip-audit, pre-commit, Gitleaks and detect-secrets were unavailable. pg_isready accepted a local connection, but the database was not proven disposable and no PostgreSQL test was run.

The canonical decision index and detailed ADR history now live under repository-root docs/decisions/. The server-local DECISIONS.md and old DECISION-REGISTER.md are pointers; historical phase reports preserve their chronology. No decision is currently marked ACCEPTED without written approval evidence. See docs/decisions/README.md and docs/reports/MISSION_03_REPORT.md.

Mission 03 security screening suppressed all matched values. Its limited regex screen reported Tanzania-phone-shaped test fixtures, example.test database URLs, and placeholder local credentials only; it did not find private-key headers or common token shapes. The ignored .env file was not opened. Gitleaks was unavailable, so no clean-history secret-scan result is claimed. See the Mission 03 report for scan scope and limitations.
