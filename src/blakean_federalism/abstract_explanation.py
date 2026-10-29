# Copyright (c) 2026 Daniel Ari Friedman
"""Plain numerical labels and source examples for the opening frequency table."""

from collections import Counter
from dataclasses import dataclass
from math import isfinite

from .corpus_statistics_models import CorpusStatistics
from .models import ResearchError

_ROUNDING_THRESHOLD = 0.005


@dataclass(frozen=True)
class FamilyExample:
    family_id: str
    title: str
    matches: int
    words: int

    def __post_init__(self) -> None:
        if not self.family_id or not self.title or self.words <= 0 or self.matches <= 0:
            raise ResearchError(
                "figure_family_example", "A named positive-word, positive-hit family is required"
            )

    @property
    def per_10000_words(self) -> float:
        return 10000 * self.matches / self.words


def display_frequency(value: float | None) -> str:
    """Distinguish an undefined denominator, measured zero and a small positive value."""
    if value is None:
        return "N/A"
    if not isfinite(value) or value < 0:
        raise ResearchError("figure_frequency", "A frequency must be finite and nonnegative")
    if 0 < value < _ROUNDING_THRESHOLD:
        return "<0.01"
    return f"{value:.2f}"


def top_family_examples(stats: CorpusStatistics, query_id: str) -> tuple[FamilyExample, ...]:
    """Select the two highest positive family frequencies from the primary-unit table."""
    if query_id not in {query.query_id for query in stats.query_specs}:
        raise ResearchError("figure_query", query_id)
    words: Counter[str] = Counter()
    matches: Counter[str] = Counter()
    titles: dict[str, set[str]] = {}
    for unit in stats.units:
        if query_id not in unit.occurrences or unit.tokens < 0 or unit.occurrences[query_id] < 0:
            raise ResearchError("figure_family_count", unit.passage_id)
        if unit.tokens == 0 and unit.occurrences[query_id] > 0:
            raise ResearchError("figure_family_count", unit.passage_id)
        words[unit.work_id] += unit.tokens
        matches[unit.work_id] += unit.occurrences[query_id]
        titles.setdefault(unit.work_id, set()).add(unit.title)
    rows = [
        FamilyExample(key, " / ".join(sorted(titles[key])), matches[key], count)
        for key, count in words.items()
        if count > 0 and matches[key] > 0
    ]
    return tuple(sorted(rows, key=lambda row: (-row.per_10000_words, row.family_id))[:2])
