"""Top-level orchestration: runs all scorers and assembles a report."""

from __future__ import annotations

from echoscan.genericness import score_genericness
from echoscan.information_gain import score_information_gain
from echoscan.models import EchoScanReport
from echoscan.overlap import score_overlap
from echoscan.textutils import word_count

# Weights for the composite Distinctiveness Score. Overlap only applies
# (and is only weighted in) when competitor content was supplied.
WEIGHT_GENERICNESS = 0.35
WEIGHT_INFO_GAIN = 0.40
WEIGHT_OVERLAP = 0.25


def _verdict(score: float) -> str:
    if score >= 80:
        return "Highly distinctive — strong information gain, low cliche density."
    if score >= 60:
        return "Reasonably distinctive — some generic patches, room to sharpen."
    if score >= 40:
        return "Borderline generic — likely to blend into AI content noise."
    return "Highly generic — rewrite recommended before publishing."


def _suggestions(report_parts: dict) -> list[str]:
    suggestions: list[str] = []
    gen = report_parts["genericness"]
    ig = report_parts["information_gain"]
    ov = report_parts["overlap"]

    if gen.cliche_density_per_100_words > 1.5:
        top = ", ".join(f'"{h["phrase"]}"' for h in gen.cliche_hits[:3])
        suggestions.append(
            f"Cut or replace overused phrases (top offenders: {top}). "
            "These are strong AI-tell signals to readers and search systems."
        )
    if gen.filler_sentence_ratio > 0.15:
        suggestions.append(
            "More than 1 in 7 sentences are templated filler — tighten structure "
            "and let concrete claims carry the piece instead of stock transitions."
        )
    if ig.evidence_density_per_100_words < 1.0:
        suggestions.append(
            "Add concrete evidence: original data, named sources, dates, or "
            "percentages. Consensus-style claims without numbers are easy for "
            "AI models (and readers) to shrug off as low information gain."
        )
    if ig.vague_claim_hits:
        top = ", ".join(f'"{h["phrase"]}"' for h in ig.vague_claim_hits[:2])
        suggestions.append(
            f'Replace unsupported hedges like {top} with a specific, attributable claim.'
        )
    if not ig.unique_entities:
        suggestions.append(
            "No named entities detected (companies, products, people). Grounding "
            "claims in specifics is one of the fastest ways to raise information gain."
        )
    if ov.per_competitor and ov.max_similarity_pct > 55:
        closest = ov.per_competitor[0]
        shared = ", ".join(closest.top_shared_terms[:5])
        suggestions.append(
            f"High overlap ({closest.similarity_pct}%) with '{closest.source}' — "
            f"shared vocabulary: {shared}. Differentiate the angle or add proprietary "
            "data/perspective this competitor doesn't have."
        )
    if not suggestions:
        suggestions.append(
            "No major issues detected — this piece scores well on distinctiveness."
        )
    return suggestions


def analyze(
    text: str,
    source: str = "input",
    competitors: dict[str, str] | None = None,
) -> EchoScanReport:
    """Run the full EchoScan pipeline over `text` and return a report.

    Args:
        text: the content to audit.
        source: label for the content (e.g. filename), used in the report.
        competitors: optional {label: text} mapping of competitor content to
            compare against for overlap scoring.
    """
    competitors = competitors or {}

    genericness = score_genericness(text)
    info_gain = score_information_gain(text)
    overlap = score_overlap(text, competitors)

    if competitors:
        composite = (
            genericness.score * WEIGHT_GENERICNESS
            + info_gain.score * WEIGHT_INFO_GAIN
            + (100 - overlap.max_similarity_pct) * WEIGHT_OVERLAP
        )
    else:
        # Renormalize weights across the two available signals.
        total_weight = WEIGHT_GENERICNESS + WEIGHT_INFO_GAIN
        composite = (
            genericness.score * (WEIGHT_GENERICNESS / total_weight)
            + info_gain.score * (WEIGHT_INFO_GAIN / total_weight)
        )
    composite = round(max(0.0, min(100.0, composite)), 1)

    suggestions = _suggestions(
        {"genericness": genericness, "information_gain": info_gain, "overlap": overlap}
    )

    return EchoScanReport(
        source=source,
        word_count=word_count(text),
        distinctiveness_score=composite,
        verdict=_verdict(composite),
        genericness=genericness,
        information_gain=info_gain,
        overlap=overlap,
        suggestions=suggestions,
    )
