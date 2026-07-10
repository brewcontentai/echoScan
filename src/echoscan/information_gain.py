"""
Information-gain scoring: proxies "unique, concrete substance" via
evidence markers (numbers, dates, citations, named entities) weighed
against vague, unsupported claim phrasing.
"""

from __future__ import annotations

from echoscan.models import InformationGainResult
from echoscan.patterns import EVIDENCE_PATTERNS, PROPER_NOUN_PATTERN, VAGUE_CLAIM_PHRASES
from echoscan.textutils import normalize, per_100_words, word_count


def score_information_gain(text: str) -> InformationGainResult:
    normalized = normalize(text)
    total_words = word_count(text)

    evidence_count = 0
    for pattern in EVIDENCE_PATTERNS:
        evidence_count += len(pattern.findall(normalized))

    entities = sorted(set(m.strip() for m in PROPER_NOUN_PATTERN.findall(normalized)))
    # Named entities count partially toward evidence too, but capped so a
    # piece can't game the score by capitalizing random words.
    entity_bonus = min(len(entities), 15)

    evidence_density = per_100_words(evidence_count, total_words)

    low = normalized.lower()
    vague_hits = []
    for phrase in VAGUE_CLAIM_PHRASES:
        count = low.count(phrase)
        if count:
            vague_hits.append({"phrase": phrase, "count": count})
    vague_total = sum(v["count"] for v in vague_hits)
    vague_density = per_100_words(vague_total, total_words)

    # Score: base on evidence density, add small entity bonus, subtract
    # for vague-claim density (unsupported assertions crowding out
    # information gain).
    score = 20.0 + min(evidence_density * 10, 65) + entity_bonus
    score -= min(vague_density * 8, 25)
    score = max(0.0, min(100.0, round(score, 1)))

    vague_hits.sort(key=lambda h: h["count"], reverse=True)

    return InformationGainResult(
        score=score,
        evidence_markers=evidence_count,
        evidence_density_per_100_words=evidence_density,
        vague_claim_hits=vague_hits,
        unique_entities=entities[:25],
    )
