# ORCA evidence-based roadmap

No delivery dates are promised. Move a milestone only when its acceptance evidence is recorded in the repository and the responsible owners approve dependent decisions.

## 1. Repository and documentation baseline

**Deliverables:** Root developer README; reconciled current/target architecture; mobile/server/TV guides; decision register; testing guide; this roadmap; AI review trace.

**Dependencies:** Read access to all project folders; verified current branch and commit.

**Acceptance:** New developer can identify each entry point and run instructions, tell demo from implemented source, locate every open decision, and see exact validation limits. Documentation links resolve; no source files change in this milestone.

**Blockers:** Flutter SDK absence limits verification of mobile commands; mobile/TV product purpose still requires owner confirmation.

## 2. Demo behavior and test stabilization

**Deliverables:** Run and review mobile widget tests/analyzer; manually review mobile, dashboard and TV demos at intended screen sizes; identify demo-only controls and copy; add tests only after source owners approve test scope.

**Dependencies:** Flutter SDK and pub.dev access; browser/device availability; owner confirmation of intended demo flows.

**Acceptance:** Commands and device/browser versions recorded; failures triaged; demo labels visible; source defects are separately approved before changing code.

**Blockers:** Flutter/Dart unavailable in current review environment. TV, mobile and dashboard have no established browser/device automation suite.

## 3. Approve product, finance, identity and device decisions

**Deliverables:** Close the relevant entries in [`docs/decisions/README.md`](decisions/README.md), including customer/staff/device identity, partner/customer cardinality, ledger semantics, payment callbacks, activation, device transport, staff roles, privacy and support recovery.

**Dependencies:** Product, finance, security/privacy/legal, hardware/embedded, operations and support owners.

**Acceptance:** Written decision records include owner, date, selected option, rejected alternatives, evidence, consequences and test cases. No unresolved financial or device-control rule is inferred from a demo.

**Blockers:** Several owners, vendor details, hardware facts, legal approvals and operating requirements are not present in the repository.

## 4. Approve API and data contracts

**Deliverables:** Versioned OpenAPI for customer/staff JSON routes and a separate device protocol; stable identity, errors, enums, integer TZS, timestamps, pagination, idempotency, freshness and compatibility rules; generated/validated client models and fixtures.

**Dependencies:** Milestone 3 and named contract owners across Django, Flutter and TV.

**Acceptance:** Server and clients pass shared contract tests; security review approves auth and object scope; staging migration/rollout compatibility is documented.

**Blockers:** Existing mobile API document is a proposal; Django has no product API routes; TV protocol is undecided.

## 5. Build backend and secure integration foundation

**Deliverables:** Approved Django APIs, customer/staff authentication and authorization, partner scoping, finance ledger, durable payment integration boundary, webhook verification/reconciliation, device provisioning and audited operations.

**Dependencies:** Approved contracts, policy decisions, PostgreSQL test environment, generated dependency locks, active CI, and integration credentials in a controlled secret manager.

**Acceptance:** Migrations and PostgreSQL concurrency tests pass; no direct DB client access from app/browser; audit and idempotency invariants hold; fake adapters pass CI; staging-only integrations have rollback plans.

**Blockers:** Current Django code is a model/service foundation only. No production auth, product API, provider, SMS, storage, background worker, or device transport exists.

## 6. Integrate mobile and TV; run end-to-end validation

**Deliverables:** Replace mobile fake repository only after API approval; implement device agent for approved target hardware; use server-confirmed payment/link/device results; test stale/offline/retry/unknown states and account recovery.

**Dependencies:** Milestones 4–5; supported TV hardware and secure provisioning; staging accounts and test fixtures.

**Acceptance:** Cross-client contract suite passes for supported app/server/device versions; synthetic end-to-end journeys include install/application, payment pending/confirmed/failure, pairing, reconnect, revocation and support recovery.

**Blockers:** Mobile app currently owns all sample state in memory; TV is HTML only; no hardware or API connection exists.

## 7. Operational, security and production-readiness review

**Deliverables:** Production threat model, privacy/legal approval, monitoring and incident ownership, rate limits, backup/restore proof, RPO/RTO, capacity/latency, cost plan, migration/rollback runbooks, dependency and secret scans, accessibility and support processes.

**Dependencies:** Stable staging system and completed end-to-end tests; named legal, security, operations and support owners.

**Acceptance:** Owners sign evidence pack; restore drill and incident exercise pass; no critical security findings remain; production release and rollback are explicitly approved.

**Blockers:** Actual Render/Supabase resources, budget, backups, legal review, alerting, recovery owners and production tests are **UNVERIFIED**.
