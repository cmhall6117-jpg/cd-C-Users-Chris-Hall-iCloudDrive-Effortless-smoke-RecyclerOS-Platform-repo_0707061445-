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

## Generic Host And GCP Prerequisites

These prerequisites apply to the generic self-hosted and Google Cloud paths.
They do not override the separately verified Railway alternative below.

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

## Railway Pilot Alternative

| Gate | Status | Evidence |
| --- | --- | --- |
| Config as code | Passed locally | Official Railway schema and repository validator passed. |
| Credential-free contract | Passed and verified | Lifecycle is `verified`; deployment and field approvals are true; access remains capped at one tester. |
| Dynamic platform port | Passed locally | Docker healthcheck and API entrypoint use `PORT`. |
| Budget envelope | Passed live | USD 20 warning and USD 30 hard limit are active. |
| Railway account and project | Passed live | Private Pro project, MFA, and passkey verified. |
| Private PostgreSQL 16 | Passed live | Private service, 5 GiB volume, and no public database domain. |
| Native and off-platform recovery | Passed for one-person pilot | PITR, daily and weekly volume backups, encrypted off-platform dump, clean restore, staging cleanup, and restore ownership passed. Automated off-platform cadence and cross-device key escrow remain non-blocking hardening under `DEF-RAILWAY-003`. |
| Public endpoint and sealed variables | Passed live | HTTPS API, private database, and sealed operator credential verified. |
| Monitoring and alert delivery | Passed for one-person pilot | Two-hour monitor, alert delivery, synthetic incident recovery, and exact-release run `33250867140` passed. |
| Protected acceptance workflow | Passed for one-person pilot | Protected acceptance run `32770410381` passed and temporary policy changes were removed afterward. |
| Live tenant-scoped API path | Passed for one-person pilot | Run `20260824212230-5fd820be` passed 18 checks from login through inventory and revoked-session rejection. |
| Manual Flutter device path | Passed for one-person pilot | Login through inventory, logout, editable mileage, and persisted Sell Whole intent are evidenced through August 29. |
| Second tester identity | Blocked beyond approved scope | The contract allows one tester; `DEF-RAILWAY-005` remains open before adding another person. |

Railway field access is approved for one named tester using synthetic or
otherwise authorized pilot data. This does not authorize a second tester,
production traffic, or closure of non-blocking hardening item
`DEF-RAILWAY-003`.

## Decision

The local-container pilot repository was deployment-ready at commit
`59bd74a78c39923ad99d583a00f352a57d8dfb95`. Google Cloud remains a
credential-free deployment candidate. Railway is the verified provider for the
approved one-person pilot: scheduled recovery, monitoring, ownership, cleanup,
protected acceptance, API smoke, and manual Flutter evidence passed. Production
and any scope beyond one tester remain no-go.
