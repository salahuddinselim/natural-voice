"""Configuration for Natural Voice: models, precedence loader, versions, logging.

Precedence (highest first): explicit argument > CLI argument > environment
variable > configuration file > built-in default. Secrets come from the
environment only — never from files, profiles, reports, or logs.
"""

from .loader import load_config
from .logging_setup import get_logger, setup_logging
from .models import NaturalVoiceConfig, ProviderConfig
from .versions import (
    ADAPTER_VERSION,
    ANALYZER_VERSION,
    COMPARISON_VERSION,
    COMPONENT_VERSIONS,
    NATURAL_VOICE_VERSION,
    PROFILE_VERSION,
    REVISION_VERSION,
    check_profile_compatibility,
)

__all__ = [
    "NaturalVoiceConfig", "ProviderConfig", "load_config",
    "get_logger", "setup_logging",
    "NATURAL_VOICE_VERSION", "ANALYZER_VERSION", "PROFILE_VERSION",
    "COMPARISON_VERSION", "REVISION_VERSION", "ADAPTER_VERSION",
    "COMPONENT_VERSIONS", "check_profile_compatibility",
]
