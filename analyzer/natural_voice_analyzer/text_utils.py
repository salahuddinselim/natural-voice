"""Low-level text utilities for the Natural Voice analyzer.

All functions are deterministic, local, and dependency-free (standard library only).
Tokenization and segmentation rules are documented below so measurements stay
reproducible. These are engineering heuristics, not claims from the research paper.

Tokenization rules (``tokenize_words``):
  - Unicode-aware: word characters match ``[^\\W\\d_']`` sequences with internal
    apostrophes kept (e.g. "don't" stays one token).
  - Numbers (``\\d+`` possibly with decimals) are tokens.
  - Normalization for counting: lowercase; surrounding punctuation stripped by the
    regex itself; internal apostrophes preserved; numbers kept as-is.
  - Rationale: preserve technical terminology and contractions instead of mangling them.

Sentence segmentation (``split_sentences``):
  - Splits on ``.`` ``!`` ``?`` ``…`` followed by whitespace + uppercase letter/digit,
    or at end of text. A small guard list of common abbreviations (Mr., Dr., e.g.,
    i.e., etc., vs., approx., …) suppresses false splits. This is a heuristic that
    works for normal English prose; it is not a full sentence parser.

Paragraph segmentation (``split_paragraphs``):
  - Blank-line-separated blocks. Single newlines inside a block do not split.

Syllable counting (``count_syllables``):
  - Vowel-group heuristic with silent-e and -es/-ed adjustments. Approximate:
    adequate for readability estimates, not exact for every word. Non-English text
    degrades gracefully (counts, not crashes).
"""

from __future__ import annotations

import re
import unicodedata

_WORD_RE = re.compile(r"[^\W\d_']+(?:'[^\W\d_']+)?|\d+(?:\.\d+)?", re.UNICODE)
_SENTENCE_END_RE = re.compile(r"([.!?…]+)(\s+)(?=[\"'“”‘’(\[]*[A-Z0-9])")

# Common abbreviations whose trailing period must not end a sentence.
_ABBREVIATIONS = frozenset({
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st",
    "e.g", "i.e", "etc", "vs", "approx", "no", "fig", "ref",
    "al", "dept", "univ", "inc", "ltd", "co",
})

_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFKC) and line endings without altering words."""
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    text = unicodedata.normalize("NFKC", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_paragraphs(text: str) -> list[str]:
    """Split blank-line-separated blocks; drop empty blocks."""
    text = normalize_text(text)
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]


def tokenize_words(text: str) -> list[str]:
    """Return word tokens in order, original casing preserved."""
    return _WORD_RE.findall(normalize_text(text))


def normalize_token(token: str) -> str:
    """Lowercase a token for frequency counting."""
    return token.lower()


def _is_abbreviation_period(text: str, pos: int) -> bool:
    """Check whether the period at ``pos`` likely belongs to a known abbreviation."""
    # Bounded window: abbreviations are short, so never scan the whole prefix
    # (scanning text[:pos] on every period would make segmentation quadratic).
    window = text[max(0, pos - 30): pos + 1]
    match = re.search(r"([A-Za-z][A-Za-z.]*)\.$", window)
    if not match:
        return False
    candidate = match.group(1).lower().rstrip(".")
    return candidate in _ABBREVIATIONS or (
        "." in match.group(1) and len(match.group(1)) <= 6
    )


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using the documented heuristic."""
    text = normalize_text(text).strip()
    if not text:
        return []
    sentences: list[str] = []
    start = 0
    for match in _SENTENCE_END_RE.finditer(text):
        punct_pos = match.start(1)
        if text[punct_pos] == "." and _is_abbreviation_period(text, punct_pos):
            continue
        chunk = text[start: match.end(1)].strip()
        if chunk:
            sentences.append(chunk)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return [s for s in sentences if _WORD_RE.search(s)]


def count_syllables(word: str) -> int:
    """Approximate syllable count for one word (heuristic, minimum 1 for non-empty)."""
    cleaned = re.sub(r"[^a-z]", "", word.lower())
    if not cleaned:
        return 0
    if len(cleaned) <= 3:
        return 1
    # Drop silent trailing 'e' (but not '-le' endings like "table").
    if cleaned.endswith("e") and not cleaned.endswith("le"):
        cleaned = cleaned[:-1]
    groups = _VOWEL_GROUP_RE.findall(cleaned)
    count = len(groups)
    # Adjust common silent endings.
    if cleaned.endswith(("es", "ed")) and count > 1:
        count -= 1
    return max(count, 1)


def words_per_sentence(sentences: list[str]) -> list[int]:
    """Word count of each sentence."""
    return [len(tokenize_words(sentence)) for sentence in sentences]
