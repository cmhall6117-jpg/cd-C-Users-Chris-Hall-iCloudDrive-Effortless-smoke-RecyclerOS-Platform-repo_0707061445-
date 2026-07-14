# Pilot Secrets Register

This register contains references and handling requirements only. It must never
contain live values.

| Secret | Runtime reference | Purpose | Rotation trigger |
| --- | --- | --- | --- |
| PostgreSQL password | `/run/secrets/postgres_password` | Database account authentication | Before pilot, suspected exposure, staff/access change |
| PostgreSQL URL | `/run/secrets/database_url` | API database connection | With PostgreSQL password or endpoint change |
| Initial operator password | `/run/secrets/operator_password` | Bootstrap missing local operator | Before first login, suspected exposure, operator change |
| TLS private key | External reverse-proxy secret reference | HTTPS termination | Certificate renewal or suspected exposure |
| Backup encryption key | External backup-system secret reference | Off-host backup encryption | Approved key rotation schedule or suspected exposure |

## Controls

- secret files are excluded from Git and the Docker build context
- the compose stack mounts secrets read-only under `/run/secrets`
- direct environment variables remain supported only for CI and controlled local tests
- the API rejects simultaneous direct and file-based values for the same secret
- backup and restore subprocess commands receive passwords through `PGPASSWORD`, not command arguments
- generated secret files use exclusive creation and are never overwritten
- changing the bootstrap operator file does not rotate an existing database credential

Database and operator credential rotation require an approved operational change
and post-rotation login/readiness verification.
