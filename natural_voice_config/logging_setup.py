"""Structured, opt-in logging. Never logs content or secrets.

Emitted fields are limited to: operation names, component/version identifiers,
counts (words, samples, attempts), validation outcomes, and error types.
Drafts, samples, profiles, prompts, responses, keys, and headers are NEVER
logged — there is no code path that formats them into a record.
"""

from __future__ import annotations

import logging

_LOGGER_NAME = "natural_voice"
_configured = False


def get_logger(component: str) -> logging.Logger:
    """Child logger for ``component`` (e.g. "revision", "comparison")."""
    return logging.getLogger(f"{_LOGGER_NAME}.{component}")


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Attach a stderr handler once; INFO when verbose, WARNING otherwise."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    if not _configured:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        _configured = True
    return logger
