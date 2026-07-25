# GCP Pilot GitHub Setup

## Approved Identity

| Field | Value |
| --- | --- |
| Google Cloud project ID | `recyleros-platform` |
| Google Cloud project number | `728951606960` |
| Pilot region | `us-east4` |
| GitHub environment | `gcp-pilot` |
| Deployment branch | `codex/gcp-pilot-environment` |

The project ID spelling above is authoritative. Do not silently change it to
`recycleros-platform`.

## Before Bootstrap

1. Confirm that billing is linked to `recyleros-platform`.
2. Create and verify a monthly budget of USD 100 with alerts at 50%, 80%, and
   100%. The first-month review ceiling is USD 150.
3. Assign the billing owner and support owner.
4. Keep `deploy/gcp/pilot/pilot.contract.json` in `planned` state.

A Google Cloud budget sends notifications but does not automatically stop
services or cap charges.

## One-Time Bootstrap

Run `deploy/gcp/pilot/bootstrap` from an authenticated Google Cloud administrator
session. Use `terraform.tfvars.example` as the input template and review the
saved plan before applying it.

The bootstrap creates:

- a versioned, non-public Terraform state bucket
- a GitHub OIDC Workload Identity Pool and provider
- a deployer service account
- project and state-bucket permissions for that deployer

It does not create a service account key. The trust condition accepts only the
configured repository and exact deployment branch.

## Protected Environment

Create a GitHub environment named `gcp-pilot` and configure:

- at least one required reviewer
- deployment branch restriction to `codex/gcp-pilot-environment`
- no environment secrets containing Google service account JSON

Add the bootstrap outputs as environment variables:

| GitHub variable | Terraform output |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | `workload_identity_provider` |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | `deployer_service_account` |
| `GCP_TERRAFORM_STATE_BUCKET` | `state_bucket` |

## First Foundation Run

1. Run `GCP Pilot Infrastructure` with operation `plan`.
2. Review the Terraform plan, especially Cloud SQL tier, disk, region, public
   networking, and Cloud Run scale limits.
3. Re-run with operation `apply` and approval text `APPLY-PILOT` only after the
   protected-environment reviewer approves billable resource creation.
4. Record the workflow URL and Terraform outputs in release evidence.

The foundation run intentionally uses `deploy_api=false`. It creates no public
field endpoint.

## First Field Release

1. Create and verify a Cloud Monitoring notification channel.
2. Run `GCP Pilot Release` with the channel resource name.
3. Enter approval text `RELEASE-PILOT`.
4. Verify readiness, login, tenant selection, and the RC1 working path.
5. Complete and record a Cloud SQL restore rehearsal before field data is used.
6. Change the contract to `verified` only when every readiness field has direct
   evidence.

The release workflow builds the existing API image, pushes it to Artifact
Registry, resolves its immutable digest, and deploys that digest to Cloud Run.
