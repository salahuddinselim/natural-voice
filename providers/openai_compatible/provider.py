"""Generic OpenAI-compatible chat-completions provider (urllib only, no SDK).

Works against any endpoint implementing the ``/chat/completions`` shape
(OpenAI itself or compatible gateways) via a configurable ``base_url``.
Compatible services differ in details (response formats, limits); this adapter
sticks to the common subset and fails clearly outside it. Credentials come from
``OPENAI_API_KEY`` (or ``api_key=`` explicitly) — never from files or logs.
Status: implemented, requires network + credentials (untested live here).
"""

from __future__ import annotations

import os

from llm.capabilities import ProviderCapabilities
from llm.errors import ConfigurationError, InvalidResponseError
from llm.interface import LLMProvider
from llm.models import normalize_response
from llm.retry import run_with_retries
from providers._http import Transport, post_json

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class OpenAICompatibleProvider(LLMProvider):
    """Chat-completions provider over plain HTTPS (stdlib only)."""

    def __init__(self, model: str | None = None, api_key: str | None = None,
                 base_url: str | None = None, temperature: float | None = None,
                 max_tokens: int | None = None, timeout_seconds: float = 60.0,
                 max_retries: int = 1, transport: Transport | None = None):
        self.model = model or DEFAULT_MODEL
        key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ConfigurationError(
                "missing API key: set OPENAI_API_KEY or pass api_key=")
        self._api_key = key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._transport = transport or post_json

    def capabilities(self) -> ProviderCapabilities:
        # Conservative: compatible endpoints vary, so only the common core is
        # declared. JSON is still requested in-prose; the engine parses robustly.
        return ProviderCapabilities(system_messages=True, temperature=True,
                                    max_tokens=True)

    def generate(self, prompt: str, **kwargs) -> str:
        if not isinstance(prompt, str):
            raise TypeError(f"prompt must be str, got {type(prompt).__name__}")
        system_prompt = kwargs.get("system_prompt")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload: dict = {"model": self.model, "messages": messages}
        temperature = kwargs.get("temperature", self.temperature)
        if temperature is not None:
            payload["temperature"] = temperature
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        headers = {"Authorization": f"Bearer {self._api_key}"}
        url = f"{self.base_url}/chat/completions"

        def _call():
            data = self._transport(url, payload, headers, self.timeout_seconds)
            try:
                text = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError) as exc:
                raise InvalidResponseError(
                    "chat-completions payload has no choices[0].message.content"
                ) from exc
            return normalize_response(text, model=self.model).text

        return run_with_retries(_call, max_retries=self.max_retries)

    @property
    def name(self) -> str:
        return "OpenAICompatibleProvider"
