# Production Readiness Checklist

## Repository Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Backend compile and tests | Passed locally | Compilation passed; 46 tests passed and 2 PostgreSQL-only tests skipped. |
| Flutter analysis and tests | Passed in CI | Push `29372078034`; PR `29372080469`. |
| SQLite initialization | Passed locally | All 10 migrations, tenant columns, and mismatch rejection passed. |
| PostgreSQL clean migration | Passed in CI | Checksum ledger and exact replay passed twice. |
| Backup checksum and clean restore | Passed in CI | Manifest verified before clean restore. |
| Production image hardening | Passed in CI | Non-root, read-only, dropped capabilities, bounded processes. |
| Controlled initial owner | Passed in CI | One-time audited owner bootstrap and login. |
| Production runtime policy | Passed locally | HTTPS origins, exact hosts, hidden docs, HSTS, release SHA. |
| Immutable release record | Passed locally | Commit, image digest, and all 11 PostgreSQL migration checksums. |
| Rollback runbook | Documented | Application and database paths are separate. |
| Composite release gate | Passed in CI | All eight jobs passed in both trigger paths. |

## External Launch Gates

| Gate | Status |
| --- | --- |
| Production account, host, network, DNS, and TLS approved | Blocked external |
| Approved registry image published and digest recorded | Blocked external |
| Managed PostgreSQL provisioned with encryption and restricted access | Blocked external |
| Point-in-time recovery, off-host backups, retention, and restore drill | Blocked external |
| Production secrets, IAM roles, rotation owners, and access review | Blocked external |
| Central logs, metrics, uptime checks, and tested alert routing | Blocked external |
| On-call, incident commander, rollback authority, and support process | Blocked external |
| Privacy, retention, terms, and business launch approval | Blocked external |
| Capacity and load target approved and tested in the target environment | Blocked external |

## Decision

Repository preparation does not authorize production traffic. Launch remains
no-go until every external gate has an owner, passing evidence, and approval.
