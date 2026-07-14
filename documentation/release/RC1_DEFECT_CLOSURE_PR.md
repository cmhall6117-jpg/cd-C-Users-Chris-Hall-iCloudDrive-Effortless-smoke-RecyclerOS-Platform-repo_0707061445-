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

Pending the first push of `codex/rc1-defect-closure`. The draft pull request
must remain a candidate until backend, SQLite, PostgreSQL, Flutter, live core
integration, and composite release-evidence jobs pass on its exact head commit.
