"""Mock provider adapter: registry-friendly alias over ``llm.mock``.

The canonical implementation stays in ``llm.mock`` (used directly by unit
tests); this package exposes it to the provider registry under "mock".
"""

from llm.mock import MockProvider

from .provider import MockProviderAdapter

__all__ = ["MockProvider", "MockProviderAdapter"]
