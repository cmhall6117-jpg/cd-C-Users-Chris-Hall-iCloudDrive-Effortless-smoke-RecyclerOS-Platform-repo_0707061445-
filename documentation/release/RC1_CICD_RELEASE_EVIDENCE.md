# RC1 CI/CD Release Evidence

## Auth Baseline

- Branch: `codex/rc1-auth-tenant-rbac`
- Commit: `9bf4490f91b914b05963208355218a863b632977`
- Draft pull request: `#6`
- Pull-request run: `29363414967`
- Push run: `29363344692`
- Result: success

Both runs passed:

- backend
- sqlite-migrations
- postgres-migrations
- flutter
- core-integration

The pull request is open, draft, and mergeable against
`codex/rc1-core-working-path`.

## Composite Gate

The workflow now includes `release-evidence`, which runs after all five required
jobs even when one fails. It writes the exact commit, branch, event, run URL,
and prerequisite results to the GitHub job summary. It succeeds only when every
required result is `success`.

This provides one auditable CI verdict without changing the underlying backend,
database, Flutter, or live-integration gates. Exact-head evidence for the new
job is pending publication of `codex/rc1-cicd-release-evidence`.

## Release Boundary

These results prove buildability, clean database initialization, authenticated
tenant isolation, RBAC, Flutter analysis/tests, and the connected RC1 path. They
do not prove durable API persistence or durable production identity; those gates
remain blocked as `DEF-RC1-007` and `DEF-RC1-010`.
