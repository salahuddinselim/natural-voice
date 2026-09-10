"""Natural Voice revision engine: LLM revision guided by local analysis.

Pipeline: draft + voice profile + comparison report + core principles → prompt →
``LLMProvider`` → validated revision. Provider-neutral: the engine depends only
on the ``LLMProvider`` interface (``llm/`` package). Tests and offline use run on
``MockProvider`` — no network, no API keys.
"""

from __future__ import annotations

import sys
from pathlib import Path

for _sibling in ("analyzer", "profile", "comparison"):
    _path = Path(__file__).resolve().parent.parent.parent / _sibling
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:  # makes the sibling ``llm`` package importable
    sys.path.insert(0, str(_root))

try:
    import natural_voice_analyzer  # noqa: F401
    import natural_voice_comparison  # noqa: F401
    import natural_voice_profile  # noqa: F401
    import llm  # noqa: F401
except ImportError:  # pragma: no cover - surfaces with context below
    raise

from .engine import MAX_ATTEMPTS, MAX_DRAFT_CHARS, revise  # noqa: E402
from .prompt_builder import MODES  # noqa: E402
from .result import REVISION_VERSION, build_result, strip_original  # noqa: E402

__version__ = REVISION_VERSION
__all__ = [
    "revise",
    "MODES",
    "MAX_ATTEMPTS",
    "MAX_DRAFT_CHARS",
    "build_result",
    "strip_original",
    "REVISION_VERSION",
    "__version__",
]
