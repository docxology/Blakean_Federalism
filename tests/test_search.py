# Copyright (c) 2026 Daniel Ari Friedman
"""Known-answer source, Unicode and limit controls for corpus-wide literal search."""

import hashlib

import pytest
from pydantic import ValidationError

from blakean_federalism.corpus import import_corpus
from blakean_federalism.models import Passage, Plane, ResearchError, Role
from blakean_federalism.search import search_corpus, search_passages
from blakean_federalism.search_models import SearchRequest, SearchResult


def passage(text, identity="p1", **changes: object):
    return Passage.model_validate(
        dict(
            passage_id=identity,
            work_id="milton",
            author_id="william-blake-1757-1827",
            title="Milton",
            edition_id="copy-d",
            edition="Test extraction",
            locator="32:22",
            locator_kind="plate",
            source_url="https://example.test/milton",
            rights="Synthetic test only",
            source_plane="reading",
            text_role="primary",
            text=text,
        )
        | changes
    )


def test_arbitrary_terms_search_all_units_not_a_query_catalog():
    units = (passage("States change. Individual identities never cease."),)
    result = search_passages(units, SearchRequest(terms=("Individual identities",)))
    assert result.total_occurrences == result.matched_source_units == 1
    hit = result.hits[0]
    assert (hit.start, hit.end, hit.expression) == (15, 36, "Individual identities")
    assert hit.text_sha256 == hashlib.sha256(units[0].text.encode()).hexdigest()
    assert (hit.source_url, hit.rights, hit.edition_id, hit.locator) == (
        units[0].source_url,
        units[0].rights,
        units[0].edition_id,
        units[0].locator,
    )
    assert SearchResult.model_validate_json(result.model_dump_json()) == result


def test_any_and_all_compare_units_not_separate_documents():
    units = (
        passage("state and nation; state", "together"),
        passage("state", "separate-a"),
        passage("nation", "separate-b"),
    )
    any_result = search_passages(units, SearchRequest(terms=("state", "nation")))
    all_result = search_passages(units, SearchRequest(terms=("state", "nation"), mode="all"))
    assert (any_result.total_occurrences, any_result.matched_source_units) == (5, 3)
    assert (all_result.total_occurrences, all_result.matched_source_units) == (3, 1)
    assert {hit.passage_id for hit in all_result.hits} == {"together"}
    assert all_result.facets[0].source_units == 3
    assert all_result.facets[0].word_tokens == 6
    assert all_result.facets[0].occurrences_per_10000_tokens == 5000


def test_result_limit_does_not_limit_facet_denominators_or_counts():
    units = (passage("state state", "b"), passage("state", "a"), passage("nothing", "c"))
    result = search_passages(units, SearchRequest(terms=("state",), limit=1))
    assert (result.eligible_source_units, result.total_occurrences, result.returned_hits) == (
        3,
        3,
        1,
    )
    assert result.matched_source_units == result.facets[0].matched_units == 2
    assert result.facets[0].word_tokens == 4
    assert result.facets[0].occurrences_per_10000_tokens == 7500
    assert result.truncated
    assert result.hits[0].passage_id == "a"


def test_primary_is_default_and_filters_are_conjunctive():
    units = (
        passage("state"),
        passage("state", "p2", source_plane="xml", text_role="unverified"),
        passage("state", "p3", source_plane="erdman", text_role="editorial"),
        passage("state", "p4", work_id="jerusalem"),
    )
    assert search_passages(units, SearchRequest(terms=("state",))).eligible_source_units == 2
    all_sources = search_passages(units, SearchRequest(terms=("state",), role=None))
    assert all_sources.eligible_source_units == 4
    result = search_passages(
        units,
        SearchRequest(terms=("state",), role=Role.UNVERIFIED, plane=Plane.XML, work_id="milton"),
    )
    assert result.eligible_source_units == 1
    assert [(h.passage_id, h.role, h.plane) for h in result.hits] == [
        ("p2", Role.UNVERIFIED, Plane.XML)
    ]
    assert result.scanned_source_units == 4
    impossible = search_passages(
        units, SearchRequest(terms=("state",), plane=Plane.XML, role=Role.PRIMARY)
    )
    assert impossible.eligible_source_units == 0
    assert impossible.facets == impossible.hits == ()


def test_absent_work_and_empty_corpus_are_explicit_zero_results():
    for units, request in (
        ((), SearchRequest(terms=("state",))),
        ((passage("state"),), SearchRequest(terms=("state",), work_id="absent")),
    ):
        result = search_passages(units, request)
        assert result.total_occurrences == result.returned_hits == result.matched_source_units == 0
        assert not result.truncated
        assert result.hits == result.facets == ()


def test_zero_hit_facets_preserve_eligible_groups_and_token_totals():
    units = (
        passage("nation here", "z", work_id="z"),
        passage("nothing here", "a", work_id="a"),
        passage("nation", "x", source_plane="xml", text_role="unverified", work_id="a"),
    )
    result = search_passages(units, SearchRequest(terms=("zzzxqv",), role=None))
    assert [f.work_id for f in result.facets] == ["a", "a", "z"]
    assert [f.plane for f in result.facets] == [Plane.READING, Plane.XML, Plane.READING]
    assert [f.word_tokens for f in result.facets] == [2, 1, 2]
    assert all(f.occurrences == f.matched_units == 0 for f in result.facets)
    assert all(f.occurrences_per_10000_tokens == 0 for f in result.facets)


def test_zero_word_token_denominator_is_null_not_zero_rate():
    result = search_passages((passage("!!!"),), SearchRequest(terms=("!",)))
    assert result.total_occurrences == 3
    assert result.facets[0].word_tokens == 0
    assert result.facets[0].occurrences_per_10000_tokens is None


def test_literal_markup_metacharacters_and_whitespace_are_not_normalized():
    text = "<state> a.b axb state nation state\nnation state  nation"
    units = (passage(text),)
    for term, expected in (
        ("<state>", ["<state>"]),
        ("a.b", ["a.b"]),
        ("state nation", ["state nation"]),
        ("state\nnation", ["state\nnation"]),
        ("state  nation", ["state  nation"]),
        ("state.*nation", []),
    ):
        result = search_passages(units, SearchRequest(terms=(term,)))
        assert [hit.expression for hit in result.hits] == expected


def test_whole_word_and_substring_search_have_distinct_results():
    units = (passage("state statement _state state_ estate state-state"),)
    whole = search_passages(units, SearchRequest(terms=("state",)))
    substring = search_passages(units, SearchRequest(terms=("state",), whole_words=False))
    assert whole.total_occurrences == 3
    assert substring.total_occurrences == 7
    assert [hit.start for hit in whole.hits] == [0, 37, 43]


def test_failed_boundary_continues_search_and_each_term_is_nonoverlapping():
    units = (passage("ababa aba"),)
    whole = search_passages(units, SearchRequest(terms=("aba",)))
    substring = search_passages(units, SearchRequest(terms=("aba",), whole_words=False))
    assert [hit.start for hit in whole.hits] == [6]
    assert [hit.start for hit in substring.hits] == [0, 6]


def test_unicode_expansions_and_astral_codepoint_offsets_are_preserved():
    text = "🜁 Straße ﬃ İ 𐐀"
    units = (passage(text),)
    result = search_passages(units, SearchRequest(terms=("STRASSE", "ffi", "i\u0307", "𐐨")))
    assert [(hit.start, hit.end, hit.expression) for hit in result.hits] == [
        (2, 8, "Straße"),
        (9, 10, "ﬃ"),
        (11, 12, "İ"),
        (13, 14, "𐐀"),
    ]
    assert all(text[h.start : h.end] == h.expression for h in result.hits)


def test_casefold_expansion_cannot_be_partially_highlighted():
    units = (passage("ß s İ i ﬃ f"),)
    request = SearchRequest(terms=("s", "i", "f"), whole_words=False)
    result = search_passages(units, request)
    assert [(hit.term, hit.start, hit.expression) for hit in result.hits] == [
        ("s", 2, "s"),
        ("i", 6, "i"),
        ("f", 10, "f"),
    ]


def test_unicode_alphanumeric_and_underscore_block_word_boundaries():
    units = (passage("²state stateⅣ éstate 𐐀state state_ state"),)
    result = search_passages(units, SearchRequest(terms=("state",)))
    assert result.total_occurrences == 1
    assert result.hits[0].end == len(units[0].text)
    assert result.facets[0].word_tokens == 6


def test_each_term_can_count_the_same_span_and_order_is_deterministic():
    units = (passage("aba", "b"), passage("aba", "a"))
    result = search_passages(units, SearchRequest(terms=("ba", "aba", "ab"), whole_words=False))
    assert [(h.passage_id, h.start, h.end, h.term) for h in result.hits] == [
        ("a", 0, 2, "ab"),
        ("a", 0, 3, "aba"),
        ("a", 1, 3, "ba"),
        ("b", 0, 2, "ab"),
        ("b", 0, 3, "aba"),
        ("b", 1, 3, "ba"),
    ]
    assert result.facets[0].occurrences == 6


def test_context_bounds_reconstruct_exact_highlight_and_can_be_zero():
    text = "alpha state omega"
    units = (passage(text),)
    result = search_passages(units, SearchRequest(terms=("state",), context_chars=2))
    hit = result.hits[0]
    assert (hit.context, hit.context_start, hit.start, hit.end) == ("a state o", 4, 6, 11)
    assert hit.context[hit.start - hit.context_start : hit.end - hit.context_start] == "state"
    zero = search_passages(units, SearchRequest(terms=("state",), context_chars=0))
    assert (zero.hits[0].context, zero.hits[0].context_start) == ("state", 6)
    clipped = search_passages(units, SearchRequest(terms=("alpha", "omega"), context_chars=500))
    assert all(h.context == text and h.context_start == 0 for h in clipped.hits)


def test_duplicate_source_unit_id_is_rejected_instead_of_double_counted():
    units = (passage("state"), passage("nation"))
    with pytest.raises(ResearchError, match="duplicate_passage_id"):
        search_passages(units, SearchRequest(terms=("state",)))


@pytest.mark.parametrize(
    "changes",
    [
        {"terms": ()},
        {"terms": ("x",) * 9},
        {"terms": ("",)},
        {"terms": (" \n\t",)},
        {"terms": ("x" * 201,)},
        {"terms": ("State", "state")},
        {"terms": ("Straße", "STRASSE")},
        {"limit": 0},
        {"limit": 1001},
        {"context_chars": -1},
        {"context_chars": 501},
        {"mode": "regex"},
        {"unknown": True},
    ],
)
def test_invalid_or_ambiguous_request_is_rejected(changes):
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({"terms": ("state",)} | changes)


def test_leading_spaces_and_eight_distinct_terms_are_literal_and_valid():
    request = SearchRequest(terms=(" state ", "a", "b", "c", "d", "e", "f", "g"))
    assert request.terms[0] == " state "
    result = search_passages((passage(" state "),), request)
    assert result.total_occurrences == 1
    assert result.hits[0].expression == " state "


def test_verified_corpus_search_binds_pin_and_retains_source_roles(captured):
    source, _, pin, destination, _ = captured
    import_corpus(source, destination, pin)
    result = search_corpus(destination, pin, SearchRequest(terms=("state", "states"), role=None))
    assert result.corpus_pin == pin
    assert result.scanned_source_units == result.eligible_source_units == 2
    assert result.total_occurrences == 4
    assert result.matched_source_units == 2
    assert [(f.role, f.occurrences) for f in result.facets] == [
        (Role.EDITORIAL, 1),
        (Role.PRIMARY, 3),
    ]


def test_search_rejects_modified_index_before_returning_any_hits(captured):
    source, _, pin, destination, _ = captured
    import_corpus(source, destination, pin)
    with (destination / "passages.sqlite").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ResearchError, match="import_checksum"):
        search_corpus(destination, pin, SearchRequest(terms=("state",)))


def test_search_rejects_a_different_external_pin(captured):
    source, _, pin, destination, _ = captured
    import_corpus(source, destination, pin)
    rebound = pin.model_copy(update={"upstream_commit": "untrusted"})
    with pytest.raises(ResearchError, match="untrusted_import_pin"):
        search_corpus(destination, rebound, SearchRequest(terms=("state",)))


def test_runtime_unicode_casefold_never_deletes_a_codepoint():
    # The identity-offset fast path relies on this complete Unicode-domain property.
    assert all(chr(codepoint).casefold() for codepoint in range(0x110000))


def test_adjacent_expansions_and_boundaries_share_exact_original_offsets():
    units = (passage("a ßﬃ Z"),)
    result = search_passages(
        units, SearchRequest(terms=("ssffi", "ss", "ffi", "z"), whole_words=False)
    )
    assert [(h.start, h.end, h.term, h.expression) for h in result.hits] == [
        (2, 3, "ss", "ß"),
        (2, 4, "ssffi", "ßﬃ"),
        (3, 4, "ffi", "ﬃ"),
        (5, 6, "z", "Z"),
    ]


def test_every_runtime_expansion_matches_fully_and_rejects_a_partial_fold():
    for codepoint in range(0x110000):
        character = chr(codepoint)
        folded = character.casefold()
        if len(folded) > 1:
            units = (passage(character),)
            full = search_passages(units, SearchRequest(terms=(folded,), whole_words=False))
            partial = search_passages(units, SearchRequest(terms=(folded[:-1],), whole_words=False))
            assert [(h.start, h.end, h.expression) for h in full.hits] == [(0, 1, character)]
            assert partial.total_occurrences == 0
