"""Result assembly for the revision engine (JSON-serializable, no chain-of-thought)."""

from __future__ import annotations

REVISION_VERSION = "0.1.0"
_VALID_IMPORTANCE = ("high", "medium", "low")


def normalize_changes(raw) -> list:
    """Coerce provider change summaries to [{dimension, description, importance}]."""
    changes = []
    if not isinstance(raw, list):
        return changes
    for item in raw:
        if not isinstance(item, dict):
            continue
        description = item.get("description")
        if not description or not isinstance(description, str):
            continue
        importance = item.get("importance", "medium")
        if importance not in _VALID_IMPORTANCE:
            importance = "medium"
        changes.append({
            "dimension": str(item.get("dimension", "general")),
            "description": description,
            "importance": importance,
        })
    return changes


def build_result(original: str, revised: str, changes: list, validation: dict,
                 mode: str, attempts: int, provider_name: str,
                 comparison_before: dict | None,
                 comparison_after: dict | None) -> dict:
    """Assemble the structured result (original kept in memory only)."""
    return {
        "revision_version": REVISION_VERSION,
        "original_text": original,
        "revised_text": revised,
        "changed": revised != original,
        "changes": normalize_changes(changes),
        "validation": validation,
        "metadata": {
            "mode": mode,
            "attempts": attempts,
            "provider": provider_name,
            "comparison_before": (comparison_before or {}).get("overall"),
            "comparison_after": (comparison_after or {}).get("overall"),
        },
    }


def strip_original(result: dict) -> dict:
    """Copy of ``result`` without ``original_text`` for persisted reports (privacy)."""
    copy = dict(result)
    copy.pop("original_text", None)
    return copy
