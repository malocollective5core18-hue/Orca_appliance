# Render deployment draft — human-operated, not deployed

**Status:** Draft. No Render service, Supabase project, secret, build, migration, or deployment was
created or changed in this phase.

## Nested Blueprint path verified 21 October 2026

Render's official docs say a Blueprint YAML file may live anywhere in the repository when its path
is selected during Blueprint creation or changed in Blueprint settings. Without that selection,
Render defaults to root `render.yaml`. The existing file is `orca_webserver/render.yaml`; select that
exact path. Its `rootDir: orca_webserver` is a separate setting that makes build/start commands
relative to the app folder. The dashboard configuration for this repository remains **UNVERIFIED**.

- [Render Blueprints (IaC)](https://render.com/docs/infrastructure-as-code)
- [Blueprints now support custom filenames and paths](https://render.com/changelog/blueprints-now-support-custom-filenames-and-paths)
- [Render monorepo support](https://render.com/docs/monorepo-support)

The custom path feature was announced 9 February 2026. Do not create a second root Blueprint that
manages the same service.

Phase 2 defaults select demo/local adapters. Render production settings now refuse to start unless
`ALLOW_DEMO_BACKENDS=true` is explicitly supplied. Set it only for an owner-designated demo/staging
service. No real payment, SMS, cloud storage, or MQTT adapter exists yet. Keep it unset/false for any
service presented as live; startup then refuses until later approved real adapters are implemented.

## Before connecting a repository

1. Confirm the repository is the intended ORCA repo and select `orca_webserver/render.yaml` as the
   Blueprint path in Render. Confirm service Root Directory is `orca_webserver` in the dashboard.
   The custom path is documented by Render; this repository's imported Blueprint configuration is
   still **UNVERIFIED**. Do not make a root file without separate owner approval.
2. Review the `starter` paid-plan draft against the approved budget and current Render pricing. Do not
   provision it until the owner accepts charges. Production must be paid and always on. Staging must
   be a separate Render service.
3. Create separate staging and production Supabase projects. Keep credentials and databases
   separate. Confirm backup and point-in-time recovery entitlements for production.
4. Apply `docs/SUPABASE_DATA_API_LOCKDOWN.md` in staging and verify its access-denial test.
5. Confirm Render outbound connectivity to Supabase. Use its session pooler, not transaction mode.

## Build, release and start commands

The Blueprint draft uses:

```sh
pip install -r requirements.txt && python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```

The first command runs at build time and does not connect to the database. Migrations run in
`preDeployCommand`, which Render documents for paid web services. If the selected service cannot run
pre-deploy commands, stop and get an owner-approved migration job/release procedure; never migrate
silently during build or on every Gunicorn worker start. Review destructive migration plans and
rollback before applying any future schema change.

**Log note:** Gunicorn access logging is disabled so URL paths and query strings are not logged.
Only the Django safe request logger emits method, status, and a server-generated request ID.

## Environment variables

Set independently in staging and production. `.env.example` contains only fake local values.

| Name | Purpose / source | Secret? | Required now |
|---|---|---:|---:|
| `DJANGO_SETTINGS_MODULE` | Set to `config.settings.production`. | No | Yes |
| `DJANGO_SECRET_KEY` | Generate a distinct random key in Render for each environment. | Yes | Yes |
| `DEBUG` | `false`. | No | Yes |
| `ALLOWED_HOSTS` | Exact Render host and approved custom hostname, comma-separated, no wildcard. | No | Yes |
| `CSRF_TRUSTED_ORIGINS` | Exact HTTPS origins, including scheme and no path. | No | Yes |
| `DATABASE_URL` | Supabase session-pooler URI copied from the correct project's Connect panel, with SSL required. | Yes | Yes |
| `DATABASE_CONNECTION_MODE` | `session`; production settings reject any other value. | No | Yes |
| `DB_CONN_MAX_AGE` | `60` seconds default. Account for every Gunicorn worker/thread when sizing DB connections. | No | Yes |
| `DISABLE_SERVER_SIDE_CURSORS` | `false` for session pooler; production refuses `true`. | No | Yes |
| `PAYMENTS_LIVE_ENABLED` | `false`; production rejects `true` until a separately approved payment phase. | No | Yes |
| `SMS_BACKEND` | `console` only in Phase 1. Production refuses an unapproved provider. | No | Yes |
| `PYTHON_VERSION` | `3.14.8`, revalidate against dependencies before upgrade. | No | Yes |
| `LOG_LEVEL` | `INFO` or `WARNING`; do not log request bodies/URLs. | No | Optional |

Never set superuser bootstrap passwords in Blueprint YAML. Create the first admin through an
owner-approved one-off secure procedure only after MFA and account recovery policy exist; neither
procedure nor bootstrap command is part of Phase 1.

## First deploy smoke checks (synthetic environment only)

1. Confirm the deploy SHA, branch, root directory, Python version, dependency output, and Render
   settings. Never share environment values.
2. Confirm build passes `collectstatic`; confirm the pre-deploy phase applies migrations successfully.
3. `GET /healthz` should return `204` with an empty body and no DB data.
4. `GET /readyz` should return `204` when the configured database is reachable and `503` without
   exception detail when it is unavailable.
5. Confirm HTTPS redirect and secure cookies on a later authenticated endpoint. Do not test a
   customer, payment, SMS, or device flow in Phase 1.
6. Confirm JSON logs contain request ID, method, and status but no path, query, phone, token, or
   payload. Use synthetic sentinel values.

## Rollback, domains and TLS

- Record the last known-good SHA before each owner-approved release. Use Render's rollback to that
  deploy if the app fails health/readiness.
- Database schema rollback is separate. Prefer forward-compatible migrations; do not roll back a
  destructive migration without an approved recovery plan and verified backup.
- Attach custom domains only after DNS ownership is verified. Confirm Render TLS certificate is
  active and HTTPS redirect works before sharing links.
- Exact Render/Supabase plans, prices, regions, backup retention, RPO/RTO, DNS, and TLS are
  **UNVERIFIED**. Human owner must select and verify them.
