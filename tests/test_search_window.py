# Copyright (c) 2026 Daniel Ari Friedman
"""Real literal-window boundary and aggregate controls."""

import itertools
import random
import re

import pytest
from pydantic import ValidationError

from blakean_federalism.search import _spans, search_passages
from blakean_federalism.search_models import SearchRequest, SearchResult
from tests.test_search import passage


@pytest.mark.parametrize(("width", "expected"), [(1, 0), (2, 2), (3, 3), (4, 3)])
def test_window_counts_participants_before_cap(width, expected):
    units = (passage("state x nation state x x x state"),)
    result = search_passages(
        units, SearchRequest(terms=("state", "nation"), mode="all", window_words=width, limit=1)
    )
    assert result.total_occurrences == expected
    assert result.facets[0].occurrences == expected
    assert result.returned_hits == min(1, expected)
    assert result.facets[0].word_tokens == 8
    assert result.facets[0].occurrences_per_10000_tokens == expected * 1250


@pytest.mark.parametrize(
    "changes",
    [
        {"window_words": 0},
        {"window_words": 201},
        {"window_words": True},
        {"window_words": 2.0},
        {"window_words": "2"},
        {"window_words": 2, "mode": "any"},
        {"window_words": 2, "terms": ("a",)},
        {"window_words": 2, "terms": ("a", "A")},
    ],
)
def test_invalid_window_rejected(changes):
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({"terms": ("a", "b"), "mode": "all"} | changes)


@pytest.mark.parametrize(
    ("text", "terms", "width", "expected"),
    [
        ("a b c", ("a b", "c"), 2, []),
        ("a b c", ("a b", "c"), 3, [(0, 3), (4, 5)]),
        ("aba", ("ab", "aba", "ba"), 1, [(0, 2), (0, 3), (1, 3)]),
        ("! ?", ("!", "?"), 1, [(0, 1), (2, 3)]),
        ("🜁 Straße\n𐐀 _z", ("STRASSE\n𐐨", "_z"), 3, [(2, 10), (11, 13)]),
        ("ß ﬃ", ("ss", "ffi"), 1, []),
        ("ß ﬃ", ("ss", "ffi"), 2, [(0, 1), (2, 3)]),
    ],
)
def test_original_unicode_phrase_and_nested_spans(text, terms, width, expected):
    result = search_passages(
        (passage(text),),
        SearchRequest(terms=terms, mode="all", whole_words=False, window_words=width),
    )
    assert [(h.start, h.end) for h in result.hits] == expected


def test_document_all_positive_window_negative():
    units = (passage("a x x b"),)
    assert (
        search_passages(units, SearchRequest(terms=("a", "b"), mode="all")).total_occurrences == 2
    )
    assert (
        search_passages(
            units, SearchRequest(terms=("a", "b"), mode="all", window_words=3)
        ).total_occurrences
        == 0
    )


def test_old_request_and_result_read_additive_null():
    old = search_passages((passage("a b"),), SearchRequest(terms=("a", "b"))).model_dump(
        mode="json"
    )
    old["request"].pop("window_words")
    assert SearchResult.model_validate(old).request.window_words is None


def test_sweep_matches_independent_cartesian_oracle():
    rng = random.Random(100)  # noqa: S311 - deterministic synthetic search cases, not security
    for _ in range(160):
        text = "".join(rng.choice(("a", "b", " ", "!", "_", "𐐀", "ß")) for _ in range(18))
        terms = rng.choice((("a", "b"), ("a", "ab", "b"), ("!", "a"), ("ss", "𐐨")))
        width = rng.randint(1, 4)
        spans = _spans(text, terms, whole_words=False)
        tokens = list(re.finditer(r"\w+", text))
        expected = set()
        for group in itertools.product(
            *(tuple(s for s in spans if s[0] == term) for term in terms)
        ):
            start, end = min(s[1] for s in group), max(s[2] for s in group)
            count = sum(t.start() < end and t.end() > start for t in tokens)
            if count <= width:
                expected.update(group)
        result = search_passages(
            (passage(text),),
            SearchRequest(terms=terms, mode="all", whole_words=False, window_words=width),
        )
        assert {(h.term, h.start, h.end) for h in result.hits} == expected, (text, terms, width)
