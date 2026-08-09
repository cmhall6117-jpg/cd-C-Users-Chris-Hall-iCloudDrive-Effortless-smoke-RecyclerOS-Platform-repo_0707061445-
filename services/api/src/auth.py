from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
import hashlib
import os
import secrets
from typing import Protocol


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Permission(StrEnum):
    READ = "tenant:read"
    OPERATE = "tenant:operate"
    ADMIN = "tenant:admin"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.OWNER: frozenset(Permission),
    Role.ADMIN: frozenset(Permission),
    Role.OPERATOR: frozenset({Permission.READ, Permission.OPERATE}),
    Role.VIEWER: frozenset({Permission.READ}),
}


@dataclass(frozen=True)
class TenantMembership:
    organization_id: str
    organization_name: str
    workspace_id: str
    workspace_name: str
    role: Role


@dataclass(frozen=True)
class AuthenticatedIdentity:
    user_id: str
    email: str
    display_name: str
    memberships: tuple[TenantMembership, ...]


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    expires_at: datetime
    identity: AuthenticatedIdentity


class AuthService(Protocol):
    storage_name: str

    def authenticate(self, email: str, password: str) -> AuthSession | None: ...

    def resolve(self, access_token: str) -> AuthenticatedIdentity | None: ...

    def revoke(self, access_token: str) -> bool: ...

    def check_readiness(self) -> bool: ...


@dataclass(frozen=True)
class LocalUser:
    user_id: str
    email: str
    display_name: str
    memberships: tuple[TenantMembership, ...]
    password_salt: bytes
    password_digest: bytes
    password_iterations: int

    @classmethod
    def from_password(
        cls,
        *,
        user_id: str,
        email: str,
        display_name: str,
        password: str,
        memberships: tuple[TenantMembership, ...],
        password_iterations: int = 200_000,
    ) -> "LocalUser":
        salt = secrets.token_bytes(16)
        return cls(
            user_id=user_id,
            email=email.casefold(),
            display_name=display_name,
            memberships=memberships,
            password_salt=salt,
            password_digest=password_digest(password, salt, password_iterations),
            password_iterations=password_iterations,
        )

    def verifies(self, password: str) -> bool:
        candidate = password_digest(
            password,
            self.password_salt,
            self.password_iterations,
        )
        return secrets.compare_digest(candidate, self.password_digest)


@dataclass(frozen=True)
class _StoredSession:
    identity: AuthenticatedIdentity
    expires_at: datetime


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def password_digest(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )


class LocalAuthService:
    """Replaceable RC1 auth boundary with process-local opaque sessions."""

    storage_name = "memory"

    def __init__(
        self,
        users: list[LocalUser],
        *,
        session_ttl: timedelta = timedelta(hours=8),
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._users = {user.email.casefold(): user for user in users}
        self._sessions: dict[str, _StoredSession] = {}
        self._session_ttl = session_ttl
        self._clock = clock

    @classmethod
    def from_environment(cls) -> "LocalAuthService":
        password = os.getenv("RECYCLEROS_LOCAL_OPERATOR_PASSWORD")
        if not password:
            return cls([])
        membership = TenantMembership(
            organization_id="org-local",
            organization_name="Effortless Smoke, LLC",
            workspace_id="workspace-local",
            workspace_name="RecyclerOS Operations",
            role=Role.OPERATOR,
        )
        operator = LocalUser.from_password(
            user_id="user-local-operator",
            email="operator@effortlesssmoke.com",
            display_name="Local Operator",
            password=password,
            memberships=(membership,),
        )
        ttl_hours = int(os.getenv("RECYCLEROS_SESSION_TTL_HOURS", "8"))
        return cls([operator], session_ttl=timedelta(hours=ttl_hours))

    def authenticate(self, email: str, password: str) -> AuthSession | None:
        user = self._users.get(email.strip().casefold())
        if user is None or not user.verifies(password):
            return None

        now = self._clock()
        identity = AuthenticatedIdentity(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name,
            memberships=user.memberships,
        )
        token = secrets.token_urlsafe(32)
        expires_at = now + self._session_ttl
        self._sessions[token_digest(token)] = _StoredSession(
            identity=identity,
            expires_at=expires_at,
        )
        return AuthSession(
            access_token=token,
            expires_at=expires_at,
            identity=identity,
        )

    def resolve(self, access_token: str) -> AuthenticatedIdentity | None:
        token_key = token_digest(access_token)
        session = self._sessions.get(token_key)
        if session is None:
            return None
        if session.expires_at <= self._clock():
            self._sessions.pop(token_key, None)
            return None
        return session.identity

    def revoke(self, access_token: str) -> bool:
        return self._sessions.pop(token_digest(access_token), None) is not None

    def check_readiness(self) -> bool:
        return True


def token_digest(access_token: str) -> str:
    return hashlib.sha256(access_token.encode("utf-8")).hexdigest()
