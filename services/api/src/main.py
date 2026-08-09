import os

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
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
from runtime_config import (
    read_config_value,
    read_csv_config,
    validate_production_web_config,
)
from service_metadata import API_VERSION
from store import InMemoryStore, WorkflowStore


def create_app(
    store: WorkflowStore | None = None,
    auth_service: AuthService | None = None,
) -> FastAPI:
    database_url = read_config_value("DATABASE_URL")
    deployment_mode = os.getenv("RECYCLEROS_DEPLOYMENT_MODE", "development").casefold()
    if (
        deployment_mode == "production"
        and not database_url
        and (store is None or auth_service is None)
    ):
        raise RuntimeError(
            "Production mode requires DATABASE_URL or DATABASE_URL_FILE for "
            "durable workflow and auth state."
        )

    trusted_hosts = read_csv_config("RECYCLEROS_TRUSTED_HOSTS")
    configured_origins = read_csv_config("RECYCLEROS_CORS_ORIGINS")
    cors_origin_regex = os.getenv(
        "RECYCLEROS_CORS_ORIGIN_REGEX",
        (
            "a^"
            if deployment_mode == "production"
            else r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
        ),
    )
    if deployment_mode == "production":
        validate_production_web_config(
            trusted_hosts=trusted_hosts,
            cors_origins=configured_origins,
            cors_origin_regex=cors_origin_regex,
        )

    if store is None:
        store = PostgresStore(database_url) if database_url else InMemoryStore()
    if auth_service is None:
        auth_service = (
            PostgresAuthService.from_environment(database_url)
            if database_url
            else LocalAuthService.from_environment()
        )

    production_docs_disabled = deployment_mode == "production"
    app = FastAPI(
        title="RecyclerOS Platform API",
        version=API_VERSION,
        docs_url=None if production_docs_disabled else "/docs",
        redoc_url=None if production_docs_disabled else "/redoc",
        openapi_url=None if production_docs_disabled else "/openapi.json",
    )
    app.state.store = store
    app.state.auth_service = auth_service
    app.state.release_sha = (
        os.getenv("RAILWAY_GIT_COMMIT_SHA")
        or os.getenv("RECYCLEROS_RELEASE_SHA")
        or "development"
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if deployment_mode == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts or ["*"],
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured_origins,
        allow_origin_regex=cors_origin_regex,
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
