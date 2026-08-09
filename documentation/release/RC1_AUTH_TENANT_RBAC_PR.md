# Establish RC1 Auth, Tenant, and RBAC

## What Changed

- Added an injected FastAPI authentication boundary with an environment-backed
  local provider and opaque expiring bearer sessions.
- Added server-owned organization/workspace memberships and owner, admin,
  operator, and viewer permission checks across every active tenant route.
- Connected Flutter login and workspace selection to the API session and
  membership response.
- Added bearer authorization to the existing Dio gateway and read-only viewer
  controls throughout the active workflow.
- Added backend, widget, transport, and live integration coverage plus security
  and release evidence.

## Why

The previous tenant baseline trusted organization and workspace headers without
binding them to an authenticated identity. This change makes the backend the
authority for identity, membership, and role while preserving the established
RC1 core path.

## Impact

Local runs must set `RECYCLEROS_LOCAL_OPERATOR_PASSWORD` before signing in as
`operator@effortlesssmoke.com`. The repository contains no default password.
Tenant requests now require the returned bearer token. Viewer memberships can
read but cannot operate.

## Validation

- `python -m compileall services/api/src`
- `PYTHONPATH=services/api/src pytest -q services/api/tests`
- GitHub Actions backend, SQLite, PostgreSQL, Flutter, and authenticated core
  integration jobs

## Deferred

Durable identities and sessions, rate limiting, refresh and revocation,
enterprise SSO, and durable workflow persistence remain tracked release work.
