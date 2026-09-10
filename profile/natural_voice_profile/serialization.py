"""Profile persistence: deterministic JSON save/load (UTF-8, no sample text)."""

from __future__ import annotations

import json
from pathlib import Path

from .validation import validate_profile


def save_profile(profile: dict, path: str | Path) -> Path:
    """Save a validated profile as pretty, key-sorted JSON (UTF-8).

    Raises:
        ValueError: if the profile fails validation (reasons included).
    """
    errors = validate_profile(profile)
    if errors:
        raise ValueError(f"refusing to save invalid profile: {'; '.join(errors)}")
    target = Path(path)
    target.write_text(
        json.dumps(profile, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    return target


def load_profile(path: str | Path) -> dict:
    """Load and validate a profile file.

    Raises:
        FileNotFoundError: missing file. ValueError: bad JSON or invalid profile.
    """
    target = Path(path)
    try:
        profile = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid JSON: {target}: {exc}") from exc
    errors = validate_profile(profile)
    if errors:
        raise ValueError(f"invalid profile in {target}: {'; '.join(errors)}")
    return profile
