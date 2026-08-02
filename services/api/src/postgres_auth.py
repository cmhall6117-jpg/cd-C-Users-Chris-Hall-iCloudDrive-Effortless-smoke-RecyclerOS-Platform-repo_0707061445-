from collections.abc import Callable
from datetime import datetime, timedelta, timezone
import json
import os
import secrets

from auth import (
    AuthenticatedIdentity,
    AuthSession,
    Role,
    TenantMembership,
    password_digest,
    token_digest,
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PostgresAuthService:
    """Durable local-account auth for the RC1 PostgreSQL runtime."""

    storage_name = "postgres"

    def __init__(
        self,
        database_url: str,
        *,
        session_ttl: timedelta = timedelta(hours=8),
        max_failures: int = 5,
        lockout_ttl: timedelta = timedelta(minutes=15),
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        if not database_url:
            raise ValueError("database_url is required")
        if max_failures < 1:
            raise ValueError("max_failures must be at least 1")
        self._database_url = database_url
        self._session_ttl = session_ttl
        self._max_failures = max_failures
        self._lockout_ttl = lockout_ttl
        self._clock = clock

    @classmethod
    def from_environment(cls, database_url: str) -> "PostgresAuthService":
        service = cls(
            database_url,
            session_ttl=timedelta(
                hours=int(os.getenv("RECYCLEROS_SESSION_TTL_HOURS", "8"))
            ),
            max_failures=int(os.getenv("RECYCLEROS_AUTH_MAX_FAILURES", "5")),
            lockout_ttl=timedelta(
                minutes=int(os.getenv("RECYCLEROS_AUTH_LOCKOUT_MINUTES", "15"))
            ),
        )
        bootstrap_password = os.getenv("RECYCLEROS_LOCAL_OPERATOR_PASSWORD")
        if bootstrap_password:
            service.bootstrap_local_operator(bootstrap_password)
        return service

    def _connect(self):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL runtime requires services/api/requirements-postgres.txt"
            ) from exc
        return psycopg.connect(self._database_url, row_factory=dict_row)

    @staticmethod
    def _audit(
        cursor,
        *,
        event_type: str,
        user_id: str | None,
        email: str | None,
        occurred_at: datetime,
        details: dict[str, object] | None = None,
    ) -> None:
        cursor.execute(
            """
            INSERT INTO auth_audit_events (
                user_id, email, event_type, occurred_at, details
            )
            VALUES (%s, %s, %s, %s, %s::jsonb)
            """,
            (
                user_id,
                email,
                event_type,
                occurred_at,
                json.dumps(details or {}),
            ),
        )

    @staticmethod
    def _identity(cursor, user) -> AuthenticatedIdentity:
        cursor.execute(
            """
            SELECT
                membership.organization_id,
                organization.name AS organization_name,
                membership.workspace_id,
                workspace.name AS workspace_name,
                membership.role
            FROM auth_tenant_memberships membership
            JOIN organizations organization
              ON organization.id = membership.organization_id
            JOIN workspaces workspace
              ON workspace.id = membership.workspace_id
             AND workspace.organization_id = membership.organization_id
            WHERE membership.user_id = %s
            ORDER BY membership.organization_id, membership.workspace_id
            """,
            (user["user_id"],),
        )
        memberships = tuple(
            TenantMembership(
                organization_id=row["organization_id"],
                organization_name=row["organization_name"],
                workspace_id=row["workspace_id"],
                workspace_name=row["workspace_name"],
                role=Role(row["role"]),
            )
            for row in cursor.fetchall()
        )
        return AuthenticatedIdentity(
            user_id=user["user_id"],
            email=user["email"],
            display_name=user["display_name"],
            memberships=memberships,
        )

    def bootstrap_local_operator(self, password: str) -> None:
        """Create the local RC1 operator once without rotating an existing secret."""
        email = "operator@effortlesssmoke.com"
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO organizations (id, name)
                VALUES ('org-local', 'Effortless Smoke, LLC')
                ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
                """
            )
            cursor.execute(
                """
                INSERT INTO workspaces (id, organization_id, name)
                VALUES (
                    'workspace-local',
                    'org-local',
                    'RecyclerOS Operations'
                )
                ON CONFLICT (id) DO UPDATE SET
                    organization_id = EXCLUDED.organization_id,
                    name = EXCLUDED.name
                """
            )
            cursor.execute(
                "SELECT id FROM auth_users WHERE LOWER(email) = %s",
                (email,),
            )
            existing = cursor.fetchone()
            if existing is None:
                user_id = "user-local-operator"
                salt = secrets.token_bytes(16)
                iterations = 200_000
                cursor.execute(
                    """
                    INSERT INTO auth_users (id, email, display_name)
                    VALUES (%s, %s, 'Local Operator')
                    """,
                    (user_id, email),
                )
                cursor.execute(
                    """
                    INSERT INTO auth_password_credentials (
                        user_id,
                        password_salt,
                        password_digest,
                        password_iterations
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        salt,
                        password_digest(password, salt, iterations),
                        iterations,
                    ),
                )
            else:
                user_id = existing["id"]

            cursor.execute(
                """
                INSERT INTO auth_tenant_memberships (
                    user_id, organization_id, workspace_id, role
                )
                VALUES (%s, 'org-local', 'workspace-local', 'operator')
                ON CONFLICT (user_id, organization_id, workspace_id) DO NOTHING
                """,
                (user_id,),
            )

    def authenticate(self, email: str, password: str) -> AuthSession | None:
        normalized_email = email.strip().casefold()
        now = self._clock()
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT failure_count, blocked_until
                FROM auth_login_attempts
                WHERE email = %s
                FOR UPDATE
                """,
                (normalized_email,),
            )
            attempts = cursor.fetchone()
            if (
                attempts is not None
                and attempts["blocked_until"] is not None
                and attempts["blocked_until"] > now
            ):
                self._audit(
                    cursor,
                    event_type="login_blocked",
                    user_id=None,
                    email=normalized_email,
                    occurred_at=now,
                )
                return None

            cursor.execute(
                """
                SELECT
                    auth_user.id AS user_id,
                    auth_user.email,
                    auth_user.display_name,
                    credential.password_salt,
                    credential.password_digest,
                    credential.password_iterations
                FROM auth_users auth_user
                JOIN auth_password_credentials credential
                  ON credential.user_id = auth_user.id
                WHERE LOWER(auth_user.email) = %s
                  AND auth_user.active = true
                """,
                (normalized_email,),
            )
            user = cursor.fetchone()
            verified = False
            if user is not None:
                candidate = password_digest(
                    password,
                    bytes(user["password_salt"]),
                    user["password_iterations"],
                )
                verified = secrets.compare_digest(
                    candidate,
                    bytes(user["password_digest"]),
                )

            if not verified:
                failure_count = (
                    attempts["failure_count"] + 1 if attempts is not None else 1
                )
                blocked_until = (
                    now + self._lockout_ttl
                    if failure_count >= self._max_failures
                    else None
                )
                cursor.execute(
                    """
                    INSERT INTO auth_login_attempts (
                        email, failure_count, last_failed_at, blocked_until
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO UPDATE SET
                        failure_count = EXCLUDED.failure_count,
                        last_failed_at = EXCLUDED.last_failed_at,
                        blocked_until = EXCLUDED.blocked_until
                    """,
                    (normalized_email, failure_count, now, blocked_until),
                )
                self._audit(
                    cursor,
                    event_type="login_failed",
                    user_id=None if user is None else user["user_id"],
                    email=normalized_email,
                    occurred_at=now,
                    details={"blocked": blocked_until is not None},
                )
                return None

            cursor.execute(
                "DELETE FROM auth_login_attempts WHERE email = %s",
                (normalized_email,),
            )
            token = secrets.token_urlsafe(32)
            expires_at = now + self._session_ttl
            cursor.execute(
                """
                INSERT INTO auth_sessions (
                    token_digest,
                    user_id,
                    created_at,
                    expires_at,
                    last_seen_at
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (token_digest(token), user["user_id"], now, expires_at, now),
            )
            self._audit(
                cursor,
                event_type="login_succeeded",
                user_id=user["user_id"],
                email=user["email"],
                occurred_at=now,
            )
            return AuthSession(
                access_token=token,
                expires_at=expires_at,
                identity=self._identity(cursor, user),
            )

    def resolve(self, access_token: str) -> AuthenticatedIdentity | None:
        now = self._clock()
        digest = token_digest(access_token)
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    session.user_id,
                    session.expires_at,
                    auth_user.email,
                    auth_user.display_name
                FROM auth_sessions session
                JOIN auth_users auth_user ON auth_user.id = session.user_id
                WHERE session.token_digest = %s
                  AND session.revoked_at IS NULL
                  AND auth_user.active = true
                FOR UPDATE OF session
                """,
                (digest,),
            )
            session = cursor.fetchone()
            if session is None:
                return None
            if session["expires_at"] <= now:
                cursor.execute(
                    """
                    UPDATE auth_sessions
                    SET revoked_at = %s
                    WHERE token_digest = %s
                    """,
                    (now, digest),
                )
                self._audit(
                    cursor,
                    event_type="session_expired",
                    user_id=session["user_id"],
                    email=session["email"],
                    occurred_at=now,
                )
                return None

            cursor.execute(
                """
                UPDATE auth_sessions
                SET last_seen_at = %s
                WHERE token_digest = %s
                """,
                (now, digest),
            )
            return self._identity(cursor, session)

    def revoke(self, access_token: str) -> bool:
        now = self._clock()
        digest = token_digest(access_token)
        with self._connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT session.user_id, auth_user.email
                FROM auth_sessions session
                JOIN auth_users auth_user ON auth_user.id = session.user_id
                WHERE session.token_digest = %s
                  AND session.revoked_at IS NULL
                FOR UPDATE OF session
                """,
                (digest,),
            )
            session = cursor.fetchone()
            if session is None:
                return False
            cursor.execute(
                """
                UPDATE auth_sessions
                SET revoked_at = %s
                WHERE token_digest = %s
                """,
                (now, digest),
            )
            self._audit(
                cursor,
                event_type="logout",
                user_id=session["user_id"],
                email=session["email"],
                occurred_at=now,
            )
            return True
