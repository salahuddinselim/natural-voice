"""Explicit request/response models for provider adapters.

The stable engine contract remains ``generate(prompt: str) -> str`` (Phase 7,
unchanged for backward compatibility). These models serve providers that need
structured metadata (model name, usage, system/user separation, capability
negotiation). ``normalize_response`` converts any provider-native payload —
plain string, ``{"text": ...}`` dict, or Anthropic-style content blocks — into
``LLMResponse`` so the engine side never branches on provider shapes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LLMRequest:
    """What the engine asks of a provider (all fields optional but the prompt)."""
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    want_structured_output: bool = False


@dataclass(frozen=True)
class LLMResponse:
    """Normalized provider output: text plus optional metadata (never secrets)."""
    text: str
    model: str | None = None
    usage: dict | None = None
    metadata: dict | None = field(default=None)


def normalize_response(raw, model: str | None = None) -> LLMResponse:
    """Normalize ``str`` | ``{"text": ...}`` | ``{"content": [...blocks...]}``.

    Raises:
        InvalidResponseError: payload carries no extractable text.
    """
    from .errors import InvalidResponseError

    if isinstance(raw, str):
        if not raw.strip():
            raise InvalidResponseError("provider returned empty text")
        return LLMResponse(text=raw, model=model)
    if isinstance(raw, dict):
        text = raw.get("text")
        if isinstance(text, str) and text.strip():
            return LLMResponse(text=text, model=raw.get("model", model),
                               usage=raw.get("usage"), metadata=raw.get("metadata"))
        blocks = raw.get("content")
        if isinstance(blocks, list):
            text = "".join(
                block.get("text", "") for block in blocks
                if isinstance(block, dict) and block.get("type") in ("text", "output_text")
                or isinstance(block, dict) and "text" in block)
            if text.strip():
                return LLMResponse(text=text, model=raw.get("model", model),
                                   usage=raw.get("usage"))
        raise InvalidResponseError("provider dict payload carries no text")
    raise InvalidResponseError(f"unsupported provider payload type: {type(raw).__name__}")
