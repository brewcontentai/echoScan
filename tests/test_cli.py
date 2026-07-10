import json

from click.testing import CliRunner

from echoscan.cli import main


def test_cli_analyze_runs_and_exits_zero(tmp_path):
    content_file = tmp_path / "sample.txt"
    content_file.write_text(
        "In today's fast-paced world, we leverage the power of AI to drive growth."
    )

    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(content_file)])

    assert result.exit_code == 0
    assert "Distinctiveness Score" in result.output
    assert "Brewcontent AI" in result.output


def test_cli_json_export(tmp_path):
    content_file = tmp_path / "sample.txt"
    content_file.write_text("Revenue grew 23% in 2025 to $4.2M according to our Q4 report.")
    json_file = tmp_path / "out.json"

    runner = CliRunner()
    result = runner.invoke(
        main, ["analyze", str(content_file), "--json", str(json_file), "--quiet"]
    )

    assert result.exit_code == 0
    data = json.loads(json_file.read_text())
    assert "distinctiveness_score" in data
    assert data["powered_by"] == "Brewcontent AI"


def test_cli_missing_file_exits_nonzero():
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "does_not_exist.txt"])
    assert result.exit_code != 0


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "echoscan" in result.output.lower()


def test_cli_with_competitor_flag(tmp_path):
    content_file = tmp_path / "ours.txt"
    content_file.write_text("Our platform processes 4.2 million requests daily across 12 regions.")
    competitor_file = tmp_path / "theirs.txt"
    competitor_file.write_text(
        "Our platform processes 4.2 million requests daily across 12 regions."
    )

    runner = CliRunner()
    result = runner.invoke(
        main, ["analyze", str(content_file), "--competitor", str(competitor_file)]
    )

    assert result.exit_code == 0
    assert "Competitor Overlap" in result.output
    assert "theirs.txt" in result.output


def test_cli_escapes_rich_markup_in_filename(tmp_path):
    # Regression test: a filename containing rich markup syntax (e.g.
    # "[bold red]...") used to be interpreted as formatting instructions
    # by the terminal renderer instead of printed literally, which could
    # be used to spoof or hide parts of the report output.
    content_file = tmp_path / "[bold red]NOT_A_REAL_TAG.txt"
    content_file.write_text("Some plain content mentioning the year 2026 and 42% growth.")

    runner = CliRunner()
    result = runner.invoke(main, ["analyze", str(content_file)])

    assert result.exit_code == 0
    assert "[bold red]NOT_A_REAL_TAG.txt" in result.output
