# Production Environment Provisioning

## Current Decision

No cloud provider, account, region, public domain, registry, managed database,
secret manager, or monitoring destination has been approved. Repository tooling
is therefore provider-neutral and creates no billable resources.

## Provider Mapping

| Capability | AWS | Azure | Google Cloud |
| --- | --- | --- | --- |
| Container registry | ECR | ACR | Artifact Registry |
| Container runtime | ECS/Fargate | Container Apps | Cloud Run |
| PostgreSQL | RDS for PostgreSQL | PostgreSQL Flexible Server | Cloud SQL |
| Public TLS route | ALB, ACM, Route 53 | Front Door, managed certificate, DNS | Load Balancer, Certificate Manager, Cloud DNS |
| Secrets | Secrets Manager | Key Vault | Secret Manager |
| Logs and alerts | CloudWatch | Azure Monitor | Cloud Monitoring |

The business owner must select one provider and approve its expected monthly
cost, billing alerts, account ownership, region, and support level before IaC or
live resources are created.

## Provisioning Order

1. Approve provider, account, region, budget, and billing alerts.
2. Create a private registry and an image-signing policy.
3. Provision a private PostgreSQL 16+ service with TLS, storage encryption,
   deletion protection, high availability, backups, and point-in-time recovery.
4. Create a least-privilege database runtime role and a separate migration role.
5. Configure the secret manager and deployment identity; do not copy credentials
   into the repository or environment contract.
6. Provision the container runtime, private database route, public TLS route,
   DNS, and exact proxy networks.
7. Connect logs, metrics, uptime checks, and alert delivery. Test the alert route.
8. Assign deployment, restore, incident, security, support, and business owners.
9. Complete a target-environment backup and restore rehearsal.
10. Commit a completed `deploy/production/environment.json` with no credentials.
11. Configure the protected GitHub `production` environment and run acceptance.

## GitHub Production Environment

Create a GitHub environment named `production` with required reviewers and no
self-approval. Restrict deployment branches to the approved release branch. Add
the dedicated verification connection as the environment secret
`PRODUCTION_DATABASE_VERIFY_URL`; it must require TLS and use a limited role
with read access only to the readiness and migration evidence queried by the tool.

The managed-database job requires a self-hosted Linux runner labelled
`recycleros-production` inside the private database network. Protect the runner
with the GitHub environment reviewers, give it no production deployment
credential, and remove or disable it after acceptance. Never make PostgreSQL
publicly accessible for a hosted CI runner.

The manual workflow `.github/workflows/production-environment-acceptance.yml`
does not deploy. After approval it checks the committed contract, public TLS and
health surface, release identity, security headers, hidden docs, managed database
TLS, role privileges, schema, active ownership, and every migration checksum.

Run it only after the environment is provisioned:

```powershell
gh workflow run production-environment-acceptance.yml `
  -f contract_path=deploy/production/environment.json `
  -f api_url=https://api.your-approved-domain.example `
  -f release_sha=<exact-40-character-release-sha> `
  -f minimum_certificate_days=14
```

The URL and SHA inputs must exactly match the committed contract. Retain the
approved workflow run with the release record.

## No-Go Rule

Do not add provider credentials, provision resources, publish the image, create
DNS, or open traffic until the provider/cost decision and accountable approvals
exist. Passing repository CI is preparation evidence, not production authority.
