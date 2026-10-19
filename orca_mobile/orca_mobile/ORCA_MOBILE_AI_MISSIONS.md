# ORCA Mobile App: AI Mission Command Prompts

Reusable mission prompts for AI coding agents (Codex, Claude Code and similar) working on the ORCA Flutter mobile app.

**How to use**
1. Paste the **Shared Context** block first, then one **Mission** block. Run one mission at a time.
2. Work on a git branch. Review the diff before merging.
3. Each mission ends with a report. Agents must not claim a command or test passed unless they ran it and saw the result.

---

## Shared Context (paste at the top of every mission)

```text
PROJECT: ORCA mobile app (Flutter). Customers of ORCA, an embedded appliance financing platform in Tanzania, use it to see what they owe on a financed appliance (for example a Smart TV), pay installments, follow ownership progress, see device status (Active or Restricted) and link the TV with an activation code.

CURRENT STATE: a single-file DEMO (lib/main.dart). All data is sample data held in AppState. There are NO real payments, NO backend and NO real TV control. Every success message says it is a demo.

ARCHITECTURE RULES (do not break)
- ORCA Cloud (backend) is the authority for financing, balances and device status. The app only DISPLAYS status and COLLECTS payment intent.
- The app never calculates whether a customer owes money to decide a restriction, never talks to the TV hardware, relay or firmware, and never invents financial rules.
- No secrets, API keys, signing keys or payment credentials in the app source or repo.
- Never show a simulated action as a real one. Success is shown only after the backend confirms.

SCREENS: Home, Pay (keypad + method + review sheet), Device (details + Link TV + demo status switch), History, Link TV (6-digit code).

DESIGN RULES
- Black / near-black dark theme and clean light theme, red accent (#D71921), dotted orca logo (assets/orca-logo-w.png for dark, assets/orca-logo-B.png for light).
- Solid thin lines (no dashed or dotted borders), no dotted backgrounds.
- Numbers in a proper typeface with tabular figures, always with thousands commas (38,000 TZS).
- Very subtle depth shadows only.
- Compact layouts: every screen fits the phone screen without page scrolling (scroll only inside long lists). Keypad keys must never look bigger than the amount display.
- Accessible: labels on all controls, 44 px touch targets where practical, contrast in both themes, respect text scaling.

GENERAL RULES
- Keep the existing technology stack. Add a dependency only if truly necessary and say why.
- Prefer targeted edits to rewrites. Do not delete working code.
- Never commit secrets. Do not deploy, publish or run destructive commands without my approval.
- If something cannot be verified, say so plainly.
```

---

## Mission 1: Configure and run the app

```text
ROLE: Senior Flutter engineer.
OBJECTIVE: Make the ORCA demo app build, run and pass basic tests on this machine.

INPUTS (project root): main.dart, orca-logo-w.png, orca-logo-B.png.

PHASE 1 - DISCOVER: run flutter --version and flutter doctor -v. Read pubspec.yaml, the platform folders and existing tests. Summarise.
PHASE 2 - INSTALL: create branch feat/orca-app. If lib/main.dart already holds app logic, move it to lib/legacy/ and tell me. Copy main.dart to lib/main.dart. Create assets/, move both PNGs in, register them under flutter: assets: in pubspec.yaml. File names are case-sensitive (orca-logo-B.png).
PHASE 3 - CLEAN: flutter pub get, dart format lib test, flutter analyze. Fix every error and warning with the smallest change. Do not redesign.
PHASE 4 - APP IDENTITY: set the display name to ORCA on Android and iOS. Keep the existing application ID / bundle ID. Lock phones to portrait.
PHASE 5 - TESTS: add widget tests for: Home shows "Amount due this month (demo)"; Pay Installment opens Pay; keys 3,8,0,0,0 show 38,000; Review with no amount shows an error and opens no sheet; Cancel adds no transaction; Confirm adds one History row (pump past 900 ms); Link TV rejects <6 digits and accepts 6. Run flutter test.
PHASE 6 - BUILD: flutter build apk --debug. No release signing.
PHASE 7 - RUN: if an emulator or device exists, check all screens in light and dark on a small and a large screen. Report overflow stripes.

FINAL REPORT: files changed; commands run with real results; what could not be verified; steps I must do myself.
SUCCESS: app builds and runs, analyze is clean, tests pass, demo labels intact.
```

---

## Mission 2: UI/UX audit and polish

```text
ROLE: Senior mobile UI/UX engineer and accessibility specialist.
OBJECTIVE: Audit and improve the ORCA app's interface without changing its product behaviour.

PHASE 1 - AUDIT (no changes yet). Inspect lib/ and list real defects with file and line: broken buttons or wrong navigation; text too large, small or clipped; overflow on 320x568, 360x640, 390x844 and tablet sizes; contrast failures in both themes; missing semantics labels; touch targets under 44 px where practical; layout jumps (for example text appearing under the keypad that pushes buttons); money numbers without commas; any dashed or dotted lines.
PHASE 2 - FIX in this order: broken journeys, then compactness (every screen fits without page scrolling), then hierarchy (amount display larger than keypad keys; one clear primary action per screen), then themes, then accessibility.
PHASE 3 - STATES: every data-driven view handles loading, empty, error, offline, disabled, and pending vs confirmed.
PHASE 4 - TABLET: on wide screens keep the content in a centred column (max ~480 px) or a side navigation. Never stretch the keypad.
PHASE 5 - VERIFY: flutter analyze, flutter test, and screenshot or golden tests for Home, Pay, Device, History and Link TV in light and dark. Report anything not tested.

STRICT CHANGE CONTROL: preserve behaviour; targeted edits only; explain non-obvious decisions.
FINAL REPORT: defects found (with locations), fixes made, tests run with real results, remaining issues.
SUCCESS: no overflow at the sizes above, both themes complete, numbers formatted, every control does what it says.
```

---

## Mission 3: Replace demo data with a real backend layer

```text
ROLE: Senior Flutter architect.
OBJECTIVE: Introduce a clean data layer so the app can talk to ORCA Cloud, while keeping the demo mode working.

FIRST ASK ME for: base URL, auth method, and the API contract (or OpenAPI file). Do not invent endpoints. If a contract is missing, write the proposed contract in docs/api-contract.md and stop for approval.

PHASE 1 - DESIGN: define abstract repositories (AuthRepository, AccountRepository, PaymentRepository, DeviceRepository, TvLinkRepository) and a DemoRepository implementation that reproduces today's sample behaviour. Choose the state-management approach already used in the project; add a package only with justification.
PHASE 2 - WIRE: AppState reads from repositories only. Screens never call HTTP directly. All money is stored as integer TZS amounts.
PHASE 3 - PAYMENTS: the app only starts a payment and then shows its status. Every payment request carries an idempotency key so retries cannot double-charge. Show "Pending" until the backend confirms, then "Confirmed". Show success only after authoritative confirmation. Handle failed, cancelled and timed-out payments with plain-language messages and a way to retry.
PHASE 4 - DEVICE STATUS: show Active or Restricted exactly as the backend reports. Poll or subscribe; the app never decides restriction.
PHASE 5 - TV LINK: send the 6-digit code to the backend; show success only when the backend confirms; handle expired, wrong and already-used codes.
PHASE 6 - ERRORS: offline banner, retry with backoff, request timeouts, no crashes on malformed responses.
PHASE 7 - CONFIG: environments (demo / staging / production) via build flavors or --dart-define. No secrets in source.
PHASE 8 - TESTS: unit tests for repositories using fakes; widget tests for loading, error, empty and pending states; test duplicate-tap and retry behaviour.

FINAL REPORT: architecture summary, files changed, tests run with real results, API assumptions, open questions.
SUCCESS: demo mode still works unchanged; real mode works against the agreed contract; no financial logic in the UI.
```

---

## Mission 4: Authentication and account

```text
ROLE: Senior Flutter engineer with mobile security experience.
OBJECTIVE: Add sign-in so each customer sees only their own account.

ASK ME FIRST which sign-in method ORCA uses (for example phone number with one-time code). Do not choose one silently.

REQUIREMENTS
- Store session tokens only in secure storage (Keychain / Keystore), never in plain preferences or logs.
- Short-lived access tokens with refresh; sign out clears everything.
- Handle expired sessions by returning to sign-in without losing the user's place where possible.
- Rate-limit-friendly one-time-code UI (resend timer, clear errors, no account enumeration in messages).
- Screens must be unreachable without a session (route guard).
- Plain-language errors; keyboard and screen-reader friendly; Swahili-ready strings.
- Tests for: signed-out redirect, expired token, wrong code, sign out clears data.

FINAL REPORT: flow description, files changed, tests with real results, security notes, anything unverified.
```

---

## Mission 5: Security and privacy review

```text
ROLE: Mobile application security reviewer.
OBJECTIVE: Review the ORCA app and fix what is safe to fix. Report the rest.

CHECK AND REPORT with file and line references:
- Secrets, keys or tokens in source, assets, logs or build files.
- Insecure storage of tokens or personal data.
- HTTP instead of HTTPS; certificate handling; consider pinning only if I approve.
- Logging of personal or payment data.
- Input validation for amounts, codes and phone numbers (the backend must also validate; the app is not a security boundary).
- Duplicate-submission and replay protection on payments and TV linking.
- Android: cleartext traffic, exported components, backup rules. iOS: ATS settings.
- Screenshots / app-switcher exposure of the amount (offer a privacy setting).
- Dependency audit: flutter pub outdated; flag abandoned or vulnerable packages.

RULES: fix low-risk issues directly; for anything that changes behaviour, propose first. Do not weaken any existing protection.
FINAL REPORT: findings by severity, fixes made, remaining risks, and what only the backend or the hardware team can fix.
```

---

## Mission 6: Test suite and CI

```text
ROLE: Flutter QA engineer.
OBJECTIVE: Build a regression-proof test suite and a CI pipeline.

PHASE 1 - Inventory current tests and coverage (flutter test --coverage).
PHASE 2 - Unit tests: formatting (commas), key handling (leading zeros, max length), validation rules, repository fakes.
PHASE 3 - Widget tests: every screen in loading, empty, error, offline and success states; review sheet cancel and confirm; no double submission when tapping Confirm twice.
PHASE 4 - Golden tests for Home, Pay, Device, History and Link TV in light and dark at 360x640 and 390x844.
PHASE 5 - Integration test of the main journey: open app, pay an installment, see it in History, link a TV.
PHASE 6 - Accessibility checks: semantics labels, tap-target size guideline, text scale 1.5x without overflow.
PHASE 7 - CI (GitHub Actions or the CI I name): flutter pub get, format check, analyze, test, build apk --debug. Cache dependencies.

FINAL REPORT: coverage before and after, tests added, real results, flaky tests, gaps.
SUCCESS: pipeline green; a deliberate regression (for example removing commas) makes a test fail.
```

---

## Mission 7: Swahili and English

```text
ROLE: Flutter localisation engineer.
OBJECTIVE: Support English and Swahili.

- Use Flutter's official localisation (flutter_localizations + ARB files). Extract every user-facing string, including errors and demo notices.
- Provide Swahili translations and mark each one NEEDS NATIVE REVIEW; do not present machine translation as final.
- Keep number format with thousands commas and TZS in both languages.
- Language switch in the header or settings; remember the choice.
- Check that longer Swahili strings do not overflow any screen at 320 px width.
- Tests for both languages on Home and Pay.

FINAL REPORT: strings extracted, translations needing review, overflow findings, tests with real results.
```

---

## Mission 8: Release preparation

```text
ROLE: Mobile release engineer.
OBJECTIVE: Prepare ORCA for internal testing and then store release. Do NOT publish anything without my explicit approval.

PHASE 1 - Versioning and changelog; app icon and splash (use the dotted orca mark); package name review.
PHASE 2 - Signing: explain how to create a release keystore and where to store it; do NOT generate or commit keys. Set up key.properties reading from environment or an ignored file.
PHASE 3 - Builds: flutter build appbundle --release and, on macOS, flutter build ipa. Enable obfuscation and split debug info; keep symbols for crash reports.
PHASE 4 - Crash and performance monitoring: propose options; add one only with my approval.
PHASE 5 - Store checklist: privacy policy URL, data-safety form answers (what is collected and why), screenshots, age rating, support contact, testing instructions with demo or staging credentials.
PHASE 6 - Rollout: internal track, then closed testing, then staged production rollout with a rollback plan.

FINAL REPORT: what is ready, what I must do myself, risks.
```

---

## Mission 9: Offline and recovery behaviour

```text
ROLE: Senior Flutter engineer.
OBJECTIVE: Make the app behave well on weak or missing connections.

- Detect connectivity and show a calm offline banner; never show stale data as fresh. Show "last updated" time.
- Cache the last known account and device status for read-only viewing.
- Payments cannot be started offline; explain why and keep the entered amount.
- Retry with exponential backoff; allow manual retry.
- Preserve form input after any recoverable failure.
- After an app restart mid-payment, check the payment's real status with the backend before showing anything.
- Tests: airplane mode, slow network, timeout, server error, app killed during a pending payment.

FINAL REPORT: behaviours implemented, tests with real results, unresolved cases.
```

---

## Mission 10: Connect the app to the TV and website

```text
ROLE: Product-minded full-stack engineer.
OBJECTIVE: Keep the mobile app, the TV app and the website consistent.

- Use one shared API contract (OpenAPI) as the source of truth for device status, activation codes and payments.
- Mobile Link TV and the TV activation screen must use the same code format (6 digits shown as 3+3) and the same expiry rules.
- Status words must match everywhere: Active, Restricted, Offline.
- Document the pairing sequence: TV requests a code, customer enters it in the app, backend confirms, TV and app both update.
- Colour tokens, wording and number formatting must match across Flutter, the TV web app and the website.
- Produce docs/integration.md with sequence diagrams (text) and a checklist of what each side must implement.

FINAL REPORT: contract, mismatches found, fixes, open questions for the backend and hardware teams.
```

---

## Standard final-report template (append to any mission)

```text
At the end, report exactly:
A. Defects found, with file and line.
B. Changes made and why.
C. What was preserved unchanged.
D. Commands and tests run, with their real results. List anything NOT tested.
E. Risks and remaining work, including anything needing a backend, hardware or my approval.
Do not claim a fix, test or feature works unless you verified it.
```
