# RC1 Core Working Path

## Scope

Branch `codex/rc1-core-working-path` connects the existing Flutter path to the
tenant-scoped FastAPI contracts:

1. Local login and organization/workspace selection.
2. Mission Control and opportunity discovery.
3. Vehicle record creation.
4. Procurement analysis.
5. Pick-list creation and persisted availability.
6. Focus Point start and completion.
7. Inventory intake.

## Integration Design

- `Rc1Gateway` is the client transport boundary.
- `DioRc1Gateway` is the default runtime implementation.
- `FakeRc1Gateway` is injected by widget tests.
- Riverpod retains transient UI state but no longer manufactures API record IDs.
- Every live workflow request carries organization and workspace headers.
- FastAPI allows configurable local browser origins without wildcard credentials.

## Validation

- Backend source compilation: passed locally.
- Backend tests: 17 passed locally in 9.52 seconds on the final local run.
- Flutter SDK: unavailable locally.
- Flutter dependency resolution, analyze, and tests: passed on GitHub Actions PR
  run `29325554779`.
- PostgreSQL and SQLite clean migration checks: passed on the same run.
- Live Flutter-to-FastAPI smoke test: passed in the `core-integration` job on the
  same run.

## Deferred

Durable API persistence, offline SQLite synchronization, live SSO, payments,
marketplace publishing, shipping, and AI credentials remain outside this branch.
