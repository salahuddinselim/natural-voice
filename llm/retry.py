"""Conservative retry helper for transient provider failures.

Retries only ``is_retryable`` exceptions (timeouts, rate limits, generic
transport errors) with linear backoff; everything else propagates immediately.
No randomness (deterministic delays), no retries by default unless the caller
opts in — the revision engine's own attempt loop stays the primary control.
"""

from __future__ import annotations

import time
from typing import Callable

from .errors import is_retryable

DEFAULT_MAX_RETRIES = 1  # conservative: one retry unless configured otherwise.
DEFAULT_BACKOFF_SECONDS = 1.0


def run_with_retries(func: Callable, max_retries: int = DEFAULT_MAX_RETRIES,
                     backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
                     sleep: Callable[[float], None] = time.sleep):
    """Call ``func()``; retry retryable failures up to ``max_retries`` times.

    ``sleep`` is injectable so tests never actually wait. Raises the last
    exception when retries are exhausted (or immediately for terminal errors).
    """
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    attempts = 0
    while True:
        try:
            return func()
        except Exception as exc:  # noqa: BLE001 - classified below, then re-raised
            if not is_retryable(exc) or attempts >= max_retries:
                raise
            attempts += 1
            sleep(backoff_seconds * attempts)
