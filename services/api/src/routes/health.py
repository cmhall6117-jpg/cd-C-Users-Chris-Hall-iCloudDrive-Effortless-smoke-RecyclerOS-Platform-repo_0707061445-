from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from service_metadata import API_VERSION

router = APIRouter()


@router.get("")
def health_check(request: Request) -> dict[str, str]:
    return {
        "status": "ok",
        "service": "recycleros-api",
        "version": API_VERSION,
        "release": request.app.state.release_sha,
        "storage": request.app.state.store.storage_name,
        "auth_storage": request.app.state.auth_service.storage_name,
    }


@router.get("/live")
def liveness_check() -> dict[str, str]:
    return {"status": "alive", "service": "recycleros-api"}


def _is_ready(component) -> bool:
    try:
        return bool(component.check_readiness())
    except Exception:
        return False


@router.get("/ready")
def readiness_check(request: Request) -> JSONResponse:
    store_ready = _is_ready(request.app.state.store)
    auth_ready = _is_ready(request.app.state.auth_service)
    ready = store_ready and auth_ready
    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if ready
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "ready" if ready else "not_ready",
            "storage": "ready" if store_ready else "not_ready",
            "auth": "ready" if auth_ready else "not_ready",
        },
    )
