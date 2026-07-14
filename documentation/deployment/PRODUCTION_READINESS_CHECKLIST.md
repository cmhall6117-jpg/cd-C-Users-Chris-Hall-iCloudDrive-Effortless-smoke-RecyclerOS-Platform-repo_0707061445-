# Production Readiness Checklist

## Repository Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Backend compile and tests | Passed locally | Compilation passed; 46 tests passed and 2 PostgreSQL-only tests skipped. |
| Flutter analysis and tests | Pending CI | Existing RC1 path retained. |
| SQLite initialization | Passed locally | All 10 migrations, tenant columns, and mismatch rejection passed. |
| PostgreSQL clean migration | Pending CI | Checksum ledger and replay gate added. |
| Backup checksum and clean restore | Pending CI | Restore now verifies its manifest. |
| Production image hardening | Pending CI | Non-root, read-only, dropped capabilities, bounded processes. |
| Controlled initial owner | Pending CI | One-time audited owner bootstrap. |
| Production runtime policy | Passed locally | HTTPS origins, exact hosts, hidden docs, HSTS, release SHA. |
| Immutable release record | Passed locally | Commit, image digest, and all 11 PostgreSQL migration checksums. |
| Rollback runbook | Documented | Application and database paths are separate. |

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
