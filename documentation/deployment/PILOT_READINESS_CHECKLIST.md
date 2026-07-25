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

## Google Cloud Pilot

| Gate | Status | Evidence |
| --- | --- | --- |
| Project identity recorded | Passed | `recyleros-platform`, project number `728951606960`. |
| Credential-free pilot contract | Passed locally | Validator reports structurally valid and not field-ready. |
| Contract guardrail tests | Passed locally | 5 tests passed. |
| Terraform format and provider validation | Passed | Local validation and GitHub Actions run `30162538935`. |
| Billing linked | Blocked external | No retained billing evidence. |
| USD 100 budget alerts verified | Blocked external | Contract remains `budget_verified=false`. |
| Keyless GitHub federation applied | Blocked external | Bootstrap is defined but has not been applied. |
| Protected `gcp-pilot` environment | Blocked external | Reviewer and variables are not yet evidenced. |
| Private Cloud SQL foundation | Blocked external | Apply requires `APPLY-PILOT` approval. |
| Immutable Cloud Run release | Blocked external | Release requires `RELEASE-PILOT` approval. |
| Monitoring alert delivery | Blocked external | Notification channel and delivery proof are absent. |
| Restore rehearsal | Blocked external | Contract evidence remains `PENDING`. |

## Decision

The local-container pilot repository was deployment-ready at commit
`59bd74a78c39923ad99d583a00f352a57d8dfb95`. A data-bearing or remotely
accessible pilot remains no-go until every external prerequisite is assigned,
configured, and evidenced. The Google Cloud pilot definitions are a new
candidate and require CI provider validation before their repository gate can
pass.
