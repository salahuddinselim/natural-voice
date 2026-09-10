"""Public comparison pipeline: draft + profile → voice consistency report.

Local and deterministic: the draft is analyzed once with the Phase 4 analyzer,
the profile is loaded once and validated, and every comparison is a pure function
of those two inputs plus explicit weights. No LLM, no network, no randomness.
"""

from __future__ import annotations

import logging

from natural_voice_analyzer import ANALYZER_VERSION, analyze_text
from natural_voice_analyzer.output import finalize
from natural_voice_config import check_profile_compatibility
from natural_voice_profile.serialization import load_profile
from natural_voice_profile.validation import validate_profile

logger = logging.getLogger("natural_voice.comparison")

from . import metrics as m
from .report import (
    DEFAULT_WEIGHTS,
    DIMENSION_ORDER,
    build_dimensions,
    build_limitations,
    build_summary,
    overall_status,
)

COMPARISON_VERSION = "0.1.0"
DRAFT_TOP_K = 50  # deeper draft inventory improves overlap recall; documented.

# Draft word-count bands for comparison confidence (HEURISTIC).
DRAFT_LOW_WORDS = 100
DRAFT_MEDIUM_WORDS = 400
_CONF_RANK = {"low": 0, "medium": 1, "high": 2}


def compare_draft(
    draft_text: str,
    profile: dict,
    weights: dict | None = None,
    draft_context: str | None = None,
    top_k: int = DRAFT_TOP_K,
) -> dict:
    """Compare a draft against an Author Voice Profile.

    Args:
        draft_text: the new writing (untrusted data: measured, never executed,
            never stored, never logged).
        profile: a Phase 5 profile dict (validated before use).
        weights: optional per-dimension weights merged over DEFAULT_WEIGHTS;
            unknown dimensions raise ValueError. Deterministic.
        draft_context: optional draft context label for mismatch warnings
            (no automatic detection is performed).
        top_k: draft N-gram inventory depth.

    Returns:
        JSON-serializable consistency report (categories only, no scores).

    Raises:
        TypeError: draft is not a string. ValueError: invalid profile/weights.
    """
    if not isinstance(draft_text, str):
        raise TypeError(f"draft_text must be str, got {type(draft_text).__name__}")
    errors = validate_profile(profile)
    if errors:
        raise ValueError(f"invalid voice profile: {'; '.join(errors)}")
    compat, notes = check_profile_compatibility(profile)
    if compat == "unsupported":
        raise ValueError(f"unsupported voice profile: {'; '.join(notes)}")
    for note in notes:
        logger.warning("profile compatibility note: %s", note)
    merged_weights = _merge_weights(weights)
    logger.info("comparison started: draft_chars=%d", len(draft_text))

    draft = analyze_text(draft_text, top_k=top_k)
    draft_words = draft["basic"]["words"]
    if not draft_words:
        return _empty_report(profile, merged_weights, draft_context)

    dimensions = build_dimensions(draft, profile, top_k)
    status = overall_status(dimensions, merged_weights)
    comparison_confidence = _comparison_confidence(profile, draft_words)
    context_note = _context_note(profile, draft_context)
    summary = build_summary(dimensions, profile, draft_words,
                            comparison_confidence, context_note)
    limitations = build_limitations(dimensions, draft_words, context_note)
    return finalize({
        "comparison_version": COMPARISON_VERSION,
        "metadata": {
            "profile_version": profile.get("profile_version"),
            "analyzer_version": ANALYZER_VERSION,
            "draft_words": draft_words,
            "draft_sentences": draft["basic"]["sentences"],
            "profile_samples": profile["metadata"]["sample_count"],
            "profile_words": profile["metadata"]["total_words"],
            "profile_context": profile["metadata"]["context"],
            "draft_context": draft_context,
            "weights": merged_weights,
        },
        "overall": {"status": status, "confidence": comparison_confidence},
        "dimensions": dimensions,
        "summary": summary,
        "limitations": limitations,
    })


def compare_draft_file(
    draft_path: str,
    profile_path: str,
    weights: dict | None = None,
    draft_context: str | None = None,
    top_k: int = DRAFT_TOP_K,
) -> dict:
    """File variant: read a UTF-8 draft and a validated profile file, then compare.

    Raises:
        ValueError: unreadable draft, invalid JSON, or invalid profile.
    """
    from pathlib import Path

    try:
        draft_text = Path(draft_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"cannot read draft file {draft_path}: {exc}") from exc
    profile = load_profile(profile_path)  # validates; raises ValueError if bad.
    return compare_draft(draft_text, profile, weights=weights,
                         draft_context=draft_context, top_k=top_k)


def _merge_weights(weights: dict | None) -> dict:
    merged = dict(DEFAULT_WEIGHTS)
    if not weights:
        return merged
    if not isinstance(weights, dict):
        raise ValueError("weights must be a dict of dimension → number")
    for dim, value in weights.items():
        if dim not in DEFAULT_WEIGHTS:
            raise ValueError(f"unknown dimension in weights: {dim!r} "
                             f"(known: {sorted(DEFAULT_WEIGHTS)})")
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"weight for {dim!r} must be a non-negative number")
        merged[dim] = float(value)
    return merged


def _comparison_confidence(profile: dict, draft_words: int) -> str:
    """Cautious combination: the weaker of profile evidence and draft evidence."""
    profile_level = profile["confidence"]["overall"]
    draft_level = ("low" if draft_words < DRAFT_LOW_WORDS
                   else ("medium" if draft_words < DRAFT_MEDIUM_WORDS else "high"))
    return profile_level if _CONF_RANK[profile_level] <= _CONF_RANK[draft_level] else draft_level


def _context_note(profile: dict, draft_context: str | None) -> str | None:
    if not draft_context:
        return None
    profile_context = profile["metadata"]["context"]
    if draft_context == profile_context:
        return None
    return (f"Context mismatch: profile is {profile_context!r} writing but the draft "
            f"is labeled {draft_context!r}; stylistic differences may reflect context, "
            f"not inconsistency.")


def _empty_report(profile: dict, weights: dict, draft_context: str | None) -> dict:
    """Graceful all-unavailable report for empty drafts (no crash, no invention)."""
    context_note = _context_note(profile, draft_context)
    dimensions = {dim: {"status": m.UNAVAILABLE, "metrics": [],
                        "explanations": [], "notes": []}
                  for dim in DIMENSION_ORDER}
    limitations = ["Draft is empty: no comparison was possible."]
    if context_note:
        limitations.append(context_note)
    limitations.append("Categories are project heuristics, not authorship measurements.")
    return finalize({
        "comparison_version": COMPARISON_VERSION,
        "metadata": {
            "profile_version": profile.get("profile_version"),
            "analyzer_version": ANALYZER_VERSION,
            "draft_words": 0,
            "draft_sentences": 0,
            "profile_samples": profile["metadata"]["sample_count"],
            "profile_words": profile["metadata"]["total_words"],
            "profile_context": profile["metadata"]["context"],
            "draft_context": draft_context,
            "weights": weights,
        },
        "overall": {"status": m.UNAVAILABLE, "confidence": "low"},
        "dimensions": dimensions,
        "summary": ["Draft is empty: no comparison was possible."],
        "limitations": limitations,
    })
