# Copyright (c) 2026 Daniel Ari Friedman
"""Real PDF label oracles from deliberately unequal synthetic source families."""

from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.analysis_figures import FOCUS, cooccurrence, rates, sensitivity
from blakean_federalism.corpus_statistics import analyze_corpus

from .test_corpus_statistics import queries, unit


def render_text(tmp_path, name, drawing, stats):
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / (name + ".pdf")
    canvas = Canvas(str(path), pagesize=(540, 445))
    drawing(canvas, stats)
    canvas.save()
    return PdfReader(path).pages[0].extract_text()


def unequal_families():
    # alpha has two copies and four tokens; beta and gamma each have two tokens.
    return analyze_corpus(
        (
            unit("a", "states nations", "alpha"),
            unit("b", "states states", "alpha"),
            unit("c", "nations unrelated", "beta"),
            unit("d", "unrelated unrelated", "gamma"),
        ),
        queries(*FOCUS),
    )


def test_rate_labels_keep_copy_and_family_denominators_distinct(tmp_path):
    content = render_text(tmp_path, "rates", rates, unequal_families())
    assert "3 occurrences" in content
    assert "3750.00 / 2500.00" in content
    assert "1/3 families" in content
    assert "2/4 units" in content
    assert "Pooled denominator: 8 tokens" in content
    # A second measurement changes all relevant copy denominators, not the family count.
    changed = analyze_corpus((unit("only", "states nations", "alpha"),), queries(*FOCUS))
    other = render_text(tmp_path, "rates-changed", rates, changed)
    assert "3750.00 / 2500.00" not in other
    assert "1/1 families" in other


def test_endpoint_labels_identify_omission_and_ties(tmp_path):
    content = render_text(tmp_path, "deletions", sensitivity, unequal_families())
    # Removing alpha leaves no states; either other omission leaves 3/6 * 10000.
    assert "0.00\nalpha\n5000.00\nbeta (+1 tied)" in content


def test_directional_conditionals_are_not_jaccard_and_reject_reversal(tmp_path):
    content = render_text(tmp_path, "overlap", cooccurrence, unequal_families())
    expected = "P(nations|states) 1.00; P(states|nations) 0.50; lift 1.50"
    assert expected in content
    assert "P(nations|states) 0.50; P(states|nations) 1.00" not in content
    assert "0.50" in content  # Jaccard uses one shared / two either families.
