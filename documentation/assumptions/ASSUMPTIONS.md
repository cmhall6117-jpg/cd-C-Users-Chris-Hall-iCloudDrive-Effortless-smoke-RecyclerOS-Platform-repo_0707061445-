# RC1 Assumptions

- The active RC1 path uses generated slices VS-001 through VS-005 plus VS-021 and VS-022 integration scaffolds.
- Later generated slices are archived as source packages but are not activated in the app or API for RC1.
- Login uses the injected FastAPI `AuthService`; local development uses a process-local provider and configured deployments use the PostgreSQL provider, while live SSO and enterprise identity remain deferred.
- Payment, marketplace publishing, shipping, SSO, and AI credentials remain out of scope for RC1 and must stay behind future interfaces or secret references.
- Tenant context for API calls is represented by `X-Organization-ID` and `X-Workspace-ID` headers and is accepted only when the authenticated identity has the matching server-owned membership.
- RC1 roles are owner, admin, operator, and viewer. Owner/admin/operator may perform the active workflow; viewer is read-only. The backend permission check is authoritative.
- The backend uses an injectable workflow store. It defaults to process-local storage without `DATABASE_URL` and selects durable PostgreSQL storage when the database is configured.
- Cross-tenant resource lookups return `404` so the API does not disclose whether another tenant owns a requested record.
- The Flutter client uses Riverpod for session UI state and `DioRc1Gateway` for the live RC1 workflow; offline SQLite synchronization remains a follow-up integration.
- `RECYCLEROS_API_BASE_URL` defaults to `http://127.0.0.1:8000`; Android emulator builds must override it with the host bridge address.
- Widget tests inject `FakeRc1Gateway`, while a focused Dio test verifies login mapping, bearer authorization, tenant headers, and backend response mapping without external network access.
- PostgreSQL users, memberships, sessions, revocation state, login attempts, and auth audit events are durable across API restarts. Refresh tokens, password recovery, and enterprise SSO remain deferred.
- `RECYCLEROS_DEPLOYMENT_MODE=production` requires `DATABASE_URL`; process-local providers are not an implicit production fallback.
- The local operator password bootstraps a missing PostgreSQL account but does not rotate an existing credential during app startup.
- The pilot API and PostgreSQL ports remain loopback-bound; remote access requires an independently managed TLS reverse proxy and DNS record.
- Pilot runtime secrets are mounted through file references and are not committed, baked into the image, or written into evidence documents.
- The API container applies idempotent RC1 migrations before starting one initial pilot worker.
- Repository readiness alone does not imply a live pilot host, approved real
  secrets, off-host backup schedule, centralized alerts, or staffed support
  coverage. The live Railway pilot remains no-go until its external controls
  are evidenced.
- Proposed pilot recovery targets are a 24-hour recovery point and 4-hour recovery time; business approval is still required.
- The short repository path `repo_0707061445` is the authoritative monorepo because longer Windows paths interrupt deep generated file copies.
- Production uses the same RC1 application image as the pilot but separates schema migration and first-owner provisioning from API startup.
- The production Compose configuration expects externally managed PostgreSQL and TLS termination; it does not run a production database or expose the API directly.
- Production releases are identified by an exact Git SHA, image SHA-256 digest, and migration checksums. A mutable image tag alone is not release evidence.
- PostgreSQL migrations are forward-only. Application rollback must remain compatible with the current schema; database restore requires a separate approved change.
- The initial production owner uses the current durable local-account provider. Live SSO remains deferred and requires a separate product and security decision.
- Repository-level production preparation does not imply a provisioned host, registry artifact, managed database, secrets, observability, on-call coverage, legal approval, or authority to open traffic.
- No cloud provider, production account, region, domain, registry, secret manager, or monitoring service is approved yet; environment tooling must remain provider-neutral.
- Provider selection and billable-resource creation require an explicit cost, account-ownership, region, and business approval decision outside repository CI.
- The committed production environment contract contains decisions and evidence only. Credential-like fields are forbidden and live values remain in managed secrets.
- GitHub production environment acceptance is manual, reviewer-gated, and read-only; it validates a deployed target but does not provision or deploy it.
- Google Cloud project `recyleros-platform` with project number `728951606960`
  is selected only for the one-to-two-person field pilot. This does not approve
  Google Cloud as the production provider.
- The approved pilot region is `us-east4`; the project ID spelling is
  authoritative even though it omits the second `c` in RecyclerOS.
- The pilot operating target is USD 30-70 per month, with a USD 100 monthly
  budget and USD 150 first-month review ceiling. Budget alerts notify but do not
  cap spend.
- The pilot accepts single-zone `db-g1-small` Cloud SQL availability. Shared-core
  availability is an explicit pilot risk and is not a production SLA.
- Google Cloud field access remains prohibited until billing, budget alerts,
  GitHub protection, monitoring delivery, support ownership, and restore
  evidence are verified.
- GitHub deployments use Workload Identity Federation restricted to the exact
  repository and deployment branch. Static Google service account keys are
  forbidden.
- Railway is the approved cost-bounded pilot provider, not the approved
  production provider. The private Pro project `recycleros-pilot` is live;
  its existence does not authorize production traffic or production data.
- The Railway planning envelope is USD 20-25 monthly with a USD 20 alert and USD 30 hard limit; field access remains blocked if the plan cannot enforce or evidence those controls.
- The project owner approved Railway field access on August 24, 2026, for Chris
  Hall as the only pilot tester. Billing controls, GitHub protection,
  monitoring delivery, support ownership, and restore evidence are verified;
  protected acceptance still must pass before this gate is recorded complete.
- The Railway API uses one US East replica, one worker, serverless sleep, a 512 MiB memory limit, and private PostgreSQL networking for one approved tester.
- Railway's PostgreSQL template is unmanaged. The August 9 manual encrypted
  off-platform backup and clean restore proves one recovery point; PITR and
  daily/weekly native schedules are active. Automated off-platform retention
  and cross-device key escrow remain separate operational requirements.
- Chris Hall is the named restore and support owner for the one-person Railway
  pilot. These assignments must be revisited before adding another tester or
  promoting the environment beyond pilot scope.
- The initial Railway pilot starts with one named operator and no credential sharing; a second tester requires a separate durable identity.
- Railway and GitHub acceptance workflows contain no provider deployment token and cannot create, mutate, or delete live resources.
- Railway health probes use `healthcheck.railway.app`; this exact hostname is
  allowed alongside the assigned public API hostname.
- GitHub-backed Railway deployments use the injected `RAILWAY_GIT_COMMIT_SHA`
  as the authoritative runtime release identity.
