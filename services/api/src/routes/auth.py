from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from auth import AuthenticatedIdentity, AuthService, AuthSession
from auth_dependencies import get_auth_service
from schemas.auth import LoginRequest
from tenant import bearer_scheme, require_identity

router = APIRouter()


def _membership_payload(membership):
    return {
        "organization_id": membership.organization_id,
        "organization_name": membership.organization_name,
        "workspace_id": membership.workspace_id,
        "workspace_name": membership.workspace_name,
        "role": membership.role.value,
    }


def _identity_payload(identity: AuthenticatedIdentity):
    return {
        "user_id": identity.user_id,
        "email": identity.email,
        "display_name": identity.display_name,
        "memberships": [
            _membership_payload(membership)
            for membership in identity.memberships
        ],
    }


def _session_payload(session: AuthSession):
    return {
        "access_token": session.access_token,
        "token_type": "bearer",
        "expires_at": session.expires_at.isoformat(),
        "identity": _identity_payload(session.identity),
    }


@router.post("/login")
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    session = auth_service.authenticate(payload.email, payload.password)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _session_payload(session)


@router.get("/me")
def get_current_identity(
    identity: AuthenticatedIdentity = Depends(require_identity),
):
    return _identity_payload(identity)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    _identity: AuthenticatedIdentity = Depends(require_identity),
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    if credentials is None or not auth_service.revoke(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
