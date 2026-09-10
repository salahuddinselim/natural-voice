"""Natural Voice analyzer: local, dependency-free linguistic measurements.

Descriptive statistics only — no authorship scores, probabilities, or verdicts.
"""

from .analyzer import ANALYZER_VERSION, analyze_text
from .output import to_json

__version__ = ANALYZER_VERSION
__all__ = ["analyze_text", "to_json", "ANALYZER_VERSION", "__version__"]
