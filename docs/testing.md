# ORCA testing and delivery guide

**Status:** IMPLEMENTED documentation; command results are recorded separately below. **Owner:** engineering and QA. **Last verified:** 21 October 2026. **Baseline:** codex/orca-cloud-foundation at 3f5e4b8.

Use synthetic data and disposable databases only. Do not send real payment, SMS, Supabase, Render, or device requests from tests.

## Commands run and observed

| Command/check | Result |
|---|---|
| Branch and history: git status --short --branch; git rev-parse HEAD; git log -n 15 --oneline | Mission 03 began on codex/orca-cloud-foundation at 3f5e4b8456b48c82d55717262f9c36ce9777a803. The worktree contained uncommitted Mission 02 documentation changes. |
| Python/Django metadata | Python 3.14.4; Django 5.2.18. |
| Flutter availability | flutter --version → flutter: command not found. Flutter analysis, tests and build are UNVERIFIED. |
| JavaScript syntax | Mission 02 ran Node --check on five extracted inline scripts across four HTML files; syntax passed. It did not run browser behavior. |
| Local Markdown link scan | Mission 02 scan passed. Mission 03 reruns after document edits are recorded in MISSION_03_REPORT.md. |
| Django check without controlling inherited DEBUG | Blocked: config/settings/base.py rejected an invalid inherited DEBUG value with “DEBUG must be a boolean value”. |
| env DEBUG=False python manage.py check --settings=config.settings.test | Pass: “System check identified no issues (0 silenced).” |
| env DEBUG=False python manage.py makemigrations --check --dry-run --settings=config.settings.test | Pass: “No changes detected”. |
| env DEBUG=False python manage.py test --settings=config.settings.test | Failed during test-module import: ModuleNotFoundError: No module named 'PIL'. Django found 13 tests; 12 executed successfully and one import-error placeholder failed. This is not a passing full suite. |
| pytest | Not run: pytest is not installed in the shared environment. |
| Pillow installation state | Pillow NOT INSTALLED in the shared environment. It is pinned in requirements.in and requirements.txt; the declaration is present, but the environment is incomplete. |
| Local PostgreSQL probe | pg_isready reported accepting connections on the default local socket. The database owner and disposability were not established, so no PostgreSQL tests or migrations were run. |
| Docker | Not installed. The optional compose file was not started. |
| Ruff, pip-audit, pip-tools, pre-commit | Not installed; no audit, lint, lock generation or hook result is claimed. |
| Secret scanner | Gitleaks and detect-secrets were unavailable. See the Mission 03 report for the bounded source/history screen and its limits. |

The earlier Phase 2 report records a separate temporary Pillow-enabled run: 40 passed and 4 PostgreSQL-only tests skipped. That historical result was not reproduced in this shared environment and is not evidence of PostgreSQL behavior.

## Django setup

The declared project target is Python 3.14; the Render Blueprint proposes 3.14.8. The observed shared interpreter was 3.14.4. Runtime pins are in requirements.in and requirements.txt. Development pins, including pytest tooling, are in requirements-dev.in and requirements-dev.txt. These .txt files are not generated transitive hash locks.

macOS/Linux, from repository root:

~~~sh
cd orca_webserver
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
export DEBUG=False
python manage.py check --settings=config.settings.test
python manage.py makemigrations --check --dry-run --settings=config.settings.test
python manage.py test --settings=config.settings.test
~~~

Windows PowerShell, from repository root:

~~~powershell
cd orca_webserver
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
$env:DEBUG = "False"
python manage.py check --settings=config.settings.test
python manage.py makemigrations --check --dry-run --settings=config.settings.test
python manage.py test --settings=config.settings.test
~~~

Set DEBUG to a recognized boolean or remove an invalid inherited value. The base settings validate it even when test settings set DEBUG=False later. Never put credentials in shell history or paste them into reports.

## Generate complete hash locks

pip-compile and uv were not installed during Mission 03. No generated lock is claimed. In a network-enabled clean Python 3.14 environment, a human may run:

~~~sh
python -m pip install pip-tools==7.6.2
pip-compile --generate-hashes --output-file=requirements.lock requirements.in
pip-compile --generate-hashes --output-file=requirements-dev.lock requirements-dev.in
python -m pip install --require-hashes -r requirements-dev.lock
pip-audit -r requirements.lock
~~~

Review the complete diff and supported Python/platform wheels before committing generated locks. requirements-dev.in includes requirements.in, so requirements-dev.lock should cover runtime and development dependencies. Do not describe the current direct pins as hash-locked.

## Django and PostgreSQL checks

Django pytest configuration is in pyproject.toml: it selects config.settings.test, recognizes tests.py modules, and declares the requires_postgres marker. The PostgreSQL test also has Django’s requires_postgres tag and skips itself when the selected database is not PostgreSQL.

The optional database in docs/dev/docker-compose.postgres.yml binds only to 127.0.0.1, uses disposable credentials, and stores data in tmpfs. It was not started during this mission. A human must confirm Docker is available and inspect the compose file before starting it.

~~~sh
docker compose -f docs/dev/docker-compose.postgres.yml up -d
pg_isready -h 127.0.0.1 -p 55432 -U orca_dev -d orca_test
cd orca_webserver
export DEBUG=False
export DATABASE_URL=postgresql://orca_dev:orca_dev_only@127.0.0.1:55432/orca_test
python manage.py migrate --settings=config.settings.postgres_test
python manage.py test --settings=config.settings.postgres_test
~~~

After tests, stop and remove this disposable database:

~~~sh
docker compose -f ../docs/dev/docker-compose.postgres.yml down
~~~

Do not substitute any hosted URL for the local DATABASE_URL. PostgreSQL concurrency and trigger behavior remain UNVERIFIED until these tests run on a verified disposable PostgreSQL instance.

## Flutter mobile app

The package entrypoint is orca_mobile/lib/main.dart. The different orca_mobile/orca_mobile/main.dart copy is not selected by pubspec.yaml. See [HUMAN_VERIFICATION.md](HUMAN_VERIFICATION.md) for exact human commands, expected outcomes and result tables. Flutter was unavailable during this run.

## Static pages and browser review

From orca_webserver, python3 -m http.server 8000 serves the static marketing/dashboard pages only. From orca_TVapp, python3 -m http.server 8001 serves the TV simulator. These commands do not start Django or create API connectivity. Follow [HUMAN_VERIFICATION.md](HUMAN_VERIFICATION.md); browser visual/runtime results are UNVERIFIED.

## Documentation links

A local link scan checks Markdown file targets, not heading anchors or external websites. Run from repository root after documentation changes:

~~~sh
python3 - <<'PY'
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

root = Path.cwd()
bad = []
for md in root.rglob("*.md"):
    if ".git" in md.parts:
        continue
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("#"):
            continue
        path = unquote(parsed.path)
        if path and not (md.parent / path).resolve().exists():
            bad.append(f"{md.relative_to(root)} -> {target}")
if bad:
    print("Broken local Markdown targets:")
    print("\\n".join(bad))
    raise SystemExit(1)
print("Local Markdown file targets exist.")
PY
~~~

## Checks to run when tools are available

From orca_webserver:

~~~sh
python -m compileall -q apps config scripts
python manage.py collectstatic --dry-run --noinput --settings=config.settings.test
ruff check .
ruff format --check .
pytest --cov
pip-audit -r requirements.txt
pre-commit run --all-files
~~~

These commands are not claimed as passing unless a dated result is recorded in [reports/MISSION_03_REPORT.md](reports/MISSION_03_REPORT.md).

## Future integration tests

No product API exists yet. After owners approve OpenAPI and the device protocol, test authentication, object/partner scope, roles, rate limits, idempotency, transitions, audit, pagination, webhook signature/replay, ledger reconciliation, device command expiry/acknowledgement, retries and support recovery. Use fake adapters and synthetic identities. Never call live ClickPesa as a test.
