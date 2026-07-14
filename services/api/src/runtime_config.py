from collections.abc import Mapping
import os
from pathlib import Path


def read_config_value(
    name: str,
    *,
    default: str | None = None,
    required: bool = False,
    environ: Mapping[str, str] | None = None,
) -> str | None:
    """Read NAME or NAME_FILE without allowing ambiguous secret sources."""
    values = os.environ if environ is None else environ
    direct_value = values.get(name)
    file_name = values.get(f"{name}_FILE")
    if direct_value is not None and file_name is not None:
        raise RuntimeError(f"Set only one of {name} or {name}_FILE.")

    value = direct_value
    if file_name is not None:
        try:
            value = Path(file_name).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read {name}_FILE.") from exc

    if value is not None:
        value = value.strip()
    if not value:
        value = default
    if required and not value:
        raise RuntimeError(f"{name} or {name}_FILE is required.")
    return value
