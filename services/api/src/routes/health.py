from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "recycleros-api",
        "version": "0.2.0",
        "storage": "memory",
    }
