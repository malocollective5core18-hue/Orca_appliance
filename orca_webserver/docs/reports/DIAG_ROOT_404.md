# ORCA Cloud root-path 404 diagnosis

**Date:** 22 October 2026
**Branch:** `codex/orca-webserver-admin-login-diagnosis` at `8d32ed8` (`codex/orca-cloud-foundation` points to the same commit).
**Scope:** Read-only diagnosis and local Django test-client reproduction. No app/configuration changes, branch switch, commit, push, deploy, Render dashboard access, or live request was performed. The worktree was clean before and after diagnosis.

## Finding

The root cause is **confirmed in source and reproduced locally**: the Django URL configuration has no `/` route. It registers `/healthz`, `/readyz`, and `/admin/` only. The configured WSGI application loads `config.settings.production`, which sets `DEBUG=False`. A request to `/` therefore receives Django's generic production 404. This explains the supplied live `GET / 404` and `HEAD / 404` logs; those logs themselves were provided by the owner, not independently fetched from Render.

The health-check success is consistent with this: Render calls `/healthz`, which has a route and returns 204. A healthy process does not imply a home page exists.

## Source evidence

| Finding | Source |
|---|---|
| URL patterns register only `healthz`, `readyz`, and `admin/`; no root path exists. | [`config/urls.py`](../../config/urls.py#L1-L10), lines 1–10. |
| WSGI defaults to production settings. | [`config/wsgi.py`](../../config/wsgi.py#L1-L9), line 7. |
| Production forces `DEBUG=False`; requires host/origin allowlists; enables HTTPS proxy handling, redirect, secure cookies and HSTS. | [`config/settings/production.py`](../../config/settings/production.py#L11-L51), lines 11–51. |
| `ROOT_URLCONF` is `config.urls`; middleware includes request-ID, Django security middleware, WhiteNoise, sessions, common and CSRF middleware. | [`config/settings/base.py`](../../config/settings/base.py#L99-L128), lines 99–128. |
| Templates are searched under `BASE_DIR/templates` and app directories. Static assets are served from the collected `staticfiles` location; a project `static/` directory is included only if it exists. | [`config/settings/base.py`](../../config/settings/base.py#L115-L128) and [lines 144–152](../../config/settings/base.py#L144-L152). |
| `healthz` returns an empty 204 without querying the database. `readyz` attempts a database connection and returns only `server_mode` JSON on success, otherwise an empty 503. | [`config/health.py`](../../config/health.py#L14-L38), lines 14–38. |
| Root is absent from the documented Django route inventory. | [`README.md`](../../README.md#L18-L28), lines 18–28; [`docs/DEPLOY_RENDER.md`](../DEPLOY_RENDER.md#L5-L8), lines 5–8. |
| Blueprint specifies `rootDir: orca_webserver`, `collectstatic`, migrations, Gunicorn WSGI start command, `/healthz`, Python 3.14.8, and production settings. | [`render.yaml`](../../render.yaml#L3-L20), lines 3–20. It is a repository Blueprint, not proof of current dashboard values. |
| Request-ID middleware sets `request.request_id`, adds `X-Request-ID`, and logs a safe completion event, then resets its context variable. | [`config/middleware.py`](../../config/middleware.py#L12-L35), lines 12–35. |
| The JSON formatter suppresses unknown log messages and reads request ID from a context variable, defaulting to `-`. | [`config/logging.py`](../../config/logging.py#L10-L45), lines 10–45. |

The project-level `templates/` and `static/` directories do not exist under `orca_webserver/`. Django admin can still use templates and static assets supplied by installed Django apps and WhiteNoise's collected assets. This does not create or imply a `/` route.

## Local reproduction (no network sockets)

A Django `Client` was used with `DJANGO_SETTINGS_MODULE=config.settings.production`, `DEBUG=false`, and synthetic local-only environment values. No real `.env` values were read. The PostgreSQL URL was a dummy loopback URL; the `readyz` database connectivity call was patched during that single request, so no database/network connection was opened. The exact command was run from `orca_webserver/`:

```sh
env -u DEBUG .venv/bin/python - <<'PY'
import os
from unittest.mock import patch

os.environ.update({
    "DJANGO_SETTINGS_MODULE": "config.settings.production",
    "DEBUG": "false",
    "DJANGO_SECRET_KEY": "local-test-only-secret-value-with-more-than-fifty-characters-000000000000",
    "DATABASE_URL": "postgresql://test:test@127.0.0.1:5432/test?sslmode=require",
    "DATABASE_CONNECTION_MODE": "session",
    "ALLOWED_HOSTS": "localhost,testserver",
    "CSRF_TRUSTED_ORIGINS": "https://localhost",
    "ALLOW_DEMO_BACKENDS": "true",
    "PAYMENTS_LIVE_ENABLED": "false",
})
import django
django.setup()
from django.test import Client

client = Client(HTTP_HOST="localhost")
for method, path in [("get", "/"), ("head", "/"), ("get", "/healthz"), ("get", "/readyz"), ("get", "/definitely-unknown")]:
    if path == "/readyz":
        with patch("config.health.connection.ensure_connection"):
            response = getattr(client, method)(path, secure=True)
    else:
        response = getattr(client, method)(path, secure=True)
    print(method.upper(), path, response.status_code,
          response.get("Content-Type", ""), len(response.content))
PY
```

Observed results:

| Request | Status | Content-Type | Body bytes | Notes |
|---|---:|---|---:|---|
| `GET /` | 404 | `text/html; charset=utf-8` | 179 | Generic Django production 404. |
| `HEAD /` | 404 | `text/html; charset=utf-8` | 0 | Headers/status match GET; HEAD has no response body. |
| `GET /healthz` | 204 | `text/html; charset=utf-8` | 0 | Process health route. |
| `GET /readyz` | 200 | `application/json` | 23 | Test-only DB probe was patched; body is `{"server_mode":"demo"}`. This does not test a live database. |
| `GET /definitely-unknown` | 404 | `text/html; charset=utf-8` | 179 | Same generic production 404 as `/`. |

All five responses included `X-Request-ID`. Responses also included `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`, `X-Content-Type-Options: nosniff`, and `X-Frame-Options: DENY`. The tested 404 body contained none of the checked debug markers (`Traceback`, `settings.py`, exception type, or Django URL-resolution details). This is evidence for the local production-settings response only; it does not independently inspect the live response body.

## Hypotheses

| Hypothesis | Result | Evidence / limit |
|---|---|---|
| (a) URL configuration has no `/` route. | **CONFIRMED** | `config/urls.py:6-10` has no root pattern; local production-settings `GET /` and `HEAD /` both return 404. |
| (b) Wrong settings module or start command caused this. | **REFUTED as the explanation for this 404; live environment partly UNVERIFIED** | WSGI defaults to `config.settings.production`; Blueprint start command targets `config.wsgi:application`; owner-provided deployment logs show the service starts and health/readiness routes resolve. Exact Render dashboard override for settings/start command is not accessible. A wrong command is unlikely to produce this specific working route map. |
| (c) `ALLOWED_HOSTS` or `CSRF_TRUSTED_ORIGINS` caused this. | **REFUTED for the observed GET/HEAD 404** | Valid `Host: localhost` under production settings reproduced the 404. Root GET/HEAD do not require CSRF. Production still requires both allowlists, and live values were not inspected; a host mismatch normally produces a bad-request response rather than this route-not-found response. |
| (d) Static files or templates were not collected. | **REFUTED as the cause of `/` returning 404** | No root view or template is registered to render. Project `templates/` and `static/` directories are absent; Django admin can use app-provided assets. Static collection serves static paths and cannot add a URL route. Live collectstatic output was not independently verified in this mission. |
| (e) Render root directory or Blueprint path is wrong. | **REFUTED as the explanation for the currently running Django route behavior; dashboard configuration UNVERIFIED** | The supplied service responds through Django at `/healthz` and `/readyz`; the repository Blueprint's `rootDir` is `orca_webserver`. Exact imported Blueprint file, dashboard Root Directory and overrides remain unverified. |
| (f) `/` is intentionally absent according to docs. | **CONFIRMED in the documented route inventory; product intent UNVERIFIED** | README and deployment guide enumerate health/readiness/admin routes and omit `/`. They do not explicitly say that visitors should receive a 404. |

## Log interpretation

- `GET /healthz 204` every five seconds is Render's configured process health probe. It shows the process answered at that path; it does not check database readiness. The Blueprint configures `/healthz`, and `healthz()` deliberately avoids the database.
- `GET / 404` and `HEAD / 404` are normal route-not-found results because the root path is unregistered. The generic body is expected with production `DEBUG=False`.
- The supplied `127.0.0.1` access-log address is the address Gunicorn sees as the immediate TCP peer in that log format. It can be a local proxy/forwarder hop; it does not establish the browser's public address. The supplied health-check peer `10.231.25.165` is consistent with a separate internal health-check source, but its exact network role is not independently verifiable from this environment.
- `WARNING django.request event=unstructured_log_suppressed status_code=404, request_id "-"` means the privacy-focused formatter discarded the free-form Django warning message and kept only safe structured fields. This prevents accidental URL/message leakage. The missing ID is a correlation gap: Django's 404 warning is emitted after the custom middleware has returned and reset its context variable. The reproduction shows the preceding `orca.request` completion event and response header have a real ID, while Django's subsequent warning gets `-`.
- **Should 404 logs have a request ID?** Yes, ideally. Keep the safe suppression, but correlate Django's warning to the request ID (for example by reading an ID attached to the log record's request object). This is a proposed follow-up only; no logging change was made. Render recommends logging `CF-Ray` for request tracing as well.

## Client IP behind Render

Render's current DDoS article says inbound web-service traffic passes through Cloudflare and Render load balancers; the app sees the proxy IP by default and should read `x-forwarded-for` for the real client IP. It also identifies `CF-Ray` as a request-tracing header. The article has no visible publication date; checked **22 October 2026**: [How Render handles DDoS attacks](https://render.com/articles/how-render-handles-ddos-attacks). Render's uptime guidance says to include `CF-Ray` in request logs; checked **22 October 2026**: [Best Practices for Maximizing Uptime](https://render.com/docs/uptime-best-practices).

Django currently sets `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` in `config/settings/production.py:43`. That setting tells Django whether the original request was HTTPS; it does not configure or validate the client IP. Django's 5.2 settings documentation says proxy headers should only be trusted when the proxy controls/strips the incoming header and sets it correctly: [Django `SECURE_PROXY_SSL_HEADER` documentation](https://docs.djangoproject.com/en/5.2/ref/settings/#secure-proxy-ssl-header), checked 22 October 2026.

Source search found no use of `HTTP_X_FORWARDED_FOR`, `REMOTE_ADDR`, or `CF-Ray` in the ORCA Django application. No current IP-based rate limiting or audit attribution was found. Render's public article does not specify the exact X-Forwarded-For chain order/sanitization guarantees for this service. Therefore, before using client IP for rate limiting, blocking, or audit attribution, verify Render's header behavior, select only the trusted proxy-provided client value, and test that a client-supplied forged header cannot choose its own IP. The chain/trust behavior is **UNVERIFIED**; no IP trust setting or middleware was changed.

## Production 404 disclosure check

**Local result: PASS.** Under `config.settings.production`, `DEBUG=False`; root and unknown-path responses were generic 179-byte HTML (0 bytes for HEAD), with no checked traceback/settings/URL resolver details and with the listed security headers. The Render response body was not fetched independently during this mission. Based on the owner-provided generic “Not Found” page it appears non-diagnostic, but live disclosure status is **UNVERIFIED** until checked directly in the browser or with a safe `curl`.

## Proposed root behavior — stop for owner approval

No option has been implemented.

| Option | Pros | Cons |
|---|---|---|
| **A. Minimal HTML welcome page**: `ORCA Cloud, demo mode`, with links to `/healthz` and `/readyz`; GET and HEAD return 200. | Human-friendly; makes the service identity clear; does not add a product API or expose personal/database data. | A hard-coded “demo mode” can become stale if the server mode changes; the view should render that label from the server's configured mode or avoid claiming a mode. |
| **B. JSON service status** at `/` with service name, `server_mode`, and links only. | Machine-readable and easy to test; small response. | Duplicates `/readyz`; browser users see raw JSON instead of a welcome page; publishing live/demo mode may be unnecessary. |
| **C. Keep `/` as 404 and document expected URLs.** | No application change or extra endpoint; least exposed surface. | Visitors continue to see “Not Found,” which is the reported problem. |

**Owner decision:** Option A approved. The welcome page renders `settings.SERVER_MODE` as `demo` or `live`, uses only local health/readiness links, and contains no secret, internal hostname, database detail, dependency version, or personal data. The existing `/healthz` and `/readyz` behavior is unchanged.

## Render dashboard checklist for the owner

Read these values back without sharing secret values or screenshots of the Environment page:

- [ ] Service type and plan (the owner previously said Free; `render.yaml` says `starter`; actual dashboard plan is **UNVERIFIED**).
- [ ] Root Directory.
- [ ] Build command.
- [ ] Start command.
- [ ] Pre-deploy command.
- [ ] Health check path (expected `/healthz`).
- [ ] Python version.
- [ ] Auto-deploy branch and deployment commit SHA.
- [ ] Environment-variable **names only** that exist; never read out or paste values.
- [ ] Custom domain(s) and TLS/certificate status.

## Implementation and verification after approval

The approved Option A was implemented on `codex/orca-webserver-admin-login-diagnosis`:

- `config/views.py` adds a small data-free HTML welcome page. It uses a strict `demo`/`live` label, links to `/healthz` and `/readyz`, and permits only GET/HEAD.
- `config/urls.py` registers the named `/` route.
- `config/middleware.py` includes the server-generated request ID as a safe structured field. `config/logging.py` can take the ID from Django's request log record after middleware context reset. Django 404 warning logs now correlate without including their path/message.
- `apps/accounts/tests.py` covers root GET/HEAD/method restriction, mode rendering, safe content/security headers, request-ID correlation for 404 and home, unknown-route 404, and unchanged `/healthz` behavior.
- `docs/DEPLOY_RENDER.md` now has an expected-responses table and exact curl checks for root, health, readiness, admin and an unknown path.

Checks run from `orca_webserver/` with the checked-in virtual environment and `DEBUG=false`:

| Command | Result |
|---|---|
| `DEBUG=false .venv/bin/python manage.py check --settings=config.settings.test` | Pass: no issues. |
| `DEBUG=false .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.settings.test` | Pass: no changes detected. |
| `DEBUG=false .venv/bin/python manage.py test --settings=config.settings.test` | Pass: 47 tests, 4 PostgreSQL-only tests skipped, 0 failures. |
| `git diff --check` | Pass for tracked changes. The new diagnostic report was also checked for whitespace before this update. |

The local production-settings TestClient reproduction above was performed before the route was added. The suite now verifies the new route under the project's fast test settings; it does not make a live Render claim.

## Remaining live/deployment checks

- No request was sent to `https://orca-appliance.onrender.com`; no Render dashboard, Shell, service logs, or live environment values were accessed.
- The deployed branch/SHA is based on owner-provided deployment output and local branch references; Render's current deploy and dashboard overrides remain **UNVERIFIED**.
- Live `/`, `/healthz`, `/readyz`, public 404 headers/body, actual database readiness, and Render's `X-Forwarded-For` trust-chain behavior remain **UNVERIFIED**.
- No production database, live migration, browser suite, security audit, commit, push, merge, or deploy was performed.


## Follow-up: serve the requested public landing page

After the status-page fix was pushed, the owner clarified that `/` should display the repository's public `index.html`. The previous page (`ORCA Cloud` plus service-mode and health links) was the result of the earlier Option A approval, but it did not match this clarified expectation.

The current local follow-up changes `config/views.py` to stream `index.html` at `/`, retains GET/HEAD support and request IDs, and updates the home-page regression test and deployment guide. The follow-up has not been committed or pushed yet. Render's deployed SHA is not verified; the owner reports seeing the status page, which is consistent with the earlier pushed commit but does not independently identify the running build.

Authentication boundary confirmed from source:

- `index.html` has navigation links with `href="#login"`, but no login section or form exists.
- `orca-dashboard-demo-1.html` has no password/login form, Django request, or API call; it creates demo/sample data in browser JavaScript.
- `/admin/` is the only implemented Django superuser login. After authentication, it opens Django admin, not the visual dashboard demo.

No login flow or dashboard integration was added in this follow-up. A real authenticated staff dashboard requires a separate implementation and authorization scope; the static demo must not be mistaken for live data.
