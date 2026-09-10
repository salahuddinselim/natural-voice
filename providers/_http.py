"""Minimal stdlib HTTPS JSON client shared by real provider adapters.

Only ``urllib`` + ``json`` — no provider SDKs anywhere in this repository.
Never logs URLs with credentials, headers, or bodies.
"""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import Callable


def post_json(url: str, payload: dict, headers: dict,
              timeout_seconds: float) -> dict:
    """POST JSON, return the decoded response object (dict or list).

    Raises:
        AuthenticationError / RateLimitError / TimeoutError / ProviderError.
    """
    from llm.errors import (
        AuthenticationError,
        ProviderError,
        RateLimitError,
        TimeoutError,
    )

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", **headers},
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise AuthenticationError(
                f"provider rejected credentials (HTTP {exc.code})") from exc
        if exc.code == 429:
            raise RateLimitError("provider rate limit exceeded") from exc
        raise ProviderError(f"provider HTTP error {exc.code}") from exc
    except (urllib.error.URLError, ConnectionError) as exc:
        raise ProviderError(f"provider connection failed: {exc}") from exc
    except socket.timeout as exc:
        from llm.errors import TimeoutError as ProviderTimeout
        raise ProviderTimeout("provider request timed out") from exc
    except json.JSONDecodeError as exc:
        from llm.errors import InvalidResponseError
        raise InvalidResponseError("provider returned non-JSON") from exc


Transport = Callable[[str, dict, dict, float], dict]
