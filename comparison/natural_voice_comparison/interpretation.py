"""Human-readable explanations for comparison rows (factual, non-anthropomorphic).

Every sentence describes a measurement relationship (draft value vs. profile range).
Forbidden vocabulary — "AI-like", "human-like", "suspicious", "detector", scores —
never appears here. Metric-specific phrasing falls back to a generic template.
"""

from __future__ import annotations

from .metrics import CLOSE, MODERATE, SIGNIFICANT, UNAVAILABLE

# metric name → (higher-means-phrase, lower-means-phrase). Direction words describe
# the draft relative to the profile ("longer sentences", not "worse sentences").
_DIRECTIONS = {
    "average_sentence_length": ("longer sentences on average", "shorter sentences on average"),
    "median_sentence_length": ("longer typical sentences", "shorter typical sentences"),
    "short_sentence_ratio": ("more short sentences", "fewer short sentences"),
    "medium_sentence_ratio": ("more medium-length sentences", "fewer medium-length sentences"),
    "long_sentence_ratio": ("more long sentences", "fewer long sentences"),
    "average_words_per_paragraph": ("longer paragraphs", "shorter paragraphs"),
    "average_sentences_per_paragraph": ("more sentences per paragraph", "fewer sentences per paragraph"),
    "median_words_per_paragraph": ("longer typical paragraphs", "shorter typical paragraphs"),
    "vocabulary_diversity": ("more varied vocabulary", "more repeated vocabulary"),
    "guiraud_r": ("richer vocabulary for its length", "plainer vocabulary for its length"),
    "average_word_length": ("longer words on average", "shorter words on average"),
    "median_word_length": ("longer typical words", "shorter typical words"),
    "punctuation_density": ("denser punctuation", "sparser punctuation"),
    "pronoun_ratio": ("more pronouns", "fewer pronouns"),
    "transitions_per_100_words": ("more transition connectives", "fewer transition connectives"),
    "flesch_reading_ease": ("easier-reading prose", "harder-reading prose"),
    "flesch_kincaid_grade": ("higher grade-level complexity", "lower grade-level complexity"),
    "gunning_fog": ("heavier, more complex sentences", "lighter sentences"),
    "coleman_liau": ("denser word-level complexity", "plainer word-level complexity"),
    "automated_readability_index": ("more complex surface text", "simpler surface text"),
}


def explain_metric(row: dict) -> str | None:
    """One factual sentence for a numeric metric row, or None if unavailable."""
    status = row.get("status")
    if status == UNAVAILABLE:
        return f"{row['name']}: not compared ({row.get('reason') or 'missing data'})."
    if status == CLOSE:
        return f"{row['name']}: close to the profile."
    direction = _direction(row)
    profile_range = _format_range(row.get("profile_range"))
    return (f"{row['name']}: {status.replace('_', ' ')} — the draft {direction} "
            f"(draft {row['draft_value']}, profile typical {profile_range}).")


def explain_overlap(row: dict, dimension: str) -> str:
    """Factual sentence for an overlap row, always carrying the topic caveat."""
    if row.get("status") == UNAVAILABLE:
        return f"{dimension} phrase overlap: not compared ({row.get('reason')})."
    overlap = row.get("overlap") or 0.0
    text = (f"{dimension} phrase overlap with recurring profile patterns: "
            f"{row['status'].replace('_', ' ')} "
            f"({len(row['matched'])} of {row['reference_size']} patterns overlap).")
    if row["status"] != CLOSE:
        text += " Topic or context differences may explain low overlap."
    return text


def _direction(row: dict) -> str:
    phrases = _DIRECTIONS.get(row["name"])
    difference = row.get("difference") or 0
    higher = difference > 0
    if phrases:
        return phrases[0] if higher else phrases[1]
    return "higher values" if higher else "lower values"


def _format_range(profile_range) -> str:
    if not profile_range:
        return "n/a"
    lo, hi = profile_range
    return f"{lo}–{hi}"


def dimension_headline(dimension: str, status: str) -> str:
    """Short headline per dimension, e.g. 'Sentence structure: Close'."""
    pretty = dimension.replace("_", " ").capitalize()
    return f"{pretty}: {status.replace('_', ' ').capitalize()}"
