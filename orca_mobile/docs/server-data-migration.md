# Move ORCA User Data to the Server

**Status:** Implementation guide for the Flutter and Django developers. Pair this with [api-contract.md](api-contract.md), which contains the proposed API endpoints and response schemas. Both documents are drafts until ORCA approves the open product, authentication, and payment decisions.

## Goal

Replace fabricated, customer-specific values in the Flutter app with authenticated, customer-scoped values returned by ORCA Cloud. A signed-in customer should see their own name, accounts, financed appliances, amounts, due dates, device status, payment methods, and payment history. The server is authoritative; the app formats and presents its responses and submits user intent.

This is a migration guide, not permission to invent the backend's financial rules or to label a simulated result as real.

## Current hard-coded data and behavior

The current implementation is concentrated in `lib/main.dart`, especially `AppState`, `_Header`, `HomeTab`, `PayTab`, `DeviceTab`, `HistoryTab`, and `LinkTvPage`.

| Current value or behavior | Current location/pattern | Required live replacement |
|---|---|---|
| Customer name `Amina` | `_Header` | `GET /api/v1/me` `display_name` |
| Appliance name/category `Hisense 55\" Smart TV` / `Smart TV` | `AppState.deviceName`, `AppState.category` | `GET /api/v1/appliances` and appliance detail response |
| Financing constants `total`, `monthly`, `nextDue` | `AppState` static constants | Server account/appliance summary and, if approved, installments endpoint |
| Due `38,000`, paid `462,000`, sample transaction amounts/dates | `AppState.due`, `paid`, `_seed()` | Account summary and paginated server payment history |
| `restricted`, `tvLinked` booleans and locally derived ownership progress | `AppState` and `_DeviceCard` | Exact server status fields and server-calculated progress; no local status inference |
| Payment methods `M-Pesa`, `Bank transfer`, `Card` | `PayTab` dropdown | `GET /api/v1/payment-methods`; display only methods available to this user |
| Payment writes directly into paid/due totals and inserts `Just now` history row | `AppState.pay()` and `PayTab.review()` | Create an idempotent payment intent, show pending, poll/read server result, refresh summary/history only after server confirmation |
| Any six-digit code considered linked after local confirmation | `LinkTvPage.submit()` / `AppState.linkTv()` | Submit code to server; show linked only after authoritative link status confirms it |
| Demo status toggle changes a real-looking device label | `DeviceTab` and `AppState.toggleRestricted()` | Remove from live mode; retain only behind an unmistakable demo-only implementation |
| Reset restores seeded customer state | `AppState.reset()` / History | Demo-only reset; no live-account reset endpoint or local reset of server data |

Review the current source before implementation in case earlier edits have moved these values. The table describes the existing demo patterns, not the desired final architecture.

## Data that should remain local

Do not move every string or asset to Django. Keep non-customer-specific presentation details in the app unless ORCA has a separate content-management requirement:

- Layout, typography, colors, icons, tab labels, and the static ORCA logo and intro video.
- Localized UI labels, accessibility semantics, and formatting of server-provided integer amounts (for example, showing `38000` as `38,000 TZS`).
- Validation that helps a user operate a form (for example, displaying six code digits), while always repeating security, ownership, eligibility, and financial validation on the server.
- A clearly separated demo repository with clearly labeled sample content for development/demo use. Never merge demo fixtures into live API data or show demo success in live mode.

## Target client data flow

```text
Flutter screen
  -> feature state/controller (loading, ready, pending, error)
  -> repository interface
  -> authenticated API client
  -> Django API
  -> authoritative ORCA account/financing/payment/device records
```

Screens should not make HTTP calls directly. Suggested repository responsibilities:

- `AuthRepository`: sign-in/session refresh/sign-out, after ORCA chooses the authentication method.
- `AccountRepository`: current customer profile and account summary.
- `ApplianceRepository` (or `DeviceRepository`): appliance list/details and any approved installment schedule.
- `PaymentRepository`: available payment methods, payment intent creation/status, and paginated history.
- `TvLinkRepository`: activation-code submission and link-status reads.
- `DemoRepository`: existing seeded behavior, demo labels, and demo reset; only injected in explicit demo mode.

Use the state-management approach already selected by the app; do not add a package merely to perform this migration. Keep currency amounts as integer TZS values in Dart models.

## Migration sequence

### 1. Agree on the contract and identity

- Review [api-contract.md](api-contract.md) with Django, product, finance, payment, and device/TV owners.
- Decide sign-in method, account-to-customer ownership, token expiry/refresh, and sign-out behavior before implementing authenticated live access.
- Confirm the meaning and calculation of every amount, due date, installment, progress percentage, status, and payment terminal state.
- Publish the approved contract as OpenAPI and use it as the Flutter/Django integration reference.

### 2. Separate demo from live mode

- Put the current `_seed()` values and simulated `pay`, `toggleRestricted`, `linkTv`, and `reset` actions into `DemoRepository` or an equally explicit demo-only boundary.
- Add an explicit environment/mode configuration such as demo, staging, and production. Select mode with build configuration or `--dart-define`; do not infer it from a failed network request.
- In live mode, never silently fall back to demo data. Show loading, empty, offline/stale, and recoverable error states as appropriate.
- Mark cached responses with freshness metadata. Do not present stale balances/status as current without indicating last update.

### 3. Add typed response models and repositories

- Create typed models for `CustomerProfile`, `AccountSummary`, `Appliance`, `Installment` (if approved), `PaymentMethod`, `Payment`, and `TvLink` based on the approved API contract.
- Parse timestamps and enums defensively. Unknown enum values must not crash the app; show a neutral unknown/unavailable state and record a privacy-safe diagnostic.
- Treat optional fields as optional. Treat missing required financial fields or malformed amounts as a data error, not as zero.
- Keep API base URLs configurable by environment. Do not put credentials, private keys, provider secrets, or production tokens in the app or repository.

### 4. Load and display authoritative reads

- On authenticated app entry, load the profile, account summary, and the customer's appliance list/details.
- Bind Home to server-returned due amount/date, financing summary, status, and recent confirmed/pending payments as the approved response permits.
- Bind Device to the selected appliance's own financing and device status. Never calculate `Restricted` from an amount or payment date.
- Bind History to paginated server records, with stable ordering and clear pending/confirmed/failed/reversed labels.
- Bind payment method options to the server list. Explain an empty/unavailable list and disable the action instead of offering hard-coded unsupported methods.
- Make the selected appliance explicit if a customer can finance more than one. Do not assume the first or only appliance is the one the user intends to view or pay.

### 5. Replace simulated writes with server-confirmed workflows

**Payment:**

1. Collect amount and a server-provided payment method selection.
2. Show a review step; client-side checks are for usability only.
3. Send the request with a newly generated idempotency key. Reuse the same key for retries of that same operation.
4. Display `pending` until Django verifies the payment provider outcome.
5. Refresh summary and history after authoritative confirmation. On failure, cancellation, timeout, or reversal, show the server status and preserve user input where retry is allowed.
6. Prevent duplicate submission in the UI as well as enforcing idempotency on the server.

**TV linking:**

1. Collect exactly the activation code format specified by the approved TV contract.
2. Submit it to Django; do not locally declare arbitrary six-digit codes valid.
3. Display pending while the server/device flow completes.
4. Display success only when the server returns the confirmed linked state. Handle invalid, expired, already-used, rate-limited, and temporary-failure outcomes distinctly without exposing another user's device information.

### 6. Secure the customer boundary

- Attach the authenticated access token through a shared API client; store tokens using platform-secure storage after the auth design is approved.
- Never accept an account/customer identifier from the screen as authorization. Django must scope every read and write to the authenticated principal and independently verify appliance/payment ownership.
- Clear sensitive in-memory/cached account data on sign-out and account change. Avoid logging tokens, activation codes, full phone numbers, payment credentials, or full provider references.
- Handle `401` through the agreed refresh/sign-out flow; do not retry an unsafe payment with a new idempotency key.

### 7. Test real behavior

Keep demo tests, then add tests around the server-backed boundary:

- Model parsing for integer TZS values, timestamps, null/unknown statuses, and malformed responses.
- Repository tests using fakes for success, empty results, pagination, timeout, offline, `401`, `429`, and server errors.
- Widget tests showing loading/error/offline/pending/confirmed states and ensuring server values reach the correct user's screens.
- Payment tests that retry with the same idempotency key, reject duplicate taps, and do not update balances/history before confirmation.
- TV-link tests that reject short input locally and only show linked after server confirmation.
- Authorization tests on Django ensuring one customer cannot read another customer's account, appliance, payment, or link by changing an ID.
- Ensure no test depends on real payment credentials or production customer data.

## Completion criteria

- No customer-specific production data is initialized from constants, seeded fixtures, or display-only defaults.
- Live profile, amounts, dates, appliances, statuses, payment methods, and history come from authenticated Django responses.
- Demo data and demo write behavior exist only in explicit demo mode and remain visibly identified as demo.
- The client does not determine balances, payment confirmation, eligibility, restrictions, or TV-link success.
- Server authorization is customer-scoped; payment and link mutations are retry-safe; sensitive data is not logged.
- Loading, empty, stale/offline, pending, error, and confirmed states are tested.
- Flutter and Django agree on an approved, versioned OpenAPI contract; integration tests cover the critical customer journeys.

## Open questions for ORCA owners

- Which sign-in/authentication and token lifecycle does ORCA use?
- Can a customer have multiple accounts, appliances, or financing agreements? How should the app let the user select among them?
- What precisely constitutes amount due, outstanding amount, installment allocation, ownership progress, and payment confirmation?
- Which providers/methods will be supported, and which outcomes require asynchronous confirmation?
- Who issues TV activation codes, what is their expiry/attempt policy, and what exact status confirms a link?
- What freshness, offline access, privacy retention, language, uptime, and expected concurrent-user requirements should the service meet?
