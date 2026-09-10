"""Post-revision validation: constraints plus style-drift detection.

A revision passes when hard constraints hold (non-empty, numbers/citations kept,
recognizably the same document). Style drift — revised text measuring *farther*
from the profile than the original — produces a warning, not a rejection: natural
variation is expected and over-optimization is forbidden.
"""

from __future__ import annotations

from . import constraints as c

_RANK = {"close": 0, "moderately_different": 1, "significantly_different": 2,
         "unavailable": -1}


def characteristic_terms(profile: dict, limit: int = 20) -> list[str]:
    """High-presence profile terms worth keeping (soft warnings only)."""
    vocab = (profile.get("vocabulary") or {})
    terms = [t.get("term") for t in (vocab.get("common_terms") or [])
             if (t.get("sample_presence") or 0) >= 1.0]
    ling = (profile.get("linguistic") or {})
    terms += [t.get("term") for t in (ling.get("common_connectives") or [])
              if (t.get("sample_presence") or 0) >= 1.0]
    seen = list(dict.fromkeys(terms))  # de-duplicate, preserve order
    return seen[:limit]


def validate_revision(original: str, revised: str, profile: dict,
                      status_before: str | None = None,
                      status_after: str | None = None) -> dict:
    """Validate one revision; returns {passed, failures[], warnings[], drift{}}}.

    ``status_before``/``status_after`` are Phase 6 overall statuses enabling the
    drift check without re-running comparison here (the engine supplies them).
    """
    check = c.check_constraints(original, revised, characteristic_terms(profile))
    drift = _drift_block(status_before, status_after)
    warnings = list(check["warnings"]) + drift["warnings"]
    return {"passed": check["passed"], "failures": check["failures"],
            "warnings": warnings, "drift": drift}


def _drift_block(before: str | None, after: str | None) -> dict:
    block = {"before": before, "after": after, "warning": None, "warnings": []}
    if before is None or after is None:
        return block
    rank_before = _RANK.get(before, -1)
    rank_after = _RANK.get(after, -1)
    if rank_before < 0 or rank_after < 0:
        return block
    if rank_after > rank_before:
        block["warning"] = (
            f"style drift: revision moved away from the profile "
            f"({before} → {after}); prefer the original phrasing where possible")
        block["warnings"].append(block["warning"])
    return block
