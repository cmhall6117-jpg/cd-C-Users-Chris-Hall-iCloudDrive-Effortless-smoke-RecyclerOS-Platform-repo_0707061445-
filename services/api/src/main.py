from fastapi import FastAPI
from routes.harvest import router as harvest_router
from routes.health import router as health_router
from routes.inventory import router as inventory_router
from routes.opportunities import router as opportunities_router
from routes.pick_list import router as pick_list_router
from routes.procurement import router as procurement_router
from routes.vehicles import router as vehicles_router
from store import InMemoryStore


def create_app(store: InMemoryStore | None = None) -> FastAPI:
    app = FastAPI(title="RecyclerOS Platform API", version="0.2.0")
    app.state.store = store or InMemoryStore()
    app.include_router(health_router, prefix="/v1/health", tags=["health"])
    app.include_router(
        opportunities_router, prefix="/v1/opportunities", tags=["opportunities"]
    )
    app.include_router(vehicles_router, prefix="/v1/vehicles", tags=["vehicles"])
    app.include_router(
        procurement_router, prefix="/v1/procurement", tags=["procurement"]
    )
    app.include_router(pick_list_router, prefix="/v1/pick-list", tags=["pick-list"])
    app.include_router(harvest_router, prefix="/v1/harvest", tags=["harvest"])
    app.include_router(inventory_router, prefix="/v1/inventory", tags=["inventory"])
    return app


app = create_app()
