import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthService, LocalAuthService
from postgres_auth import PostgresAuthService
from postgres_store import PostgresStore
from routes.auth import router as auth_router
from routes.harvest import router as harvest_router
from routes.health import router as health_router
from routes.inventory import router as inventory_router
from routes.opportunities import router as opportunities_router
from routes.pick_list import router as pick_list_router
from routes.procurement import router as procurement_router
from routes.vehicles import router as vehicles_router
from store import InMemoryStore, WorkflowStore


def create_app(
    store: WorkflowStore | None = None,
    auth_service: AuthService | None = None,
) -> FastAPI:
    database_url = os.getenv("DATABASE_URL")
    deployment_mode = os.getenv("RECYCLEROS_DEPLOYMENT_MODE", "development").casefold()
    if (
        deployment_mode == "production"
        and not database_url
        and (store is None or auth_service is None)
    ):
        raise RuntimeError(
            "Production mode requires DATABASE_URL for durable workflow and auth state."
        )

    if store is None:
        store = PostgresStore(database_url) if database_url else InMemoryStore()
    if auth_service is None:
        auth_service = (
            PostgresAuthService.from_environment(database_url)
            if database_url
            else LocalAuthService.from_environment()
        )

    app = FastAPI(title="RecyclerOS Platform API", version="0.4.0")
    app.state.store = store
    app.state.auth_service = auth_service
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
