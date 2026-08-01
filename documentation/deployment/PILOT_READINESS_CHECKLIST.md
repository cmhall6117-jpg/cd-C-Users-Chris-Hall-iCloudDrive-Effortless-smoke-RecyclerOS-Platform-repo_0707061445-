# Pilot Readiness Checklist

## Automated Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Backend compile and tests | Passed locally | 38 passed; 1 PostgreSQL-only test skipped. |
| Liveness and readiness behavior | Passed locally | `test_pilot_runtime.py`. |
| Secret-file configuration | Passed locally | Direct/file conflict and file-read tests. |
| Backup command secret handling | Passed locally | Password is absent from the `pg_dump` command. |
| Restore confirmation controls | Passed locally | Exact database confirmation and name validation tests. |
| Pilot compose validation | Passed in CI | Runs `29369194654` and `29369197183`. |
| Non-root read-only container smoke | Passed in CI | `pilot-container` reached dependency readiness. |
| Clean PostgreSQL backup/restore rehearsal | Passed in CI | Populated auth/workflow data verified after restore. |
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

The repository is deployment-ready at commit
`59bd74a78c39923ad99d583a00f352a57d8dfb95`. A data-bearing or remotely
accessible pilot remains no-go until every external prerequisite is assigned,
configured, and evidenced.

## Railway Pilot Alternative

| Gate | Status | Evidence |
| --- | --- | --- |
| Config as code | Passed locally | Official Railway schema and repository validator passed. |
| Credential-free contract | Passed locally | Planned contract is valid and not field-ready. |
| Dynamic platform port | Passed locally | Docker healthcheck and API entrypoint use `PORT`. |
| Budget envelope | Planned | USD 12-25 estimate, USD 20 alert, USD 30 hard limit. |
| Railway account and project | Blocked external | No approved account or billable resource exists. |
| Private PostgreSQL 16 | Blocked external | Service and volume are not provisioned. |
| Native and off-platform recovery | Blocked external | Backups and restore rehearsal are not evidenced. |
| Public endpoint and sealed variables | Blocked external | Domain and live secrets do not exist. |
| Monitoring and alert delivery | Blocked external | Uptime and cost alert delivery are not evidenced. |
| Protected acceptance workflow | Pending CI/external | Workflow exists; GitHub environment and live target do not. |

Railway field access remains no-go until the strict contract reports field-ready,
the manual acceptance workflow passes, and all `DEF-RAILWAY-*` defects close.
