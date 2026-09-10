"""Deterministic mock provider for tests and offline use.

No network, no API keys. The mock returns scripted output so every revision test
is reproducible. It can echo the prompt's DRAFT block (exercising the delimiters),
return structured JSON revisions, or simulate failure modes.
"""

from __future__ import annotations

import json
import re
from typing import Callable

from .interface import LLMProvider

DRAFT_BEGIN = "DRAFT\nBEGIN"
DRAFT_END = "\nEND"


class MockProvider(LLMProvider):
    """Scripted provider: ``handler`` is fixed text or ``(prompt) -> text``."""

    def __init__(self, handler: str | Callable[[str], str] = ""):
        if not isinstance(handler, str) and not callable(handler):
            raise TypeError("handler must be str or callable")
        self._handler = handler

    def generate(self, prompt: str, **kwargs) -> str:
        if not isinstance(prompt, str):
            raise TypeError(f"prompt must be str, got {type(prompt).__name__}")
        if callable(self._handler):
            return self._handler(prompt)
        return self._handler

    @classmethod
    def fixed(cls, text: str) -> "MockProvider":
        """Always return ``text`` (valid revision, empty, or malformed)."""
        return cls(text)

    @classmethod
    def echo(cls) -> "MockProvider":
        """Return the prompt's DRAFT block verbatim (unchanged-output case)."""
        def _echo(prompt: str) -> str:
            match = re.search(
                re.escape(DRAFT_BEGIN) + r"\n(.*)" + re.escape(DRAFT_END) + r"(?=\n|$)",
                prompt, re.DOTALL)
            return match.group(1) if match else ""
        return cls(_echo)

    @classmethod
    def json_revision(cls, revised_text: str, changes: list | None = None) -> "MockProvider":
        """Return a structured-JSON revision payload, as a real provider should."""
        return cls(json.dumps({
            "revised_text": revised_text,
            "change_summary": changes or [],
        }, ensure_ascii=False))

    def capabilities(self):
        from .capabilities import ProviderCapabilities
        # Scripted output can be JSON-shaped, but nothing is streamed and no
        # sampling controls exist — declared honestly.
        return ProviderCapabilities(structured_output=True)

    @property
    def name(self) -> str:
        return "MockProvider"
