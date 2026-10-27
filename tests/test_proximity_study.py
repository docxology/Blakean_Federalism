# Copyright (c) 2026 Daniel Ari Friedman
"""Independent tiny-corpus window enumeration and malformed-aggregate controls."""

import itertools
import re
from pathlib import Path
from typing import Literal, TypeAlias

import pytest
import reportlab
from pydantic import TypeAdapter, ValidationError
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.corpus import import_corpus, load_import
from blakean_federalism.figure_style import registry
from blakean_federalism.models import CorpusPin, Passage, Plane, ResearchError, Role
from blakean_federalism.proximity_figure import draw_proximity_study
from blakean_federalism.proximity_study import (
    BUDGETS,
    PAIRS,
    ProximityStudy,
    build_proximity_study,
    produce_proximity_study,
)
from blakean_federalism.search import matching_spans
from blakean_federalism.search_models import SearchRequest
from blakean_federalism.search_study import build_search_study

Captured: TypeAlias = tuple[Path, Path, CorpusPin, Path, list[dict[str, str | None]]]


def passage(text: str, identity: str = "p1", *, work_id: str = "milton") -> Passage:
    return Passage(
        passage_id=identity,
        work_id=work_id,
        author_id="test-author",
        title="Test",
        edition_id="test",
        edition="Test",
        locator="test",
        locator_kind="plate",
        source_url="https://example.test",
        rights="Synthetic",
        source_plane=Plane.READING,
        text_role=Role.PRIMARY,
        text=text,
    )


def test_fixed_grid_agrees_with_independent_literal_cartesian_oracle(captured: Captured) -> None:
    _, _, pin, _, _ = captured
    texts = (
        "state individual state " + "x " * 9 + "individual",
        "states " + "x " * 15 + "individuals",
        "nation liberty nation",
        "nations " + "x " * 63 + "imagination",
        "system imagination labour misery",
        "system " + "x " * 31 + "imagination",
        "!!!",
    )
    units = tuple(passage(t, f"p{i}", work_id=f"family{i % 2}") for i, t in enumerate(texts))
    study = build_proximity_study(units, pin)
    assert len(study.rows) == 30
    for row in study.rows:
        expected = dict.fromkeys(row.request.terms, 0)
        matched = 0
        for source in texts:
            groups = tuple(
                tuple(re.finditer(r"\b" + term + r"\b", source)) for term in row.request.terms
            )
            selected: set[tuple[str, int, int]] = set()
            tokens = tuple(re.finditer(r"\w+", source))
            for group in itertools.product(*groups):
                start, end = min(h.start() for h in group), max(h.end() for h in group)
                cost = sum(t.start() < end and t.end() > start for t in tokens)
                if row.request.window_words is None or cost <= row.request.window_words:
                    selected.update(
                        (term, h.start(), h.end())
                        for term, h in zip(row.request.terms, group, strict=True)
                    )
            matched += bool(selected)
            for term, _, _ in selected:
                expected[term] += 1
        assert {t.term: t.occurrences for t in row.terms} == expected
        assert row.matched_source_units == matched
        assert row.total_occurrences == sum(expected.values())
        assert row.eligible_source_units == len(units)
    assert ProximityStudy.model_validate_json(study.model_dump_json()) == study


@pytest.mark.parametrize(
    "change", ["count", "term", "rate", "nan", "denominator", "request", "grid", "monotone"]
)
def test_mutated_aggregate_rejected(captured: Captured, change: str) -> None:
    _, _, pin, _, _ = captured
    original = build_proximity_study((passage("state individual"),), pin)
    row = original.rows[0]
    if change == "count":
        row = row.model_copy(update={"total_occurrences": row.total_occurrences + 1})
    elif change == "term":
        row = row.model_copy(
            update={"terms": (row.terms[0].model_copy(update={"term": "wrong"}), row.terms[1])}
        )
    elif change == "rate":
        row = row.model_copy(update={"occurrences_per_10000_tokens": 0})
    elif change == "nan":
        row = row.model_copy(update={"occurrences_per_10000_tokens": float("nan")})
    elif change == "denominator":
        row = row.model_copy(update={"eligible_word_tokens": row.eligible_word_tokens + 1})
    elif change == "request":
        row = row.model_copy(
            update={"request": row.request.model_copy(update={"whole_words": False})}
        )
    rows = (row, *original.rows[1:])
    if change == "grid":
        rows = rows[:-1]
    if change == "monotone":
        zero = build_proximity_study((passage("state xxxx"),), pin)
        rows = (row, zero.rows[1], *original.rows[2:])
    invalid = original.model_copy(update={"rows": rows})
    with pytest.raises((ResearchError, ValidationError)):
        _ = ProximityStudy.model_validate_json(invalid.model_dump_json())


def test_zero_denominators_have_undefined_rates(captured: Captured) -> None:
    _, _, pin, _, _ = captured
    study = build_proximity_study((passage("!!!"),), pin)
    assert all(
        r.total_occurrences == 0
        and r.occurrences_per_10000_tokens is None
        and r.eligible_word_tokens == 0
        for r in study.rows
    )


def test_production_rejects_synthetic_import_instead_of_relabeling(captured: Captured) -> None:
    source, _, pin, imported, _ = captured
    _ = import_corpus(source, imported, pin)
    _, units = load_import(imported, pin)
    retained = build_search_study(units, pin)
    with pytest.raises(ResearchError, match="proximity_pin"):
        _ = produce_proximity_study(imported, pin, retained)


def test_proximity_figure_has_real_six_row_vector_page(captured: Captured, tmp_path: Path) -> None:
    _, _, pin, _, _ = captured
    study = build_proximity_study((passage("state individual"),), pin)
    font = Path(reportlab.__file__).parent / "fonts/Vera.ttf"
    registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(font)))
    output = tmp_path / "proximity.pdf"
    canvas = Canvas(str(output), pagesize=(540, 445))
    draw_proximity_study(canvas, study)
    canvas.save()
    reader = PdfReader(output)
    assert len(reader.pages) == 1
    assert TypeAdapter(tuple[float, float, float, float]).validate_python(
        reader.pages[0]["/MediaBox"]
    ) == (0, 0, 540, 445)
    extracted = reader.pages[0].extract_text()
    assert all(term in extracted for pair in PAIRS for term in pair)
    assert all(str(budget) in extracted for budget in BUDGETS if budget)


def test_production_detects_modified_import_before_reporting(captured: Captured) -> None:
    source, _, pin, imported, _ = captured
    _ = import_corpus(source, imported, pin)
    _, units = load_import(imported, pin)
    retained = build_search_study(units, pin)
    with (imported / "passages.sqlite").open("ab") as stream:
        _ = stream.write(b"invalid checksum")
    with pytest.raises(ResearchError, match="import_checksum"):
        _ = produce_proximity_study(imported, pin, retained)


def test_aggregate_contains_no_source_context_fields(captured: Captured) -> None:
    _, _, pin, _, _ = captured
    study = build_proximity_study((passage("state individual"),), pin)
    for row in study.rows:
        assert set(type(row).model_fields) == {
            "request",
            "eligible_source_units",
            "eligible_word_tokens",
            "eligible_source_families",
            "matched_source_units",
            "matched_source_families",
            "total_occurrences",
            "occurrences_per_10000_tokens",
            "terms",
            "facets",
        }
        assert all(set(type(term).model_fields) == {"term", "occurrences"} for term in row.terms)


@pytest.mark.parametrize(
    ("mode", "window", "text", "expected"),
    [
        ("any", None, "state state", (("state", 0, 5), ("state", 6, 11))),
        ("all", None, "state state", ()),
        ("all", None, "state x individual", (("state", 0, 5), ("individual", 8, 18))),
        ("all", 2, "state x individual", ()),
        ("all", 3, "state x individual", (("state", 0, 5), ("individual", 8, 18))),
    ],
)
def test_public_spans_gate_preserves_original_offsets_before_cap(
    mode: Literal["any", "all"],
    window: int | None,
    text: str,
    expected: tuple[tuple[str, int, int], ...],
) -> None:
    request = SearchRequest(terms=("state", "individual"), mode=mode, window_words=window, limit=1)
    assert matching_spans(text, request) == expected
