# ORCA Mobile

Flutter customer-app prototype for the ORCA appliance-financing family. This project is currently an explicitly labeled **demo**; it is not connected to a live account, payment provider, ORCA Cloud API, or TV device.

## Role in the ORCA family

The production mobile app is the customer's authenticated client. It should read customer-scoped account/appliance/payment/link state from the central ORCA Cloud service and submit customer intent (such as a payment request or TV activation code). ORCA Cloud must remain authoritative for identity, balances, payment confirmation, appliance state, and TV linking. The app must not communicate directly with a TV or payment provider to make an authoritative change.

See the repository-level [system architecture](../SYSTEM-ARCHITECTURE.md) for target message flows, roles, security boundaries, and integration gates.

## Current implementation

- Flutter/Dart project; `pubspec.yaml` uses Dart SDK `^3.13.5`, Flutter, `cupertino_icons`, and `video_player`.
- Build entry point: `lib/main.dart` (`flutter run` from this directory).
- Main app tabs: Home, Pay, Device, History, and Link TV, with an intro flow.
- `AppState` in `lib/main.dart` owns demo values in memory: example customer/device, TZS amounts, sample history, simulated payment, simulated restriction, simulated TV link, and reset.
- UI messages say demo/simulation; no real payment moves and no actual device is controlled.
- Branding assets are in `assets/`; Flutter platform shells exist for Android, iOS, macOS, Windows, Linux, and web.
- `test/widget_test.dart` is the package test location. The current test's actual coverage/result is **UNVERIFIED** here.
- `orca_mobile/main.dart` is a separate older/different copy of the entrypoint. It is not selected by `pubspec.yaml`; use `lib/main.dart` unless the team formally chooses and merges that duplicate.

## Integration state and source of truth

`docs/api-contract.md` describes **proposed** `/api/v1/` customer endpoints. Its status is Draft for review, not an approved deployed contract. `docs/server-data-migration.md` gives the migration path away from hard-coded local values. No HTTP client or API/auth integration is configured in `pubspec.yaml` today.

Do not implement calls from screens until backend/product owners approve the base URL, authentication/token lifecycle, schema, payment rules, TV-code rules, and staging environment. Once approved, keep HTTP behind typed API/repository layers, with explicit demo and live implementations. Live mode must never fall back to seeded demo data after an error.

## Intended responsibilities

1. Authenticate a customer through the approved ORCA Cloud identity flow.
2. Fetch only that customer's profile, account summary, appliances, payment methods, payments, and TV-link state.
3. Display integer TZS amounts and server-provided statuses; format them for the selected locale without recalculating financial state.
4. Submit payment intent with a stable idempotency key; show pending until the server confirms the gateway outcome.
5. Submit the TV code to ORCA Cloud; report linked only after the server confirms it.
6. Show loading, empty, stale/offline, pending, and recoverable-error states without fabricating success.

## Local development

From this folder, use the Flutter SDK compatible with the Dart constraint in `pubspec.yaml`:

```sh
flutter pub get
flutter analyze
flutter test
flutter run
```

These commands require an installed Flutter SDK and package access. They are instructions; passing results have not been asserted by this document.

Never put production tokens, API keys, provider credentials, signing keys, or database URLs in Dart source, assets, `--dart-define` values committed to the repository, screenshots, or logs. Configure environment-specific non-secret API origins at build/run time after the API owner provides them.

## Coordination

Coordinate account fields, status enums, pagination, timestamps, auth, idempotency, payment transitions, code expiry, and errors with the backend. Coordinate activation copy and state transitions with the TV/device team. Keep API examples illustrative until the backend publishes an approved OpenAPI contract.
