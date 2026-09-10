"""Orchestrator for the Natural Voice analyzer.

``analyze_text`` runs every measurement exactly once over shared tokenization
results where practical and returns a JSON-serializable dict. Output contains
descriptive statistics only — no scores, verdicts, or authorship claims.
"""

from __future__ import annotations

from . import features
from .output import finalize

ANALYZER_VERSION = "0.1.0"


def analyze_text(
    text: str,
    top_k: int = 20,
    include_character_ngrams: bool = False,
    char_n: int = 3,
    language: str = "en",
) -> dict:
    """Analyze ``text`` and return a JSON-serializable feature dict.

    Args:
        text: input text (treated as untrusted data; never executed or logged).
        top_k: number of most-frequent items returned for vocabulary/N-gram lists.
        include_character_ngrams: opt-in character n-gram inventory (off by default).
        char_n: length of character n-grams when enabled.
        language: language tag recorded in metadata (readability is English-calibrated).

    Raises:
        TypeError: if ``text`` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    if top_k < 1:
        raise ValueError("top_k must be >= 1")

    result = {
        "metadata": {
            "analyzer_version": ANALYZER_VERSION,
            "language": language,
        },
        "basic": features.basic_features(text),
        "sentence_structure": features.sentence_structure(text),
        "paragraph_structure": features.paragraph_structure(text),
        "vocabulary": features.vocabulary_features(text, top_k=top_k),
        "punctuation": features.punctuation_features(text),
        "readability": features.readability_features(text),
        "linguistic": features.linguistic_features(text),
        "ngrams": features.ngram_features(text, top_k=top_k),
    }
    if include_character_ngrams:
        result["ngrams"]["character_ngrams"] = features.character_ngram_features(
            text, n=char_n, top_k=top_k
        )
    return finalize(result)
