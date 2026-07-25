# GCP Pilot Bootstrap

This root creates only the Terraform state bucket, keyless GitHub trust, and the
deployer identity needed by the repeatable pilot environment. It is intentionally
separate because GitHub cannot use Workload Identity Federation until the trust
relationship exists.

Run it once from an authenticated administrator session such as Google Cloud
Shell. Review the plan before applying it:

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out bootstrap.tfplan
terraform apply bootstrap.tfplan
```

Record the three outputs as GitHub environment variables:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_DEPLOYER_SERVICE_ACCOUNT`
- `GCP_TERRAFORM_STATE_BUCKET`

The provider accepts only the exact repository and branch in
`github_deploy_ref`. Change that constraint deliberately when the deployment
branch changes. Do not create or download a service account key.
