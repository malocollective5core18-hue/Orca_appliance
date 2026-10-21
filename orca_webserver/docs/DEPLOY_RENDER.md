# Friendly Render deployment guide for ORCA

**Purpose:** deploy an isolated ORCA Cloud foundation preview for the owner and developers to inspect. This guide does not make ORCA production-ready. No Render service, database, secret, payment, or deployment was created while writing it.

## First, know what you are deploying

The current Django app serves the public landing page at `/`, provides bilingual customer signup/login and role-routed account screens under `/accounts/`, process health at `/healthz`, database readiness at `/readyz`, and superuser-only Django admin at `/admin/`. It still does **not** include customer-finance/device product APIs, an operational staff dashboard, MFA enforcement, or real SMS, ClickPesa, Cloudinary/object-storage, or TV device connections. The HTML dashboard and Flutter/TV apps remain demos and do not connect to this server.

Use only synthetic preview data. Do not invite customers, accept payments, upload business-critical images, or treat Django admin as the finished ORCA product. Do not put Cloudinary, ClickPesa, or `DJANGO_SUPERUSER_*` values into Render: the current app does not use them.

## Before you start

- [ ] Confirm you have access to the GitHub repository `malocollective5core18-hue/Orca_appliance`.
- [ ] Pick the exact branch and commit you intend to preview. Check the GitHub branch page first; this guide does not confirm which branch has the latest code.
- [ ] Confirm the Render plan and monthly cost with the owner. The Blueprint currently says `starter`; Render plan names/prices can change. Do not create a paid resource until the cost is approved.
- [ ] Choose whether this is only an isolated preview. The current adapters are demo/local backends. Do not present it as a live service.
- [ ] Prepare a separate database for this preview. The repository guidance currently targets a Supabase **session pooler**, but its compatibility, region, plan and backup policy must be checked in the owner’s Supabase account.
- [ ] Keep the GitHub repository and database private to authorized developers. Use synthetic records only.

## What the Blueprint configures

The file is [`render.yaml`](../render.yaml). It lives under `orca_webserver/`, so during Render Blueprint setup select this exact file path. Its `rootDir: orca_webserver` means commands run from that folder. Do not create a second Blueprint for the same service.

Configured commands:

| Stage | Command | Purpose |
|---|---|---|
| Build | `pip install -r requirements.txt && python manage.py collectstatic --noinput` | Install pinned runtime packages and prepare static assets. |
| Pre-deploy | `python manage.py migrate --noinput` | Apply schema changes before the new instance receives traffic. |
| Start | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120` | Serve Django on Render’s assigned port. |
| Health | `/healthz` | Return an empty `204` when the process responds. It does not prove the database is ready. |
| Home | `/` | Serve the existing public ORCA landing page from `index.html`. |

Render documents that a pre-deploy command runs before release and a failing build/pre-deploy/start prevents the new deploy from replacing the current working deploy. Review migration changes and keep an owner-managed rollback plan. [Render deploy steps](https://render.com/docs/deploys) · [Blueprint reference](https://render.com/docs/blueprint-spec)

## Step 1 — Create the isolated database

1. In the owner’s Supabase organization, create a **separate preview project**. Do not reuse production or personal customer data.
2. Use the database connection panel to obtain the PostgreSQL **session pooler** URL. Keep the URL private; it contains a password.
3. Confirm the selected pooler uses a supported port and SSL. The app rejects transaction-pooler port `6543` and requires SSL in production settings.
4. Confirm backups/recovery are suitable for a disposable preview. A preview database is not a backup plan.

If Supabase is not available, stop and ask the owner before changing database provider or the approved connection mode. Do not paste a database URL into chat, a GitHub issue, a document, or a command that will be saved in shell history.

## Step 2 — Connect the repository in Render

1. Open Render and choose **New → Blueprint**.
2. Connect `malocollective5core18-hue/Orca_appliance` and choose the approved branch.
3. Select `orca_webserver/render.yaml` as the Blueprint file. Confirm the Root Directory is `orca_webserver`.
4. Review the proposed service name, instance plan, build, pre-deploy and start commands. Confirm any cost before applying.
5. Keep automatic deploys disabled for the first preview. Review each commit and deploy manually.
6. Apply only after the owner confirms repository branch, database, plan and isolated-preview purpose.

Render supports selecting a Blueprint file path and a service root directory; verify the values in the dashboard after import. [Render Blueprints](https://render.com/docs/infrastructure-as-code) · [Monorepo root directories](https://render.com/docs/monorepo-support)

## Step 3 — Set environment variables in Render

Open the service’s **Environment** page. Enter values there; do not upload the local `.env`. Django reads process environment variables directly and does not load `.env` or `.env.example`.

The Blueprint supplies non-secret defaults such as settings module, `DEBUG=false`, Python version and adapter selectors. Set/confirm these required values separately for this preview:

| Variable | Preview value / guidance |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` (Blueprint default). |
| `DJANGO_SECRET_KEY` | Generate a unique random value of at least 50 characters using Render’s Generate option or a trusted local generator. Never reuse the local example key. |
| `DATABASE_URL` | Private SSL-enabled session-pooler URL from the separate preview database. |
| `DATABASE_CONNECTION_MODE` | `session` (Blueprint default; required by production settings). |
| `ALLOWED_HOSTS` | Exact Render hostname, such as `service-name.onrender.com`, without scheme/path; comma-separate approved custom hosts. No `*`. |
| `CSRF_TRUSTED_ORIGINS` | Exact HTTPS origins, e.g. `https://service-name.onrender.com`; comma-separate approved origins. |
| `ALLOW_DEMO_BACKENDS` | Set `true` only for this explicitly isolated, owner-approved demo preview. This permits the configured fake/local adapters. Never mistake it for production integration approval. |

Also check `DB_CONN_MAX_AGE=60`, `DISABLE_SERVER_SIDE_CURSORS=false`, `PAYMENTS_LIVE_ENABLED=false`, `PAYMENTS_PROVIDER=fake_clickpesa`, `STORAGE_BACKEND=local`, `SMS_BACKEND=console`, `DEVICE_TRANSPORT=database`, and `LOG_LEVEL=INFO`. Keep all payment and messaging behavior fake/local. Do not add real provider credentials.

Render environment variables are service settings and can trigger a new deploy when changed; review the resulting deploy before relying on it. [Render environment variables](https://render.com/docs/configure-environment-variables)

## Step 4 — Deploy and watch the logs

1. Start the deploy from the reviewed branch/SHA.
2. Watch the build stage. It must install `requirements.txt` and finish `collectstatic`.
3. Watch pre-deploy. `migrate --noinput` must finish successfully.
4. Watch startup. Gunicorn must bind to `0.0.0.0:$PORT`; Django must not exit with a missing/invalid setting error.
5. Record the branch, commit SHA, deploy time, and pass/fail result. Never copy secret values, database URLs, or request data into the report.

A successful build only means the configured build command completed. A successful deploy does not prove product journeys or integrations exist.

## Step 5 — Verify the deployed service

Replace `<service-host>` with the public hostname; do not include angle brackets in commands. Run these checks after recording the deployed branch and commit SHA:

```sh
curl -sS -D - -o /tmp/orca-home.html https://<service-host>/
curl -sS -I https://<service-host>/
curl -sS -D - -o /dev/null https://<service-host>/healthz
curl -sS -D - https://<service-host>/readyz
curl -sS -D - -o /dev/null https://<service-host>/admin/
curl -sS -D - -o /dev/null https://<service-host>/not-a-real-route/
```

Expected responses:

| Path | Method | Expected status | Body | Caller / purpose |
|---|---|---:|---|---|
| `/` | GET | `200` | Existing public ORCA landing page (`index.html`). | Public visitor. |
| `/` | HEAD | `200` | No body; same content type and content length as GET. | HTTP probes or clients that only inspect headers. |
| `/healthz` | GET | `204` | Empty. | Render process health check. Does not test the database. |
| `/readyz` | GET | `200` when database connects; `503` otherwise | On 200, JSON `{"server_mode":"demo"}` or `{"server_mode":"live"}`. On 503, empty. | Owner/operator checking database readiness. |
| `/admin/` | GET | `302` or `200` | Redirect to login or Django admin page. | Authorized owner inspecting Django admin. |
| Unknown path | GET | `404` | Generic production not-found page without debug details. | Negative routing check. |

Check that `/` renders the public landing page and `X-Request-ID` is present on application responses. `/accounts/signup/` creates customer accounts and redirects to the responsive customer account screen. `/accounts/login/` routes users to the customer or staff screen. Superusers may register any supported role; administrators may register customer-service accounts only; customer-service users cannot register accounts. Only superusers can open `/admin/`. The static `orca-dashboard-demo-1.html` remains an unauthenticated visual demo with generated sample data; do not present it as a live staff dashboard.

## Account access in the preview

Customer signup is available at `/accounts/signup/`. Administrator and customer-service accounts must be created by an authorized superuser/administrator using the staff dashboard; public signup cannot choose a staff role. Use synthetic identities only. The current login has no email verification, recovery flow, invitation delivery, or MFA, so keep the preview private.

## Superuser for the preview

Only if the owner explicitly wants to inspect Django admin, create a preview-only administrator using the Render service Shell after the first successful migration:

```sh
python manage.py createsuperuser
```

Enter a dedicated preview email and a unique password at the prompts. Do not set `DJANGO_SUPERUSER_PASSWORD` in YAML or paste the password into chat. The project has no environment-based superuser bootstrap and no implemented MFA enforcement yet. Therefore restrict access to the preview and do not use this as a production admin account.

## Troubleshooting

| Symptom | Check |
|---|---|
| Build says a Python package is missing | Confirm Root Directory is `orca_webserver` and build installs `requirements.txt`. |
| Settings fail on missing secret/database/host | Set the required Render variables above. Do not set them in `.env.example` with real values. |
| Error says demo backends are forbidden | This preview requires explicit owner-approved `ALLOW_DEMO_BACKENDS=true`; otherwise the production settings intentionally fail closed. Do not bypass this for a live service. |
| `DATABASE_URL` rejected for SSL or pooler | Use the preview project's SSL-enabled session pooler, not transaction mode/port `6543`. Never share the URL. |
| `400 Bad Request` / invalid host | Add the exact hostname to `ALLOWED_HOSTS`; add its HTTPS origin to `CSRF_TRUSTED_ORIGINS`. |
| Static admin styling is missing | Review `collectstatic` output and WhiteNoise static settings; redeploy after correcting the build. |
| `/healthz` fails | Check Gunicorn startup, assigned `$PORT`, and deployment logs. `/healthz` does not require database readiness. |
| `/readyz` returns `503` | Check database availability, SSL, session-pooler URL and network access; do not paste credentials into logs/chat. |

## Before calling this production-ready

These are open gates, not features provided by deployment configuration:

- Implement and test customer finance/device APIs and enforced MFA. The current account login is an initial session-based flow; it does not include email verification, password recovery, MFA, or staff onboarding audit events.
- Approve privacy, legal, data retention, support and incident response.
- Implement real SMS/payment/storage/device adapters with separate security review. ClickPesa has no sandbox; automated tests must use the fake adapter. Never test with real transactions.
- Configure durable object storage before relying on uploads. Current storage is local filesystem and Render service filesystems are not durable storage across deploys/restarts unless a persistent disk is deliberately configured. No Cloudinary adapter exists.
- Configure and exercise database backups and restore; confirm retention, RPO and RTO.
- Verify CSP enforcement, HTTPS/cookies, monitoring, rate limits and production domain ownership.
- Complete PostgreSQL concurrency, Flutter, browser, device and end-to-end checks on synthetic data.

See [`HUMAN_VERIFICATION.md`](HUMAN_VERIFICATION.md), [`SUPABASE_DATA_API_LOCKDOWN.md`](SUPABASE_DATA_API_LOCKDOWN.md), and [`LIVE_SMOKE_TEST.md`](LIVE_SMOKE_TEST.md). Keep production status **NOT READY** until owners close and record these gates.
