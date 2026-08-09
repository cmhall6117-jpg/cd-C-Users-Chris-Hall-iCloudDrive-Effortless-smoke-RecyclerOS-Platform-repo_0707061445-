# Pilot Deployment Runbook

## Scope

This runbook deploys the existing RC1 API and PostgreSQL path for a controlled
pilot. It does not activate another vertical slice or configure public DNS, TLS,
SSO, payment, marketplace, shipping, or AI credentials.

The pilot compose stack binds API and PostgreSQL ports to loopback only. A
separately managed TLS reverse proxy is required before remote users may connect.

## Host Prerequisites

- Linux host with current Docker Engine and Docker Compose v2
- persistent disk sized for PostgreSQL and backup staging
- approved password manager or secret store
- encrypted off-host backup destination
- TLS reverse proxy, certificate, and DNS record for remote access
- centralized container log destination and alert recipient

## Prepare Configuration

1. Create the local environment file from `deploy/pilot/pilot.env.example`.
2. Set `RECYCLEROS_TRUSTED_HOSTS` to the exact API hostnames.
3. Set explicit browser origins if Flutter web will be used.
4. Keep `RECYCLEROS_API_WORKERS=1` for the initial pilot.

Create initial secret files without displaying their values:

```powershell
python tools/scripts/pilot_prepare_secrets.py --directory deploy/pilot/secrets
```

Immediately import `operator_password` into the approved password manager. The
files under `deploy/pilot/secrets` are ignored by Git and must remain readable
only by the deployment account.

## Start

```powershell
docker compose --env-file deploy/pilot/pilot.env -f deploy/pilot/compose.yml up --build -d
```

The API container applies the ordered PostgreSQL migrations before starting
Uvicorn. Startup fails if the database secret cannot be read, production mode
lacks trusted hosts, or a migration fails.

## Verify

```powershell
Invoke-RestMethod http://127.0.0.1:8000/v1/health/live
Invoke-RestMethod http://127.0.0.1:8000/v1/health/ready
docker compose --env-file deploy/pilot/pilot.env -f deploy/pilot/compose.yml ps
```

Expected results:

- liveness returns `alive`
- readiness returns `ready` for workflow storage and auth
- both containers are running and healthy
- login succeeds with the operator account and the password stored in the password manager

## Rollback

1. Stop intake and record the rollback decision.
2. Create and verify a database backup.
3. Set `RECYCLEROS_API_IMAGE` to the previously approved image.
4. Recreate only the API container.
5. Re-run liveness, readiness, login, and the RC1 smoke path.

Do not delete the PostgreSQL volume during an application rollback. A database
restore is a separate, destructive procedure governed by the backup runbook.

## Stop

```powershell
docker compose --env-file deploy/pilot/pilot.env -f deploy/pilot/compose.yml down
```

This command leaves the named PostgreSQL volume intact. Do not add `--volumes`
unless data destruction has been explicitly approved and a verified backup exists.
