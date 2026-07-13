# RC1 Assumptions

- The active RC1 path uses generated slices VS-001 through VS-005 plus VS-021 and VS-022 integration scaffolds.
- Later generated slices are archived as source packages but are not activated in the app or API for RC1.
- Login and workspace selection are local scaffold screens only; live SSO and enterprise identity are deferred.
- Payment, marketplace publishing, shipping, SSO, and AI credentials remain out of scope for RC1 and must stay behind future interfaces or secret references.
- Tenant context for API calls is represented by `X-Organization-ID` and `X-Workspace-ID` headers.
- The short repository path `repo_0707061445` is the authoritative monorepo because longer Windows paths interrupt deep generated file copies.
