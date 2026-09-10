"""Natural Voice profile builder: samples → analyzer → aggregated voice profile.

Local-only, dependency-free (plus the sibling ``natural_voice_analyzer`` package).
Derived statistics only — never stores, logs, or transmits writing samples.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import natural_voice_analyzer  # noqa: F401  (normal install or PYTHONPATH use)
except ImportError:  # pragma: no cover - repo-checkout convenience path
    _sibling = Path(__file__).resolve().parent.parent.parent / "analyzer"
    if str(_sibling) not in sys.path:
        sys.path.insert(0, str(_sibling))
    import natural_voice_analyzer  # noqa: F401

from .builder import (  # noqa: E402
    CONTEXTS,
    PROFILE_VERSION,
    build_profile,
    build_profile_from_files,
)
from .serialization import load_profile, save_profile  # noqa: E402
from .validation import is_valid, validate_profile  # noqa: E402

__version__ = PROFILE_VERSION
__all__ = [
    "build_profile",
    "build_profile_from_files",
    "save_profile",
    "load_profile",
    "validate_profile",
    "is_valid",
    "PROFILE_VERSION",
    "CONTEXTS",
    "__version__",
]
