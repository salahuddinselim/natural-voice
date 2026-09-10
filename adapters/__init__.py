"""Agent adapter discovery (OpenCode / Claude Code / Codex).

An adapter is a directory containing a ``SKILL.md`` with valid ``name``/``description``
frontmatter. ``list_adapters()`` scans the bundled ``adapters/`` directory only —
no core logic lives here, so discovery can never pull platform code into the core.
"""

from __future__ import annotations

from pathlib import Path

_ADAPTERS_DIR = Path(__file__).resolve().parent


def list_adapters() -> list[str]:
    """Sorted names of bundled adapters that ship a SKILL.md (deterministic)."""
    return sorted(
        entry.name for entry in _ADAPTERS_DIR.iterdir()
        if entry.is_dir() and (entry / "SKILL.md").is_file()
        and not entry.name.startswith(("_", ".")))


def adapter_skill_path(name: str) -> Path:
    """Filesystem path of an adapter's SKILL.md; ValueError for unknown names."""
    path = _ADAPTERS_DIR / name / "SKILL.md"
    if name not in list_adapters() or not path.is_file():
        raise ValueError(f"unknown adapter {name!r} "
                         f"(available: {list_adapters()})")
    return path
