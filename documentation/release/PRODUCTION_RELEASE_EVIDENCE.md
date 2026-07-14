# Production Release Evidence

## Candidate

- Branch: `codex/production-launch-preparation`
- Base: `codex/pilot-deployment-readiness`
- Verified implementation commit: `847a1bed5e9a438d3a85758954abdca1400525a6`
- Image digest: not published; external launch blocker

## Repository Evidence

| Gate | Result | Evidence |
| --- | --- | --- |
| Focused production tests | Passed | 13 production and operations tests. |
| Production and workflow YAML parse | Passed | Local PyYAML validation. |
| Python compilation | Passed | API source, production entrypoints, and tools compiled. |
| Full backend suite | Passed locally | 46 passed; 2 PostgreSQL-only tests skipped. |
| SQLite initialization | Passed locally | 10 migrations and tenant enforcement checks. |
| Secret and release artifact ignores | Passed locally | All production secret, env, and release paths are ignored. |
| Release manifest generation | Passed locally | Complete commit, image digest, and 11 migration checksums. |
| PostgreSQL migration ledger and restore | Passed in CI | Push `29372078034`; PR `29372080469`. |
| Production container | Passed in CI | Migration, bootstrap, two workers, headers, release SHA, login. |
| Flutter | Passed in CI | Dependencies, analyzer, tests, and live core path. |
| Composite release evidence | Passed in CI | Both exact-commit trigger paths passed all eight jobs. |

Exact-commit evidence:

- push run `29372078034`
- pull-request run `29372080469`

Both runs completed successfully for
`847a1bed5e9a438d3a85758954abdca1400525a6`.

## Launch Decision

Repository production-preparation gates passed. Production traffic is no-go because the
target infrastructure, published image digest, managed data protection, secrets,
monitoring, support ownership, and business approvals are external blockers.
