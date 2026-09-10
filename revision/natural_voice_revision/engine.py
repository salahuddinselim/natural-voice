"""Revision engine: draft + profile + comparison + principles → LLM → validated revision.

The engine is provider-neutral: it talks only to ``LLMProvider``. The default
single attempt keeps behavior conservative; ``max_attempts=2`` allows one guided
retry that fixes exactly the reported violations. Provider transport failures
raise; empty/malformed/unusable outputs become failed validations, never crashes.
"""

from __future__ import annotations

import json
import logging

from natural_voice_comparison import compare_draft
from natural_voice_config import check_profile_compatibility
from natural_voice_profile.validation import validate_profile

logger = logging.getLogger("natural_voice.revision")

from .prompt_builder import (
    MODES,
    build_prompt,
    contains_bypass_intent,
)
from .result import build_result
from .validation import validate_revision

MAX_DRAFT_CHARS = 50000  # oversized inputs are rejected, not truncated silently.
MAX_ATTEMPTS = 3


def revise(
    draft: str,
    profile: dict,
    comparison: dict | None = None,
    provider=None,
    mode: str = "conservative",
    user_request: str = "",
    max_attempts: int = 1,
) -> dict:
    """Revise ``draft`` for clarity and voice consistency; return a result dict.

    Args:
        draft: original text (untrusted data: measured and revised, never
            executed; retained in the in-memory result only).
        profile: validated Phase 5 Author Voice Profile.
        comparison: Phase 6 report for the draft (computed when omitted).
        provider: an ``LLMProvider`` implementation (required).
        mode: conservative (default) | balanced | expressive.
        user_request: revision instruction; detector-evasion intent is refused.
        max_attempts: 1 (default) to 3; retries address reported violations only.

    Raises:
        TypeError: bad argument types or provider without ``generate``.
        ValueError: empty/oversized draft, invalid profile/mode/attempts, or
            detector-evasion intent in ``user_request``.
        ProviderError: provider transport/authentication failure.
    """
    _check_inputs(draft, profile, provider, mode, user_request, max_attempts)
    if comparison is None:
        comparison = compare_draft(draft, profile)
    status_before = (comparison.get("overall") or {}).get("status")

    revised, changes, attempts = draft, [], 0
    comparison_after, status_after = None, None
    fix_notes: list | None = None
    validation = {"passed": False, "failures": ["no attempt made"],
                  "warnings": [], "drift": {}}
    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        prompt = build_prompt(draft, profile, comparison, user_request, mode,
                              fix_notes=fix_notes)
        response = provider.generate(prompt)
        revised, changes = _parse_response(response)
        comparison_after, status_after = _recompare(revised, profile, draft)
        validation = validate_revision(draft, revised, profile,
                                       status_before=status_before,
                                       status_after=status_after)
        if validation["passed"]:
            break
        fix_notes = list(validation["failures"])

    logger.info("revision finished: passed=%s attempts=%d changed=%s",
                validation["passed"], attempts, revised != draft)
    return build_result(draft, revised, changes, validation, mode, attempts,
                        _provider_name(provider), comparison, comparison_after)


def _require_compatible_profile(profile: dict) -> None:
    status, notes = check_profile_compatibility(profile)
    if status == "unsupported":
        raise ValueError(f"unsupported voice profile: {'; '.join(notes)}")
    for note in notes:
        logger.warning("profile compatibility note: %s", note)


def _check_inputs(draft, profile, provider, mode, user_request, max_attempts) -> None:
    if not isinstance(draft, str):
        raise TypeError(f"draft must be str, got {type(draft).__name__}")
    if not draft.strip():
        raise ValueError("draft must not be empty")
    if len(draft) > MAX_DRAFT_CHARS:
        raise ValueError(f"draft exceeds {MAX_DRAFT_CHARS} characters "
                         f"({len(draft)}); split it and revise in parts")
    errors = validate_profile(profile)
    if errors:
        raise ValueError(f"invalid voice profile: {'; '.join(errors)}")
    _require_compatible_profile(profile)
    logger.info("revision started: mode=%s draft_chars=%d max_attempts=%d",
                mode, len(draft), max_attempts)
    if provider is None or not hasattr(provider, "generate"):
        raise TypeError("provider must implement LLMProvider.generate")
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if not isinstance(user_request, str):
        raise TypeError("user_request must be str")
    if contains_bypass_intent(user_request):
        raise ValueError(
            "revision requests must describe legitimate writing goals "
            "(clarity, flow, concision, voice consistency); "
            "detector-evasion requests are refused")
    if not isinstance(max_attempts, int) or not 1 <= max_attempts <= MAX_ATTEMPTS:
        raise ValueError(f"max_attempts must be an int in 1..{MAX_ATTEMPTS}")


def _parse_response(response) -> tuple[str, list]:
    """Structured JSON preferred; plain-text fallback; unusable → empty revision."""
    if not isinstance(response, str) or not response.strip():
        return "", []
    text = response.strip()
    if text.startswith("{"):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return "", []  # malformed JSON: fail validation, do not guess.
        if isinstance(payload, dict) and isinstance(payload.get("revised_text"), str):
            return payload["revised_text"], payload.get("change_summary", [])
        return "", []
    return text, []


def _recompare(revised: str, profile: dict, draft: str):
    """Re-analyze + re-compare when possible; degrade gracefully on failure."""
    if revised == draft:
        return None, None  # unchanged: no new information, skip recompute.
    report = _safe_recompare(revised, profile)
    status = (report.get("overall") or {}).get("status") if report else None
    return report, status


def _safe_recompare(revised: str, profile: dict):
    try:
        if not revised.strip():
            return None
        return compare_draft(revised, profile)
    except (ValueError, TypeError):
        return None


def _provider_name(provider) -> str:
    name = getattr(provider, "name", None)
    if isinstance(name, str):
        return name
    return type(provider).__name__
