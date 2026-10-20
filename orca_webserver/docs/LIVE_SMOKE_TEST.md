# ClickPesa live smoke test — human only, deferred

**Do not run in Phase 1.** ClickPesa has no sandbox: API calls are live and may move funds. No request
or credential was used while writing this procedure. Official docs were checked 20 October 2026;
recheck them and obtain the owner's written approval before use.

## Preconditions

- Owner has completed KYC, created the ClickPesa application, and stored credentials only in the
  approved secret manager.
- Owner explicitly approves the exact date, environment, test amount, team-owned phone, and caller.
- The owner confirms collection method, wallet availability, fees, minimum amount, and whether the
  provider permits the selected test. These values remain **UNVERIFIED** until preview/dashboard
  confirmation.
- `PAYMENTS_LIVE_ENABLED` remains false outside the exact approved smoke-test window. Do not enable
  it for CI or general staging traffic.
- Use a team-owned phone and a real staff-controlled wallet; never use customer funds or a customer
  account.

## Human procedure after a later payment phase exists

1. Verify the official current API host, auth headers, token lifetime, preview and initiation schema.
2. Generate one access token and reuse it until shortly before expiry. Refresh after one 401 only;
   never generate a token for every request. Pre-KYC docs state 100 API calls/day including token
   generation and TZS 100,000 cumulative; do not treat either cap as a testing allowance.
3. Call the documented fee/availability preview first. Do not initiate unless the phone, amount,
   reference, available wallet, fee and amount due all match the written approval.
4. Initiate exactly one smallest allowed USSD Push transaction to the team-owned phone. Do not use
   Hosted Checkout or BillPay without separate approval.
5. Confirm the result server-to-server using the payment status query. A browser/app return or
   handset screenshot alone is not proof. Preserve the distinction between received (`SUCCESS`) and
   settled (`SETTLED`) until finance approves ledger policy.
6. Record date/time, environment, API call count, non-secret order reference, approved amount,
   redacted status and operator in the owner's secure record. Do not put token, API key, phone,
   account, or raw payment payload in this repository or logs.
7. Reconcile the provider result and finance record. Stop on mismatch, timeout, duplicate, unknown
   status, or unexpected fee; notify the owner and do not retry blindly.

## Approval record template

```text
Approval ID:
Approved by:
Date/window:
Environment:
Team-owned phone identifier (masked in shared notes):
Maximum calls:
Maximum amount:
Allowed method:
Expected fee/status:
Operator:
Result / reconciliation reference:
```
