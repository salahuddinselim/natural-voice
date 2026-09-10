"""Registry adapter for the deterministic mock provider (offline, no keys)."""

from __future__ import annotations

from llm.mock import MockProvider


class MockProviderAdapter(MockProvider):
    """``MockProvider`` configured through registry kwargs.

    ``handler`` (fixed text or callable) mirrors ``llm.mock.MockProvider``;
    passing nothing yields an empty-output mock (useful for rejection-path tests).
    """

    def __init__(self, handler="", **kwargs):
        if kwargs:
            raise ValueError(f"mock provider takes no options, got {sorted(kwargs)}")
        super().__init__(handler)
