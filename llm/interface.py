"""Provider-neutral LLM interface (abstract base class)."""

from __future__ import annotations

import abc

from .errors import ProviderError  # canonical base; re-exported for compatibility.


class LLMProvider(abc.ABC):
    """Abstract text-generation provider.

    Future adapters (OpenAI, Anthropic, local models, …) subclass this and
    implement ``generate``. Configuration (keys, endpoints, model names) belongs
    to the implementation and its caller — environment variables or dependency
    injection — never in Natural Voice core, and never in version control.
    """

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Return the provider's raw text response for ``prompt``.

        Raises:
            ProviderError: on transport, authentication, or service failures.
            TypeError: if ``prompt`` is not a string.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Human-readable provider identifier for result metadata."""
        return type(self).__name__

    def capabilities(self):
        """Declared abilities; base default is conservative (all False).

        Providers override with their real capabilities. Core code must treat
        every capability as possibly-absent (see ``llm.capabilities``).
        """
        from .capabilities import ProviderCapabilities
        return ProviderCapabilities()
