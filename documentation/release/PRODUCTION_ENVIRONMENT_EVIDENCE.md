# Production Environment Evidence

## Candidate

- Branch: `codex/production-environment-provisioning`
- Base: `codex/production-launch-preparation`
- Provider: unselected
- Live resources created: none
- Production acceptance run: blocked until environment selection and provisioning

## Repository Evidence

| Gate | Result | Evidence |
| --- | --- | --- |
| Example contract structure | Passed locally | Placeholder-safe validation. |
| Strict ready contract | Passed locally | Complete fixture passes strict mode. |
| Credential field rejection | Passed locally | Embedded database URL is rejected. |
| Network policy rejection | Passed locally | Public database configuration is rejected. |
| Public endpoint evaluation | Passed locally | Expected TLS, health, headers, release, and hidden docs. |
| Public endpoint negative cases | Passed locally | Expiring TLS and wrong release fail. |
| Managed database evaluation | Passed locally | TLS, limited role, version, schema, owner, ledger. |
| Workflow YAML | Passed locally | CI and manual acceptance workflows parse. |
| Python compilation | Passed locally | API, entrypoints, and tools compiled. |
| Full backend suite | Passed locally | 54 passed; 2 PostgreSQL-only tests skipped. |
| SQLite initialization | Passed locally | 10 migrations and tenant enforcement. |
| Full GitHub CI suite | Pending | Exact-head push and PR evidence required. |

## External Evidence Required

- provider, account, region, budget, and billing ownership
- registry publication, image digest, signature, and provenance
- managed database resource and restricted network evidence
- secret manager, IAM review, rotation ownership, and GitHub environment protection
- public DNS/TLS and trusted proxy evidence
- centralized logs, metrics, uptime, and tested alert delivery
- restore rehearsal, approved RPO/RTO, and retention
- named operators and technical, security, and business approvals
- successful manual production environment acceptance workflow

## Decision

The repository can validate a production environment without knowing its cloud
provider or secrets. Actual provisioning and production traffic remain no-go.
