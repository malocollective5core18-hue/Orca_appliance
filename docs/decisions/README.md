# ORCA decision index

**Status:** canonical index; no item below is marked ACCEPTED without separate owner approval evidence. **Owner:** decision owners listed per item. **Last reviewed:** 21 October 2026. **Baseline:** codex/orca-cloud-foundation at 3f5e4b8.

The detailed ADR history is in [ADRS.md](ADRS.md). Status describes the current decision state, separately from whether some foundation code exists.

| ID | Title | Status | Owner role | Date | Record |
|---|---|---|---|---|---|
| ADR-001 | Backend location and repository scope | PROPOSED | Product/engineering; platform | 20 Oct 2026 | [Details](ADRS.md#adr-001--server-location-and-repository-scope) |
| ADR-002 | Payment provider and safe development mode | PROPOSED | Finance/payment; security | 20 Oct 2026 | [Details](ADRS.md#adr-002--payment-provider-safety) |
| ADR-003 | Customer, staff and device identity | PROPOSED | Security; product/support | 20 Oct 2026 | [Details](ADRS.md#adr-003--identity-methods) |
| ADR-004 | Partner tenancy | PROPOSED; schema foundation exists | Product/finance; backend/security | 20 Oct 2026 | [Details](ADRS.md#adr-004--partner-tenancy) |
| ADR-005 | Ledger and restriction policy | PROPOSED | Finance/product; compliance | 20 Oct 2026 | [Details](ADRS.md#adr-005--ledger-and-restrictions) |
| ADR-006 | TV identity and pairing | PROPOSED; hardware input needed | Hardware/embedded; backend/security | 20 Oct 2026 | [Details](ADRS.md#adr-006--tv-identity-and-pairing) |
| ADR-007 | Device transport | PROPOSED | Hardware/embedded; platform/security | 20 Oct 2026 | [Details](ADRS.md#adr-007--device-transport) |
| ADR-008 | SMS vendor | OPEN | Product/support; procurement/security | 20 Oct 2026 | [Details](ADRS.md#adr-008--sms-vendor) |
| ADR-009 | Hosting and database environments | PROPOSED; hosted proof UNVERIFIED | Platform/operations; finance/security | 20 Oct 2026 | [Details](ADRS.md#adr-009--hosting-and-database-environments) |
| ADR-010 | Health checks and monitoring | Health endpoints IMPLEMENTED; monitoring decision OPEN | Platform/operations; security | 20 Oct 2026 | [Details](ADRS.md#adr-010--health-checks-and-monitoring) |
| ADR-011 | Privacy and legal gates | PROPOSED; legal approval OPEN | Privacy/legal; security | 20 Oct 2026 | [Details](ADRS.md#adr-011--privacy-and-legal-gates) |
| ADR-012 | Reference repositories | PROPOSED | Engineering; security/licensing | 20 Oct 2026 | [Details](ADRS.md#adr-012--reference-repositories) |
| ADR-013 | Offline ports and demo mode | IMPLEMENTED FOUNDATION | Backend; platform/security | 21 Oct 2026 | [Details](ADRS.md#adr-013--offline-ports-and-demo-mode) |
| ADR-014 | Product image visibility and object storage | PROPOSED; owner approval OPEN | Product/content; security/privacy/platform | 21 Oct 2026 | [Details](ADRS.md#adr-014--product-image-visibility-and-object-storage) |
| ADR-015 | Domain records and lifecycle | IMPLEMENTED FOUNDATION; production API OPEN | Backend; finance/security | 21 Oct 2026 | [Details](ADRS.md#adr-015--domain-records-and-lifecycle) |

## Status rules

- PROPOSED means an option is documented but not explicitly approved.
- IMPLEMENTED FOUNDATION means repository source implements part of the behavior; it does not mean production operation is proven.
- OPEN means an owner choice or approval is still required.
- UNVERIFIED means evidence is missing.
- BLOCKED means a required decision, dependency, or external proof is missing.

Owner roles, not inferred individual approvers, are listed above. Record written approval evidence and date before changing a status to ACCEPTED. A prior ADR heading alone is not approval evidence.

DECISION-REGISTER.md and orca_webserver/docs/DECISIONS.md are pointers to this canonical index and its detailed records.
