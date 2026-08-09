import argparse
import os
from pathlib import Path
import secrets


def _write_exclusive(path: Path, value: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as secret_file:
        secret_file.write(value)


def prepare_secrets(directory: Path) -> tuple[Path, ...]:
    directory.mkdir(parents=True, exist_ok=True)
    postgres_password = secrets.token_urlsafe(36)
    operator_password = secrets.token_urlsafe(36)
    values = {
        "postgres_password": postgres_password,
        "database_url": (
            "postgresql://recycleros:"
            f"{postgres_password}@postgres:5432/recycleros_pilot"
        ),
        "operator_password": operator_password,
    }
    paths = tuple(directory / name for name in values)
    existing = [path for path in paths if path.exists()]
    if existing:
        raise RuntimeError(
            "Refusing to overwrite pilot secrets: "
            + ", ".join(str(path) for path in existing)
        )
    for name, value in values.items():
        _write_exclusive(directory / name, value)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create initial RecyclerOS pilot secret files."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("deploy/pilot/secrets"),
    )
    args = parser.parse_args()

    for path in prepare_secrets(args.directory.resolve()):
        print(f"CREATED {path}")
    print("Store the operator password in the approved password manager.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
