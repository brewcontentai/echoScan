"""Shared text-normalization helpers."""

from __future__ import annotations

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_SPLIT = re.compile(r"\b\w+\b")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    text = normalize(text)
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def word_count(text: str) -> int:
    return len(_WORD_SPLIT.findall(text))


def per_100_words(count: int, total_words: int) -> float:
    if total_words == 0:
        return 0.0
    return round((count / total_words) * 100, 2)
