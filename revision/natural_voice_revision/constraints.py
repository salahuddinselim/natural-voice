"""Hard and soft revision constraints (pure functions, no LLM calls).

Hard failures reject a revision: empty output, lost numbers, lost citations,
extreme length change, or near-total rewrite (low similarity). Soft warnings
flag dropped characteristic terms without rejecting. Thresholds are engineering
heuristics, documented below — not scientific findings.
"""

from __future__ import annotations

import difflib
import re

# Word-count ratio bounds: revised must stay within [0.3x, 3.0x] of the original.
# HEURISTIC: catches truncation/runaway generation, not legitimate editing range.
MIN_LENGTH_RATIO = 0.3
MAX_LENGTH_RATIO = 3.0

# difflib similarity floor below which the revision is no longer recognizably
# the same document. HEURISTIC: echo ≈ 1.0; genuine rewrites stay well above 0.25.
MIN_SIMILARITY = 0.25

_NUMBER_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?%?")
_CITATION_RES = (
    re.compile(r"\[\d+(?:\s*[-,]\s*\d+)*\]"),          # [1], [2-4]
    re.compile(r"\([A-Z][A-Za-z'’\-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z'’\-]+)?"
               r"(?:\s+et al\.)?,?\s+\d{4}[a-z]?\)"),  # (Author, 2024)
    re.compile(r"[A-Z][A-Za-z'’\-]+(?:\s+et al\.)?\s*\(\d{4}[a-z]?\)"),  # Smith et al. (2025)
)


def extract_numbers(text: str) -> set[str]:
    """All numeric tokens (percentages, decimals, grouped thousands, years)."""
    return set(_NUMBER_RE.findall(text or ""))


def extract_citations(text: str) -> set[str]:
    """Citation-like markers ([1], (Author, 2024), Smith et al. (2025))."""
    found: set[str] = set()
    for pattern in _CITATION_RES:
        found.update(pattern.findall(text or ""))
    return found


def word_count(text: str) -> int:
    return len(re.findall(r"[^\W\d_']+(?:'[^\W\d_']+)?|\d+(?:\.\d+)?", text or "", re.UNICODE))


def similarity(original: str, revised: str) -> float:
    """difflib ratio on word tokens (0–1); recognizability, not quality."""
    a = (original or "").split()
    b = (revised or "").split()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def check_constraints(original: str, revised: str,
                      characteristic_terms: list | None = None) -> dict:
    """Validate one revision; returns {passed, failures[], warnings[]}.

    ``characteristic_terms``: profile terms with sample_presence == 1.0 worth
    keeping when already present in the original (soft warnings only).
    """
    failures: list[str] = []
    warnings: list[str] = []
    revised = revised or ""
    if not revised.strip():
        return {"passed": False, "failures": ["empty revision"], "warnings": warnings}

    original_numbers = extract_numbers(original)
    missing_numbers = sorted(n for n in original_numbers if n not in revised)
    if missing_numbers:
        failures.append(f"lost numerical values: {missing_numbers[:10]}")

    original_cites = extract_citations(original)
    missing_cites = sorted(c for c in original_cites if c not in revised)
    if missing_cites:
        failures.append(f"lost citation markers: {missing_cites[:10]}")

    original_words = word_count(original)
    revised_words = word_count(revised)
    if original_words:
        ratio = revised_words / original_words
        if not (MIN_LENGTH_RATIO <= ratio <= MAX_LENGTH_RATIO):
            failures.append(
                f"excessive length change: {original_words} → {revised_words} words "
                f"(ratio {ratio:.2f} outside [{MIN_LENGTH_RATIO}, {MAX_LENGTH_RATIO}])")

    sim = similarity(original, revised)
    if sim < MIN_SIMILARITY:
        failures.append(
            f"revision is unrecognizable as the same document "
            f"(similarity {sim:.2f} < {MIN_SIMILARITY})")

    for term in characteristic_terms or []:
        if len(term) > 3 and term.isalpha() and term in (original or "").lower() \
                and term not in revised.lower():
            warnings.append(f"dropped characteristic term: {term!r}")
            if len(warnings) >= 10:
                break

    return {"passed": not failures, "failures": failures, "warnings": warnings}
