import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthService, LocalAuthService
from routes.auth import router as auth_router
from routes.harvest import router as harvest_router
from routes.health import router as health_router
from routes.inventory import router as inventory_router
from routes.opportunities import router as opportunities_router
from routes.pick_list import router as pick_list_router
from routes.procurement import router as procurement_router
from routes.vehicles import router as vehicles_router
from store import InMemoryStore


def create_app(
    store: InMemoryStore | None = None,
    auth_service: AuthService | None = None,
) -> FastAPI:
    app = FastAPI(title="RecyclerOS Platform API", version="0.3.0")
    app.state.store = store or InMemoryStore()
    app.state.auth_service = auth_service or LocalAuthService.from_environment()
    configured_origins = [
        origin.strip()
        for origin in os.getenv("RECYCLEROS_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured_origins,
        allow_origin_regex=os.getenv(
            "RECYCLEROS_CORS_ORIGIN_REGEX",
            r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        ),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Authorization",
            "Content-Type",
            "X-Organization-ID",
            "X-Workspace-ID",
        ],
    )
    app.include_router(health_router, prefix="/v1/health", tags=["health"])
    app.include_router(auth_router, prefix="/v1/auth", tags=["auth"])
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
