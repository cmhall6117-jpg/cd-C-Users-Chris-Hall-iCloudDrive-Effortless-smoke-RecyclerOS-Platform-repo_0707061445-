from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Protocol
from uuid import uuid4

from tenant import TenantContext


class WorkflowStore(Protocol):
    storage_name: str

    def check_readiness(self) -> bool: ...

    def create_opportunity(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any]: ...

    def list_opportunities(self, tenant: TenantContext) -> list[dict[str, Any]]: ...

    def get_opportunity(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None: ...

    def create_vehicle(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None: ...

    def get_vehicle(
        self, vehicle_identifier: str, tenant: TenantContext
    ) -> dict[str, Any] | None: ...

    def get_or_create_procurement_analysis(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None: ...

    def create_pick_list_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None: ...

    def list_pick_list_items(self, tenant: TenantContext) -> list[dict[str, Any]]: ...

    def update_pick_list_availability(
        self,
        pick_list_item_id: str,
        availability_status: str,
        tenant: TenantContext,
    ) -> dict[str, Any] | None: ...

    def start_harvest_session(
        self, vehicle_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None: ...

    def complete_harvest_session(
        self, harvest_session_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None: ...

    def create_inventory_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None: ...

    def list_inventory_items(self, tenant: TenantContext) -> list[dict[str, Any]]: ...


class InMemoryStore:
    """Process-local RC1 store behind the API's persistence boundary."""

    storage_name = "memory"

    def __init__(self) -> None:
        self._lock = RLock()
        self._sequences: dict[str, int] = {}
        self._opportunities: dict[str, dict[str, Any]] = {}
        self._vehicles: dict[str, dict[str, Any]] = {}
        self._procurement_analyses: dict[str, dict[str, Any]] = {}
        self._pick_list_items: dict[str, dict[str, Any]] = {}
        self._harvest_sessions: dict[str, dict[str, Any]] = {}
        self._inventory_items: dict[str, dict[str, Any]] = {}

    def check_readiness(self) -> bool:
        return True

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _id() -> str:
        return str(uuid4())

    def _code(self, prefix: str) -> str:
        self._sequences[prefix] = self._sequences.get(prefix, 0) + 1
        return f"{prefix}-{self._sequences[prefix]:06d}"

    @staticmethod
    def _tenant_fields(tenant: TenantContext) -> dict[str, str]:
        return {
            "organization_id": tenant.organization_id,
            "workspace_id": tenant.workspace_id,
        }

    @staticmethod
    def _belongs_to(record: dict[str, Any], tenant: TenantContext) -> bool:
        return (
            record["organization_id"] == tenant.organization_id
            and record["workspace_id"] == tenant.workspace_id
        )

    def create_opportunity(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any]:
        with self._lock:
            opportunity_id = self._id()
            record = {
                "opportunity_id": opportunity_id,
                "opportunity_code": self._code("OPP"),
                **self._tenant_fields(tenant),
                **values,
                "status": "discovered",
                "vehicle_id": None,
                "created_at": self._now(),
                "event_created": "opportunity.discovered",
            }
            self._opportunities[opportunity_id] = record
            return deepcopy(record)

    def list_opportunities(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._lock:
            return [
                deepcopy(record)
                for record in self._opportunities.values()
                if self._belongs_to(record, tenant)
            ]

    def get_opportunity(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._lock:
            record = self._opportunities.get(opportunity_id)
            if record is None or not self._belongs_to(record, tenant):
                return None
            return deepcopy(record)

    def create_vehicle(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._lock:
            opportunity_id = values.pop("opportunity_id", None)
            opportunity = None
            if opportunity_id is not None:
                opportunity = self._opportunities.get(opportunity_id)
                if opportunity is None or not self._belongs_to(opportunity, tenant):
                    return None

            vehicle_id = self._id()
            now = self._now()
            record = {
                "vehicle_id": vehicle_id,
                "vehicle_code": self._code("VEH"),
                **self._tenant_fields(tenant),
                **values,
                "opportunity_id": opportunity_id,
                "lifecycle_status": "discovered",
                "created_at": now,
                "updated_at": now,
                "timeline": [
                    {
                        "event_type": "vehicle.created",
                        "title": "Vehicle Record Created",
                        "occurred_at": now,
                    }
                ],
                "event_created": "vehicle.created",
            }
            self._vehicles[vehicle_id] = record
            if opportunity is not None:
                opportunity["vehicle_id"] = vehicle_id
                opportunity["status"] = "converted"
            return deepcopy(record)

    def get_vehicle(
        self, vehicle_identifier: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._lock:
            record = self._vehicles.get(vehicle_identifier)
            if record is None:
                record = next(
                    (
                        item
                        for item in self._vehicles.values()
                        if item["vehicle_code"] == vehicle_identifier
                    ),
                    None,
                )
            if record is None or not self._belongs_to(record, tenant):
                return None
            return deepcopy(record)

    def get_or_create_procurement_analysis(
        self, opportunity_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._lock:
            opportunity = self._opportunities.get(opportunity_id)
            if opportunity is None or not self._belongs_to(opportunity, tenant):
                return None

            existing = self._procurement_analyses.get(opportunity_id)
            if existing is not None:
                return deepcopy(existing)

            record = {
                "procurement_analysis_id": self._id(),
                **self._tenant_fields(tenant),
                "opportunity_id": opportunity_id,
                "auction_access_type": "nonDealerPublic",
                "recommended_intent": opportunity["procurement_intent"],
                "scenarios": [
                    {
                        "intent": "resale",
                        "projected_revenue": 9500,
                        "projected_costs": 7550,
                        "recommended_max_bid": 4800,
                        "projected_net_profit": 1950,
                        "projected_margin_percent": 20.5,
                        "confidence_score": 72,
                    },
                    {
                        "intent": "personalUse",
                        "projected_revenue": 0,
                        "projected_costs": 5300,
                        "recommended_max_bid": 5300,
                        "projected_net_profit": 0,
                        "projected_margin_percent": 0,
                        "confidence_score": 65,
                    },
                    {
                        "intent": "partOut",
                        "projected_revenue": 8500,
                        "projected_costs": 5250,
                        "recommended_max_bid": 3900,
                        "projected_net_profit": 3250,
                        "projected_margin_percent": 38.2,
                        "confidence_score": 81,
                    },
                ],
                "created_at": self._now(),
            }
            self._procurement_analyses[opportunity_id] = record
            return deepcopy(record)

    def create_pick_list_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._lock:
            vehicle = self._vehicles.get(values["vehicle_id"])
            if vehicle is None or not self._belongs_to(vehicle, tenant):
                return None

            item_id = self._id()
            record = {
                "pick_list_item_id": item_id,
                **self._tenant_fields(tenant),
                **values,
                "availability_status": values.get("availability_status", "pending"),
                "created_at": self._now(),
            }
            self._pick_list_items[item_id] = record
            return deepcopy(record)

    def list_pick_list_items(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._lock:
            return [
                deepcopy(record)
                for record in self._pick_list_items.values()
                if self._belongs_to(record, tenant)
            ]

    def update_pick_list_availability(
        self,
        pick_list_item_id: str,
        availability_status: str,
        tenant: TenantContext,
    ) -> dict[str, Any] | None:
        with self._lock:
            record = self._pick_list_items.get(pick_list_item_id)
            if record is None or not self._belongs_to(record, tenant):
                return None
            record["availability_status"] = availability_status
            record["updated_at"] = self._now()
            return deepcopy(record)

    def start_harvest_session(
        self, vehicle_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._lock:
            vehicle = self._vehicles.get(vehicle_id)
            if vehicle is None or not self._belongs_to(vehicle, tenant):
                return None

            session_id = self._id()
            record = {
                "harvest_session_id": session_id,
                **self._tenant_fields(tenant),
                "vehicle_id": vehicle_id,
                "started_at": self._now(),
                "ended_at": None,
                "status": "active",
                "timer_status": "active",
                "event_created": "focus_point.started",
            }
            self._harvest_sessions[session_id] = record
            return deepcopy(record)

    def complete_harvest_session(
        self, harvest_session_id: str, tenant: TenantContext
    ) -> dict[str, Any] | None:
        with self._lock:
            record = self._harvest_sessions.get(harvest_session_id)
            if record is None or not self._belongs_to(record, tenant):
                return None
            record["ended_at"] = self._now()
            record["status"] = "completed"
            record["timer_status"] = "stopped"
            record["event_created"] = "focus_point.completed"
            return deepcopy(record)

    def create_inventory_item(
        self, tenant: TenantContext, values: dict[str, Any]
    ) -> dict[str, Any] | None:
        with self._lock:
            vehicle_id = values.get("source_vehicle_id")
            if vehicle_id is not None:
                vehicle = self._vehicles.get(vehicle_id)
                if vehicle is None or not self._belongs_to(vehicle, tenant):
                    return None

            session_id = values.get("harvest_session_id")
            if session_id is not None:
                session = self._harvest_sessions.get(session_id)
                if session is None or not self._belongs_to(session, tenant):
                    return None

            item_id = self._id()
            now = self._now()
            record = {
                "inventory_item_id": item_id,
                "inventory_code": self._code("INV"),
                **self._tenant_fields(tenant),
                **values,
                "created_at": now,
                "updated_at": now,
                "event_created": "inventory.created",
            }
            self._inventory_items[item_id] = record
            return deepcopy(record)

    def list_inventory_items(self, tenant: TenantContext) -> list[dict[str, Any]]:
        with self._lock:
            return [
                deepcopy(record)
                for record in self._inventory_items.values()
                if self._belongs_to(record, tenant)
            ]
