# SQLite Migration Order

Run migrations in this order after merging packages:

1. 001_initial_offline_schema.sql
2. 002_opportunity_discovery.sql
3. 003_vehicle_digital_twin.sql
4. 004_procurement_workspace.sql
5. 005_pick_list_focus_point.sql
6. 006_inventory_intake.sql
7. 007_sales_fulfillment.sql
8. 008_kpi_mission_control.sql
9. 009_cycle_count_inventory_accuracy.sql
10. 010_scrap_vehicle_closeout.sql
11. 011_compliance_disposal.sql
12. 012_revenue_growth_promotions.sql
13. 013_customer_intelligence.sql
14. 014_financial_intelligence.sql
15. 015_rules_decision_engine.sql
16. 016_search_knowledge_center.sql
17. 017_notification_task_center.sql
18. 018_sync_health_device_status.sql
19. 019_admin_users_roles.sql
20. 020_audit_trail_event_viewer.sql
21. 021_registers_release_binders.sql

Important: SQLite ALTER TABLE statements must be guarded by a migration manager to prevent duplicate-column errors.
