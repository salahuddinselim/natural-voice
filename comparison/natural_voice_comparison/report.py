"""Report assembly: dimensions, overall status, summary, limitations.

Dimension statuses aggregate metric scores (close=0, moderately_different=1,
significantly_different=2) by mean with cutoffs <0.5 → close, <1.25 →
moderately_different, else significantly_different. Overall status aggregates
dimension scores by configurable weights (renormalized over available dimensions)
with the same cutoffs. All cutoffs are project heuristics, documented here.
"""

from __future__ import annotations

from . import metrics as m
from .interpretation import dimension_headline, explain_metric, explain_overlap

DIMENSION_ORDER = (
    "sentence_structure",
    "paragraph_structure",
    "vocabulary",
    "punctuation",
    "readability",
    "cohesion",
    "ngrams",
)

DEFAULT_WEIGHTS = {
    "sentence_structure": 1.0,
    "paragraph_structure": 1.0,
    "vocabulary": 1.0,
    "punctuation": 0.8,
    "readability": 0.8,
    "cohesion": 0.8,
    "ngrams": 0.7,
}

_SCORES = {m.CLOSE: 0, m.MODERATE: 1, m.SIGNIFICANT: 2}


def build_dimensions(draft: dict, profile: dict, top_k: int) -> dict:
    """Compare every supported dimension; returns {dimension: dimension_report}."""
    from natural_voice_analyzer.features import PUNCTUATION_MARKS

    dimensions = {}
    dimensions["sentence_structure"] = _dimension(
        "sentence_structure",
        _sentence_metrics(draft, profile),
        notes=["Buckets short<12 / medium 12–25 / long>25 words (descriptive only)."],
    )
    dimensions["paragraph_structure"] = _dimension(
        "paragraph_structure", _paragraph_metrics(draft, profile), notes=[])
    dimensions["vocabulary"] = _dimension(
        "vocabulary", _vocabulary_metrics(draft, profile), notes=[])
    dimensions["punctuation"] = _dimension(
        "punctuation",
        _punctuation_metrics(draft, profile, PUNCTUATION_MARKS), notes=[])
    dimensions["readability"] = _dimension(
        "readability", _readability_metrics(draft, profile),
        notes=["Readability estimates describe surface complexity, not quality."])
    dimensions["cohesion"] = _dimension(
        "cohesion", _cohesion_metrics(draft, profile), notes=[])
    dimensions["ngrams"] = _dimension(
        "ngrams", _ngram_metrics(draft, profile),
        notes=["Low phrase overlap often reflects topic/context differences."])
    return dimensions


def overall_status(dimensions: dict, weights: dict) -> str:
    """Weighted mean of dimension scores with documented cutoffs."""
    total, total_w = 0.0, 0.0
    for dim, report in dimensions.items():
        if report["status"] == m.UNAVAILABLE:
            continue
        w = weights.get(dim, 0.0)
        total += _SCORES[report["status"]] * w
        total_w += w
    if not total_w:
        return m.UNAVAILABLE
    mean = total / total_w
    return m.CLOSE if mean < 0.5 else (m.MODERATE if mean < 1.25 else m.SIGNIFICANT)


def build_summary(dimensions: dict, profile: dict, draft_words: int,
                  comparison_confidence: str, context_note: str | None) -> list[str]:
    """Answer: what matches, what differs, how strong is the evidence, cautions."""
    matches = [d for d, r in dimensions.items() if r["status"] == m.CLOSE]
    differs = [(d, r) for d, r in dimensions.items()
               if r["status"] in (m.MODERATE, m.SIGNIFICANT)]
    lines = []
    if matches:
        lines.append("Close to the profile: " + ", ".join(matches) + ".")
    for dim, report in differs:
        worst = _worst_metrics(report["metrics"])
        lines.append(dimension_headline(dim, report["status"]) + ". " + worst)
    lines.append(
        f"This comparison is based on {profile['metadata']['sample_count']} profile "
        f"samples ({profile['metadata']['total_words']} words) and a draft of "
        f"{draft_words} words.")
    if comparison_confidence == "low":
        lines.append("Comparison confidence is low: interpret differences cautiously.")
    if context_note:
        lines.append(context_note)
    ngram_status = dimensions.get("ngrams", {}).get("status")
    if ngram_status in (m.MODERATE, m.SIGNIFICANT):
        lines.append("N-gram overlap is limited; topic or context differences may explain this.")
    return lines


def build_limitations(dimensions: dict, draft_words: int,
                      context_note: str | None) -> list[str]:
    """Caveats: unavailable data, short drafts, heuristic nature, research boundary."""
    unavailable = [d for d, r in dimensions.items() if r["status"] == m.UNAVAILABLE]
    limits = []
    if unavailable:
        limits.append("Unavailable dimensions (not enough data, not errors): "
                      + ", ".join(unavailable) + ".")
    if draft_words < 100:
        limits.append("Draft is very short (<100 words): sentence, paragraph, N-gram, "
                      "and readability comparisons are limited.")
    elif draft_words < 400:
        limits.append("Draft is short (<400 words): N-gram and paragraph comparisons "
                      "carry less weight.")
    if context_note:
        limits.append(context_note)
    limits.append("Categories (close/moderately/significantly different) are project "
                  "heuristics, not validated authorship measurements.")
    limits.append("Research-boundary: features inform style comparison only; this system "
                  "does not reproduce the paper's classifier and makes no "
                  "human/AI determination.")
    return limits


# --- dimension metric builders -------------------------------------------------

def _sentence_metrics(draft, profile):
    section = profile.get("sentence_structure") or {}
    struct = draft.get("sentence_structure", {})
    rows = [
        m.compare_numeric("average_sentence_length", struct.get("average_length"),
                          section.get("average_length")),
        m.compare_numeric("median_sentence_length", struct.get("median_length"),
                          section.get("median_length")),
        m.compare_numeric("short_sentence_ratio", struct.get("short_ratio"),
                          section.get("short_ratio")),
        m.compare_numeric("medium_sentence_ratio", struct.get("medium_ratio"),
                          section.get("medium_ratio")),
        m.compare_numeric("long_sentence_ratio", struct.get("long_ratio"),
                          section.get("long_ratio")),
    ]
    draft_cov = struct.get("coefficient_of_variation")
    rows.append(m.compare_stability_label(
        "sentence_length_variation", draft_cov, section.get("length_stability")))
    return rows


def _paragraph_metrics(draft, profile):
    section = profile.get("paragraph_structure") or {}
    para = draft.get("paragraph_structure", {})
    rows = [
        m.compare_numeric("average_words_per_paragraph",
                          para.get("average_words_per_paragraph"),
                          section.get("average_words_per_paragraph")),
        m.compare_numeric("average_sentences_per_paragraph",
                          para.get("average_sentences_per_paragraph"),
                          section.get("average_sentences_per_paragraph")),
        m.compare_numeric("median_words_per_paragraph",
                          para.get("median_words_per_paragraph"),
                          section.get("median_words_per_paragraph")),
    ]
    mean = para.get("average_words_per_paragraph")
    std = para.get("words_std")
    draft_cov = (std / mean) if (mean and std is not None and mean) else None
    rows.append(m.compare_stability_label(
        "paragraph_size_variation", draft_cov, section.get("size_stability")))
    return rows


def _vocabulary_metrics(draft, profile):
    section = profile.get("vocabulary") or {}
    vocab = draft.get("vocabulary", {})
    rows = [
        m.compare_numeric("vocabulary_diversity", vocab.get("type_token_ratio"),
                          section.get("diversity")),
        m.compare_numeric("guiraud_r", vocab.get("guiraud_r"), section.get("guiraud_r")),
        m.compare_numeric("average_word_length", vocab.get("average_word_length"),
                          section.get("average_word_length")),
        m.compare_numeric("median_word_length", vocab.get("median_word_length"),
                          section.get("median_word_length")),
    ]
    draft_terms = {w for w, _ in (vocab.get("top_words") or [])}
    rows.append(m.compare_overlap("shared_characteristic_terms", draft_terms,
                                  section.get("common_terms")))
    return rows


def _punctuation_metrics(draft, profile, marks):
    section = profile.get("punctuation") or {}
    punct = draft.get("punctuation", {})
    rows = [m.compare_numeric("punctuation_density", punct.get("punctuation_density"),
                              (section.get("density") or {}))]
    per_100 = punct.get("per_100_words") or {}
    for mark in marks:
        rows.append(m.compare_numeric(
            f"punctuation_{mark}_per_100",
            per_100.get(mark),
            ((section.get(mark) or {}).get("per_100_words"))))
    return rows


def _readability_metrics(draft, profile):
    section = profile.get("readability") or {}
    read = draft.get("readability", {})
    return [m.compare_numeric(name, read.get(name), section.get(name))
            for name in ("flesch_reading_ease", "flesch_kincaid_grade",
                         "gunning_fog", "coleman_liau",
                         "automated_readability_index")]


def _cohesion_metrics(draft, profile):
    section = profile.get("linguistic") or {}
    ling = draft.get("linguistic", {})
    words = draft.get("basic", {}).get("words") or 0
    transitions = (ling.get("transition_count") / words * 100) if words else None
    rows = [
        m.compare_numeric("pronoun_ratio", ling.get("pronoun_ratio"),
                          section.get("pronoun_ratio")),
        m.compare_numeric("transitions_per_100_words", transitions,
                          section.get("transitions_per_100_words")),
    ]
    draft_conns = set((ling.get("transition_counts") or {}).keys())
    rows.append(m.compare_overlap("shared_connectives", draft_conns,
                                  section.get("common_connectives")))
    return rows


def _ngram_metrics(draft, profile):
    section = profile.get("ngrams") or {}
    grams = draft.get("ngrams", {})
    draft_bi = {phrase for phrase, _ in (grams.get("bigrams") or [])}
    draft_tri = {phrase for phrase, _ in (grams.get("trigrams") or [])}
    return [
        m.compare_overlap("common_bigrams", draft_bi, section.get("common_bigrams")),
        m.compare_overlap("common_trigrams", draft_tri, section.get("common_trigrams")),
    ]


# --- small helpers ---------------------------------------------------------------

def _worst_metrics(metrics: list) -> str:
    """Up to two strongest deviations, most significant first (deterministic)."""
    order = {m.SIGNIFICANT: 0, m.MODERATE: 1}
    bad = [r for r in metrics if r["status"] in order]
    bad.sort(key=lambda r: (order[r["status"]], r["name"]))
    parts = []
    for row in bad[:2]:
        if row["kind"] == "overlap":
            parts.append(explain_overlap(row, "phrases"))
        else:
            parts.append(explain_metric(row))
    return " ".join(p for p in parts if p)

def _dimension(name: str, rows: list, notes: list) -> dict:
    available = [r for r in rows if r["status"] != m.UNAVAILABLE]
    explanations = []
    for row in rows:
        if row["kind"] == "overlap":
            explanations.append(explain_overlap(row, name.replace("_", " ")))
        else:
            text = explain_metric(row)
            if text and row["status"] != m.CLOSE:
                explanations.append(text)
    if not available:
        status = m.UNAVAILABLE
    else:
        mean = sum(_SCORES[r["status"]] for r in available) / len(available)
        status = m.CLOSE if mean < 0.5 else (m.MODERATE if mean < 1.25 else m.SIGNIFICANT)
    return {"status": status, "metrics": rows,
            "explanations": explanations, "notes": notes}
