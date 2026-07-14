# RC1 Flutter Baseline

## Scope

Branch: `codex/rc1-flutter-baseline`

Parent: `codex/rc1-backend-baseline`

The Flutter baseline connects the existing primary-path screens into one local
workflow:

1. Sign in.
2. Select organization workspace.
3. Open Mission Control.
4. Create an opportunity.
5. Create its vehicle record.
6. Review procurement scenarios.
7. Add the vehicle to the pick list and confirm availability.
8. Complete a focus-point session and select harvested parts.
9. Create an inventory item.

## Implementation

- Added one Riverpod workflow state for active RC1 records.
- Added the shared `recycleros_domain` package as an app dependency.
- Added the missing vehicle relationship to `PickListItem`.
- Replaced hard-coded route targets with typed path helpers and live parameters.
- Rebuilt all primary-path screens with validation, empty states, disabled states,
  and success feedback.
- Added a restrained operational theme and responsive page frame.
- Removed static demo responses and damaged text encoding from active screens.
- Added a mobile-viewport widget test for the full RC1 path.

## Validation Status

Local Flutter execution is blocked because neither `flutter` nor `dart` is
available on the workstation executable path. Current-branch GitHub Actions
evidence is required before this baseline can pass its build gate.

## Known Limitations

- Authentication remains local; live SSO is out of RC1 scope.
- Workflow records remain process-local in Flutter.
- Backend API transport and offline SQLite synchronization are separate follow-up
  integrations.
