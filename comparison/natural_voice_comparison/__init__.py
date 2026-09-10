"""Natural Voice comparison engine: draft vs. Author Voice Profile.

Local, deterministic style-consistency reports (close / moderately_different /
significantly_different). No authorship scores, probabilities, or verdicts —
never answers who or what wrote a text.
"""

from __future__ import annotations

import sys
from pathlib import Path

for _sibling in ("analyzer", "profile"):
    _path = Path(__file__).resolve().parent.parent.parent / _sibling
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

try:
    import natural_voice_analyzer  # noqa: F401
    import natural_voice_profile  # noqa: F401
except ImportError:  # pragma: no cover - import error surfaces with context below
    raise

from .comparator import (  # noqa: E402
    COMPARISON_VERSION,
    compare_draft,
    compare_draft_file,
)
from .report import DEFAULT_WEIGHTS, DIMENSION_ORDER  # noqa: E402

__version__ = COMPARISON_VERSION
__all__ = [
    "compare_draft",
    "compare_draft_file",
    "DEFAULT_WEIGHTS",
    "DIMENSION_ORDER",
    "COMPARISON_VERSION",
    "__version__",
]
