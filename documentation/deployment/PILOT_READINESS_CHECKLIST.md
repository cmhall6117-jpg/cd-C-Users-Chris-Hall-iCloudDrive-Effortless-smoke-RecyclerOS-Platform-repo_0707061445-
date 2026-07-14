# Pilot Readiness Checklist

## Automated Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Backend compile and tests | Passed locally | 38 passed; 1 PostgreSQL-only test skipped. |
| Liveness and readiness behavior | Passed locally | `test_pilot_runtime.py`. |
| Secret-file configuration | Passed locally | Direct/file conflict and file-read tests. |
| Backup command secret handling | Passed locally | Password is absent from the `pg_dump` command. |
| Restore confirmation controls | Passed locally | Exact database confirmation and name validation tests. |
| Pilot compose validation | Pending CI | `pilot-container` job. |
| Non-root read-only container smoke | Pending CI | `pilot-container` job. |
| Clean PostgreSQL backup/restore rehearsal | Pending CI | `postgres-migrations` job. |
| Flutter and live core path | Passed on baseline | Retained RC1 workflow gates. |

## External Prerequisites

| Prerequisite | Status |
| --- | --- |
| Pilot host selected and hardened | Blocked external |
| DNS and TLS reverse proxy provisioned | Blocked external |
| Real pilot secrets stored and access limited | Blocked external |
| Encrypted off-host backup target and schedule configured | Blocked external |
| Restore owner and maintenance window approved | Blocked external |
| Central logs and readiness alerts routed | Blocked external |
| Pilot users, support owner, and rollback authority approved | Blocked external |

## Decision

The repository may reach deployment-ready status after automated CI evidence.
A data-bearing or remotely accessible pilot remains no-go until every external
prerequisite is assigned, configured, and evidenced.
