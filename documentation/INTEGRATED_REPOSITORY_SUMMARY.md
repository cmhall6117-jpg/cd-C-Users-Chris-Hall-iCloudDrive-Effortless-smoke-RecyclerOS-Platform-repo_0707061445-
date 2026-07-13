# RecyclerOS Integrated Local Repository Summary

## Integrated Repository

Authoritative working repository:

`repo_0707061445`

This short root-level path is intentional. The scaffold packages include deeply nested generated files, and Windows path limits can interrupt operations under longer folder names.

## Packages Merged

- Development Foundation
- VS-001 Opportunity Discovery
- VS-002 Vehicle Digital Twin
- VS-003 Procurement Workspace
- VS-004 Pick List & Focus Point
- VS-005 Inventory Intake
- VS-021 Integration Readiness
- VS-022 Local Integration Bundle

## Preserved Artifacts

- Source package README and documentation files were preserved under `documentation/source_packages`.
- Incoming conflicting generated files were preserved under `documentation/integration_conflicts`.
- Postgres migrations were preserved under `database/migrations/postgres`.
- SQLite migrations were preserved under `database/migrations/sqlite`.
- Merge activity was captured in `documentation/INTEGRATION_MERGE_MANIFEST.md`.

## Backend Registration

Registered FastAPI routers in `services/api/src/main.py`:

- `/v1/health`
- `/v1/opportunities`
- `/v1/vehicles`
- `/v1/procurement`
- `/v1/harvest`
- `/v1/inventory`

## Flutter Route Registration

Registered Flutter routes in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`:

- `/`
- `/opportunities`
- `/vehicles/:vehicleCode`
- `/procurement/:opportunityId`
- `/pick-list`
- `/focus-point/:vehicleId`
- `/inventory/intake`

## Dart Model Resolution

- Promoted the fuller VS-001 `Opportunity` model shape into the active domain model.
- Promoted the fuller VS-002 `Vehicle` model shape into the active domain model.
- Resolved duplicate `ProcurementIntent` declarations by keeping `procurement_intent.dart` as canonical and importing it into `procurement_scenario.dart`.
- Expanded `recycleros_domain.dart` exports for merged models and events.
