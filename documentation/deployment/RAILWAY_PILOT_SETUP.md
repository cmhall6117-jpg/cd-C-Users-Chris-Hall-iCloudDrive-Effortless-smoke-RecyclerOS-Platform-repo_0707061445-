# Railway Pilot Setup

## Purpose

This is the budget-conscious hosting path for one designated field tester, with
capacity for a second tester after a separate account is provisioned. It is a
controlled pilot, not the production environment. The repository creates no
Railway account, project, billing commitment, database, domain, or secret.

The verified one-person pilot uses Railway Pro so native point-in-time recovery
and scheduled volume backups are available. Its recorded operating envelope is
USD 20-25 per month, with a USD 20 alert and a USD 30 hard usage limit. Do not
expand billable resources without account-owner approval. If the selected plan
cannot enforce the hard limit, leave `hard_limit_verified` false and keep field
access blocked.

## Account Controls

1. Create or use the Effortless Smoke Railway account and enable two-factor
   authentication before connecting GitHub.
2. Use the account-owner-approved Pro plan for the verified pilot. Reconfirm
   price and usage terms before changing plans or enabling more resources.
3. Create project `recycleros-pilot` and an environment named `pilot` in the US
   East region.
4. Configure the USD 20 usage alert and USD 30 hard usage limit. Test alert
   delivery and record the evidence outside the repository.
5. Limit Railway project access to the deployment owner and support owner.

## PostgreSQL Service

1. Add Railway's PostgreSQL database template and name the service `Postgres`.
2. Pin the image to the Railway SSL-enabled PostgreSQL 16 major tag. Do not use
   an unbounded `latest` tag for the pilot database.
3. Confirm the persistent volume is mounted at the database data path and limit
   expected pilot storage to 5 GiB.
4. Leave the TCP proxy disabled during normal operation. The API uses the
   private reference `${{Postgres.DATABASE_URL}}`.
5. Enable daily and weekly Railway volume backups.
6. Record that Railway's PostgreSQL template is unmanaged: Effortless Smoke
   retains responsibility for upgrades, recovery, security, and monitoring.

Railway volume backups are not the only recovery copy. Wiping a volume also
deletes its backups, so field readiness additionally requires an encrypted
off-platform logical backup and an evidenced restore rehearsal.

## API Service

1. Add the GitHub repository as service `recycleros-api` and select branch
   `codex/railway-pilot-environment`.
2. Keep the source root at `/`; the Docker build needs the API, migration, and
   repository script paths.
3. Set the config-as-code path to
   `/deploy/railway/pilot/railway.json`.
4. Enable Railway's wait-for-CI/check-suites control before automatic deploys.
5. Keep PR environments disabled for this budget pilot.
6. Generate one Railway public domain for the API. Do not add a database TCP
   proxy or a second public service.
7. Import the non-secret values from
   `deploy/railway/pilot/variables.example`.
8. Generate a unique operator password of at least 24 characters in the
   approved password manager. Set it only as the sealed Railway variable
   `RECYCLEROS_LOCAL_OPERATOR_PASSWORD`.
9. Confirm `DATABASE_URL` is a reference to the `Postgres` service and
   `RECYCLEROS_TRUSTED_HOSTS` contains the exact Railway public domain plus
   Railway's documented `healthcheck.railway.app` probe hostname.
10. Deploy only after the branch's GitHub checks pass.

Railway injects `RAILWAY_GIT_COMMIT_SHA` into GitHub-backed deployments. The
API uses that value as the release identity ahead of any provider-neutral
`RECYCLEROS_RELEASE_SHA` value, so an automatic deployment cannot report the
previous commit.

The API applies forward-only PostgreSQL migrations before starting. A failed
migration, missing database URL, missing trusted host, or failed dependency
readiness must fail deployment rather than falling back to process-local data.

## GitHub Acceptance

Create a protected GitHub environment named `railway-pilot` with the business
owner as required reviewer. Restrict it to
`codex/railway-pilot-environment`. No Railway deployment token or database URL
belongs in GitHub for this acceptance workflow.

After the live controls and recovery evidence are complete, update
`deploy/railway/pilot/pilot.contract.json` with non-secret facts only:

- Railway project ID, API URL, and exact deployed commit
- verified cost alert and hard limit
- enabled native and off-platform backups
- restore rehearsal reference
- sealed-variable, two-factor, monitoring, ownership, and approval evidence

Set `lifecycle` to `verified` only when every strict field is true. Then run:

```powershell
gh workflow run railway-pilot-acceptance.yml `
  -f contract_path=deploy/railway/pilot/pilot.contract.json `
  -f api_url=https://your-service.up.railway.app `
  -f release_sha=<exact-40-character-deployed-sha> `
  -f minimum_certificate_days=14
```

The workflow is read-only. It validates the approved contract, TLS, liveness,
readiness, release identity, security headers, and hidden API documentation.

## Field Access Rule

Begin with one named tester using the assigned operator account; never share the
credential. A second tester remains blocked until a separate durable identity is
provisioned and verified. Use only synthetic or explicitly authorized pilot
data. Field access remains no-go while any `DEF-RAILWAY-*` defect is open.

## Provider References

- [Railway pricing](https://docs.railway.com/pricing)
- [Railway cost controls](https://docs.railway.com/pricing/cost-control)
- [Config as code](https://docs.railway.com/config-as-code)
- [Private networking](https://docs.railway.com/private-networking)
- [PostgreSQL template](https://docs.railway.com/databases/postgresql)
- [Volume backups](https://docs.railway.com/volumes/backups)
