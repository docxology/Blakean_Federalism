# Copyright (c) 2026 Daniel Ari Friedman
"""Real PDF controls for undefined rates and finite-deletion plots."""

from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.analysis_figures import FOCUS, cooccurrence, rates, sensitivity
from blakean_federalism.corpus_statistics import analyze_corpus

from .test_corpus_statistics import queries, unit


@pytest.mark.parametrize(
    ("drawing", "minimum_na"), [(rates, 16), (sensitivity, 8), (cooccurrence, 64)]
)
def test_undefined_statistics_stay_na_in_real_pdf(tmp_path, drawing, minimum_na):
    stats = analyze_corpus((unit("empty", ""),), queries(*FOCUS))
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / "undefined.pdf"
    canvas = Canvas(str(path), pagesize=(540, 445))
    drawing(canvas, stats)
    canvas.save()
    text = PdfReader(path).pages[0].extract_text()
    assert text.count("N/A") >= minimum_na
    assert "nan" not in text.casefold()
    assert "infinity" not in text.casefold()


def test_single_family_deletion_has_no_rate_but_pooled_zero_is_preserved(tmp_path):
    stats = analyze_corpus((unit("one", "unrelated tokens"),), queries(*FOCUS))
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / "single.pdf"
    canvas = Canvas(str(path), pagesize=(540, 445))
    sensitivity(canvas, stats)
    canvas.save()
    text = PdfReader(path).pages[0].extract_text()
    assert text.count("N/A: no defined deletion rate") == len(FOCUS)
    assert all(q.copy_retaining.rate_per_10000_tokens == 0 for q in stats.queries)


def test_positive_single_family_rate_sets_visible_axis_and_overlap(tmp_path):
    stats = analyze_corpus((unit("one", " ".join(FOCUS)),), queries(*FOCUS))
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / "positive.pdf"
    canvas = Canvas(str(path), pagesize=(540, 445))
    sensitivity(canvas, stats)
    canvas.showPage()
    cooccurrence(canvas, stats)
    canvas.save()
    pages = PdfReader(path).pages
    assert "1250.0" in pages[0].extract_text()
    assert pages[1].extract_text().count("1.00") >= 64
    assert all(q.copy_retaining.rate_per_10000_tokens == 1250 for q in stats.queries)
