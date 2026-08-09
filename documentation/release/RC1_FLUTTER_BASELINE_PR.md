# Establish RC1 Flutter Baseline

## What Changed

- Connected login, workspace selection, Mission Control, opportunity, vehicle,
  procurement, pick list, focus point, and inventory intake through one Riverpod
  workflow state.
- Replaced fixed demo navigation with typed routes and live record identifiers.
- Wired the Flutter app to the shared RecyclerOS domain package.
- Added real form validation, operational controls, empty states, disabled states,
  and success feedback.
- Added a complete mobile-viewport widget test for the primary RC1 path.
- Repaired the active-screen text encoding defects.

## Why

The integrated Flutter scaffold exposed the required routes, but screens did not
share state, route parameters were ignored, and most controls had no behavior.
This change establishes the first testable local user journey without enabling
deferred SSO, payment, marketplace, shipping, or AI integrations.

## Developer Impact

Screens consume `rc1WorkflowProvider`, route construction uses `AppPaths`, and
the app imports canonical models from `recycleros_domain`. API transport can be
introduced behind the workflow controller without rebuilding the screens.

## Validation

- Local source and diff review: passed.
- Local Flutter SDK: unavailable.
- `flutter pub get`, `flutter analyze`, and `flutter test`: passed on GitHub Actions run `29323035764`.
- Backend, SQLite migration, and PostgreSQL migration jobs: passed on the same run.

## Known Limitations

State is process-local and does not yet call the RC1 FastAPI backend or persist to
offline SQLite.
