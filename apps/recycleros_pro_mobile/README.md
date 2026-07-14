# RecyclerOS Pro Mobile

The RC1 Flutter client implements the operational path from sign-in through
inventory intake. Workflow transitions use the tenant-scoped FastAPI API by
default, while tests inject an in-memory fake gateway.

## Run

Start the FastAPI service, then run Flutter:

```text
flutter pub get
flutter run
```

The default API URL is `http://127.0.0.1:8000`. Override it at build time:

```text
flutter run --dart-define=RECYCLEROS_API_BASE_URL=http://localhost:8000
```

Use `http://10.0.2.2:8000` for an Android emulator reaching an API on the host.

## Validate

```text
flutter analyze
flutter test
```

## RC1 Integration Boundary

Riverpod owns session UI state, `Rc1Gateway` defines workflow operations, and
`DioRc1Gateway` maps API responses into the shared `recycleros_domain` models.
Every workflow call sends `X-Organization-ID` and `X-Workspace-ID`. Login remains
local; live SSO and offline SQLite synchronization are deferred.
