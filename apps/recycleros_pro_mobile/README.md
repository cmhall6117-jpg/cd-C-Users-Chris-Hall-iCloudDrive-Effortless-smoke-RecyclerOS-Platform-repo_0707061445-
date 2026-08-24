# RecyclerOS Pro Mobile

The RC1 Flutter client implements the operational path from sign-in through
inventory intake. Workflow transitions use the tenant-scoped FastAPI API by
default, while tests inject an in-memory fake gateway.

## Run

Start FastAPI with `RECYCLEROS_LOCAL_OPERATOR_PASSWORD` set, then run Flutter:

```text
flutter pub get
flutter run
```

The default API URL is `http://127.0.0.1:8000`. Override it at build time:

```text
flutter run --dart-define=RECYCLEROS_API_BASE_URL=http://localhost:8000
```

Use `http://10.0.2.2:8000` for an Android emulator reaching an API on the host.

For the controlled iPhone pilot, GitHub Pages builds the web target with the
exact Railway API URL from `deploy/railway/pilot/pilot.contract.json`. The
public shell contains no account credential or API token. Railway accepts
browser requests only from the exact Pages origin committed in
`deploy/railway/pilot/variables.example`.

## Validate

```text
flutter analyze
flutter test
```

## RC1 Integration Boundary

Riverpod owns session UI state, `Rc1Gateway` defines workflow operations, and
`DioRc1Gateway` maps API responses into the shared `recycleros_domain` models.
Login exchanges credentials for an opaque bearer token and server-owned tenant
memberships. Workspace selection uses those memberships, and every workflow
call sends the token plus `X-Organization-ID` and `X-Workspace-ID`. Viewer
memberships are read-only in the UI, while the API remains authoritative for
all roles. Live SSO, durable sessions, and offline SQLite synchronization are
deferred behind the existing gateway and auth interfaces.
