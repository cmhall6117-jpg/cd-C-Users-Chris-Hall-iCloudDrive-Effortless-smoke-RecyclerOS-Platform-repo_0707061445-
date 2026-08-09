from typing import Any

from tenant import TenantContext


class PostgresStore:
    """Durable RC1 workflow store backed by the consolidated PostgreSQL schema."""

    storage_name = "postgres"

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("database_url is required")
        self._database_url = database_url

    def _connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL runtime requires services/api/requirements-postgres.txt"
            ) from exc
        return psycopg.connect(self._database_url, row_factory=dict_row)

    def check_readiness(self) -> bool:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    to_regclass('public.opportunities') IS NOT NULL
                    AND to_regclass('public.vehicles') IS NOT NULL
                    AND to_regclass('public.inventory_items') IS NOT NULL
                    AND to_regclass('public.rc1_code_sequences') IS NOT NULL
                    AS ready
                """
            )
            return bool(cursor.fetchone()["ready"])

    @staticmethod
    def _tenant_values(tenant: TenantContext) -> tuple[str, str]:
        return tenant.organization_id, tenant.workspace_id

    @staticmethod
    def _next_code(cursor, prefix: str) -> str:
        cursor.execute(
            """
            UPDATE rc1_code_sequences
            SET next_value = next_value + 1
            WHERE prefix = %s
            RETURNING next_value - 1 AS value
            """,
            (prefix,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Missing RC1 code sequence for {prefix}.")
        return f"{prefix}-{row['value']:06d}"

    def create_opportunity(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cursor:
            code = self._next_code(cursor, "OPP")
            cursor.execute(
                """
                INSERT INTO opportunities (
                    opportunity_code,
                    organization_id,
                    workspace_id,
                    title,
                    source_type,
                    procurement_intent,
                    vin,
                    year,
                    make,
                    model,
                    estimated_max_bid,
                    estimated_net_profit,
                    confidence_score,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    'discovered'
                )
                RETURNING
                    id AS opportunity_id,
                    opportunity_code,
                    organization_id,
                    workspace_id,
                    title,
                    source_type,
                    procurement_intent,
                    vin,
                    year,
                    make,
                    model,
                    estimated_max_bid,
                    estimated_net_profit,
                    confidence_score,
                    status,
                    vehicle_id,
                    created_at
                """,
                (
                    code,
                    *self._tenant_values(tenant),
                    values["title"],
                    values.get("source_type", "manual"),
                    values.get("procurement_intent", "undecided"),
                    values.get("vin"),
                    values.get("year"),
                    values.get("make"),
                    values.get("model"),
                    values.get("estimated_max_bid"),
                    values.get("estimated_net_profit"),
                    values.get("confidence_score"),
                ),
            )
            record = dict(cursor.fetchone())
            record["event_created"] = "opportunity.discovered"
            return record

    def list_opportunities(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id AS opportunity_id,
                    opportunity_code,
                    organization_id,
                    workspace_id,
                    title,
                    source_type,
                    procurement_intent,
                    vin,
                    year,
                    make,
                    model,
                    estimated_max_bid,
                    estimated_net_profit,
                    confidence_score,
                    status,
                    vehicle_id,
                    created_at
                FROM opportunities
                WHERE organization_id = %s AND workspace_id = %s
                ORDER BY created_at, id
                """,
                self._tenant_values(tenant),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_opportunity(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id AS opportunity_id,
                    opportunity_code,
                    organization_id,
                    workspace_id,
                    title,
                    source_type,
                    procurement_intent,
                    vin,
                    year,
                    make,
                    model,
                    estimated_max_bid,
                    estimated_net_profit,
                    confidence_score,
                    status,
                    vehicle_id,
                    created_at
                FROM opportunities
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                """,
                (opportunity_id, *self._tenant_values(tenant)),
            )
            row = cursor.fetchone()
            return None if row is None else dict(row)

    def create_vehicle(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        opportunity_id = values.get("opportunity_id")
        with self._connect() as conn, conn.cursor() as cursor:
            if opportunity_id is not None:
                cursor.execute(
                    """
                    SELECT id
                    FROM opportunities
                    WHERE id::text = %s
                      AND organization_id = %s
                      AND workspace_id = %s
                    FOR UPDATE
                    """,
                    (opportunity_id, *self._tenant_values(tenant)),
                )
                if cursor.fetchone() is None:
                    return None

            code = self._next_code(cursor, "VEH")
            cursor.execute(
                """
                INSERT INTO vehicles (
                    vehicle_code,
                    organization_id,
                    workspace_id,
                    vin,
                    year,
                    make,
                    model,
                    trim,
                    engine,
                    transmission,
                    drivetrain,
                    mileage,
                    lifecycle_status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    'discovered'
                )
                RETURNING
                    id AS vehicle_id,
                    vehicle_code,
                    organization_id,
                    workspace_id,
                    vin,
                    year,
                    make,
                    model,
                    trim,
                    engine,
                    transmission,
                    drivetrain,
                    mileage,
                    lifecycle_status,
                    created_at,
                    updated_at
                """,
                (
                    code,
                    *self._tenant_values(tenant),
                    values.get("vin"),
                    values.get("year"),
                    values.get("make"),
                    values.get("model"),
                    values.get("trim"),
                    values.get("engine"),
                    values.get("transmission"),
                    values.get("drivetrain"),
                    values.get("mileage"),
                ),
            )
            record = dict(cursor.fetchone())
            vehicle_id = record["vehicle_id"]
            record["opportunity_id"] = opportunity_id
            record["event_created"] = "vehicle.created"

            cursor.execute(
                """
                INSERT INTO vehicle_timeline (
                    vehicle_id,
                    organization_id,
                    workspace_id,
                    title,
                    occurred_at
                )
                VALUES (%s, %s, %s, 'Vehicle Record Created', %s)
                RETURNING title, occurred_at
                """,
                (
                    vehicle_id,
                    *self._tenant_values(tenant),
                    record["created_at"],
                ),
            )
            timeline = dict(cursor.fetchone())
            timeline["event_type"] = "vehicle.created"
            record["timeline"] = [timeline]

            if opportunity_id is not None:
                cursor.execute(
                    """
                    UPDATE opportunities
                    SET vehicle_id = %s, status = 'converted'
                    WHERE id::text = %s
                      AND organization_id = %s
                      AND workspace_id = %s
                    """,
                    (
                        vehicle_id,
                        opportunity_id,
                        *self._tenant_values(tenant),
                    ),
                )
            return record

    def get_vehicle(
        self, vehicle_identifier: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    v.id AS vehicle_id,
                    v.vehicle_code,
                    v.organization_id,
                    v.workspace_id,
                    v.vin,
                    v.year,
                    v.make,
                    v.model,
                    v.trim,
                    v.engine,
                    v.transmission,
                    v.drivetrain,
                    v.mileage,
                    v.lifecycle_status,
                    v.created_at,
                    v.updated_at,
                    o.id AS opportunity_id
                FROM vehicles v
                LEFT JOIN opportunities o
                  ON o.vehicle_id = v.id
                 AND o.organization_id = v.organization_id
                 AND o.workspace_id = v.workspace_id
                WHERE (v.id::text = %s OR v.vehicle_code = %s)
                  AND v.organization_id = %s
                  AND v.workspace_id = %s
                """,
                (
                    vehicle_identifier,
                    vehicle_identifier,
                    *self._tenant_values(tenant),
                ),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            record = dict(row)
            cursor.execute(
                """
                SELECT title, description, occurred_at
                FROM vehicle_timeline
                WHERE vehicle_id = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                ORDER BY occurred_at, id
                """,
                (record["vehicle_id"], *self._tenant_values(tenant)),
            )
            record["timeline"] = [dict(item) for item in cursor.fetchall()]
            for item in record["timeline"]:
                item["event_type"] = "vehicle.created"
            return record

    def get_or_create_procurement_analysis(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (opportunity_id,))
            cursor.execute(
                """
                SELECT procurement_intent
                FROM opportunities
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                """,
                (opportunity_id, *self._tenant_values(tenant)),
            )
            opportunity = cursor.fetchone()
            if opportunity is None:
                return None

            cursor.execute(
                """
                SELECT
                    id AS procurement_analysis_id,
                    organization_id,
                    workspace_id,
                    opportunity_id,
                    auction_access_type,
                    recommended_intent,
                    created_at
                FROM procurement_analyses
                WHERE opportunity_id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                ORDER BY created_at
                LIMIT 1
                """,
                (opportunity_id, *self._tenant_values(tenant)),
            )
            analysis = cursor.fetchone()
            if analysis is None:
                cursor.execute(
                    """
                    INSERT INTO procurement_analyses (
                        opportunity_id,
                        organization_id,
                        workspace_id,
                        auction_access_type,
                        recommended_intent
                    )
                    VALUES (%s, %s, %s, 'nonDealerPublic', %s)
                    RETURNING
                        id AS procurement_analysis_id,
                        organization_id,
                        workspace_id,
                        opportunity_id,
                        auction_access_type,
                        recommended_intent,
                        created_at
                    """,
                    (
                        opportunity_id,
                        *self._tenant_values(tenant),
                        opportunity["procurement_intent"],
                    ),
                )
                analysis = cursor.fetchone()
                scenarios = (
                    ("resale", 9500, 7550, 4800, 1950, 20.5, 72),
                    ("personalUse", 0, 5300, 5300, 0, 0, 65),
                    ("partOut", 8500, 5250, 3900, 3250, 38.2, 81),
                )
                for scenario in scenarios:
                    cursor.execute(
                        """
                        INSERT INTO procurement_scenarios (
                            procurement_analysis_id,
                            organization_id,
                            workspace_id,
                            intent,
                            projected_revenue,
                            projected_costs,
                            recommended_max_bid,
                            projected_net_profit,
                            projected_margin_percent,
                            confidence_score
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            analysis["procurement_analysis_id"],
                            *self._tenant_values(tenant),
                            *scenario,
                        ),
                    )

            record = dict(analysis)
            cursor.execute(
                """
                SELECT
                    intent,
                    projected_revenue,
                    projected_costs,
                    recommended_max_bid,
                    projected_net_profit,
                    projected_margin_percent,
                    confidence_score
                FROM procurement_scenarios
                WHERE procurement_analysis_id = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                ORDER BY id
                """,
                (
                    record["procurement_analysis_id"],
                    *self._tenant_values(tenant),
                ),
            )
            record["scenarios"] = [dict(row) for row in cursor.fetchall()]
            return record

    def create_pick_list_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM vehicles
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                """,
                (values["vehicle_id"], *self._tenant_values(tenant)),
            )
            if cursor.fetchone() is None:
                return None
            cursor.execute(
                """
                INSERT INTO pick_list_items (
                    vehicle_id,
                    organization_id,
                    workspace_id,
                    yard_name,
                    yard_row,
                    availability_status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id AS pick_list_item_id,
                    organization_id,
                    workspace_id,
                    vehicle_id,
                    yard_name,
                    yard_row,
                    availability_status,
                    created_at
                """,
                (
                    values["vehicle_id"],
                    *self._tenant_values(tenant),
                    values["yard_name"],
                    values.get("yard_row"),
                    values.get("availability_status", "pending"),
                ),
            )
            return dict(cursor.fetchone())

    def list_pick_list_items(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id AS pick_list_item_id,
                    organization_id,
                    workspace_id,
                    vehicle_id,
                    yard_name,
                    yard_row,
                    availability_status,
                    created_at
                FROM pick_list_items
                WHERE organization_id = %s AND workspace_id = %s
                ORDER BY created_at, id
                """,
                self._tenant_values(tenant),
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_pick_list_availability(
        self,
        pick_list_item_id: str,
        availability_status: str,
        tenant: TenantContext,
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE pick_list_items
                SET availability_status = %s
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                RETURNING
                    id AS pick_list_item_id,
                    organization_id,
                    workspace_id,
                    vehicle_id,
                    yard_name,
                    yard_row,
                    availability_status,
                    created_at,
                    NOW() AS updated_at
                """,
                (
                    availability_status,
                    pick_list_item_id,
                    *self._tenant_values(tenant),
                ),
            )
            row = cursor.fetchone()
            return None if row is None else dict(row)

    def start_harvest_session(
        self, vehicle_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM vehicles
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                """,
                (vehicle_id, *self._tenant_values(tenant)),
            )
            if cursor.fetchone() is None:
                return None
            cursor.execute(
                """
                INSERT INTO harvest_sessions (
                    vehicle_id,
                    organization_id,
                    workspace_id,
                    status
                )
                VALUES (%s, %s, %s, 'active')
                RETURNING
                    id AS harvest_session_id,
                    organization_id,
                    workspace_id,
                    vehicle_id,
                    started_at,
                    ended_at,
                    status
                """,
                (vehicle_id, *self._tenant_values(tenant)),
            )
            record = dict(cursor.fetchone())
            record["timer_status"] = "active"
            record["event_created"] = "focus_point.started"
            return record

    def complete_harvest_session(
        self, harvest_session_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE harvest_sessions
                SET ended_at = NOW(), status = 'completed'
                WHERE id::text = %s
                  AND organization_id = %s
                  AND workspace_id = %s
                RETURNING
                    id AS harvest_session_id,
                    organization_id,
                    workspace_id,
                    vehicle_id,
                    started_at,
                    ended_at,
                    status
                """,
                (harvest_session_id, *self._tenant_values(tenant)),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            record = dict(row)
            record["timer_status"] = "stopped"
            record["event_created"] = "focus_point.completed"
            return record

    def _resolve_storage_location(
        self,
        cursor,
        location_identifier: str | None,
        tenant: TenantContext,
    ) -> tuple[bool, Any | None]:
        if location_identifier is None:
            return True, None
        cursor.execute(
            """
            SELECT id, organization_id, workspace_id
            FROM storage_locations
            WHERE id::text = %s OR location_code = %s
            LIMIT 1
            """,
            (location_identifier, location_identifier),
        )
        row = cursor.fetchone()
        if row is not None:
            belongs = (
                row["organization_id"] == tenant.organization_id
                and row["workspace_id"] == tenant.workspace_id
            )
            return belongs, row["id"] if belongs else None
        cursor.execute(
            """
            INSERT INTO storage_locations (
                location_code,
                name,
                organization_id,
                workspace_id
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                location_identifier,
                location_identifier,
                *self._tenant_values(tenant),
            ),
        )
        return True, cursor.fetchone()["id"]

    def create_inventory_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cursor:
            vehicle_id = values.get("source_vehicle_id")
            if vehicle_id is not None:
                cursor.execute(
                    """
                    SELECT id
                    FROM vehicles
                    WHERE id::text = %s
                      AND organization_id = %s
                      AND workspace_id = %s
                    """,
                    (vehicle_id, *self._tenant_values(tenant)),
                )
                if cursor.fetchone() is None:
                    return None

            session_id = values.get("harvest_session_id")
            if session_id is not None:
                cursor.execute(
                    """
                    SELECT id
                    FROM harvest_sessions
                    WHERE id::text = %s
                      AND organization_id = %s
                      AND workspace_id = %s
                    """,
                    (session_id, *self._tenant_values(tenant)),
                )
                if cursor.fetchone() is None:
                    return None

            location_ok, location_id = self._resolve_storage_location(
                cursor,
                values.get("storage_location_id"),
                tenant,
            )
            if not location_ok:
                return None

            code = self._next_code(cursor, "INV")
            cursor.execute(
                """
                INSERT INTO inventory_items (
                    inventory_code,
                    organization_id,
                    workspace_id,
                    part_name,
                    source_vehicle_id,
                    harvest_session_id,
                    storage_location_id,
                    condition,
                    status,
                    quantity,
                    estimated_value
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id AS inventory_item_id,
                    inventory_code,
                    organization_id,
                    workspace_id,
                    part_name,
                    source_vehicle_id,
                    harvest_session_id,
                    storage_location_id,
                    condition,
                    status,
                    quantity,
                    estimated_value,
                    created_at,
                    updated_at
                """,
                (
                    code,
                    *self._tenant_values(tenant),
                    values["part_name"],
                    vehicle_id,
                    session_id,
                    location_id,
                    values.get("condition", "usedUntested"),
                    values.get("status", "available"),
                    values.get("quantity", 1),
                    values.get("estimated_value"),
                ),
            )
            record = dict(cursor.fetchone())
            record["event_created"] = "inventory.created"
            return record

    def list_inventory_items(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id AS inventory_item_id,
                    inventory_code,
                    organization_id,
                    workspace_id,
                    part_name,
                    source_vehicle_id,
                    harvest_session_id,
                    storage_location_id,
                    condition,
                    status,
                    quantity,
                    estimated_value,
                    created_at,
                    updated_at
                FROM inventory_items
                WHERE organization_id = %s AND workspace_id = %s
                ORDER BY created_at, id
                """,
                self._tenant_values(tenant),
            )
            return [dict(row) for row in cursor.fetchall()]
