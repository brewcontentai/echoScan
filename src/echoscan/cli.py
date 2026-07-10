"""EchoScan command-line interface. Built by Brewcontent.ai."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from echoscan import __version__, analyze
from echoscan.models import EchoScanReport

console = Console()

BANNER = (
    "[bold cyan]EchoScan[/bold cyan] [dim]— Content Distinctiveness & Information-Gain Auditor[/dim]\n"
    "[bold magenta]Built by [link=https://brewcontent.ai]Brewcontent.ai[/link][/bold magenta]"
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] file not found: {path}")
        sys.exit(1)
    except UnicodeDecodeError:
        console.print(f"[bold red]Error:[/bold red] could not decode file as UTF-8: {path}")
        sys.exit(1)


def _score_color(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    if score >= 40:
        return "dark_orange"
    return "red"


def _render(report: EchoScanReport) -> None:
    # Everything below interpolates content derived from the analyzed file
    # (filenames, competitor labels, extracted terms) into rich's console
    # markup. Rich treats "[...]" as formatting instructions, so any of
    # that untrusted content must be escaped before printing — otherwise a
    # crafted filename or competitor label could inject/spoof console
    # output (e.g. a file named "[green]PASSED[/]report.txt").
    console.print(Panel.fit(BANNER, border_style="cyan"))

    color = _score_color(report.distinctiveness_score)
    console.print(
        f"\n[bold]{escape(report.source)}[/bold]  ({report.word_count} words)\n"
        f"[bold {color}]Distinctiveness Score: {report.distinctiveness_score}/100[/bold {color}]  "
        f"— {escape(report.verdict)}\n"
    )

    table = Table(title="Component Scores", show_lines=False)
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_column("Detail")

    table.add_row(
        "Genericness (higher = more distinctive)",
        f"{report.genericness.score}/100",
        f"{report.genericness.cliche_density_per_100_words} cliches/100w, "
        f"{report.genericness.filler_sentence_ratio * 100:.0f}% filler sentences",
    )
    table.add_row(
        "Information Gain",
        f"{report.information_gain.score}/100",
        f"{report.information_gain.evidence_density_per_100_words} evidence markers/100w, "
        f"{len(report.information_gain.unique_entities)} named entities",
    )
    if report.overlap.per_competitor:
        table.add_row(
            "Competitor Overlap (lower = more distinctive)",
            f"{report.overlap.max_similarity_pct}%",
            f"closest match: {escape(report.overlap.per_competitor[0].source)}",
        )
    console.print(table)

    if report.genericness.cliche_hits:
        console.print("\n[bold]Top cliche phrases detected:[/bold]")
        for hit in report.genericness.cliche_hits[:5]:
            console.print(f"  • \"{escape(hit['phrase'])}\" x{hit['count']}")

    console.print("\n[bold]Suggestions:[/bold]")
    for s in report.suggestions:
        console.print(f"  → {escape(s)}")
    console.print()


@click.group()
@click.version_option(version=__version__, prog_name="echoscan")
def main() -> None:
    """EchoScan — Content Distinctiveness & Information-Gain Auditor.

    Built by Brewcontent.ai.
    """


@main.command()
@click.argument("content_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--competitor",
    "competitor_files",
    multiple=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to a competitor content file, for overlap scoring. Repeatable.",
)
@click.option(
    "--json",
    "json_out",
    type=click.Path(path_type=Path),
    default=None,
    help="Write the full report as JSON to this path.",
)
@click.option("--quiet", is_flag=True, help="Suppress the rich terminal report.")
def analyze_cmd(content_file: Path, competitor_files: tuple[Path, ...], json_out: Path | None, quiet: bool) -> None:
    """Analyze CONTENT_FILE and print/export a distinctiveness report."""
    text = _read_text(content_file)

    competitors = {}
    for cf in competitor_files:
        competitors[cf.name] = _read_text(cf)

    report = analyze(text, source=content_file.name, competitors=competitors)

    if not quiet:
        _render(report)

    if json_out:
        json_out.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        console.print(f"[dim]Report written to {json_out}[/dim]")


main.add_command(analyze_cmd, name="analyze")


if __name__ == "__main__":
    main()
