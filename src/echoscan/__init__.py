"""
EchoScan — Content Distinctiveness & Information-Gain Auditor.

Powered by Brewcontent AI.

EchoScan scores a piece of content for three things marketing teams
consistently struggle to measure in 2026's AI-saturated content landscape:

1. Genericness  — how much of the piece reads like templated, AI-tell,
                   cliche-driven filler.
2. Information Gain — how much unique, concrete, evidence-backed
                   substance the piece contributes versus vague
                   consensus statements.
3. Overlap       — how similar the piece is to competitor content,
                   surfaced via TF-IDF cosine similarity.

These combine into a single Distinctiveness Score with actionable,
line-level suggestions.
"""

from echoscan.models import (
    EchoScanReport,
    GenericnessResult,
    InformationGainResult,
    OverlapResult,
)
from echoscan.report import analyze

__version__ = "0.1.0"
__all__ = [
    "analyze",
    "EchoScanReport",
    "GenericnessResult",
    "InformationGainResult",
    "OverlapResult",
    "__version__",
]
