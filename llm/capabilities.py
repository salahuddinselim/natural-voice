"""Provider capabilities and negotiation (no hidden assumptions).

The engine must never assume every provider supports structured output,
streaming, system messages, or sampling controls. Providers declare what they
can do; callers adapt (structured output requested when available, robust text
parsing otherwise — the revision parser already handles both).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderCapabilities:
    """Declared abilities of one provider implementation."""
    structured_output: bool = False
    streaming: bool = False
    system_messages: bool = False
    temperature: bool = False
    max_tokens: bool = False


def negotiate_structured_output(capabilities: ProviderCapabilities) -> str:
    """How the caller should request structured output from this provider.

    Returns "structured" when the provider supports it, else "text-fallback".
    The revision engine always requests JSON in-prose AND parses robustly, so
    both paths are safe; this helper just tells adapters which path to prefer
    (e.g. whether to set a JSON response-format flag).
    """
    return "structured" if capabilities.structured_output else "text-fallback"
