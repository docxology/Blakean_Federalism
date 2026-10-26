# Copyright (c) 2026 Daniel Ari Friedman
"""Aggregate study counts retain all source roles and reject changed totals."""

import json
from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.corpus import import_corpus, load_import
from blakean_federalism.models import ResearchError
from blakean_federalism.search_figure import draw_search_study
from blakean_federalism.search_study import SearchStudy, build_search_study


def test_study_counts_and_real_vector_output(captured, tmp_path):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    _, passages = load_import(dest, pin)
    changed = (
        passages[0].model_copy(
            update={"text": "liberty freedom minute particulars general forms brotherhood nation"}
        ),
        passages[1],
    )
    study = build_search_study(changed, pin)
    assert study.source_units == 2
    assert [q.total_occurrences for q in study.queries] == [1, 1, 1, 1, 1, 2, 0]
    assert all(sum(f.source_units for f in q.facets) == 2 for q in study.queries)
    raw = study.model_dump_json()
    assert "text_sha256" not in raw
    assert "context" not in json.loads(raw)
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / "study.pdf"
    canvas = Canvas(str(path), pagesize=(540, 445))
    draw_search_study(canvas, study)
    canvas.save()
    text = PdfReader(path).pages[0].extract_text()
    assert "Nonsense control: 0 hits" in text
    assert "minute particulars" in text


@pytest.mark.parametrize("change", ["empty", "duplicate", "count", "eligible", "facets", "units"])
def test_study_rejects_inconsistent_membership(captured, change):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    _, passages = load_import(dest, pin)
    data = build_search_study(passages, pin).model_dump(mode="json")
    if change == "empty":
        data["queries"] = []
    if change == "duplicate":
        data["queries"].append(data["queries"][0])
    if change == "count":
        data["queries"][0]["total_occurrences"] += 1
    if change == "eligible":
        data["queries"][0]["eligible_source_units"] += 1
    if change == "facets":
        data["queries"][0]["facets"].append(data["queries"][0]["facets"][0])
    if change == "units":
        data["queries"][0]["facets"][0]["matched_units"] = 99
    with pytest.raises(ResearchError):
        SearchStudy.model_validate(data)
