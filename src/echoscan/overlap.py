"""
Competitor overlap scoring via TF-IDF cosine similarity.

No network calls: competitor content is supplied as local text/files by
the caller (CLI flag or library argument), which keeps EchoScan
deterministic, offline-friendly, and safe to run in CI.
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from echoscan.models import CompetitorOverlap, OverlapResult


def score_overlap(text: str, competitors: dict[str, str]) -> OverlapResult:
    if not competitors:
        return OverlapResult(max_similarity_pct=0.0, per_competitor=[])

    labels = list(competitors.keys())
    corpus = [text] + [competitors[label] for label in labels]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Raised by scikit-learn when the entire corpus has no vocabulary
        # left after stop-word removal — e.g. empty content, or content
        # that is only stop words. Overlap simply can't be computed in
        # that case, so degrade to "no overlap" instead of crashing.
        return OverlapResult(
            max_similarity_pct=0.0,
            per_competitor=[
                CompetitorOverlap(source=label, similarity_pct=0.0, top_shared_terms=[])
                for label in labels
            ],
        )

    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    feature_names = vectorizer.get_feature_names_out()
    target_vec = matrix[0].toarray().flatten()
    per_competitor: list[CompetitorOverlap] = []

    for label, sim, row in zip(labels, similarities, matrix[1:].toarray()):
        shared_mask = (row > 0) & (target_vec > 0)
        shared_terms_scores = [
            (feature_names[i], row[i] * target_vec[i])
            for i in range(len(feature_names))
            if shared_mask[i]
        ]
        shared_terms_scores.sort(key=lambda x: x[1], reverse=True)
        top_terms = [t for t, _ in shared_terms_scores[:8]]

        per_competitor.append(
            CompetitorOverlap(
                source=label,
                similarity_pct=round(float(sim) * 100, 1),
                top_shared_terms=top_terms,
            )
        )

    per_competitor.sort(key=lambda c: c.similarity_pct, reverse=True)
    max_sim = per_competitor[0].similarity_pct if per_competitor else 0.0

    return OverlapResult(max_similarity_pct=max_sim, per_competitor=per_competitor)
