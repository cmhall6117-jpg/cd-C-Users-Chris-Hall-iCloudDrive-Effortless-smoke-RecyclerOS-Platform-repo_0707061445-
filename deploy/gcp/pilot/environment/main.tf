locals {
  services = toset([
    "artifactregistry.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "servicenetworking.googleapis.com",
    "sqladmin.googleapis.com",
  ])

  runtime_project_roles = toset([
    "roles/cloudsql.client",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])

  create_public_monitoring = (
    var.deploy_api &&
    var.allow_unauthenticated_api &&
    length(var.notification_channel_ids) > 0
  )
}

resource "google_project_service" "pilot" {
  for_each = local.services

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "containers" {
  project       = var.project_id
  location      = var.region
  repository_id = "recycleros-pilot"
  description   = "RecyclerOS pilot container images"
  format        = "DOCKER"

  cleanup_policies {
    id     = "retain-recent-versions"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }

  cleanup_policies {
    id     = "delete-old-versions"
    action = "DELETE"

    condition {
      older_than = "2592000s"
    }
  }

  depends_on = [google_project_service.pilot]
}

resource "google_compute_network" "pilot" {
  project                 = var.project_id
  name                    = "recycleros-pilot"
  auto_create_subnetworks = false

  depends_on = [google_project_service.pilot]
}

resource "google_compute_subnetwork" "cloud_run" {
  project                  = var.project_id
  name                     = "recycleros-pilot-cloud-run"
  region                   = var.region
  network                  = google_compute_network.pilot.id
  ip_cidr_range            = "10.42.0.0/26"
  private_ip_google_access = true
}

resource "google_compute_global_address" "private_services" {
  project       = var.project_id
  name          = "recycleros-pilot-private-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 24
  network       = google_compute_network.pilot.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.pilot.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_services.name]

  depends_on = [google_project_service.pilot]
}

resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = "recycleros-pilot-runtime"
  display_name = "RecyclerOS pilot Cloud Run runtime"

  depends_on = [google_project_service.pilot]
}

resource "google_project_iam_member" "runtime" {
  for_each = local.runtime_project_roles

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_sql_database_instance" "pilot" {
  project             = var.project_id
  name                = "recycleros-pilot-pg16"
  region              = var.region
  database_version    = "POSTGRES_16"
  deletion_protection = true

  settings {
    edition           = "ENTERPRISE"
    tier              = "db-g1-small"
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 25
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                     = "05:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7

      backup_retention_settings {
        retained_backups = 14
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.pilot.id
      enable_private_path_for_google_cloud_services = true
    }

    maintenance_window {
      day          = 7
      hour         = 7
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = false
      record_client_address   = false
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "application" {
  project  = var.project_id
  name     = "recycleros_pilot"
  instance = google_sql_database_instance.pilot.name
}

ephemeral "random_password" "database" {
  length  = 32
  special = false
}

resource "google_sql_user" "application" {
  project             = var.project_id
  name                = "recycleros_runtime"
  instance            = google_sql_database_instance.pilot.name
  password_wo         = ephemeral.random_password.database.result
  password_wo_version = var.database_password_version
}

resource "google_secret_manager_secret" "database_url" {
  project   = var.project_id
  secret_id = "recycleros-pilot-database-url"

  replication {
    auto {}
  }

  depends_on = [google_project_service.pilot]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret = google_secret_manager_secret.database_url.id
  secret_data_wo = format(
    "postgresql://recycleros_runtime:%s@/recycleros_pilot?host=/cloudsql/%s&sslmode=disable",
    ephemeral.random_password.database.result,
    google_sql_database_instance.pilot.connection_name,
  )
  secret_data_wo_version = var.database_password_version

  depends_on = [
    google_sql_database.application,
    google_sql_user.application,
  ]
}

ephemeral "random_password" "operator" {
  length           = 32
  special          = true
  override_special = "!#%+,-.:=?@_"
}

resource "google_secret_manager_secret" "operator_password" {
  project   = var.project_id
  secret_id = "recycleros-pilot-operator-password"

  replication {
    auto {}
  }

  depends_on = [google_project_service.pilot]
}

resource "google_secret_manager_secret_version" "operator_password" {
  secret                 = google_secret_manager_secret.operator_password.id
  secret_data_wo         = ephemeral.random_password.operator.result
  secret_data_wo_version = var.operator_password_version
}

resource "google_secret_manager_secret_iam_member" "database_url_runtime" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_secret_manager_secret_iam_member" "operator_password_runtime" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.operator_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "api" {
  count = var.deploy_api ? 1 : 0

  project             = var.project_id
  name                = "recycleros-pilot-api"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false

  template {
    service_account                  = google_service_account.runtime.email
    timeout                          = "60s"
    max_instance_request_concurrency = 20

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    vpc_access {
      egress = "PRIVATE_RANGES_ONLY"

      network_interfaces {
        network    = google_compute_network.pilot.name
        subnetwork = google_compute_subnetwork.cloud_run.name
        tags       = ["recycleros-pilot-api"]
      }
    }

    volumes {
      name = "cloudsql"

      cloud_sql_instance {
        instances = [google_sql_database_instance.pilot.connection_name]
      }
    }

    containers {
      image = var.api_image

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "RECYCLEROS_DEPLOYMENT_MODE"
        value = "pilot"
      }

      env {
        name  = "RECYCLEROS_RELEASE_SHA"
        value = var.release_sha
      }

      env {
        name  = "RECYCLEROS_TRUSTED_HOSTS"
        value = "*.run.app"
      }

      env {
        name  = "RECYCLEROS_CORS_ORIGINS"
        value = var.cors_origins
      }

      env {
        name = "DATABASE_URL"

        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "RECYCLEROS_LOCAL_OPERATOR_PASSWORD"

        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.operator_password.secret_id
            version = "latest"
          }
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      startup_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 5
        period_seconds        = 5
        failure_threshold     = 12

        http_get {
          path = "/v1/health/ready"
          port = 8000
        }
      }

      liveness_probe {
        initial_delay_seconds = 0
        timeout_seconds       = 5
        period_seconds        = 15
        failure_threshold     = 4

        http_get {
          path = "/v1/health/live"
          port = 8000
        }
      }
    }
  }

  depends_on = [
    google_project_iam_member.runtime,
    google_secret_manager_secret_iam_member.database_url_runtime,
    google_secret_manager_secret_iam_member.operator_password_runtime,
    google_secret_manager_secret_version.database_url,
    google_secret_manager_secret_version.operator_password,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_api" {
  count = var.deploy_api && var.allow_unauthenticated_api ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_monitoring_uptime_check_config" "api" {
  count = local.create_public_monitoring ? 1 : 0

  project      = var.project_id
  display_name = "RecyclerOS pilot API readiness"
  timeout      = "10s"
  period       = "60s"
  checker_type = "STATIC_IP_CHECKERS"

  monitored_resource {
    type = "uptime_url"
    labels = {
      host       = trimprefix(google_cloud_run_v2_service.api[0].uri, "https://")
      project_id = var.project_id
    }
  }

  http_check {
    path         = "/v1/health/ready"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  depends_on = [google_cloud_run_v2_service_iam_member.public_api]
}

resource "google_monitoring_alert_policy" "api_unavailable" {
  count = local.create_public_monitoring ? 1 : 0

  project      = var.project_id
  display_name = "RecyclerOS pilot API unavailable"
  combiner     = "OR"

  conditions {
    display_name = "Readiness check failed"

    condition_threshold {
      filter = format(
        "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"%s\"",
        google_monitoring_uptime_check_config.api[0].uptime_check_id,
      )
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      duration        = "120s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_NEXT_OLDER"
        cross_series_reducer = "REDUCE_COUNT_TRUE"
        group_by_fields      = ["resource.label.host"]
      }
    }
  }

  notification_channels = var.notification_channel_ids

  documentation {
    content   = "RecyclerOS pilot readiness has failed. Follow the pilot runbook before resuming field tests."
    mime_type = "text/markdown"
  }
}
