from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from tenant import TenantContext, require_tenant_context

router = APIRouter()

@router.post('/focus-point/start')
def start_focus_point(vehicle_id: str, tenant: TenantContext = Depends(require_tenant_context)):
    now = datetime.now(timezone.utc)
    return {'harvest_session_id': 'HVS-DEMO-000001', 'organization_id': tenant.organization_id, 'workspace_id': tenant.workspace_id, 'vehicle_id': vehicle_id, 'started_at': now.isoformat(), 'event_created': 'focus_point.started', 'timer_status': 'active'}

@router.post('/focus-point/complete')
def complete_focus_point(harvest_session_id: str, tenant: TenantContext = Depends(require_tenant_context)):
    now = datetime.now(timezone.utc)
    return {'harvest_session_id': harvest_session_id, 'organization_id': tenant.organization_id, 'workspace_id': tenant.workspace_id, 'ended_at': now.isoformat(), 'event_created': 'focus_point.completed', 'timer_status': 'stopped'}
