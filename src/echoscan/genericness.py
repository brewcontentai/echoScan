"""Genericness scoring: detects AI-tell / marketing-cliche phrasing."""

from __future__ import annotations

from echoscan.models import GenericnessResult
from echoscan.patterns import CLICHE_PHRASES
from echoscan.textutils import normalize, per_100_words, split_sentences, word_count


def score_genericness(text: str) -> GenericnessResult:
    normalized = normalize(text).lower()
    total_words = word_count(text)
    sentences = split_sentences(text)

    hits: list[dict] = []
    for phrase in CLICHE_PHRASES:
        count = normalized.count(phrase)
        if count:
            hits.append({"phrase": phrase, "count": count})

    total_hits = sum(h["count"] for h in hits)
    density = per_100_words(total_hits, total_words)

    filler_sentences = 0
    for sentence in sentences:
        low = sentence.lower()
        if any(phrase in low for phrase in CLICHE_PHRASES):
            filler_sentences += 1
    filler_ratio = round(filler_sentences / len(sentences), 3) if sentences else 0.0

    # Score: start at 100 (fully distinctive phrasing), subtract for cliche
    # density and filler-sentence ratio. Tuned so ~1 cliche per 100 words
    # costs ~12 points, and an all-filler piece bottoms out near 0.
    score = 100.0
    score -= min(density * 12, 70)
    score -= min(filler_ratio * 40, 30)
    score = max(0.0, min(100.0, round(score, 1)))

    hits.sort(key=lambda h: h["count"], reverse=True)

    return GenericnessResult(
        score=score,
        cliche_hits=hits,
        cliche_density_per_100_words=density,
        filler_sentence_ratio=filler_ratio,
    )
