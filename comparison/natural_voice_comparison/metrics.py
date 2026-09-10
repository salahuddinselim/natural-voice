"""Per-metric comparison primitives (deterministic, local, no thresholds hidden).

Status model for numeric metrics (all HEURISTIC, documented here):
  1. If the draft value falls inside the profile ``typical_range`` (mean ± std
     across profile samples) → "close".
  2. Else if profile std is usable (> tiny): z = (draft - mean) / std;
     |z| ≤ 2 → "moderately_different", |z| > 2 → "significantly_different".
     (Inside-range already implies |z| ≤ 1, so step 2 only sees |z| > 1.)
  3. Else (std is 0/None, e.g. single-sample profiles): relative difference
     |draft - mean| / max(|mean|, eps) with the feature-spec fallback bands —
     ≤ 0.20 → "close", ≤ 0.40 → "moderately_different", else "significantly_different".
Missing profile mean or missing draft value → "unavailable" (never invented).

Overlap metrics (N-grams, shared terms) use presence-weighted overlap ratios with
their own documented bands; low overlap is reported with a topic/context caveat,
never as an authorship signal.
"""

from __future__ import annotations

import math

CLOSE = "close"
MODERATE = "moderately_different"
SIGNIFICANT = "significantly_different"
UNAVAILABLE = "unavailable"

_EPS = 1e-9


def compare_numeric(name: str, draft_value, aggregate: dict | None) -> dict:
    """Compare one draft number against a profile aggregate stat block."""
    row: dict = {"name": name, "kind": "numeric",
                 "draft_value": draft_value,
                 "profile_value": None, "profile_range": None,
                 "difference": None, "z_score": None,
                 "status": UNAVAILABLE, "reason": None}
    if aggregate is None:
        row["reason"] = "no profile data"
        return row
    mean = aggregate.get("mean")
    if draft_value is None or not _finite(draft_value):
        row["profile_value"] = mean
        row["profile_range"] = aggregate.get("typical_range")
        row["reason"] = "draft value unavailable"
        return row
    if mean is None or not _finite(mean):
        row["reason"] = "profile value unavailable"
        return row
    row["profile_value"] = mean
    row["profile_range"] = aggregate.get("typical_range")
    row["difference"] = draft_value - mean
    std = aggregate.get("std")
    lo, hi = (aggregate.get("typical_range") or (None, None))
    if lo is not None and hi is not None and lo <= draft_value <= hi:
        row["status"] = CLOSE
        row["reason"] = None
        if _usable_std(std):
            row["z_score"] = (draft_value - mean) / std
        return row
    if _usable_std(std):
        z = (draft_value - mean) / std
        row["z_score"] = z
        row["status"] = MODERATE if abs(z) <= 2.0 else SIGNIFICANT
        row["reason"] = None
        return row
    # Stable/degenerate profile spread: relative-difference fallback bands.
    denom = max(abs(mean), _EPS)
    rel = abs(draft_value - mean) / denom
    row["status"] = CLOSE if rel <= 0.20 else (MODERATE if rel <= 0.40 else SIGNIFICANT)
    row["reason"] = "profile spread is zero; relative-difference fallback"
    return row


def compare_overlap(name: str, draft_phrases: set[str],
                    profile_items: list, min_presence: float = 0.5) -> dict:
    """Presence-weighted overlap of draft phrases against recurring profile patterns.

    Reference set = profile patterns with sample_presence >= min_presence.
    overlap = matched / reference; weighted_overlap weights by presence.
    Bands (HEURISTIC): ≥ 0.5 → close; ≥ 0.2 → moderately_different; else
    significantly_different. Empty reference set → unavailable. A low-overlap
    caveat is always attached — topic/context differences explain low overlap.
    """
    reference = [item for item in (profile_items or [])
                 if (item.get("sample_presence") or 0) >= min_presence]
    row: dict = {"name": name, "kind": "overlap",
                 "reference_size": len(reference),
                 "matched": [], "overlap": None, "weighted_overlap": None,
                 "status": UNAVAILABLE, "reason": None,
                 "caveat": ("low overlap may reflect topic or context differences, "
                            "not inconsistency")}
    if not reference:
        row["reason"] = "profile has no recurring patterns at presence >= 0.5"
        return row
    matched = [item["ngram"] if "ngram" in item else item["term"]
               for item in reference
               if (item.get("ngram", item.get("term")) in draft_phrases)]
    presence_sum = sum(item.get("sample_presence", 0) for item in reference)
    matched_presence = sum(item.get("sample_presence", 0) for item in reference
                           if (item.get("ngram", item.get("term")) in draft_phrases))
    overlap = len(matched) / len(reference)
    weighted = (matched_presence / presence_sum) if presence_sum else 0.0
    row["matched"] = sorted(matched)
    row["overlap"] = overlap
    row["weighted_overlap"] = weighted
    row["status"] = CLOSE if overlap >= 0.5 else (MODERATE if overlap >= 0.2 else SIGNIFICANT)
    return row


def compare_stability_label(name: str, draft_cov: float | None,
                            profile_label: str | None) -> dict:
    """Compare spread bands (stable/moderate/variable): same → close, adjacent →
    moderately_different, opposite ends → significantly_different. Missing → unavailable."""
    order = ["stable", "moderate", "variable"]
    row: dict = {"name": name, "kind": "stability",
                 "draft_value": _cov_to_label(draft_cov),
                 "profile_value": profile_label,
                 "status": UNAVAILABLE, "reason": None}
    if row["draft_value"] is None:
        row["reason"] = "draft spread unavailable"
        return row
    if profile_label not in order:
        row["reason"] = "profile spread label unavailable"
        return row
    gap = abs(order.index(row["draft_value"]) - order.index(profile_label))
    row["status"] = CLOSE if gap == 0 else (MODERATE if gap == 1 else SIGNIFICANT)
    return row


def cov_to_label_public(cov: float | None) -> str | None:
    """Map a coefficient of variation to the shared stability bands."""
    return _cov_to_label(cov)


def _cov_to_label(cov: float | None) -> str | None:
    if cov is None or not _finite(cov):
        return None
    if cov < 0.15:
        return "stable"
    if cov < 0.35:
        return "moderate"
    return "variable"


def _usable_std(std) -> bool:
    return std is not None and _finite(std) and std > _EPS


def _finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) \
        and math.isfinite(value)
