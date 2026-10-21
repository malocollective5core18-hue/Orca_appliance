# Mission 02 documentation claim audit

**Status:** Source/documentation comparison completed; runtime claims are limited to recorded command output. **Owner:** engineering reviewer. **Audited:** 21 October 2026. **Branch/baseline:** codex/orca-cloud-foundation at 3f5e4b8.

This samples ten factual claims per document changed in Mission 02, prioritizing claims about source, running behavior, integrations, tests and deployment. VERIFIED means source or dated output supports the stated fact; it does not mean production-ready. UNVERIFIED means evidence is absent or only a proposal exists. Claims that would imply live operation are worded as explicit negative assertions or marked UNVERIFIED.

## Root README.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Three projects occupy separate folders. | orca_mobile/, orca_webserver/, orca_TVapp/ | VERIFIED | None. |
| Mobile is a demo with in-memory state. | orca_mobile/lib/main.dart:127-195 | VERIFIED | None. |
| TV project is a simulator. | orca_TVapp/orca-tv-demo-1.html:97-98,162 | VERIFIED | None. |
| Django product API is absent. | orca_webserver/config/urls.py:6-9 | VERIFIED | None. |
| Mobile entrypoint defaults to lib/main.dart. | orca_mobile/pubspec.yaml:1-34 | VERIFIED | Nested copy identified as different/unselected. |
| Product integration is target-only. | config/urls.py:6-9; API proposal heading | VERIFIED | None. |
| Dashboard is sample-data only. | orca-dashboard-demo-1.html:154-165 | VERIFIED | None. |
| Dashboard stores theme preference in localStorage. | orca-dashboard-demo-1.html:7,239 | VERIFIED | None. |
| Render runtime is Python 3.14.8. | orca_webserver/render.yaml runtime declaration | VERIFIED as proposed config | README states it is proposed, not deployed. |
| Requirements are direct pins, not a generated hash lock. | README.md:72; requirements files | VERIFIED | None. |

## SYSTEM-ARCHITECTURE.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Django project and migrations exist. | orca_webserver/config/urls.py; apps/domain/models.py:25-100; migrations/ | VERIFIED | None. |
| Product API routes are absent. | config/urls.py:6-9 | VERIFIED | None. |
| Mobile entrypoint is lib/main.dart. | pubspec.yaml:1-34; lib/main.dart:127 | VERIFIED | None. |
| Mobile sample values are in-memory. | lib/main.dart:127-149,170-195 | VERIFIED | None. |
| Two widget tests are declared. | test/widget_test.dart:6-19 | VERIFIED | Execution remains unverified. |
| Dashboard builds sample records. | orca-dashboard-demo-1.html:154-165 | VERIFIED | None. |
| Dashboard localStorage use is theme-only. | orca-dashboard-demo-1.html:7,239 | VERIFIED | None. |
| TV simulator starts local state. | orca_TVapp/orca-tv-demo-1.html:97-98 | VERIFIED | None. |
| TV source has local developer controls. | orca-tv-demo-1.html:149-170 | VERIFIED | None. |
| Render/Supabase deployment is live. | No account/deploy evidence; Blueprint is source only | UNVERIFIED | Deployment proof is disclaimed. |

## orca_mobile/README.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Dart SDK constraint is ^3.13.5. | pubspec.yaml:7-8 | VERIFIED | None. |
| video_player is declared. | pubspec.yaml:10-20 | VERIFIED | None. |
| AppState is in-memory. | lib/main.dart:127-149 | VERIFIED | None. |
| Demo payment mutates local totals/history. | lib/main.dart:170-175 | VERIFIED | Demo-only label retained. |
| Local TV link action toggles state. | lib/main.dart:183-185 | VERIFIED | Says no server confirmation. |
| Widget test file contains two tests. | test/widget_test.dart:6-19 | VERIFIED | Execution separately marked UNVERIFIED. |
| Selected asset paths are top-level assets/. | pubspec.yaml:22-27 | VERIFIED | Duplicate assets called out. |
| Platform shells are checked in. | android/, ios/, web/, linux/, macos/, windows/ | VERIFIED as files present | README avoids claiming successful builds. |
| Production authentication is not implemented. | Selected app source has no network/auth client | VERIFIED | None. |
| Flutter build passed. | Flutter unavailable in Mission 02/03 | UNVERIFIED | Added human verification commands/results table. |

## orca_mobile/docs/api-contract.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Document is proposal-only. | Status paragraph; config/urls.py:6-9 | VERIFIED | Proposal warning retained. |
| /api/v1/me is a proposed endpoint, not a live route. | API proposal status; config/urls.py:6-9 | VERIFIED | None. |
| Bearer-token lifecycle is approved. | No customer auth route; ADR-003 draft | UNVERIFIED | Lifecycle explicitly open. |
| Money uses integer TZS in proposal. | Proposal conventions; models.py:93-100 | VERIFIED as draft only | Examples marked synthetic. |
| Cursor pagination is proposed only. | API proposal conventions; no route in config/urls.py:6-9 | VERIFIED | None. |
| Payment intent is explicitly not payment confirmation. | API proposal payment section; factory.py:7-12 | VERIFIED | None. |
| Customer identity response is authoritative. | No customer API implementation | UNVERIFIED | Sample schema labeled illustrative. |
| TV-link endpoint is proposed, not registered. | API proposal endpoint table; config/urls.py:6-9 | VERIFIED | None. |
| Error envelope is an illustrative proposal. | API proposal section 8; status at top | VERIFIED | Examples explicitly labelled synthetic. |
| Staff/device auth is specified here. | Proposal says these are separate contracts | VERIFIED | None. |

## orca_mobile/docs/server-data-migration.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Mobile-to-Django migration is not implemented. | lib/main.dart:127-195; no API client dependency | VERIFIED | Status prominently says future guide. |
| Product API routes are absent. | config/urls.py:6-9 | VERIFIED | None. |
| Selected entrypoint is lib/main.dart. | pubspec.yaml:1-34 | VERIFIED | Duplicate ambiguity corrected. |
| Demo transaction state is local. | lib/main.dart:127-149,170-175 | VERIFIED | None. |
| Reset restores seeded values. | lib/main.dart:188-195 | VERIFIED | None. |
| ImageAsset is metadata; no upload route is registered. | models.py:439-473; config/urls.py:6-9 | VERIFIED | None. |
| Target API names are planning aids only. | Migration guide status; config/urls.py:6-9 | VERIFIED | None. |
| Server balance authority is running. | No ledger API; no live evidence | UNVERIFIED | Kept as target responsibility only. |
| Customer auth/session is not implemented. | config/urls.py:6-9; migration guide | VERIFIED | None. |
| A real mobile data migration ran. | No migration/deployment result recorded | UNVERIFIED | No live migration claim. |

## orca_webserver/README.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Two static marketing variants exist. | index.html and indexb.html | VERIFIED | Canonical page remains open. |
| Dashboard generates samples. | orca-dashboard-demo-1.html:154-165 | VERIFIED | None. |
| localStorage stores theme. | orca-dashboard-demo-1.html:7,239 | VERIFIED | None. |
| Django routes health/readiness/admin. | config/urls.py:6-9 | VERIFIED | None. |
| Django admin is not the staff product. | Only admin.site.urls is registered | VERIFIED | None. |
| Settings read environment directly. | config/settings/base.py:1-5 | VERIFIED | README says Django does not load .env.example. |
| requirements.txt contains direct pins, not a generated lock. | orca_webserver/requirements.txt; README | VERIFIED | None. |
| Nested Render Blueprint is deployed. | render.yaml exists; no owner-account evidence | UNVERIFIED | README calls it a draft. |
| Media upload route is absent. | urls.py:6-9; ImageAsset metadata only | VERIFIED | None. |
| Python static server serves files only. | README local static server instructions | VERIFIED | None. |

## orca_TVapp/README.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| TV source is an HTML simulator. | orca-tv-demo-1.html:97-98 | VERIFIED | None. |
| State is in JavaScript memory. | fresh() and S=fresh() at lines 97-98 | VERIFIED | None. |
| Demo reset is local. | line 162 | VERIFIED | None. |
| TV demo code is local and does not contact a server. | orca-tv-demo-1.html:97,159,165 | VERIFIED | None. |
| TV payment action is a demo. | orca-tv-demo-1.html:130,147 | VERIFIED | None. |
| Cloud reachability label is sample simulator state. | orca-tv-demo-1.html:125-126 | VERIFIED | None. |
| No TV-to-Django request path is present. | simulator source; config/urls.py:6-9 | VERIFIED | None. |
| TV platform is supported. | No installable TV package or platform metadata | UNVERIFIED | Hardware/platform stays open. |
| Browser behavior passed. | No browser result | UNVERIFIED | Human result table added. |
| External font works offline. | Google Fonts URL; offline test absent | UNVERIFIED | README notes external font dependency. |

## docs/decisions/DECISION-REGISTER.md as written in Mission 02

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Register contained 15 rows. | Original file; ADR-001 through ADR-015 in server record | VERIFIED | Migrated into root index. |
| Rows listed owner roles. | Original register row text | VERIFIED | Root index keeps owner roles. |
| Detailed ADRs existed in server file. | orca_webserver/docs/DECISIONS.md contained ADR-001–015 | VERIFIED | History moved to docs/decisions/ADRS.md; server file is a pointer. |
| Customer phone plus SMS was approved. | No separate approval artifact located | UNVERIFIED | Changed canonical status to PROPOSED. |
| Staff TOTP was approved. | No separate approval artifact located | UNVERIFIED | Changed canonical status to PROPOSED. |
| Single-schema partner policy was approved. | Schema exists but does not prove approval | UNVERIFIED | Separated schema implementation from policy status. |
| Polling was approved over MQTT. | ADR text only; no protocol proof | UNVERIFIED | Changed canonical status to PROPOSED. |
| Fake ClickPesa boundary exists in source. | apps/adapters/factory.py:7-12 returns only FakeClickPesa | VERIFIED in source | Safety boundary recorded as proposal/source state, not live provider. |
| S3-compatible provider is not configured. | factory.py:15-20 | VERIFIED | ADR-014 stays PROPOSED. |
| Canonical index requires written approval evidence before ACCEPTED. | docs/decisions/README.md status rules | VERIFIED | None. |

## docs/roadmap.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Roadmap has seven milestones. | docs/roadmap.md sections 1-7 | VERIFIED | None. |
| All Milestone 1 checks passed. | Flutter and browser checks remain absent | UNVERIFIED | Acceptance still requires human evidence. |
| Product API is absent. | config/urls.py:6-9 | VERIFIED | None. |
| Mobile sample data is in memory. | lib/main.dart:127-195 | VERIFIED | None. |
| TV repository contains HTML only. | orca_TVapp tracked files | VERIFIED for current repo | Hardware support remains UNVERIFIED. |
| Payments remain future integration work. | factory.py:7-12; config/urls.py:6-9 | VERIFIED | None. |
| PostgreSQL tests passed. | Prior report skipped 4; no safe local test executed now | UNVERIFIED | Roadmap lists tests as acceptance evidence. |
| Flutter tests passed. | flutter unavailable | UNVERIFIED | Human checklist is pending. |
| Backup restore is unverified and a future gate. | Roadmap milestone 7 | VERIFIED | None. |
| Effort estimates are rough, not commitments. | Roadmap effort note | VERIFIED | None. |

## docs/testing.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Observed Python version is 3.14.4. | python --version output recorded | VERIFIED | Render proposed 3.14.8 remains separate. |
| Pillow is runtime-declared. | requirements.in:6 and requirements.txt:6 | VERIFIED | Missing import is attributed to environment only. |
| Pillow is absent from shared venv. | importlib.metadata and test import output | VERIFIED | None. |
| Django check passes with DEBUG=False. | Recorded exact output in this guide | VERIFIED | Setup explicitly sets a recognized boolean. |
| Migration drift check reports no changes. | Recorded exact output in this guide | VERIFIED | None. |
| Full suite did not complete. | 13 discovered; missing-PIL import error | VERIFIED | None. |
| pytest is unavailable in the shared environment. | command output/package metadata | VERIFIED | None. |
| Local PostgreSQL responds. | pg_isready output | VERIFIED | No tests run without disposability proof. |
| Local database is disposable. | Ownership/identity not established | UNVERIFIED | Compose file is optional, not started. |
| Flutter tests were not run. | flutter command not found | VERIFIED | None. |

## orca_webserver/docs/AI_REVIEW_TRACE.md

| Claim | Evidence | Status | Fix applied |
|---|---|---|---|
| Phase 1/2 commits are 849ef54 and adcc4e1. | git log; trace timeline | VERIFIED | None. |
| Mission 02 baseline is 3f5e4b8. | HEAD and log | VERIFIED | Current Mission 03 report records it. |
| Phase 2 domain models and migration exist. | apps/domain/models.py; migrations 0001/0002 | VERIFIED | None. |
| Routes include health/readiness/admin. | config/urls.py:6-9 | VERIFIED | None. |
| No live payment provider is connected. | factory.py:7-12 | VERIFIED | None. |
| Image upload API is absent. | urls.py:6-9; ImageAsset model only | VERIFIED | None. |
| Historical Phase 2 suite reported 40/4. | PHASE2_REPORT.md:31-40 | VERIFIED as historical output | Kept separate from current rerun. |
| Mission 02 rerun lacked Pillow in environment. | import error; Pillow declaration in requirements | VERIFIED | Clarified declaration exists. |
| Flutter/browser checks are unverified. | Flutter unavailable; no browser suite | VERIFIED | None. |
| Root GitHub Actions/CODEOWNERS are not active. | No tracked root workflow or CODEOWNERS | VERIFIED | None. |

## Status corrections from the audit

The earlier root register copied Accepted labels from old ADR headings without a separate owner-approval artifact. Mission 03 preserves the historical ADR text but makes the current index PROPOSED, OPEN or IMPLEMENTED FOUNDATION. Same-repository placement, phone plus SMS sign-in, staff two-factor, one-schema partner rows, polling before MQTT, fake ClickPesa until live approval and later S3-compatible storage remain PROPOSED pending written confirmation.

No live payment, SMS, cloud storage, hosting, mobile API, TV hardware or client/server integration was verified. See [Mission 02 report](MISSION_02_REPORT.md) and [canonical decision index](../decisions/README.md).
