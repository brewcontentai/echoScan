from echoscan.overlap import score_overlap


def test_no_competitors_returns_zero():
    result = score_overlap("some content here", {})
    assert result.max_similarity_pct == 0.0
    assert result.per_competitor == []


def test_identical_text_scores_high_similarity():
    text = "Marketing teams struggle with attribution across long B2B sales cycles."
    result = score_overlap(text, {"competitor_a": text})
    assert result.max_similarity_pct > 90


def test_unrelated_text_scores_low_similarity():
    text = "Marketing teams struggle with attribution across long B2B sales cycles."
    competitor = "The recipe calls for two cups of flour and a teaspoon of baking soda."
    result = score_overlap(text, {"competitor_a": competitor})
    assert result.max_similarity_pct < 20


def test_multiple_competitors_ranked_by_similarity():
    text = "AI content marketing tools are reshaping demand generation strategy."
    close = "AI content marketing tools are reshaping demand generation approaches."
    far = "The weather today is sunny with a light breeze from the northwest."
    result = score_overlap(text, {"close": close, "far": far})
    assert result.per_competitor[0].source == "close"


def test_empty_corpus_degrades_gracefully_instead_of_raising():
    # Regression test: scikit-learn's TfidfVectorizer raises
    # "empty vocabulary" when the whole corpus has no tokens left after
    # stop-word removal (e.g. empty text, or stop-words-only text). This
    # used to propagate as an uncaught ValueError and crash the CLI.
    result = score_overlap("", {"rival.txt": ""})
    assert result.max_similarity_pct == 0.0
    assert len(result.per_competitor) == 1
    assert result.per_competitor[0].source == "rival.txt"
    assert result.per_competitor[0].similarity_pct == 0.0
    assert result.per_competitor[0].top_shared_terms == []


def test_stopwords_only_corpus_degrades_gracefully():
    result = score_overlap("the a an of", {"rival.txt": "the a an of"})
    assert result.max_similarity_pct == 0.0
