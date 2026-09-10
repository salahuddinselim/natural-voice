"""LLM provider abstraction for Natural Voice (platform-independent).

The revision engine depends only on ``LLMProvider`` — concretely the stable
``generate(prompt: str) -> str`` contract (unchanged since Phase 7). Structured
companions live alongside it: ``llm.models`` (LLMRequest/LLMResponse +
normalization), ``llm.capabilities`` (declared abilities + negotiation),
``llm.errors`` (standardized hierarchy), ``llm.retry`` (transient-failure helper).

Provider credentials, when a real provider is used, come from the caller's
environment or dependency injection — never from this package, and never
committed to the repository. Tests use ``llm.mock`` (no network, no keys).
"""

from .capabilities import ProviderCapabilities, negotiate_structured_output
from .errors import (
    AuthenticationError,
    ConfigurationError,
    InvalidResponseError,
    ProviderError,
    RateLimitError,
    TimeoutError,
    UnsupportedCapabilityError,
    is_retryable,
)
from .interface import LLMProvider, ProviderError as _ProviderError
from .mock import MockProvider
from .models import LLMRequest, LLMResponse, normalize_response
from .retry import DEFAULT_MAX_RETRIES, run_with_retries

assert ProviderError is _ProviderError  # single canonical base class.

__all__ = [
    "LLMProvider", "ProviderError", "MockProvider",
    "LLMRequest", "LLMResponse", "normalize_response",
    "ProviderCapabilities", "negotiate_structured_output",
    "AuthenticationError", "ConfigurationError", "InvalidResponseError",
    "RateLimitError", "TimeoutError", "UnsupportedCapabilityError",
    "is_retryable", "DEFAULT_MAX_RETRIES", "run_with_retries",
]
