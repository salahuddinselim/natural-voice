"""Validation for Author Voice Profiles.

``validate_profile`` returns a list of error strings (empty = valid);
``is_valid`` is the boolean shorthand. Rejects malformed profiles, including
non-finite numbers, unknown enum values, and any raw-sample storage keys.
"""

from __future__ import annotations

import math

from .builder import CONTEXTS, PROFILE_VERSION
from .confidence import LEVELS

REQUIRED_TOP_KEYS = (
    "profile_version", "metadata", "confidence", "vocabulary",
    "sentence_structure", "paragraph_structure", "punctuation",
    "readability", "linguistic", "ngrams", "patterns", "outlier_notes",
)

# Keys that would indicate stored source documents — forbidden anywhere.
RAW_TEXT_KEYS = frozenset({
    "full_text", "raw_text", "raw_document", "original_sample",
    "original_samples", "samples", "sample_text", "documents",
})


def validate_profile(profile) -> list[str]:
    """Return error strings describing every problem found ([] when valid)."""
    errors: list[str] = []
    if not isinstance(profile, dict):
        return ["profile must be a JSON object"]
    for key in REQUIRED_TOP_KEYS:
        if key not in profile:
            errors.append(f"missing required key: {key}")
    if not errors:
        _check_version(profile, errors)
        _check_metadata(profile, errors)
        _check_confidence(profile, errors)
        _check_numbers(profile, errors)
        _check_raw_keys(profile, errors)
    return errors


def is_valid(profile) -> bool:
    """True when ``validate_profile`` reports no errors."""
    return not validate_profile(profile)


def _check_version(profile, errors) -> None:
    if profile.get("profile_version") != PROFILE_VERSION:
        errors.append(
            f"profile_version must be {PROFILE_VERSION!r}, "
            f"got {profile.get('profile_version')!r}")


def _check_metadata(profile, errors) -> None:
    metadata = profile.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
        return
    for key in ("sample_count", "total_words", "language", "context"):
        if key not in metadata:
            errors.append(f"metadata missing key: {key}")
    if not isinstance(metadata.get("sample_count"), int) or metadata.get("sample_count", 0) < 1:
        errors.append("metadata.sample_count must be an int >= 1")
    if not isinstance(metadata.get("total_words"), int) or metadata.get("total_words", 0) < 1:
        errors.append("metadata.total_words must be an int >= 1")
    language = metadata.get("language")
    if not isinstance(language, str) or not language.strip():
        errors.append("metadata.language must be a non-empty string")
    if metadata.get("context") not in CONTEXTS:
        errors.append(f"metadata.context must be one of {CONTEXTS}")


def _check_confidence(profile, errors) -> None:
    confidence = profile.get("confidence")
    if not isinstance(confidence, dict):
        errors.append("confidence must be an object")
        return
    if confidence.get("overall") not in LEVELS:
        errors.append(f"confidence.overall must be one of {LEVELS}")


def _check_numbers(profile, errors) -> None:
    def walk(value, path):
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            if not math.isfinite(value):
                errors.append(f"non-finite number at {path}")
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
    for key in REQUIRED_TOP_KEYS:
        if key in profile:
            walk(profile[key], key)


def _check_raw_keys(profile, errors) -> None:
    def walk(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in RAW_TEXT_KEYS:
                    errors.append(f"forbidden raw-sample key at {path}.{key}")
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
    walk(profile, "profile")
