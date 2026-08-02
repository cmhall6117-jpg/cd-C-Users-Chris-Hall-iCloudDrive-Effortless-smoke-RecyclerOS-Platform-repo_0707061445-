# RecyclerOS Platform API

The RC1 backend exposes the opportunity discovery, vehicle record, procurement,
pick list, focus point, and inventory intake workflow through FastAPI.

## Local Run

From the repository root:

```powershell
$env:RECYCLEROS_LOCAL_OPERATOR_PASSWORD = Read-Host "Local operator password"
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir services\api\src --reload
```

The API is available at `http://127.0.0.1:8000`, with OpenAPI documentation at
`http://127.0.0.1:8000/docs`.

Health endpoints are separated by purpose:

- `GET /v1/health/live` confirms the API process is running.
- `GET /v1/health/ready` confirms workflow storage and auth dependencies are ready.
- `GET /v1/health` reports the active provider names and API version.

Local Flutter web origins on `localhost` and `127.0.0.1` are allowed by default.
Deployment origins must be set explicitly as a comma-separated list:

```powershell
$env:RECYCLEROS_CORS_ORIGINS = "https://app.example.com"
```

`RECYCLEROS_CORS_ORIGIN_REGEX` can replace the default local-only origin regular
expression. Credentials are disabled, and the API never enables a wildcard
origin by default.

The local identity provider creates `operator@effortlesssmoke.com` only when
`RECYCLEROS_LOCAL_OPERATOR_PASSWORD` is set. The repository contains no default
password. Authenticate with `POST /v1/auth/login`, then send its opaque token
with both tenant headers:

```text
Authorization: Bearer <access token>
X-Organization-ID: org-local
X-Workspace-ID: workspace-local
```

`GET /v1/auth/me` returns the authenticated identity and server-owned tenant
memberships. A request is accepted only when the organization/workspace pair is
one of those memberships. Client-supplied role values are ignored. Use
`POST /v1/auth/logout` to revoke the current bearer session.

RC1 permissions are:

| Role | Read | Operate | Admin |
| --- | --- | --- | --- |
| owner | Yes | Yes | Yes |
| admin | Yes | Yes | Yes |
| operator | Yes | Yes | No |
| viewer | Yes | No | No |

## Validation

```powershell
.\.venv\Scripts\python.exe -m compileall services\api\src
$env:PYTHONPATH = "services\api\src"
.\.venv\Scripts\python.exe -m pytest -q services\api\tests
```

## Persistence Boundary

Without `DATABASE_URL`, RC1 uses process-local workflow and auth implementations
for development and unit tests. When `DATABASE_URL` is set, the API selects the
PostgreSQL workflow and auth providers. Production mode fails closed if the
durable database is missing:

```powershell
$env:DATABASE_URL = "postgresql://user:password@localhost:5432/recycleros"
$env:RECYCLEROS_DEPLOYMENT_MODE = "production"
$env:RECYCLEROS_LOCAL_OPERATOR_PASSWORD = Read-Host "Initial operator password"
$env:RECYCLEROS_TRUSTED_HOSTS = "api.example.com"
```

The operator secret bootstraps the account only when it does not exist; app
restarts do not rotate an existing credential. PostgreSQL stores users,
memberships, opaque token digests, revocation state, login attempts, and auth
audit events. The optional controls are:

- `RECYCLEROS_SESSION_TTL_HOURS` (default `8`)
- `RECYCLEROS_AUTH_MAX_FAILURES` (default `5`)
- `RECYCLEROS_AUTH_LOCKOUT_MINUTES` (default `15`)

Live SSO, password recovery, refresh tokens, and external identity credentials
remain deferred behind `AuthService`.

Production secrets may be mounted as files by setting `DATABASE_URL_FILE` and
`RECYCLEROS_LOCAL_OPERATOR_PASSWORD_FILE`. The API rejects configurations that
set both a direct value and its matching `_FILE` reference.

## Pilot Container

The hardened pilot image is defined in `services/api/Dockerfile`, and the
secret-backed stack is in `deploy/pilot/compose.yml`. See
`documentation/deployment/PILOT_DEPLOYMENT_RUNBOOK.md` before starting it. The
stack binds both published ports to loopback and requires a separate TLS reverse
proxy for remote access.

## Production Runtime

Production uses the same image with `services/api/production_entrypoint.py` and
`deploy/production/compose.yml`. The production entrypoint does not apply
migrations or bootstrap users. Those operations run as explicit one-shot
services before API startup.

Production requires durable PostgreSQL, exact trusted hosts, exact HTTPS browser
origins, an explicit proxy allowlist, and a 40-character release SHA. API docs
are disabled and security headers are enabled. See
`documentation/deployment/PRODUCTION_DEPLOYMENT_RUNBOOK.md` for the controlled
release, verification, and no-go process.
