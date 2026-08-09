output "artifact_registry_repository" {
  description = "Docker repository used for pilot API images."
  value       = google_artifact_registry_repository.containers.name
}

output "cloud_sql_connection_name" {
  description = "Cloud SQL connection name used by the Cloud Run Unix socket."
  value       = google_sql_database_instance.pilot.connection_name
}

output "cloud_sql_private_ip" {
  description = "Private database address. No public database address is created."
  value       = google_sql_database_instance.pilot.private_ip_address
}

output "api_url" {
  description = "Cloud Run API URL when deploy_api is true."
  value       = try(google_cloud_run_v2_service.api[0].uri, null)
}

output "runtime_service_account" {
  description = "Cloud Run runtime identity."
  value       = google_service_account.runtime.email
}

output "operator_email" {
  description = "Initial pilot operator username."
  value       = "operator@effortlesssmoke.com"
}

output "operator_password_secret" {
  description = "Secret Manager resource containing the generated operator password."
  value       = google_secret_manager_secret.operator_password.id
}

output "uptime_check_id" {
  description = "Monitoring uptime check ID when public monitoring is enabled."
  value       = try(google_monitoring_uptime_check_config.api[0].uptime_check_id, null)
}
