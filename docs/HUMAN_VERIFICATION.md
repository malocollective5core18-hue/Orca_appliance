# ORCA human verification record

**Status:** BLOCKED pending tools owned by a human developer. **Owner:** mobile and QA leads. **Last checked:** 21 October 2026. **Baseline:** branch codex/orca-cloud-foundation at 3f5e4b8.

These checks must run from the project folder shown. Use sample data only. Do not connect to production services, enter customer data, or use live payment credentials.

## Flutter mobile

From the repository root:

~~~sh
cd orca_mobile
flutter --version
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
~~~

Expected outcomes: compatible Flutter/Dart version is reported; dependencies resolve; analyzer and widget tests exit zero; the debug APK builds. A successful build proves compilation only, not real device behavior or API integration.

| Date | OS | Flutter/Dart versions | Command | Exit/result | Failure summary |
|---|---|---|---|---|---|
| | | | | | |

## Browser-only pages and TV simulator

Serve each folder and open the named paths in a current desktop browser. Do not enter real customer information.

~~~sh
cd orca_webserver
python3 -m http.server 8000
~~~

Open /index.html, /indexb.html, and /orca-dashboard-demo-1.html at http://127.0.0.1:8000/.

~~~sh
cd orca_TVapp
python3 -m http.server 8001
~~~

Open /orca-tv-demo-1.html at http://127.0.0.1:8001/.

Expected outcomes: each page loads its local assets; the dashboard and TV controls update only demo state; reload resets the TV simulator. Record console errors and viewport. This does not verify Django, network integration, hosted content, or physical TV behavior.

| Date | Browser/version | Page | Viewport | Expected behavior | Result | Console/network notes |
|---|---|---|---|---|---|---|
| | | | | | | |

## Django/PostgreSQL checks

Follow [testing.md](testing.md). Run PostgreSQL checks only against the disposable local database defined by [dev/docker-compose.postgres.yml](dev/docker-compose.postgres.yml). Verify DATABASE_URL points to localhost port 55432 before tests. Never paste its value into a report.

| Date | Python/PostgreSQL versions | Command | Result/counts | Database confirmed disposable? | Notes |
|---|---|---|---|---|---|
| | | | | | |

Return completed tables and sanitized failure messages to the repository owner. Do not include environment values, credentials, tokens, personal data, or database URLs.
