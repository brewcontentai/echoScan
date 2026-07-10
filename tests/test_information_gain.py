from echoscan.information_gain import score_information_gain


def test_evidence_dense_text_scores_higher_than_vague_text():
    dense = (
        "We surveyed 214 marketing teams (n=214) in 2026 and found 63% cited "
        "attribution as their top challenge, according to our internal report."
    )
    vague = (
        "Studies show that many experts agree marketing attribution is broadly "
        "considered a significant challenge for a growing number of teams."
    )
    dense_result = score_information_gain(dense)
    vague_result = score_information_gain(vague)
    assert dense_result.score > vague_result.score


def test_detects_evidence_markers():
    text = "Revenue grew 23% in 2025, reaching $4.2M according to our Q4 report."
    result = score_information_gain(text)
    assert result.evidence_markers > 0


def test_detects_named_entities():
    text = "Jasper and Copy.ai both scored lower than Brewcontent AI on our benchmark."
    result = score_information_gain(text)
    assert len(result.unique_entities) > 0


def test_empty_text_does_not_crash():
    result = score_information_gain("")
    assert result.evidence_markers == 0
