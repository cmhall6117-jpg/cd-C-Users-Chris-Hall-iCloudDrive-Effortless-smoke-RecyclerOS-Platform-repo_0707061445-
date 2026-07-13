from fastapi import FastAPI
from routes.harvest import router as harvest_router
from routes.health import router as health_router
from routes.inventory import router as inventory_router
from routes.opportunities import router as opportunities_router
from routes.procurement import router as procurement_router
from routes.vehicles import router as vehicles_router

app = FastAPI(title="RecyclerOS Platform API", version="0.1.0")
app.include_router(health_router, prefix="/v1/health", tags=["health"])
app.include_router(opportunities_router, prefix="/v1/opportunities", tags=["opportunities"])
app.include_router(vehicles_router, prefix="/v1/vehicles", tags=["vehicles"])
app.include_router(procurement_router, prefix="/v1/procurement", tags=["procurement"])
app.include_router(harvest_router, prefix="/v1/harvest", tags=["harvest"])
app.include_router(inventory_router, prefix="/v1/inventory", tags=["inventory"])
