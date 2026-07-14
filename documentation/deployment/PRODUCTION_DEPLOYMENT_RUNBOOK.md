# Production Deployment Runbook

## Scope

This runbook deploys the existing RecyclerOS RC1 path from an approved,
digest-pinned image. It does not activate additional vertical slices or enable
live SSO, payment, marketplace, shipping, or AI credentials.

The production Compose file runs only the migration, first-owner bootstrap, and
API processes. PostgreSQL, TLS termination, DNS, secret storage, logs, alerts,
and backups are external managed services. The API remains loopback-bound behind
the approved TLS reverse proxy.

## Required Approval Evidence

- exact release commit and image digest
- green push and pull-request production gates for that commit
- production release manifest retained with the change record
- pre-deployment database backup with a verified checksum and off-host copy
- migration review and rollback decision owner
- approved host, TLS, DNS, managed PostgreSQL, secrets, alerts, and on-call route

Do not continue when any item is missing.

## Prepare The Release

1. Copy `deploy/production/production.env.example` to
   `deploy/production/production.env` on the deployment host.
2. Replace every example value. Pin `RECYCLEROS_API_IMAGE_DIGEST` to the approved
   registry digest and `RECYCLEROS_RELEASE_SHA` to its exact 40-character commit.
3. Set exact public hostnames and HTTPS browser origins. Wildcards and HTTP
   browser origins are rejected.
4. Place the managed PostgreSQL URL in
   `deploy/production/secrets/database_url`. Restrict it to the deployment
   account and import the source value from the approved secret manager.
5. Validate the resolved configuration:

```powershell
docker compose --env-file deploy/production/production.env -f deploy/production/compose.yml config --quiet
```

Create the release manifest and attach it to the change record:

```powershell
python tools/scripts/production_release_manifest.py `
  --image $env:RECYCLEROS_API_IMAGE `
  --digest $env:RECYCLEROS_API_IMAGE_DIGEST `
  --commit $env:RECYCLEROS_RELEASE_SHA `
  --output build_artifacts/production_releases/release.json
```

## Back Up And Migrate

Create a backup and verify its manifest before changing the schema. Copy both
files to the approved encrypted destination. Then run the one-shot migration:

```powershell
docker compose --env-file deploy/production/production.env -f deploy/production/compose.yml run --rm migrate
```

The migration runner takes a PostgreSQL advisory lock and records each filename
and SHA-256 checksum in `recycleros_schema_migrations`. It skips an exact replay
and fails if an applied migration file changed.

## Provision The First Owner

Run this once for a new production database. Place a generated password of at
least 16 characters in
`deploy/production/secrets/bootstrap_owner_password`, import it into the
approved password manager, and set the exact confirmation only for this command:

```powershell
$env:RECYCLEROS_BOOTSTRAP_CONFIRM = $env:RECYCLEROS_BOOTSTRAP_OWNER_EMAIL
docker compose --profile bootstrap --env-file deploy/production/production.env -f deploy/production/compose.yml run --rm bootstrap-owner
Remove-Item Env:RECYCLEROS_BOOTSTRAP_CONFIRM
```

The command creates one owner membership and an audit event. It refuses an
existing email. Remove the bootstrap secret file after verified login; API
containers never receive it.

## Deploy And Verify

```powershell
docker compose --env-file deploy/production/production.env -f deploy/production/compose.yml up -d api
```

Verify through both loopback and the public TLS endpoint:

- `/v1/health/live` returns `alive`
- `/v1/health/ready` returns ready storage and auth dependencies
- `/v1/health` reports the approved release SHA
- `/docs` and `/openapi.json` return `404`
- HSTS and the documented security headers are present through the public route
- first-owner login succeeds and an authenticated tenant-scoped read succeeds
- logs reach the central destination and a test readiness alert reaches on-call

Record command output, approver, operator, start/end time, image digest, database
backup manifest, and final decision in the production release evidence.

## Launch Decision

Open traffic only when every repository and external gate in
`PRODUCTION_READINESS_CHECKLIST.md` is passed with evidence. Otherwise keep the
service loopback-bound and record a no-go decision.
