"""Typed result containers shared across EchoScan's scoring modules."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class GenericnessResult:
    score: float  # 0 (fully generic) - 100 (fully distinctive phrasing)
    cliche_hits: list[dict[str, Any]] = field(default_factory=list)
    cliche_density_per_100_words: float = 0.0
    filler_sentence_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InformationGainResult:
    score: float  # 0 (no unique substance) - 100 (dense, unique substance)
    evidence_markers: int = 0
    evidence_density_per_100_words: float = 0.0
    vague_claim_hits: list[dict[str, Any]] = field(default_factory=list)
    unique_entities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompetitorOverlap:
    source: str
    similarity_pct: float
    top_shared_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OverlapResult:
    max_similarity_pct: float = 0.0
    per_competitor: list[CompetitorOverlap] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_similarity_pct": self.max_similarity_pct,
            "per_competitor": [c.to_dict() for c in self.per_competitor],
        }


@dataclass
class EchoScanReport:
    source: str
    word_count: int
    distinctiveness_score: float
    verdict: str
    genericness: GenericnessResult
    information_gain: InformationGainResult
    overlap: OverlapResult
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "word_count": self.word_count,
            "distinctiveness_score": self.distinctiveness_score,
            "verdict": self.verdict,
            "genericness": self.genericness.to_dict(),
            "information_gain": self.information_gain.to_dict(),
            "overlap": self.overlap.to_dict(),
            "suggestions": self.suggestions,
            "built_by": "Brewcontent.ai",
        }
