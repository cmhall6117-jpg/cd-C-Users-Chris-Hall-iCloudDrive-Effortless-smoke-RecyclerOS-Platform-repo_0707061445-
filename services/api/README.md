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
