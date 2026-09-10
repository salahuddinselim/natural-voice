"""Author Voice Profile builder: samples → Phase 4 analysis → aggregated profile.

Local-only: samples are analyzed in memory and never stored, logged, uploaded, or
sent anywhere. The profile contains derived statistics (means, ranges, common
patterns) — never the original documents. Short quoted phrases inside N-gram
inventories are characteristic patterns, not stored documents.

Schema note: the envelope (``profile_version``, ``metadata``, ``confidence`` levels
low/medium/high) follows the Phase 5 specification; the dimension vocabularies
(formality bands, punctuation bands, transition bands) reuse Phase 3's
``analysis/voice-profile-spec.md``. One deliberate deviation: Phase 3 used confidence
``low | moderate | strong``; Phase 5 mandates ``low | medium | high`` and governs.
"""

from __future__ import annotations

import logging

from natural_voice_analyzer import ANALYZER_VERSION, analyze_text
from natural_voice_analyzer.features import PUNCTUATION_MARKS
from natural_voice_analyzer.output import finalize

logger = logging.getLogger("natural_voice.profile")

from .aggregation import (
    aggregate_ngrams,
    aggregate_numeric,
    aggregate_terms,
    detect_outliers,
    sample_weight,
    stability_label,
)
from .confidence import build_confidence

PROFILE_VERSION = "0.1.0"
CONTEXTS = ("general", "academic", "technical", "casual")
READABILITY_METRICS = (
    "flesch_reading_ease",
    "flesch_kincaid_grade",
    "gunning_fog",
    "coleman_liau",
    "automated_readability_index",
)
NGRAM_TOP_N = 30
TERM_TOP_N = 30


def build_profile(
    samples: list[str],
    context: str = "general",
    language: str = "en",
    top_k: int = 30,
    include_character_ngrams: bool = False,
) -> dict:
    """Build an Author Voice Profile from genuine writing samples.

    Args:
        samples: list of sample texts (each treated as untrusted data: measured,
            never executed, never stored, never logged).
        context: one of general/academic/technical/casual (metadata only; no
            automatic classification is performed).
        language: language tag recorded in metadata (analyzer is English-calibrated).
        top_k: inventory depth per sample for word/N-gram lists.
        include_character_ngrams: opt-in character n-gram inventory per sample.

    Returns:
        JSON-serializable profile dict (derived statistics only).

    Raises:
        TypeError: non-string sample or invalid argument types.
        ValueError: empty sample list, no usable samples, bad context/top_k.
    """
    _check_args(samples, context, language, top_k)
    analyses, skipped = _analyze_samples(samples, language, top_k,
                                         include_character_ngrams)
    if not analyses:
        raise ValueError("no usable writing samples (all empty or whitespace-only)")
    weights = [sample_weight(a["basic"]["words"]) for a in analyses]
    words = [a["basic"]["words"] for a in analyses]
    total_words = sum(words)

    feature_coverage: dict[str, int] = {}

    def agg(getter, name):
        values = [getter(a) for a in analyses]
        result = aggregate_numeric(values, weights)
        feature_coverage[name] = result["n"]
        return result

    def num(section, key):
        return agg(lambda a, s=section, k=key: a[s].get(k), f"{section}.{key}")

    sentence_avg = num("sentence_structure", "average_length")
    ttr = num("vocabulary", "type_token_ratio")
    words_per_para = num("paragraph_structure", "average_words_per_paragraph")

    profile = {
        "profile_version": PROFILE_VERSION,
        "metadata": {
            "sample_count": len(analyses),
            "total_words": total_words,
            "language": language.lower(),
            "context": context,
            "analyzer_version": ANALYZER_VERSION,
            "skipped_samples": skipped,
        },
        "vocabulary": {
            "diversity": ttr,
            "diversity_stability": stability_label(ttr["mean"], ttr["std"]),
            "guiraud_r": num("vocabulary", "guiraud_r"),
            "average_word_length": num("vocabulary", "average_word_length"),
            "median_word_length": num("vocabulary", "median_word_length"),
            "common_terms": aggregate_terms(
                [{w: c for w, c in a["vocabulary"]["top_words"]} for a in analyses],
                words, top_n=TERM_TOP_N),
        },
        "sentence_structure": {
            "average_length": sentence_avg,
            "length_stability": stability_label(sentence_avg["mean"], sentence_avg["std"]),
            "median_length": num("sentence_structure", "median_length"),
            "short_ratio": num("sentence_structure", "short_ratio"),
            "medium_ratio": num("sentence_structure", "medium_ratio"),
            "long_ratio": num("sentence_structure", "long_ratio"),
        },
        "paragraph_structure": {
            "average_words_per_paragraph": words_per_para,
            "size_stability": stability_label(words_per_para["mean"], words_per_para["std"]),
            "average_sentences_per_paragraph": num(
                "paragraph_structure", "average_sentences_per_paragraph"),
            "median_words_per_paragraph": num(
                "paragraph_structure", "median_words_per_paragraph"),
        },
        "punctuation": {
            mark: {"per_100_words": agg(
                lambda a, m=mark: a["punctuation"]["per_100_words"].get(m),
                f"punctuation.{mark}")}
            for mark in PUNCTUATION_MARKS
        } | {"density": num("punctuation", "punctuation_density")},
        "readability": {
            metric: agg(lambda a, m=metric: a["readability"].get(m),
                        f"readability.{metric}")
            for metric in READABILITY_METRICS
        },
        "linguistic": {
            "pronoun_ratio": num("linguistic", "pronoun_ratio"),
            "transitions_per_100_words": agg(
                lambda a: (a["linguistic"]["transition_count"] / a["basic"]["words"] * 100)
                if a["basic"]["words"] else None,
                "linguistic.transitions_per_100_words"),
            "common_connectives": aggregate_terms(
                [a["linguistic"]["transition_counts"] for a in analyses],
                words, top_n=TERM_TOP_N),
        },
        "ngrams": {
            "common_bigrams": aggregate_ngrams(
                [a["ngrams"]["bigrams"] for a in analyses], words, top_n=NGRAM_TOP_N),
            "common_trigrams": aggregate_ngrams(
                [a["ngrams"]["trigrams"] for a in analyses], words, top_n=NGRAM_TOP_N),
        },
        "patterns": _build_patterns(analyses, words),
        "outlier_notes": (
            detect_outliers([a["sentence_structure"]["average_length"] for a in analyses],
                            "average_sentence_length")
            + detect_outliers([a["basic"]["words"] for a in analyses], "word_count")
        ),
    }
    profile["confidence"] = build_confidence(
        len(analyses), total_words, feature_coverage, skipped)
    logger.info("profile built: samples=%d words=%d confidence=%s",
                len(analyses), total_words,
                profile["confidence"]["overall"])
    return finalize(profile)


def build_profile_from_files(
    paths: list[str],
    context: str = "general",
    language: str = "en",
    top_k: int = 30,
    include_character_ngrams: bool = False,
) -> dict:
    """Build a profile from text files (UTF-8). Files are read and measured only.

    Raises:
        ValueError: listing paths that are missing or unreadable.
    """
    from pathlib import Path

    samples = []
    bad = []
    for raw in paths:
        path = Path(raw)
        try:
            samples.append(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            bad.append(str(raw))
    if bad:
        raise ValueError(f"cannot read sample files: {', '.join(bad)}")
    return build_profile(samples, context=context, language=language, top_k=top_k,
                         include_character_ngrams=include_character_ngrams)


def _check_args(samples, context, language, top_k) -> None:
    if not isinstance(samples, list) or not samples:
        raise ValueError("samples must be a non-empty list of strings")
    for sample in samples:
        if not isinstance(sample, str):
            raise TypeError(f"each sample must be str, got {type(sample).__name__}")
    if context not in CONTEXTS:
        raise ValueError(f"context must be one of {CONTEXTS}, got {context!r}")
    if not isinstance(language, str) or not language.strip():
        raise ValueError("language must be a non-empty string")
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be an int >= 1")


def _analyze_samples(samples, language, top_k, include_character_ngrams):
    """Analyze each sample once; skip empties (counted, never stored)."""
    analyses = []
    skipped = 0
    for sample in samples:
        if not sample.strip():
            skipped += 1
            continue
        result = analyze_text(sample, top_k=top_k,
                              include_character_ngrams=include_character_ngrams,
                              language=language)
        if not result["basic"]["words"]:
            skipped += 1
            continue
        analyses.append(result)
    return analyses, skipped


def _build_patterns(analyses, words) -> dict:
    """Recurring phrases, connectives, and structural tendencies (deterministic)."""
    trigrams = aggregate_ngrams([a["ngrams"]["trigrams"] for a in analyses],
                                words, top_n=NGRAM_TOP_N)
    repeated = [item for item in trigrams if (item["sample_presence"] or 0) >= 0.5]
    connectives = aggregate_terms(
        [a["linguistic"]["transition_counts"] for a in analyses], words, top_n=10)
    notes = []
    short = aggregate_numeric(
        [a["sentence_structure"]["short_ratio"] for a in analyses])
    long_ = aggregate_numeric(
        [a["sentence_structure"]["long_ratio"] for a in analyses])
    if short["mean"] is not None and short["mean"] > 0.5:
        notes.append("majority of sentences are short")
    if long_["mean"] is not None and long_["mean"] > 0.5:
        notes.append("majority of sentences are long")
    para = aggregate_numeric(
        [a["paragraph_structure"]["average_sentences_per_paragraph"] for a in analyses])
    if para["mean"] is not None:
        if para["mean"] <= 2.5:
            notes.append("typically short paragraphs")
        elif para["mean"] >= 6:
            notes.append("typically long paragraphs")
    return {
        "repeated_phrases": repeated,
        "recurring_connectives": [c["term"] for c in connectives],
        "structural_notes": notes,
        "note": ("observable tendencies only; no beliefs, traits, or "
                 "personal attributes are inferred"),
    }
