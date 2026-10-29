# Copyright (c) 2026 Daniel Ari Friedman
"""Real counting examples distinguish source length, copies, zero and undefined values."""

import pytest

from blakean_federalism.abstract_explanation import (
    FamilyExample,
    display_frequency,
    top_family_examples,
)
from blakean_federalism.corpus_statistics import analyze_corpus
from blakean_federalism.models import ResearchError

from .test_corpus_statistics import queries, unit


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, "N/A"),
        (0, "0.00"),
        (0.0001, "<0.01"),
        (0.0049, "<0.01"),
        (0.0051, "0.01"),
        (4.097819928, "4.10"),
        (10000, "10000.00"),
    ],
)
def test_visible_frequencies_keep_small_positive_values_distinct_from_zero(value, expected):
    assert display_frequency(value) == expected


@pytest.mark.parametrize("value", [-0.1, float("inf"), float("-inf"), float("nan")])
def test_invalid_display_values_are_refused(value):
    with pytest.raises(ResearchError, match="figure_frequency"):
        display_frequency(value)


def test_family_examples_keep_copies_and_use_their_words_as_the_denominator():
    data = (
        unit("a1", "imagination ordinary", "alpha", title="First title"),
        unit("a2", "imagination ordinary", "alpha", title="Second title"),
        unit("b", "imagination", "beta"),
        unit("c", "ordinary", "gamma"),
    )
    observed = top_family_examples(analyze_corpus(data, queries("imagination")), "imagination")
    assert [(row.family_id, row.matches, row.words) for row in observed] == [
        ("beta", 1, 1),
        ("alpha", 2, 4),
    ]
    assert [row.per_10000_words for row in observed] == [10000, 5000]
    assert observed[1].title == "First title / Second title"
    assert all(row.matches > 0 and row.words > 0 for row in observed)


def test_family_frequency_ties_have_stable_recorded_id_order():
    data = tuple(unit(name, "imagination", name) for name in ("zeta", "beta", "alpha"))
    forward = top_family_examples(analyze_corpus(data, queries("imagination")), "imagination")
    reverse = top_family_examples(
        analyze_corpus(tuple(reversed(data)), queries("imagination")), "imagination"
    )
    assert forward == reverse
    assert [row.family_id for row in forward] == ["alpha", "beta"]


@pytest.mark.parametrize("text", ["...", "ordinary"])
def test_zero_hits_have_no_positive_family_examples(text):
    stats = analyze_corpus((unit("empty", text),), queries("imagination"))
    assert top_family_examples(stats, "imagination") == ()


def test_unknown_query_is_refused():
    stats = analyze_corpus((unit("a", "imagination"),), queries("imagination"))
    with pytest.raises(ResearchError, match="figure_query"):
        top_family_examples(stats, "unknown")


@pytest.mark.parametrize(
    "changes",
    [{"tokens": -1}, {"tokens": 0}, {"occurrences": {}}, {"occurrences": {"imagination": -1}}],
)
def test_inconsistent_primary_unit_counts_are_refused(changes):
    stats = analyze_corpus((unit("a", "imagination"),), queries("imagination"))
    changed = stats.model_copy(update={"units": (stats.units[0].model_copy(update=changes),)})
    with pytest.raises(ResearchError, match="figure_family_count"):
        top_family_examples(changed, "imagination")


@pytest.mark.parametrize(
    "values",
    [("", "A", 1, 1), ("a", "", 1, 1), ("a", "A", 0, 1), ("a", "A", 1, 0)],
)
def test_family_examples_require_named_positive_counts(values):
    with pytest.raises(ResearchError, match="figure_family_example"):
        FamilyExample(*values)
