"""Provider registry: construct providers by name without touching core code.

``register_provider`` / ``get_provider`` / ``list_providers`` let future
providers plug in from outside this package. Built-ins: "mock" (offline,
no credentials), "openai-compatible" (stdlib HTTP, needs endpoint + key),
"anthropic" (stdlib HTTP, needs API key). The revision engine only ever sees
``LLMProvider`` instances — never these names.
"""

from __future__ import annotations

from typing import Callable

_FACTORIES: dict[str, Callable[..., object]] = {}


def register_provider(name: str, factory: Callable[..., object]) -> None:
    """Register a zero-or-more-argument factory under ``name`` (overwrites)."""
    if not name or not isinstance(name, str):
        raise ValueError("provider name must be a non-empty string")
    if not callable(factory):
        raise TypeError("factory must be callable")
    _FACTORIES[name] = factory


def get_provider(name: str, **kwargs):
    """Build the named provider; ValueError for unknown names."""
    try:
        factory = _FACTORIES[name]
    except KeyError:
        raise ValueError(f"unknown provider {name!r} "
                         f"(available: {list_providers()})") from None
    return factory(**kwargs)


def list_providers() -> list[str]:
    """Sorted names of registered providers (deterministic)."""
    return sorted(_FACTORIES)


def _register_builtins() -> None:
    from .anthropic.provider import AnthropicProvider
    from .mock.provider import MockProviderAdapter
    from .openai_compatible.provider import OpenAICompatibleProvider
    register_provider("mock", MockProviderAdapter)
    register_provider("openai-compatible", OpenAICompatibleProvider)
    register_provider("anthropic", AnthropicProvider)


_register_builtins()
