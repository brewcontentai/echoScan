"""
Static linguistic pattern libraries used by the scoring modules.

Kept in one place so they're easy to extend/tune without touching scoring
logic — this list is the single biggest lever for improving EchoScan's
accuracy over time.
"""

from __future__ import annotations

# Phrases that are strong "AI-tell" / marketing-cliche signals. Matched
# case-insensitively as substrings against normalized text.
CLICHE_PHRASES: list[str] = [
    "in today's fast-paced world",
    "in today's digital age",
    "in the ever-evolving landscape",
    "in the ever-changing landscape",
    "navigate the complexities",
    "unlock the full potential",
    "unlock the power of",
    "seamlessly integrate",
    "seamlessly integrates",
    "game changer",
    "game-changer",
    "cutting-edge",
    "state-of-the-art",
    "revolutionize",
    "revolutionizing",
    "delve into",
    "diving deep into",
    "it's important to note",
    "it is important to note",
    "at the end of the day",
    "when it comes to",
    "in conclusion",
    "in summary",
    "furthermore",
    "moreover",
    "leverage synergies",
    "leverage the power of",
    "paradigm shift",
    "holistic approach",
    "robust solution",
    "best-in-class",
    "world-class",
    "next-level",
    "take it to the next level",
    "move the needle",
    "low-hanging fruit",
    "circle back",
    "deep dive",
    "unprecedented",
    "in this article, we will",
    "in this blog post, we will",
    "let's dive in",
    "without further ado",
    "at its core",
    "boils down to",
    "the key takeaway",
    "the bottom line",
    "one size fits all",
    "think outside the box",
    "empower businesses",
    "empower organizations",
    "drive growth",
    "unlock growth",
    "supercharge",
    "elevate your",
    "transform the way",
    "redefine the way",
    "a testament to",
    "plays a crucial role",
    "plays a vital role",
    "cannot be overstated",
    "in a nutshell",
]

# Hedge / vague-claim phrases that typically signal unsupported, low
# information-gain assertions rather than concrete evidence.
VAGUE_CLAIM_PHRASES: list[str] = [
    "studies show",
    "research shows",
    "experts agree",
    "experts say",
    "it is widely known",
    "it is well known",
    "many believe",
    "some say",
    "many experts",
    "industry leaders",
    "many companies",
    "numerous studies",
    "a growing number of",
    "more and more",
    "increasingly",
    "significant impact",
    "substantial impact",
    "proven to work",
    "widely regarded",
]

# Regex-detectable evidence markers: concrete numbers, percentages, dates,
# currency, and citation-style phrasing that suggest real information gain.
import re  # noqa: E402

EVIDENCE_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b\d{1,3}(,\d{3})*(\.\d+)?%\b"),               # percentages
    re.compile(r"\$\s?\d[\d,]*(\.\d+)?\s?(k|m|b|bn|million|billion)?", re.I),
    re.compile(r"\baccording to\b", re.I),
    re.compile(r"\bsource:\s*\S+", re.I),
    re.compile(r"\b\d+(\.\d+)?x\b", re.I),                        # multipliers e.g. 3.2x
    re.compile(r"\bn\s?=\s?\d+", re.I),                           # sample sizes
    re.compile(r"\b(19|20)\d{2}\b"),                              # years (single pattern —
                                                                   # do not also match \d{4}
                                                                   # generically, or years get
                                                                   # double-counted as evidence)
    re.compile(r"\[\d+\]"),                                       # citation markers
    re.compile(r"\bhttps?://\S+"),
]

# Simple proper-noun / named-entity heuristic: capitalized multi-word runs
# not at sentence start, used as a proxy for concrete, specific references
# (company names, product names, people) that generic content avoids.
PROPER_NOUN_PATTERN = re.compile(
    r"(?<!^)(?<![.!?]\s)\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})\b"
)
