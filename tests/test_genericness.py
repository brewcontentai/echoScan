from echoscan.genericness import score_genericness


def test_detects_cliche_phrases():
    text = "In today's fast-paced world, we leverage the power of AI to drive growth."
    result = score_genericness(text)
    assert result.cliche_density_per_100_words > 0
    assert any(h["phrase"] == "in today's fast-paced world" for h in result.cliche_hits)


def test_clean_technical_text_scores_high():
    text = (
        "Our API processes 4.2 million requests per day across 12 regions, with a "
        "p99 latency of 180ms as measured in our March 2026 load test."
    )
    result = score_genericness(text)
    assert result.score >= 90


def test_all_filler_scores_low():
    text = (
        "In today's fast-paced world, it's important to note that at the end of the "
        "day, businesses must leverage synergies. In conclusion, this is a game changer. "
        "Moreover, furthermore, in summary, we must think outside the box."
    )
    result = score_genericness(text)
    assert result.score < 40


def test_empty_text_does_not_crash():
    result = score_genericness("")
    assert result.score == 100.0
    assert result.cliche_hits == []
