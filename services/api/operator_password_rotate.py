import argparse
import getpass

from postgres_auth import PostgresAuthService
from runtime_config import read_config_value


PILOT_OPERATOR_EMAIL = "operator@effortlesssmoke.com"
MINIMUM_PASSWORD_LENGTH = 24


def _password() -> str:
    password = getpass.getpass("New operator password: ")
    confirmation = getpass.getpass("Confirm new operator password: ")
    if password != confirmation:
        raise RuntimeError("The password confirmation does not match.")
    if password != password.strip():
        raise RuntimeError("The password cannot start or end with whitespace.")
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise RuntimeError(
            f"The password must be at least {MINIMUM_PASSWORD_LENGTH} characters."
        )
    return password


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rotate the durable RecyclerOS pilot operator credential."
    )
    parser.add_argument("--email", default=PILOT_OPERATOR_EMAIL)
    parser.add_argument("--confirm-email", required=True)
    args = parser.parse_args(argv)

    email = args.email.strip().casefold()
    if args.confirm_email.strip().casefold() != email:
        raise RuntimeError("--confirm-email must exactly match --email.")

    database_url = read_config_value("DATABASE_URL", required=True)
    revoked_sessions = PostgresAuthService(database_url).rotate_password(
        email=email,
        password=_password(),
    )
    print(
        "PASS operator credential rotated; "
        f"revoked sessions: {revoked_sessions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
