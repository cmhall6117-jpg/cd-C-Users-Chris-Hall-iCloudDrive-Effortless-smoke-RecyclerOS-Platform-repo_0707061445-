# Connect RC1 Core Working Path

## What Changed

- Connected Flutter opportunity, vehicle, procurement, pick-list, Focus Point,
  and inventory transitions to the tenant-scoped FastAPI API through Dio.
- Added an injectable `Rc1Gateway` and deterministic fake for widget tests.
- Removed client-side manufacturing of API record identifiers.
- Added persisted pick-list availability with tenant-isolation coverage.
- Added configurable local CORS handling and preflight tests.
- Expanded the full Flutter workflow test to verify tenant context on all eight
  gateway operations.
- Added a CI smoke test that starts FastAPI and drives the live Dio gateway
  through the complete core path.
- Enabled RC1 GitHub Actions on all `codex/rc1-*` branch pushes.

## Validation

- `python -m compileall services/api/src`: passed locally.
- `pytest -q services/api/tests`: 17 passed locally in 9.03 seconds.
- `flutter pub get`: pending GitHub Actions.
- `flutter analyze`: pending GitHub Actions.
- `flutter test`: pending GitHub Actions.
- SQLite and PostgreSQL clean migration checks: pending current-branch CI.

## Known Limitations

- The backend store remains process-local and is not durable across restarts.
- Local Flutter validation is blocked because the workstation has no Flutter SDK.
- Login and workspace selection remain local; live SSO is intentionally deferred.
- Offline SQLite synchronization is not connected to the gateway in this branch.

## Base Branch

`codex/rc1-flutter-baseline`
