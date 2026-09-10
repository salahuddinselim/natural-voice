"""Standardized provider exceptions (platform-independent).

Provider adapters translate SDK/HTTP-specific failures into these types so core
code (revision engine, CLI) only handles this hierarchy — never provider-native
exception classes. ``ProviderError`` remains the catch-all base (backward
compatible with Phase 7, which raised it directly).
"""


class ProviderError(Exception):
    """Any provider-side failure (transport, service, or unexpected response)."""


class AuthenticationError(ProviderError):
    """Credentials missing, invalid, or rejected. Never retried."""


class RateLimitError(ProviderError):
    """Provider throttled the request. Retried with backoff when configured."""


class TimeoutError(ProviderError):
    """Request exceeded the configured timeout. Retried when configured."""


class InvalidResponseError(ProviderError):
    """Response arrived but is unusable (bad JSON envelope, empty content blocks).
    Never retried — retrying the same request reproduces the same parse failure."""


class UnsupportedCapabilityError(ProviderError):
    """Provider cannot do what was asked (e.g. no structured output when the
    caller made it mandatory). Never retried; the caller must adapt instead."""


class ConfigurationError(ProviderError):
    """Bad provider configuration (unknown provider, missing model/endpoint,
    malformed options). Never retried."""


def is_retryable(exc: BaseException) -> bool:
    """True only for transient failures worth retrying (timeouts, rate limits,
    and generic transport/provider errors). Auth, config, bad responses, and
    unsupported capabilities are terminal by design."""
    return isinstance(exc, (TimeoutError, RateLimitError)) or (
        isinstance(exc, ProviderError)
        and not isinstance(exc, (
            AuthenticationError, InvalidResponseError,
            UnsupportedCapabilityError, ConfigurationError,
        ))
    )
