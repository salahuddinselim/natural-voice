"""Anthropic Messages API provider (urllib only, no SDK).

Credentials come from ``ANTHROPIC_API_KEY`` (or ``api_key=`` explicitly) —
never from files or logs. Anthropic requires a model and max_tokens per call;
defaults are documented below and overridable. Core code never sees
Anthropic-native shapes: responses are normalized to plain text.
Status: implemented, requires network + credentials (untested live here).
"""

from __future__ import annotations

import os

from llm.capabilities import ProviderCapabilities
from llm.errors import ConfigurationError
from llm.interface import LLMProvider
from llm.models import normalize_response
from llm.retry import run_with_retries
from providers._http import Transport, post_json

DEFAULT_BASE_URL = "https://api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 1024


class AnthropicProvider(LLMProvider):
    """Anthropic Messages API over plain HTTPS (stdlib only)."""

    def __init__(self, model: str | None = None, api_key: str | None = None,
                 base_url: str | None = None, temperature: float | None = None,
                 max_tokens: int | None = None, timeout_seconds: float = 60.0,
                 max_retries: int = 1, transport: Transport | None = None):
        self.model = model or DEFAULT_MODEL
        key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ConfigurationError(
                "missing API key: set ANTHROPIC_API_KEY or pass api_key=")
        self._api_key = key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._transport = transport or post_json

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(system_messages=True, temperature=True,
                                    max_tokens=True)

    def generate(self, prompt: str, **kwargs) -> str:
        if not isinstance(prompt, str):
            raise TypeError(f"prompt must be str, got {type(prompt).__name__}")
        payload: dict = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": [{"role": "user", "content": prompt}],
        }
        system_prompt = kwargs.get("system_prompt")
        if system_prompt:
            payload["system"] = system_prompt
        temperature = kwargs.get("temperature", self.temperature)
        if temperature is not None:
            payload["temperature"] = temperature
        headers = {"x-api-key": self._api_key,
                   "anthropic-version": ANTHROPIC_VERSION}
        url = f"{self.base_url}/v1/messages"

        def _call():
            data = self._transport(url, payload, headers, self.timeout_seconds)
            return normalize_response(data, model=self.model).text

        return run_with_retries(_call, max_retries=self.max_retries)

    @property
    def name(self) -> str:
        return "AnthropicProvider"
