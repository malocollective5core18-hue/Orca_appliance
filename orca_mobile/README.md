# ORCA Mobile

ORCA Mobile is the Flutter customer-app prototype for the ORCA appliance-financing family. The checked-in app is **demo-only**: it uses seeded in-memory data and simulated payment, device-status, and TV-link actions. It is not connected to ORCA Cloud, a payment provider, or a physical TV.

## Verified project configuration

- Package: `orca_mobile`; `pubspec.yaml` requires Dart SDK `^3.13.5` and includes Flutter, `cupertino_icons`, `video_player`, Flutter test/lints, and launcher-icon tooling.
- Lock: `pubspec.lock` is committed. It records package versions but is not a guarantee that the current local SDK has been tested.
- Flutter entry point: `lib/main.dart`, selected by the normal Flutter package layout. `orca_mobile/main.dart` is a separate older/different copy and is **not selected** by `pubspec.yaml`. Do not delete or synchronize it casually.
- Assets referenced by the selected app: `assets/orca-logo-w.png`, `assets/orca-logo-B.png`, and `assets/orca-intro.mp4`. A second set of similarly named files exists in `orca_mobile/`; those are not the pubspec asset paths.
- Platform shells are checked in for Android, iOS, web, Windows, macOS, and Linux. Their presence does not prove builds or device testing passed.
- Widget test file: `test/widget_test.dart`. It checks a demo home amount/action and navigation to the pay screen. Test execution is **UNVERIFIED** in the Mission 02 environment because Flutter was unavailable.

## Current screens and data behavior

`lib/main.dart` contains the intro flow and Home, Pay, Device, History, and Link TV screens. `AppState` stores the sample customer/device, TZS amounts, sample transaction history, draft payment, simulated restriction state, simulated TV link, and reset behavior in memory. Restarting the app restores sample defaults; this is not persistent customer storage.

The pay flow changes local totals/history and shows a demo confirmation. The device screen includes demo restriction/status controls. The link screen accepts any six-digit code in demo and marks the local app state linked. None of these actions makes a payment, contacts a server, or controls hardware. Keep demo labels and sample data unmistakable.

## Intended role in the ORCA family

The production app should authenticate a customer to ORCA Cloud, read only that customer's approved profile/appliance/finance data, submit payment or linking intent, and display server-confirmed results. ORCA Cloud must own identity, authorization, balances, payment confirmation, device status, and the result of TV linking. The app must not decide that an account is overdue or a payment succeeded.

The API contract in [`docs/api-contract.md`](docs/api-contract.md) is a proposal. The server-data migration guide is [`docs/server-data-migration.md`](docs/server-data-migration.md). There is no matching product API in `orca_webserver/config/urls.py`; only health/readiness and Django admin routes are currently registered.

## Local development

Install a Flutter SDK whose bundled Dart version satisfies `^3.13.5`, then run from this directory:

```sh
flutter --version
flutter pub get
flutter analyze
flutter test
flutter run
```

These are developer commands, not claims of passing results. Record Flutter/Dart versions and full command output when checking in results. For a web build, use `flutter run -d chrome` only after Chrome and Flutter web support are available; no build result is asserted here.

## Security and integration rules

- Never commit production tokens, API keys, payment credentials, signing keys, database URLs, customer exports, or private activation codes.
- Do not put credentials in assets, source constants, screenshots, logs, or committed `--dart-define` values.
- Do not call a payment provider directly from the Flutter app. The server must create intent and confirm the outcome.
- Do not declare a TV linked merely because a six-digit value was entered. Wait for an approved server contract and server confirmation.
- In future live mode, network failure must never fall back silently to seeded demo state. Demo and live repositories must be isolated and visibly identified.
- Coordinate field names, enums, timestamps, pagination, integer TZS amounts, errors, auth, idempotency and compatibility changes with the API owner before implementing HTTP calls.

## Limitations and next steps

- Authentication, secure session storage, API client, repository abstraction, server-backed data, offline cache, and customer authorization are not implemented.
- No localization selection or production English/Swahili review has been verified in this prototype.
- Supported target platform/device performance and intro-video playback on physical devices are **UNVERIFIED**.
- First run Flutter analysis/tests, then resolve product and security decisions. Implement the approved contract behind typed models and repositories only after backend routes and contract tests exist.

See the root [`SYSTEM-ARCHITECTURE.md`](../SYSTEM-ARCHITECTURE.md), [`docs/testing.md`](../docs/testing.md), and [`docs/roadmap.md`](../docs/roadmap.md) for cross-project boundaries and next gates.
