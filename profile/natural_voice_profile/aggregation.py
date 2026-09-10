"""Aggregation helpers for the profile builder.

All helpers are deterministic (sorted outputs, no randomness) and reusable.
Weighting and stability rules are project engineering heuristics, not scientific
findings — each is labeled HEURISTIC where it appears.
"""

from __future__ import annotations

import math
import statistics


def sample_weight(word_count: int) -> float:
    """Reliability weight of one sample from its word count.

    HEURISTIC: weight = sqrt(words). Statistical reliability grows sublinearly
    with length, and the square root bounds domination — a 100x longer sample
    carries 10x weight, not 100x. Minimum weight 1.0 for empty samples.
    """
    return math.sqrt(max(int(word_count), 1))


def aggregate_numeric(values: list, weights: list | None = None) -> dict:
    """Aggregate per-sample numeric values, skipping None (missing).

    Returns mean (weighted when ``weights`` given, else unweighted), median/min/
    max/std unweighted across samples (they describe cross-sample spread, i.e.
    stability — see ``stability_label``), plus ``n`` (samples contributing) and
    ``typical_range`` = [mean - std, mean + std] (HEURISTIC compact band for
    Phase 6 closeness checks; with n == 1 the range collapses to [mean, mean]).
    All-None input yields n == 0 with every statistic None.
    """
    paired = [(v, w) for v, w in zip(values, weights or [1.0] * len(values))
              if v is not None and math.isfinite(v)]
    if not paired:
        return {"mean": None, "median": None, "std": None, "min": None,
                "max": None, "n": 0, "typical_range": None}
    vals = [v for v, _ in paired]
    wts = [w for _, w in paired]
    total_w = sum(wts)
    mean = sum(v * w for v, w in paired) / total_w if total_w else None
    std = statistics.pstdev(vals) if len(vals) >= 2 else 0.0
    typical = [mean - std, mean + std] if mean is not None else None
    return {
        "mean": mean,
        "median": statistics.median(vals),
        "std": std,
        "min": min(vals),
        "max": max(vals),
        "n": len(vals),
        "typical_range": typical,
    }


def stability_label(mean: float | None, std: float | None) -> str | None:
    """Qualitative spread label from the coefficient of variation.

    HEURISTIC bands: CoV < 0.15 → "stable"; < 0.35 → "moderate"; else "variable".
    Returns None when the statistic is missing. Describes variation only — never
    quality or authorship.
    """
    if mean is None or std is None or not math.isfinite(mean) or not math.isfinite(std):
        return None
    if not mean:
        return "stable" if std == 0 else "variable"
    cov = abs(std / mean)
    if cov < 0.15:
        return "stable"
    if cov < 0.35:
        return "moderate"
    return "variable"


def aggregate_ngrams(per_sample_ngrams: list, per_sample_words: list,
                     top_n: int = 30) -> list:
    """Aggregate sample-level n-gram lists without letting long samples dominate.

    Each sample contributes its own (phrase, count) inventory; aggregation records
    per phrase: total raw ``count``, mean normalized ``frequency`` (count / sample
    words, averaged over samples containing the phrase), and ``sample_presence``
    (fraction of samples containing it). Sorted by presence desc, frequency desc,
    phrase asc — deterministic. Capped at ``top_n`` entries.
    """
    totals: dict[str, int] = {}
    freq_sums: dict[str, float] = {}
    presence: dict[str, int] = {}
    n = len(per_sample_ngrams)
    for grams, words in zip(per_sample_ngrams, per_sample_words):
        seen: set[str] = set()
        for phrase, count in grams:
            totals[phrase] = totals.get(phrase, 0) + count
            if words:
                freq_sums[phrase] = freq_sums.get(phrase, 0.0) + count / words
            seen.add(phrase)
        for phrase in seen:
            presence[phrase] = presence.get(phrase, 0) + 1
    ranked = sorted(
        totals,
        key=lambda p: (-(presence.get(p, 0) / n if n else 0),
                       -(freq_sums.get(p, 0.0) / max(presence.get(p, 1), 1)),
                       p),
    )
    result = []
    for phrase in ranked[:top_n]:
        present = presence.get(phrase, 0)
        result.append({
            "ngram": phrase,
            "count": totals[phrase],
            "frequency": (freq_sums.get(phrase, 0.0) / present) if present else None,
            "sample_presence": (present / n) if n else None,
        })
    return result


def aggregate_terms(per_sample_counts: list, per_sample_words: list,
                    top_n: int = 30) -> list:
    """Aggregate word-frequency dicts like n-grams (presence + mean rate)."""
    as_lists = [[(w, c) for w, c in counts.items()]
                for counts in per_sample_counts]
    return [
        {"term": item["ngram"], "count": item["count"],
         "frequency": item["frequency"], "sample_presence": item["sample_presence"]}
        for item in aggregate_ngrams(as_lists, per_sample_words, top_n=top_n)
    ]


def detect_outliers(per_sample_values: list, feature_name: str,
                    minimum_samples: int = 4) -> list:
    """Flag sample indices whose value deviates strongly from the rest.

    HEURISTIC: |z| > 2 against the unweighted mean/std, requires at least
    ``minimum_samples`` (default 4) — below that, variation is recorded but no
    sample is singled out. Outliers are preserved in the profile; notes only
    record their positions (indices, never text).
    """
    vals = [(i, v) for i, v in enumerate(per_sample_values)
            if v is not None and math.isfinite(v)]
    if len(vals) < minimum_samples:
        return []
    numbers = [v for _, v in vals]
    mean = statistics.fmean(numbers)
    std = statistics.pstdev(numbers)
    if not std:
        return []
    return [
        {"sample_index": i, "feature": feature_name, "value": v,
         "z_score": (v - mean) / std}
        for i, v in vals if abs((v - mean) / std) > 2.0
    ]
