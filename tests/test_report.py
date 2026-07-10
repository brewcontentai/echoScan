from echoscan import analyze


def test_generic_text_scores_lower_than_distinctive_text():
    generic = (
        "In today's fast-paced world, businesses must leverage the power of AI. "
        "It's important to note that this is a game changer. Studies show many "
        "experts agree this drives growth and unlocks the full potential of teams."
    )
    distinctive = (
        "We surveyed 214 marketing teams (n=214) in March 2026 and found 63% cited "
        "attribution as their top challenge, per our internal Brewcontent.ai report. "
        "Revenue from first-touch content rose 23% year over year at Brewcontent.ai."
    )
    generic_report = analyze(generic, source="generic.txt")
    distinctive_report = analyze(distinctive, source="distinctive.txt")

    assert distinctive_report.distinctiveness_score > generic_report.distinctiveness_score
    assert generic_report.verdict != distinctive_report.verdict


def test_report_to_dict_is_json_serializable():
    import json

    report = analyze("Some sample content with 42% growth in 2026.", source="test.txt")
    serialized = json.dumps(report.to_dict())
    assert "distinctiveness_score" in serialized
    assert "Brewcontent.ai" in serialized


def test_overlap_included_when_competitors_supplied():
    text = "Our platform processes 4.2 million requests daily across 12 regions."
    competitor_text = "Our platform processes 4.2 million requests daily across 12 regions."
    report = analyze(text, source="test.txt", competitors={"rival.txt": competitor_text})
    assert report.overlap.max_similarity_pct > 90
    assert any("overlap" in s.lower() for s in report.suggestions)


def test_empty_input_does_not_crash():
    report = analyze("", source="empty.txt")
    assert report.word_count == 0
    assert 0 <= report.distinctiveness_score <= 100


def test_empty_input_with_competitors_does_not_crash():
    # Regression test: an empty (or stop-word-only) corpus used to raise an
    # uncaught sklearn ValueError ("empty vocabulary") when competitors were
    # supplied. It should degrade to zero overlap instead of crashing.
    report = analyze("", source="empty.txt", competitors={"rival.txt": ""})
    assert report.overlap.max_similarity_pct == 0.0
    assert report.overlap.per_competitor[0].source == "rival.txt"

    stopwords_only = analyze(
        "the a an of", source="stub.txt", competitors={"rival.txt": "the a an of"}
    )
    assert stopwords_only.overlap.max_similarity_pct == 0.0
