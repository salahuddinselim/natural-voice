"""Configuration models (secrets never live here — only non-secret settings)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderConfig:
    """Non-secret provider settings. Secrets travel via environment only."""
    provider: str = "mock"
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    timeout_seconds: float = 60.0
    max_retries: int = 1
    base_url: str | None = None  # override for OpenAI-compatible endpoints.


@dataclass(frozen=True)
class NaturalVoiceConfig:
    """Top-level configuration: provider settings plus engine behavior."""
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    mode: str = "conservative"
    verbose: bool = False
