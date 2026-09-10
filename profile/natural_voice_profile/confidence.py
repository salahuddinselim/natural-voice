"""Profile confidence levels (engineering heuristics, not validated probabilities).

The overall level reflects evidence quantity — total words, sample count — because
more, longer samples support more reliable tendencies. Per-feature coverage records
how many samples each measurement rests on. Levels are categorical (low/medium/high);
no pseudo-precise percentages are emitted.
"""

from __future__ import annotations

# HEURISTIC thresholds, aligned with analysis/voice-profile-spec.md §4:
# low below ~500 words or fewer than 2 samples; high at 1500+ words across 4+ samples.
LOW_WORD_THRESHOLD = 500
HIGH_WORD_THRESHOLD = 1500
HIGH_SAMPLE_THRESHOLD = 4

LEVELS = ("low", "medium", "high")


def overall_confidence(sample_count: int, total_words: int) -> str:
    """Overall evidence level for a profile."""
    if sample_count < 2 or total_words < LOW_WORD_THRESHOLD:
        return "low"
    if sample_count >= HIGH_SAMPLE_THRESHOLD and total_words >= HIGH_WORD_THRESHOLD:
        return "high"
    return "medium"


def build_confidence(sample_count: int, total_words: int,
                     feature_coverage: dict, skipped_samples: int = 0) -> dict:
    """Confidence block stored in the profile."""
    return {
        "overall": overall_confidence(sample_count, total_words),
        "sample_count": sample_count,
        "total_words": total_words,
        "skipped_samples": skipped_samples,
        "feature_coverage": feature_coverage,
        "note": ("engineering heuristic based on evidence quantity; "
                 "not a statistical probability"),
    }
