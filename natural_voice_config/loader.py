"""Configuration loading with one documented precedence rule:

    explicit function argument > CLI argument > environment variable
    > configuration file > built-in default

Secrets (API keys) are NEVER read from configuration files by this loader —
only from the environment — so a committed JSON file can never leak a key.

Environment variables:
    NATURAL_VOICE_PROVIDER, NATURAL_VOICE_MODEL, NATURAL_VOICE_TEMPERATURE,
    NATURAL_VOICE_MAX_TOKENS, NATURAL_VOICE_TIMEOUT, NATURAL_VOICE_RETRIES,
    NATURAL_VOICE_BASE_URL, NATURAL_VOICE_MODE, NATURAL_VOICE_VERBOSE.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import NaturalVoiceConfig, ProviderConfig

_ENV_PREFIX = "NATURAL_VOICE_"


def load_config(cli_args: dict | None = None, env=None,
                file_path: str | Path | None = None) -> NaturalVoiceConfig:
    """Assemble configuration from defaults <- file <- env <- CLI args.

    Args:
        cli_args: flat dict (e.g. {"provider": ..., "model": ...}); None values
            are ignored so unset flags never override. Unknown keys raise ValueError.
        env: mapping (defaults to ``os.environ``); only ``NATURAL_VOICE_*`` read.
        file_path: optional JSON file with {"provider": {...}, "mode": ...}.
    """
    file_values = _read_file(file_path) if file_path else {}
    env_values = _read_env(env if env is not None else os.environ)
    merged = _merge(_defaults(), file_values, env_values, cli_args or {})
    return NaturalVoiceConfig(
        provider=ProviderConfig(**merged["provider"]), mode=merged["mode"],
        verbose=merged["verbose"])


def _defaults() -> dict:
    return {"provider": {"provider": "mock", "model": None, "temperature": None,
                         "max_tokens": None, "timeout_seconds": 60.0,
                         "max_retries": 1, "base_url": None},
            "mode": "conservative", "verbose": False}


def _read_file(file_path) -> dict:
    try:
        data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load config file {file_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config file {file_path} must contain a JSON object")
    _reject_secrets(data, str(file_path))
    return _pick_known(data)


def _read_env(env) -> dict:
    get = lambda name: env.get(_ENV_PREFIX + name)
    provider: dict = {}
    for key, env_name, cast in (
            ("provider", "PROVIDER", str), ("model", "MODEL", str),
            ("temperature", "TEMPERATURE", float), ("max_tokens", "MAX_TOKENS", int),
            ("timeout_seconds", "TIMEOUT", float), ("max_retries", "RETRIES", int),
            ("base_url", "BASE_URL", str)):
        raw = get(env_name)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        try:
            provider[key] = cast(raw)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"invalid {_ENV_PREFIX + env_name}={raw!r}") from exc
    result: dict = {}
    if provider:
        result["provider"] = provider
    mode = get("MODE")
    if mode:
        result["mode"] = mode
    verbose = get("VERBOSE")
    if verbose is not None:
        result["verbose"] = str(verbose).strip().lower() in ("1", "true", "yes", "on")
    return result


def _pick_known(data: dict) -> dict:
    allowed_top = {"provider", "mode", "verbose"}
    unknown = set(data) - allowed_top
    if unknown:
        raise ValueError(f"unknown config keys: {sorted(unknown)}")
    result = {}
    if isinstance(data.get("provider"), dict):
        allowed = {"provider", "model", "temperature", "max_tokens",
                   "timeout_seconds", "max_retries", "base_url"}
        unknown_p = set(data["provider"]) - allowed
        if unknown_p:
            raise ValueError(f"unknown provider config keys: {sorted(unknown_p)}")
        result["provider"] = dict(data["provider"])
    for key in ("mode", "verbose"):
        if key in data:
            result[key] = data[key]
    return result


_PROVIDER_KEYS = frozenset({"provider", "model", "temperature", "max_tokens",
                             "timeout_seconds", "max_retries", "base_url"})


def _normalize(layer: dict, source: str) -> dict:
    """Accept provider keys nested ({"provider": {...}}) or flat (CLI-style);
    reject anything unknown."""
    normalized: dict = {"provider": {}, "mode": None, "verbose": None}
    unknown = set(layer) - _PROVIDER_KEYS - {"mode", "verbose"}
    if unknown:
        raise ValueError(f"unknown config keys in {source}: {sorted(unknown)}")
    nested = layer.get("provider")
    if isinstance(nested, dict):
        unknown_nested = set(nested) - _PROVIDER_KEYS
        if unknown_nested:
            raise ValueError(
                f"unknown provider config keys in {source}: {sorted(unknown_nested)}")
        normalized["provider"].update(
            {k: v for k, v in nested.items() if v is not None})
    elif nested is not None:
        # Flat form (CLI-style): {"provider": "anthropic"} names the provider.
        normalized["provider"]["provider"] = nested
    for key in _PROVIDER_KEYS - {"provider"}:
        if layer.get(key) is not None:
            normalized["provider"][key] = layer[key]
    for key in ("mode", "verbose"):
        if layer.get(key) is not None:
            normalized[key] = layer[key]
    return normalized


def _merge(*layers: dict) -> dict:
    merged: dict = {"provider": {}, "mode": None, "verbose": None}
    for layer in layers:
        normalized = _normalize(layer, "configuration")
        merged["provider"].update(normalized["provider"])
        for key in ("mode", "verbose"):
            if layer.get(key) is not None:
                merged[key] = layer[key]
    base = _defaults()
    provider = {**base["provider"], **merged["provider"]}
    return {"provider": provider,
            "mode": merged["mode"] if merged["mode"] is not None else base["mode"],
            "verbose": merged["verbose"] if merged["verbose"] is not None else base["verbose"]}


def _reject_secrets(data: dict, where: str) -> None:
    """Refuse config files that look like they contain secrets (fail closed)."""
    suspects = ("api_key", "apikey", "secret", "token", "password", "credential")
    def walk(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                if any(word in str(key).lower() for word in suspects):
                    raise ValueError(
                        f"config file {where} must not contain secrets "
                        f"(key {path}.{key}); use environment variables")
                walk(item, f"{path}.{key}")
    walk(data, "$")
