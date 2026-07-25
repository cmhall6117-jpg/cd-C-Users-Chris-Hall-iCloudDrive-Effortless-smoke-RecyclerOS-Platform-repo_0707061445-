output "deployer_service_account" {
  description = "GitHub Actions service account email."
  value       = google_service_account.deployer.email
}

output "state_bucket" {
  description = "Terraform state bucket name."
  value       = google_storage_bucket.terraform_state.name
}

output "workload_identity_provider" {
  description = "Full provider resource name used by google-github-actions/auth."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "github_deploy_ref" {
  description = "Only this Git ref is currently trusted to deploy."
  value       = var.github_deploy_ref
}
