import os

from postgres_auth import PostgresAuthService
from runtime_config import read_config_value


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required.")
    return value


def main() -> int:
    database_url = read_config_value("DATABASE_URL", required=True)
    password = read_config_value(
        "RECYCLEROS_BOOTSTRAP_OWNER_PASSWORD",
        required=True,
    )
    if len(password) < 16:
        raise RuntimeError(
            "RECYCLEROS_BOOTSTRAP_OWNER_PASSWORD must be at least 16 characters."
        )

    email = _required("RECYCLEROS_BOOTSTRAP_OWNER_EMAIL").casefold()
    if os.getenv("RECYCLEROS_BOOTSTRAP_CONFIRM", "").casefold() != email:
        raise RuntimeError(
            "RECYCLEROS_BOOTSTRAP_CONFIRM must exactly match the owner email."
        )

    service = PostgresAuthService(database_url)
    service.bootstrap_production_owner(
        email=email,
        display_name=_required("RECYCLEROS_BOOTSTRAP_OWNER_DISPLAY_NAME"),
        password=password,
        organization_id=_required("RECYCLEROS_BOOTSTRAP_ORGANIZATION_ID"),
        organization_name=_required("RECYCLEROS_BOOTSTRAP_ORGANIZATION_NAME"),
        workspace_id=_required("RECYCLEROS_BOOTSTRAP_WORKSPACE_ID"),
        workspace_name=_required("RECYCLEROS_BOOTSTRAP_WORKSPACE_NAME"),
    )
    print(f"PASS initial production owner provisioned for {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
