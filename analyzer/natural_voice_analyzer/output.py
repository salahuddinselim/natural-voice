"""Output finalization: rounding and JSON-serialization helpers."""

from __future__ import annotations

import json

_FLOAT_PRECISION = 4


def finalize(result: dict) -> dict:
    """Round all floats to 4 decimals so output is stable and JSON-serializable."""
    return _round_floats(result)


def to_json(result: dict, pretty: bool = False) -> str:
    """Serialize an analysis result to JSON (``ensure_ascii=False`` for Unicode)."""
    if pretty:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


def _round_floats(value):
    if isinstance(value, float):
        return round(value, _FLOAT_PRECISION)
    if isinstance(value, dict):
        return {key: _round_floats(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_round_floats(item) for item in value]
    return value
