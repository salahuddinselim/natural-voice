"""Feature measurements for the Natural Voice analyzer.

Every function returns descriptive statistics only. Nothing here judges quality or
origin: there are no authorship scores, probabilities, or detector-related outputs.

Research traceability (paper: Nguyen, Hatua, Sung — "How to Detect AI-Generated Texts?"):
  - research-informed: word/character counts, word density, punctuation counts,
    readability formulas, N-gram inventories, pronoun/transition distributions
    (closed-class analogue of the paper's POS-related counts).
  - engineering decisions (ours, not the paper's): exact tokenization rules,
    sentence-length buckets, per-100-word normalization, Guiraud's R, threshold
    values, schema shape. The paper did not use these implementations.

Conventions:
  - Counts are ints, ratios are floats rounded to 4 decimals at the output layer.
  - Uncomputable values (e.g. readability of empty text) are ``None``, never invented.
  - Thresholds marked HEURISTIC are project choices, not scientific findings.
"""

from __future__ import annotations

import math
import re
import statistics
from collections import Counter

from .text_utils import (
    count_syllables,
    normalize_token,
    split_paragraphs,
    split_sentences,
    tokenize_words,
    words_per_sentence,
)

# Sentence-length buckets in words. HEURISTIC (matches analysis/voice-profile-spec.md).
SHORT_MAX = 11      # short: fewer than 12 words
MEDIUM_MAX = 25     # medium: 12–25 words; long: more than 25 words

# Punctuation marks inventoried by the analyzer.
PUNCTUATION_MARKS = [".", ",", ";", ":", "!", "?", "(", ")", "-", "—", '"']

# Closed English pronoun list for the linguistic section. Closed-class counting is
# deterministic; open-class POS (nouns/verbs/adjectives) is NOT guessed from word
# lists and remains a planned future feature.
PRONOUNS = frozenset({
    "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "we", "us", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",
    "who", "whom", "whose", "which", "what",
    "one", "ones", "oneself", "someone", "anyone", "everyone", "no one",
})

# Closed connective inventory for transition-frequency measurement. Records what the
# author uses from this list; authors may use others, which then appear in N-grams.
TRANSITION_CONNECTIVES = frozenset({
    "however", "therefore", "because", "although", "also", "then",
    "for example", "in addition", "moreover", "furthermore", "nevertheless",
    "consequently", "accordingly", "meanwhile", "otherwise", "instead",
    "first", "second", "third", "finally", "next", "thus", "hence",
    "though", "since", "while", "whereas", "despite", "unless", "until",
    "but", "and", "so", "yet", "or", "nor",
})


def basic_features(text: str) -> dict:
    """Character/word/sentence/paragraph counts and averages.

    - characters: all characters including whitespace.
    - characters_no_spaces: all characters excluding any whitespace.
    - average_word_length: mean token length in characters.
    - average_sentence_length: mean words per sentence (None when no sentences).
    - average_paragraph_length: mean words per paragraph (None when no paragraphs).
    """
    characters = len(text)
    characters_no_spaces = len("".join(text.split()))
    tokens = tokenize_words(text)
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)
    sentence_lengths = words_per_sentence(sentences)
    paragraph_lengths = [len(tokenize_words(p)) for p in paragraphs]
    return {
        "characters": characters,
        "characters_no_spaces": characters_no_spaces,
        "words": len(tokens),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "average_word_length": _mean([len(t) for t in tokens]),
        "average_sentence_length": _mean(sentence_lengths),
        "average_paragraph_length": _mean(paragraph_lengths),
        "median_sentence_length": _median(sentence_lengths),
        "min_sentence_length": min(sentence_lengths) if sentence_lengths else None,
        "max_sentence_length": max(sentence_lengths) if sentence_lengths else None,
    }


def sentence_structure(text: str) -> dict:
    """Sentence-length distribution and variation (descriptive buckets only)."""
    lengths = words_per_sentence(split_sentences(text))
    total = len(lengths)
    short = sum(1 for n in lengths if n <= SHORT_MAX)
    medium = sum(1 for n in lengths if SHORT_MAX < n <= MEDIUM_MAX)
    long = sum(1 for n in lengths if n > MEDIUM_MAX)
    std = statistics.pstdev(lengths) if len(lengths) >= 2 else (0.0 if lengths else None)
    mean = statistics.fmean(lengths) if lengths else None
    return {
        "count": total,
        "average_length": mean,
        "median_length": _median(lengths),
        "min_length": min(lengths) if lengths else None,
        "max_length": max(lengths) if lengths else None,
        "standard_deviation": std,
        # Coefficient of variation = std / mean; describes spread relative to scale.
        "coefficient_of_variation": (std / mean) if (std is not None and mean) else None,
        "short_ratio": (short / total) if total else None,
        "medium_ratio": (medium / total) if total else None,
        "long_ratio": (long / total) if total else None,
        "bucket_thresholds": {"short_max": SHORT_MAX, "medium_max": MEDIUM_MAX},
    }


def paragraph_structure(text: str) -> dict:
    """Paragraph lengths in words and sentences; blank-line-separated blocks."""
    paragraphs = split_paragraphs(text)
    word_lengths = [len(tokenize_words(p)) for p in paragraphs]
    sent_lengths = [len(split_sentences(p)) for p in paragraphs]
    return {
        "count": len(paragraphs),
        "average_words_per_paragraph": _mean(word_lengths),
        "median_words_per_paragraph": _median(word_lengths),
        "min_words_per_paragraph": min(word_lengths) if word_lengths else None,
        "max_words_per_paragraph": max(word_lengths) if word_lengths else None,
        "words_std": statistics.pstdev(word_lengths) if len(word_lengths) >= 2 else (
            0.0 if word_lengths else None),
        "average_sentences_per_paragraph": _mean(sent_lengths),
        "median_sentences_per_paragraph": _median(sent_lengths),
        "min_sentences_per_paragraph": min(sent_lengths) if sent_lengths else None,
        "max_sentences_per_paragraph": max(sent_lengths) if sent_lengths else None,
    }


def vocabulary_features(text: str, top_k: int = 20) -> dict:
    """Vocabulary diversity and repetition (lowercased, punctuation stripped by tokenizer).

    - type_token_ratio = unique / total. Strongly length-dependent: only compare TTR
      across texts of similar length; Guiraud's R (types / sqrt(tokens)) is the more
      stable companion metric for longer texts.
    - top_words: most frequent normalized tokens with counts.
    - repeated_words: tokens occurring more than twice, with counts.
    Numbers and contractions are kept as tokens (see text_utils rules).
    """
    tokens = [normalize_token(t) for t in tokenize_words(text)]
    total = len(tokens)
    counts = Counter(tokens)
    unique = len(counts)
    word_lengths = [len(t) for t in tokens]
    return {
        "total_words": total,
        "unique_words": unique,
        "type_token_ratio": (unique / total) if total else None,
        "guiraud_r": (unique / math.sqrt(total)) if total else None,
        "average_word_length": _mean(word_lengths),
        "median_word_length": _median(word_lengths),
        "min_word_length": min(word_lengths) if word_lengths else None,
        "max_word_length": max(word_lengths) if word_lengths else None,
        "word_length_std": statistics.pstdev(word_lengths) if len(word_lengths) >= 2 else (
            0.0 if word_lengths else None),
        "top_words": counts.most_common(top_k),
        "repeated_words": sorted(
            ((w, c) for w, c in counts.items() if c > 2),
            key=lambda item: (-item[1], item[0]),
        ),
    }


def punctuation_features(text: str) -> dict:
    """Raw counts and per-100-word frequencies per mark, plus overall density.

    punctuation_density = total inventoried marks / word count (None when no words).
    """
    words = len(tokenize_words(text))
    counts = {mark: text.count(mark) for mark in PUNCTUATION_MARKS}
    # Quotation marks: also count common Unicode variants under '"'.
    counts['"'] += sum(text.count(variant) for variant in ("“", "”", "„"))
    total = sum(counts.values())
    return {
        "counts": counts,
        "per_100_words": {
            mark: (count / words * 100) if words else None
            for mark, count in counts.items()
        },
        "total": total,
        "punctuation_density": (total / words) if words else None,
    }


def readability_features(text: str) -> dict:
    """Standard readability estimates (English prose; heuristic syllable counts).

    Implemented with the standard published formulas: Flesch Reading Ease,
    Flesch-Kincaid Grade, Gunning Fog, Coleman-Liau, Automated Readability Index.
    Dale-Chall, Spache, and Linsear Write need external word lists and are omitted.
    All values are None when the text has no sentences or no words. Language
    limitation: formulas are calibrated on English; other languages degrade.
    """
    tokens = tokenize_words(text)
    sentences = split_sentences(text)
    words = len(tokens)
    num_sentences = len(sentences)
    if not words or not num_sentences:
        return {
            "flesch_reading_ease": None,
            "flesch_kincaid_grade": None,
            "gunning_fog": None,
            "coleman_liau": None,
            "automated_readability_index": None,
            "note": "insufficient text",
        }
    syllables = sum(count_syllables(t) for t in tokens)
    characters = sum(len(t) for t in tokens)
    words_per_sentence = words / num_sentences
    syllables_per_word = syllables / words
    complex_words = sum(1 for t in tokens if count_syllables(t) >= 3)
    letters_per_100 = characters / words * 100
    sentences_per_100 = num_sentences / words * 100
    return {
        "flesch_reading_ease": 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word,
        "flesch_kincaid_grade": 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59,
        "gunning_fog": 0.4 * (words_per_sentence + 100 * complex_words / words),
        "coleman_liau": 0.0588 * letters_per_100 - 0.296 * sentences_per_100 - 15.8,
        "automated_readability_index": (
            4.71 * (characters / words) + 0.5 * words_per_sentence - 21.43
        ),
        "note": "heuristic syllable counts; English calibration",
    }


def linguistic_features(text: str) -> dict:
    """Closed-class distributions only: pronouns and transition connectives.

    Open-class POS (nouns/verbs/adjectives/adverbs) would require a tagger and is
    deliberately NOT guessed from word lists — see README limitations. NER and
    grammar-error measurement are likewise planned, not implemented.
    """
    tokens = [normalize_token(t) for t in tokenize_words(text)]
    total = len(tokens)
    counts = Counter(tokens)
    pronoun_total = sum(counts[p] for p in PRONOUNS if p in counts)
    lowered = " " + " ".join(tokens) + " "
    connective_counts = {
        conn: lowered.count(f" {conn} ") for conn in TRANSITION_CONNECTIVES
    }
    connective_counts = {k: v for k, v in connective_counts.items() if v}
    return {
        "total_words": total,
        "pronoun_count": pronoun_total,
        "pronoun_ratio": (pronoun_total / total) if total else None,
        "pronoun_counts": {p: counts[p] for p in PRONOUNS if p in counts},
        "transition_count": sum(connective_counts.values()),
        "transition_counts": dict(sorted(
            connective_counts.items(), key=lambda item: (-item[1], item[0]))),
        "nouns": None,
        "verbs": None,
        "adjectives": None,
        "adverbs": None,
        "named_entities": None,
        "notes": "open-class POS, NER, and error analysis are planned, not estimated",
    }


def ngram_features(text: str, top_k: int = 20) -> dict:
    """Most frequent word bigrams/trigrams over normalized tokens."""
    tokens = [normalize_token(t) for t in tokenize_words(text)]
    bigrams = Counter(zip(tokens, tokens[1:])) if len(tokens) >= 2 else Counter()
    trigrams = Counter(zip(tokens, tokens[1:], tokens[2:])) if len(tokens) >= 3 else Counter()
    return {
        "top_k": top_k,
        "bigrams": [[" ".join(gram), count] for gram, count in bigrams.most_common(top_k)],
        "trigrams": [[" ".join(gram), count] for gram, count in trigrams.most_common(top_k)],
    }


def character_ngram_features(text: str, n: int = 3, top_k: int = 20) -> dict:
    """Most frequent character n-grams (lowercased, whitespace collapsed). Optional."""
    cleaned = re.sub(r"\s+", " ", text.lower()).strip()
    grams = Counter(cleaned[i: i + n] for i in range(len(cleaned) - n + 1)) if len(cleaned) >= n else Counter()
    return {
        "n": n,
        "top_k": top_k,
        "ngrams": [[gram, count] for gram, count in grams.most_common(top_k)],
    }


def _mean(values: list) -> float | None:
    return statistics.fmean(values) if values else None


def _median(values: list) -> float | None:
    return statistics.median(values) if values else None
