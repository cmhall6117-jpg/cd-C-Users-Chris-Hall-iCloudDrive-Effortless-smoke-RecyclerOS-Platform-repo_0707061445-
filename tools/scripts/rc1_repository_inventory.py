from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    output_dir = root / "documentation" / "repository"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "REPOSITORY_INVENTORY.md"

    lines = [
        "# Repository Inventory",
        "",
        "This inventory records original package zip contents and the active files currently present in the RC1 monorepo.",
        "",
        "## Archived Source Packages",
        "",
    ]

    for zip_path in sorted((root / "archive" / "source_packages").glob("*.zip")):
        lines.append(f"### {zip_path.name}")
        lines.append("")
        with ZipFile(zip_path) as zf:
            for name in sorted(info.filename for info in zf.infolist() if not info.is_dir()):
                lines.append(f"- `{name}`")
        lines.append("")

    lines.extend(["## Active Repository Files", ""])
    skipped = {".git", "build_artifacts"}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in skipped:
            continue
        lines.append(f"- `{rel.as_posix()}`")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
