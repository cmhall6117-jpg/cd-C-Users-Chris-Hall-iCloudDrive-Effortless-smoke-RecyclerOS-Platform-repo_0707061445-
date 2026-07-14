from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
def health_check(request: Request) -> dict[str, str]:
    return {
        "status": "ok",
        "service": "recycleros-api",
        "version": "0.4.0",
        "storage": request.app.state.store.storage_name,
        "auth_storage": request.app.state.auth_service.storage_name,
    }
