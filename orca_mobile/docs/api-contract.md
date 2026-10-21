# ORCA Mobile API Contract Proposal

**Status:** **PROPOSAL ONLY — not approved and not implemented.** The current Django project has no matching product API routes or OpenAPI document. This draft is for backend/product/finance/security review only. The existence of Django domain models does not make any endpoint below operational.

**Example data:** All JSON bodies, names, IDs, dates, amounts, and codes below are synthetic illustrations, not real responses or customer records.

**Purpose:** Give the ORCA Flutter app reliable, customer-scoped access to the information needed for Home, Pay, Device, History, and Link TV. ORCA Cloud remains authoritative for customer identity, account balances, payment status, appliance status, and TV-link outcomes. The app displays server values and submits customer intent; it must not infer financial or device-control decisions.

## 1. Decisions required before production

- **Authentication:** choose ORCA's sign-in method (for example, phone plus one-time code) and token/session lifecycle. The endpoints below assume authenticated requests use `Authorization: Bearer <access_token>`; do not ship until this is agreed.
- **Payment providers:** confirm which rails are supported (for example, M-Pesa, bank transfer, or card), provider initiation/redirect requirements, settlement callbacks, and what “confirmed” means for each provider.
- **Financing policy:** backend/product must define what amounts are accepted, allocation rules, due dates, fees, partial payments, overpayments, reversals, and any status effects. The client must not implement these rules.
- **TV linking:** confirm code expiry, attempt limits, and whether a code is scoped to a customer, appliance, or TV session.
- **Deployment:** provide staging/production base URLs, API owner, support contact, and availability/retention requirements. No credentials belong in the Flutter repository.

## 2. API conventions

- Base path: `/api/v1/` (proposed); HTTPS only outside local development.
- JSON request and response bodies use UTF-8. Money is an integer number of TZS, never a floating-point value. Example: `38000` means TZS 38,000.
- Timestamps are ISO 8601 UTC, e.g. `2026-10-17T10:15:30Z`. Return display dates in a stable machine format and let the client localize them.
- Every response should include a `request_id` (also accepted from a response header) for support and server log correlation.
- Authenticated resources are always scoped to the authenticated customer. Ignore/reject customer IDs supplied by the client for authorization decisions. Return `404` for inaccessible resource IDs where revealing existence would leak another customer's data.
- Use explicit enums and nullable fields. Do not encode status in free-form message text.
- Proposed list pagination uses opaque cursor tokens: `?limit=20&cursor=...`. Return a stable order and `next_cursor`; do not require the app to download a customer's entire history.
- Paths in the endpoint table are complete paths. Any shorter path repeated in a subsection is a suffix relative to `/api/v1`; use the exact table path when implementing or reviewing a request. All JSON bodies shown in this document are illustrative examples, not captured server responses.
- Customer auth is shown as bearer-token auth only to make the proposal concrete. Token issuer, lifetime, refresh, revocation, secure storage, sign-out, recovery and multi-device session behavior are **OPEN**. Do not implement a token lifecycle from this example.
- Use the error envelope in §8 for all proposed endpoints. `request_id` must be generated/validated by the server and must not contain PII. Staff and device authentication are separate contracts and are not specified by this customer API proposal.

## 3. Proposed endpoints

All paths below are proposals, to be reviewed before implementation.

| Method and path | Purpose | Auth |
|---|---|---|
| `GET /api/v1/me` | Customer profile and account identity | Required |
| `GET /api/v1/account/summary` | Home totals, current amount due, next due, and ownership progress | Required |
| `GET /api/v1/appliances` | Appliances financed by the signed-in customer | Required |
| `GET /api/v1/appliances/{appliance_id}` | Appliance details and authoritative status | Required |
| `GET /api/v1/appliances/{appliance_id}/installments` | Backend-provided installment schedule, if customer-facing schedule is approved | Required |
| `GET /api/v1/payment-methods` | Methods currently available to this customer | Required |
| `POST /api/v1/payments` | Create or resume a payment intent | Required; idempotent |
| `GET /api/v1/payments/{payment_id}` | Read authoritative payment state | Required |
| `GET /api/v1/payments` | Paginated payment history | Required |
| `POST /api/v1/tv-links` | Submit a TV activation code for validation/linking | Required; idempotent |
| `GET /api/v1/tv-links/{link_id}` | Read TV-link processing result | Required |

The server may combine summary and appliance reads for performance only if the ownership, freshness, and error semantics remain clear. Do not create a broad unauthenticated endpoint that accepts a user ID.

## 4. Customer and account data

### `GET /me`

Return only the minimum profile data required by the app:

```json
{
  "id": "cus_123",
  "display_name": "Amina",
  "preferred_language": "en",
  "created_at": "2026-01-10T09:00:00Z"
}
```

Do not return full identity documents, payment credentials, or another customer's information to the mobile app unless a separately approved feature requires it.

### `GET /account/summary`

```json
{
  "currency": "TZS",
  "total_financed_amount": 1200000,
  "total_paid_amount": 462000,
  "outstanding_amount": 738000,
  "amount_due": 38000,
  "due_date": "2026-10-28",
  "ownership_progress_percent": 38,
  "last_updated_at": "2026-10-17T10:15:30Z"
}
```

The server must calculate and validate these values from the authoritative ledger/financing records. The client may format integers with thousands separators, but must not recalculate the balance, decide eligibility, infer a restriction, or treat a displayed projection as a server decision. Define the meaning and rounding of ownership progress with product/finance; the example is illustrative only.

A missing account should be represented explicitly (for example, `404` with code `account_not_found`) rather than returning fabricated zero balances.

## 5. Appliance data and status

### Appliance representation

```json
{
  "id": "app_456",
  "display_name": "Hisense 55\" Smart TV",
  "category": "Smart TV",
  "currency": "TZS",
  "purchase_amount": 1200000,
  "paid_amount": 462000,
  "outstanding_amount": 738000,
  "monthly_installment_amount": 100000,
  "next_due_amount": 38000,
  "next_due_date": "2026-10-28",
  "financing_status": "active",
  "device_status": "active",
  "connectivity_status": "online",
  "tv_link_status": "linked",
  "last_updated_at": "2026-10-17T10:15:30Z"
}
```

Suggested enum values:

- `financing_status`: `active`, `completed`, `closed` (confirm exact business states).
- `device_status`: `active`, `restricted`, `offline`, `unknown` (confirm whether `offline` is a device status or connectivity-only; never infer it from network reachability).
- `connectivity_status`: `online`, `offline`, `unknown`.
- `tv_link_status`: `linked`, `not_linked`, `pending`, `unknown`.

Return statuses exactly as the backend determines them, with `last_updated_at`. The Flutter app is read-only for device status. It must never control TV hardware, relays, firmware, or restrictions. Do not provide an app-facing endpoint to toggle a restriction for real accounts.

The installments endpoint, if approved, should return server-calculated rows with stable IDs, due dates, amounts, and statuses such as `upcoming`, `due`, `partially_paid`, `paid`, or `overdue`. Define the allowed states and handling of reschedules/adjustments with product/finance.

## 6. Payment intent and history

### Create payment: `POST /payments`

Request:

```json
{
  "appliance_id": "app_456",
  "amount": 38000,
  "currency": "TZS",
  "payment_method_id": "mpesa"
}
```

Headers:

```http
Authorization: Bearer <access_token>
Idempotency-Key: <random-unique-operation-id>
Content-Type: application/json
```

The app creates one idempotency key per user-confirmed payment attempt and reuses that same key for retries of that attempt. The server must enforce uniqueness scoped to the authenticated customer and operation, persist the original result, and return that result for a duplicate request; do not create a second provider charge. Define key retention and behavior for a key reused with a different request body.

Response example:

```json
{
  "id": "pay_789",
  "status": "pending",
  "amount": 38000,
  "currency": "TZS",
  "payment_method": "mpesa",
  "created_at": "2026-10-17T10:15:30Z",
  "next_action": {
    "type": "none",
    "url": null
  }
}
```

Possible statuses: `pending`, `confirmed`, `failed`, `cancelled`, `expired`, `reversed`. Product/payment owners must confirm the list and transitions. A client request only creates payment intent; it is not proof of payment. Show success and update authoritative balances/history only after the server reports `confirmed`. For asynchronous provider flows, the server must verify provider callbacks and expose status through the payment read endpoint (or an explicitly agreed push mechanism). A client must not be able to mark a payment confirmed.

The backend decides whether the amount and method are valid, how money is allocated, and whether the payment can proceed. Return a clear validation error for rejected amounts or unavailable methods; do not rely on Flutter validation for security or financial correctness.

### Payment methods

`GET /payment-methods` returns only currently usable methods, with stable IDs and display labels; include any required next-action type, but never return secret provider credentials.

### Payment history

`GET /payments?limit=20&cursor=...` returns:

```json
{
  "items": [
    {
      "id": "pay_789",
      "appliance_id": "app_456",
      "type": "installment",
      "amount": 38000,
      "currency": "TZS",
      "status": "confirmed",
      "payment_method": "mpesa",
      "created_at": "2026-10-17T10:15:30Z",
      "confirmed_at": "2026-10-17T10:16:12Z",
      "reference": "••••1234"
    }
  ],
  "next_cursor": null
}
```

Do not expose full account numbers, phone numbers, card numbers, provider secrets, or unnecessary personal data in history. Use server-side pagination with deterministic ordering (for example, `created_at` plus ID).

## 7. TV activation/link

### Submit code: `POST /tv-links`

```json
{
  "appliance_id": "app_456",
  "activation_code": "123456"
}
```

Use an idempotency key for retries. Response:

```json
{
  "id": "link_321",
  "status": "pending",
  "created_at": "2026-10-17T10:15:30Z"
}
```

Possible terminal outcomes should distinguish `linked`, `invalid_code`, `expired_code`, `already_used`, and `failed`, subject to the TV/backend contract. Never echo the activation code in logs, analytics, or response payloads. Apply server-side rate limits and attempt limits; do not reveal whether a code belongs to another customer. The app reports success only after `GET /tv-links/{link_id}` returns the confirmed linked outcome.

## 8. Errors and freshness

Use a stable JSON error shape:

```json
{
  "error": {
    "code": "payment_method_unavailable",
    "message": "This payment method is currently unavailable.",
    "retryable": false,
    "field_errors": {}
  },
  "request_id": "req_abc123"
}
```

Suggested HTTP handling:

- `400` malformed request; `401` missing/expired session; `403` authenticated but action disallowed; `404` not found/inaccessible; `409` idempotency conflict or incompatible current state; `422` business validation; `429` rate limit (include `Retry-After`); `5xx` temporary server/provider failure.
- Keep messages customer-safe and non-enumerating. Do not return stack traces, SQL, provider secrets, or internal risk rules.
- On network/server errors, the app retains entered form data, marks cached information as potentially stale, and offers retry where safe. It must not convert errors into a fake success or silently overwrite local display with guessed balances.

## 9. Security and authorization requirements

- Enforce TLS in staging and production. Never ship tokens, API keys, provider credentials, or signing secrets in the app or public repository.
- Authenticate every customer-data endpoint and authorize every object against the authenticated customer on every request (including payment status, appliance, installment, and TV link IDs).
- Apply least-privilege service credentials, secure token storage on mobile, token expiry/revocation, and an agreed refresh/sign-out flow.
- Validate amounts, currency, appliance ownership, available payment methods, activation codes, and state transitions on the server. Client-side validation is for usability only.
- Rate-limit sign-in/code verification, payment initiation, and TV-link attempts. Add abuse monitoring without logging sensitive values.
- Redact access tokens, activation codes, full phone numbers, payment references, and financial personal data from logs and analytics. Use `request_id` for correlation.
- Use verified payment-provider webhooks; validate signatures and prevent replay. Never trust a client assertion that a provider payment succeeded.

## 10. Reliability and multi-customer scale

These are implementation requirements for review, not a prescribed hosting vendor:

- Keep account/financing records and a payment ledger authoritative and auditable. Write financial state changes transactionally; preserve immutable provider and internal references needed for reconciliation.
- Enforce database constraints for customer ownership, unique idempotency keys, and provider event IDs. Use indexes for customer-scoped lookup and stable history pagination.
- Make provider initiation and webhook processing retry-safe. For work spanning the database and external providers, use durable queued jobs/outbox-style delivery and idempotent consumers; do not hold a database transaction open during a slow provider call.
- Define request timeouts, bounded retries with backoff, health/readiness checks, backup/restore, and alerting for payment backlog, webhook failures, elevated error rates, and reconciliation mismatches.
- Return `last_updated_at` on changing financial/device data. Document freshness expectations and how the client refreshes after payment or TV-link state changes.
- Load-test expected peak concurrent users and payment/status polling. Set pagination and response-size limits. Add per-user and global rate limits to prevent one client from overwhelming the service.
- Track audit events for financial and status changes, with actor/source and timestamps, while excluding secrets and unnecessary personal data.
- Publish an OpenAPI 3 specification from the approved implementation and test compatibility against Flutter-facing response fixtures.

## 11. Flutter integration boundaries

- Add repository interfaces for account summary, appliances, installments, payments, and TV links. Screens should call repositories, not HTTP directly.
- Keep demo mode isolated from live mode. Clearly identify demo data; never mix demo transactions with real server history.
- The backend supplies the authoritative account and device values. The app formats numbers for display, gathers the selected amount/method/code, displays pending states, and refreshes server state after outcomes.
- Use the same enum names and field meanings across Django, OpenAPI, and Flutter models. Unknown enum values must degrade safely to an “Unknown” display state rather than crash.

## 12. Approval checklist

Before production integration, ORCA owners should approve:

- [ ] Authentication/sign-in method, token refresh, revocation, and sign-out behavior.
- [ ] API base URLs, ownership model, and OpenAPI document.
- [ ] Definitions for balances, due amounts, ownership progress, date/time zone, and installment schedule.
- [ ] Payment rails, request/response actions, statuses, webhook confirmation, retries, reversals, and reconciliation rules.
- [ ] TV-link code issuer, expiry, rate limits, and terminal status meanings.
- [ ] Data retention, privacy obligations, support tracing, rate limits, availability target, and peak-load assumptions.
- [ ] User-facing wording and English/Swahili localization requirements.
- [ ] Named API/schema owner; OpenAPI version/release policy; token/session issue, refresh, revocation and recovery lifecycle.
- [ ] Customer/account/appliance cardinality and privacy-reviewed object authorization rules.
- [ ] Shared contract tests and compatibility policy for mobile, Django and any device-facing protocol.

## Implementation status check (21 October 2026)

The inspected Django `config/urls.py` contains `/healthz`, `/readyz`, and `/admin/` only. There are no `/api/v1/` routes, serializers or generated OpenAPI file in this repository. This proposal must remain unimplemented until its open decisions are approved. The domain database foundation in `orca_webserver/apps/domain/` is not an API and does not establish customer or staff authorization.
