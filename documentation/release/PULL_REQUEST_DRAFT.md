# Draft Pull Request

## Title

Integrate RecyclerOS Pro RC1 monorepo

## Base Branch

`main`

## Head Branch

`codex/rc1-repository-integration`

## Body

This PR integrates RecyclerOS Pro Release Candidate 1 into the first functional monorepo for Effortless Smoke, LLC.

### Scope

- Assembles generated scaffolds into one monorepo.
- Archives all discovered original ZIP packages under `archive/source_packages`.
- Adds repository inventory and RC1 evidence documentation.
- Registers FastAPI routers for the RC1 path.
- Registers Flutter routes for the primary working path:
  Login -> Workspace Selection -> Mission Control -> Opportunity Discovery -> Vehicle Record -> Procurement -> Pick List -> Inventory Intake.
- Adds tenant context enforcement using `X-Organization-ID` and `X-Workspace-ID`.
- Adds SQLite and PostgreSQL migration runners.
- Adds GitHub Actions for backend, Flutter, SQLite migrations, PostgreSQL migrations, and tenant isolation checks.

### Evidence

- SQLite clean initialization passed locally.
- PostgreSQL migration execution is blocked locally because Docker/PostgreSQL tooling is unavailable.
- Backend and Flutter automated checks are defined in CI but blocked locally by dependency/toolchain timeouts.

### Release Gate Status

See:

- `documentation/release/RC1_RELEASE_EVIDENCE.md`
- `documentation/defects/DEFECT_REGISTER.md`
- `documentation/build/BUILD_REPORT.md`
- `documentation/tests/SMOKE_TEST_REPORT.md`

### Deferred by Request

Live payment, marketplace, SSO, shipping, and AI credentials are not implemented in RC1.

## Open PR Command

After adding a remote and pushing the branch:

```powershell
gh pr create --draft --base main --head codex/rc1-repository-integration --title "Integrate RecyclerOS Pro RC1 monorepo" --body-file documentation/release/PULL_REQUEST_DRAFT.md
```
