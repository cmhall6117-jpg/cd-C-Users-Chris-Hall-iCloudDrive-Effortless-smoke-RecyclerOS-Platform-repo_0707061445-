from fastapi import FastAPI

# Import route modules after merging vertical slice packages.
from routes.health import router as health_router
from routes.opportunities import router as opportunities_router
from routes.vehicles import router as vehicles_router
from routes.procurement import router as procurement_router
from routes.harvest import router as harvest_router
from routes.inventory import router as inventory_router
from routes.sales import router as sales_router
from routes.dashboard import router as dashboard_router
from routes.cycle_counts import router as cycle_counts_router
from routes.scrap import router as scrap_router
from routes.compliance import router as compliance_router
from routes.promotions import router as promotions_router
from routes.customers import router as customers_router
from routes.finance import router as finance_router
from routes.decisions import router as decisions_router
from routes.search import router as search_router
from routes.notifications import router as notifications_router
from routes.sync_health import router as sync_health_router
from routes.admin import router as admin_router
from routes.audit import router as audit_router

app = FastAPI(title="RecyclerOS Platform API", version="0.1.0")

app.include_router(health_router, prefix="/v1/health", tags=["health"])
app.include_router(opportunities_router, prefix="/v1/opportunities", tags=["opportunities"])
app.include_router(vehicles_router, prefix="/v1/vehicles", tags=["vehicles"])
app.include_router(procurement_router, prefix="/v1/procurement", tags=["procurement"])
app.include_router(harvest_router, prefix="/v1/harvest", tags=["harvest"])
app.include_router(inventory_router, prefix="/v1/inventory", tags=["inventory"])
app.include_router(sales_router, prefix="/v1/sales", tags=["sales"])
app.include_router(dashboard_router, prefix="/v1/dashboard", tags=["dashboard"])
app.include_router(cycle_counts_router, prefix="/v1/cycle-counts", tags=["cycle-counts"])
app.include_router(scrap_router, prefix="/v1/scrap", tags=["scrap"])
app.include_router(compliance_router, prefix="/v1/compliance", tags=["compliance"])
app.include_router(promotions_router, prefix="/v1/promotions", tags=["promotions"])
app.include_router(customers_router, prefix="/v1/customers", tags=["customers"])
app.include_router(finance_router, prefix="/v1/finance", tags=["finance"])
app.include_router(decisions_router, prefix="/v1/decisions", tags=["decisions"])
app.include_router(search_router, prefix="/v1/search", tags=["search"])
app.include_router(notifications_router, prefix="/v1/notifications", tags=["notifications"])
app.include_router(sync_health_router, prefix="/v1/sync-health", tags=["sync-health"])
app.include_router(admin_router, prefix="/v1/admin", tags=["admin"])
app.include_router(audit_router, prefix="/v1/audit", tags=["audit"])
