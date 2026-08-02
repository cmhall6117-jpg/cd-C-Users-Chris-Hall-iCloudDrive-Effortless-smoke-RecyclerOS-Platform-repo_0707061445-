# RC1 Assumptions

- The active RC1 path uses generated slices VS-001 through VS-005 plus VS-021 and VS-022 integration scaffolds.
- Later generated slices are archived as source packages but are not activated in the app or API for RC1.
- Login and workspace selection are local scaffold screens only; live SSO and enterprise identity are deferred.
- Payment, marketplace publishing, shipping, SSO, and AI credentials remain out of scope for RC1 and must stay behind future interfaces or secret references.
- Tenant context for API calls is represented by `X-Organization-ID` and `X-Workspace-ID` headers.
- The backend baseline uses an injectable, process-local store to validate RC1 workflow contracts; durable PostgreSQL API persistence is the next backend increment.
- Cross-tenant resource lookups return `404` so the API does not disclose whether another tenant owns a requested record.
- The Flutter client uses Riverpod for session UI state and `DioRc1Gateway` for the live RC1 workflow; offline SQLite synchronization remains a follow-up integration.
- `RECYCLEROS_API_BASE_URL` defaults to `http://127.0.0.1:8000`; Android emulator builds must override it with the host bridge address.
- Widget tests inject `FakeRc1Gateway`, while a focused Dio test verifies tenant headers and backend response mapping without external network access.
- Flutter sign-in validates local form state only. Live SSO and credential exchange remain deferred.
- The short repository path `repo_0707061445` is the authoritative monorepo because longer Windows paths interrupt deep generated file copies.
