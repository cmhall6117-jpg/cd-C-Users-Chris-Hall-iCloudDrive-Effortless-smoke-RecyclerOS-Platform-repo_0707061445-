# RC1 Defect Closure

## Summary

- add PostgreSQL workflow persistence for the existing RC1 path
- add durable PostgreSQL identities, memberships, sessions, revocation, login throttling, and auth audit records
- fail closed when production mode lacks durable database configuration
- verify workflow and auth state across fresh app instances in PostgreSQL CI
- upgrade official GitHub Actions to Node 24 major versions

## Scope

This closes existing RC1 durability and CI defects without activating another
vertical slice. Live SSO, password recovery, refresh tokens, payment,
marketplace, shipping, and AI credentials remain deferred behind interfaces and
secret references.

## Local Verification

- backend compile: passed
- backend tests: 28 passed, 1 PostgreSQL-only test skipped
- SQLite clean initialization: passed all 10 migrations and tenant checks
- `git diff --check`: passed

## CI Verification

At commit `7beea835073e42e8f07b90afbf1c4687e972d734`, push run
`29366652838` and pull-request run `29366685297` passed:

- backend compile and automated tests
- SQLite clean initialization and tenant checks
- all 11 PostgreSQL migrations plus durable restart coverage
- Flutter dependency, analyzer, and test gates
- authenticated live Flutter-to-FastAPI integration
- composite release-evidence gate

All check runs reported zero annotations after the Node 24 action upgrades.
