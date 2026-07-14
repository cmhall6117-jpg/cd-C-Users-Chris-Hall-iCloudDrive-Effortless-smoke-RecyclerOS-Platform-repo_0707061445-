# RC1 Auth, Tenant, and RBAC Boundary

## Scope

This increment authenticates the existing RC1 working path without adding a new
vertical slice. FastAPI owns identity, tenant membership, and role decisions;
Flutter consumes those decisions and does not claim authority.

## Authentication

- `AuthService` is the injected identity boundary.
- `LocalAuthService` is the RC1 local implementation.
- A local operator exists only when `RECYCLEROS_LOCAL_OPERATOR_PASSWORD` is set.
- Passwords are verified with PBKDF2-HMAC-SHA256 and are never returned.
- Login returns an opaque random bearer token. Only its SHA-256 lookup key is
  retained in process memory.
- Sessions expire after eight hours by default. The duration can be changed with
  `RECYCLEROS_SESSION_TTL_HOURS`.

## Tenant Enforcement

Tenant-scoped requests require all three values:

```text
Authorization: Bearer <opaque token>
X-Organization-ID: <organization>
X-Workspace-ID: <workspace>
```

The API resolves the token, then requires an exact organization/workspace match
in the identity's server-owned memberships. Missing headers return `400`,
missing or invalid authentication returns `401`, and unassigned tenant context
returns `403`. Cross-tenant record lookups continue to return `404` after valid
tenant authentication so another tenant's record existence is not disclosed.

## Roles and Permissions

| Role | `tenant:read` | `tenant:operate` | `tenant:admin` |
| --- | --- | --- | --- |
| owner | Yes | Yes | Yes |
| admin | Yes | Yes | Yes |
| operator | Yes | Yes | No |
| viewer | Yes | No | No |

Read endpoints require `tenant:read`. Create, update, focus-point, and inventory
operations require `tenant:operate`. Flutter disables write controls for a
viewer, but every API route independently enforces permission. Client-provided
role headers are ignored.

## Deferred Production Controls

The local provider is an integration implementation, not the production
identity system. Users, memberships, and sessions are process-local. Durable
identity storage, replica-safe sessions, refresh, revocation, login rate
limiting, recovery, audit integration, and enterprise SSO remain deferred behind
`AuthService`. No live SSO or external credentials are introduced by this work.

## Evidence

`services/api/tests/test_auth_rbac.py` covers valid and invalid login, bearer
requirements, expiry, membership mismatch, role spoof rejection, viewer
read-only behavior, and owner/admin/operator write access. Tenant-isolation and
full-path tests authenticate through the same injected boundary. Flutter tests
cover failed login, viewer controls, bearer propagation, tenant headers, and the
authenticated live path.
