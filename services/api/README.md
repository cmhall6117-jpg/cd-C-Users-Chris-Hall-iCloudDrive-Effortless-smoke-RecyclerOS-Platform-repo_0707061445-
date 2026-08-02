# RecyclerOS Platform API

The RC1 backend exposes the opportunity discovery, vehicle record, procurement,
pick list, focus point, and inventory intake workflow through FastAPI.

## Local Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir services\api\src --reload
```

The API is available at `http://127.0.0.1:8000`, with OpenAPI documentation at
`http://127.0.0.1:8000/docs`.

Tenant-scoped requests require both headers:

```text
X-Organization-ID: org-local
X-Workspace-ID: workspace-local
```

## Validation

```powershell
.\.venv\Scripts\python.exe -m compileall services\api\src
$env:PYTHONPATH = "services\api\src"
.\.venv\Scripts\python.exe -m pytest -q services\api\tests
```

## Persistence Boundary

RC1 currently uses the process-local `InMemoryStore` implementation. The API
factory accepts a store instance so a PostgreSQL implementation can replace it
without changing route contracts. Records are not durable across API restarts.
