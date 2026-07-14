import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def build_manifest(*, root: Path, image: str, digest: str, commit: str) -> dict:
    if not image or "@" in image:
        raise RuntimeError("Image must be a repository name without a digest.")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise RuntimeError("Digest must be a complete sha256 image digest.")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("Commit must be a complete 40-character Git SHA.")

    migration_directory = root / "database" / "migrations" / "postgres"
    migrations = []
    for migration in sorted(migration_directory.glob("*.sql")):
        migrations.append(
            {
                "filename": migration.name,
                "sha256": hashlib.sha256(migration.read_bytes()).hexdigest(),
            }
        )
    if not migrations:
        raise RuntimeError("No PostgreSQL migrations were found.")

    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "image": image,
        "image_digest": digest,
        "migrations": migrations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an immutable RecyclerOS production release manifest."
    )
    parser.add_argument("--image", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise RuntimeError(f"Release manifest already exists: {output}")
    root = Path(__file__).resolve().parents[2]
    manifest = build_manifest(
        root=root,
        image=args.image,
        digest=args.digest,
        commit=args.commit,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PASS production release manifest {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
