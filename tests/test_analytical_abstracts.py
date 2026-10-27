# Copyright (c) 2026 Daniel Ari Friedman
"""Real PDF, numerical mutation and input-refusal checks for analytical abstracts."""

import re

import pytest
from reportlab.pdfbase import pdfmetrics

from blakean_federalism.abstract_captions import analytical_captions
from blakean_federalism.analysis_figures import FOCUS
from blakean_federalism.analytical_abstracts import analytical_drawings
from blakean_federalism.corpus_statistics import analyze_corpus
from blakean_federalism.institutional_experiment_models import Intervention
from blakean_federalism.models import ResearchError

from .test_abstract_analysis import experiment
from .test_corpus_statistics import queries, unit
from .test_illuminated_abstracts import illuminated as illuminated_fixture
from .test_illuminated_abstracts import observed as observations_fixture
from .test_illuminated_abstracts import prepared as workbench_fixture
from .test_illuminated_abstracts import render

illuminated = illuminated_fixture
observed = observations_fixture
prepared = workbench_fixture


@pytest.fixture
def analytical(illuminated):
    root, report, artwork = illuminated
    return root, report.model_copy(update={"producer_version": "0.14.0"}), {"J1": artwork["J1"]}


def test_four_vector_pages_preserve_j1_and_embed_valid_used_fonts(analytical):
    root, report, artwork = analytical
    drawings = analytical_drawings(report, artwork)
    assert set(drawings) == {"abstract-1", "abstract-2", "abstract-3", "abstract-4"}
    for index, (key, drawing) in enumerate(drawings.items()):
        page = render(root / f"analytical-{key}.pdf", drawing)
        assert tuple(page.mediabox) == (0, 0, 540, 520)
        assert len(page.images) == int(index == 0)
        if index == 0:
            assert page.images[0].image.size == (32, 48)
            assert page.images[0].image.getpixel((0, 0)) == (176, 0, 32)
        operations = page.get_contents().operations
        used_fonts = set()
        current_font = None
        for args, op in operations:
            if op == b"Tf":
                current_font = args[0]
            if op == b"Tj" and args[0]:
                used_fonts.add(current_font)
        assert used_fonts
        fonts = page["/Resources"]["/Font"]
        for name in used_fonts:
            font = fonts[name].get_object()
            assert font["/FontDescriptor"]["/FontFile2"].get_data().startswith(b"\x00\x01\x00\x00")
            assert font["/ToUnicode"].get_data()
        assert any(op == b"Tj" for _, op in operations)
        assert any(op in (b"S", b"B", b"B*") for _, op in operations)


def test_curved_marks_are_small_circles_not_decorative_arches(analytical):
    root, report, artwork = analytical
    for key, drawing in analytical_drawings(report, artwork).items():
        page = render(root / f"paths-{key}.pdf", drawing)
        points, curves = [], 0
        for args, op in page.get_contents().operations:
            if op == b"n":
                points, curves = [], 0
            if op in (b"m", b"l", b"c"):
                points.extend(zip(map(float, args[::2]), map(float, args[1::2]), strict=True))
                curves += op == b"c"
            if curves and op in (b"S", b"s", b"B", b"B*", b"f", b"f*"):
                xs, ys = zip(*points, strict=True)
                assert curves == 4
                assert 0 < max(xs) - min(xs) <= 20
                assert max(xs) - min(xs) == pytest.approx(max(ys) - min(ys))


def test_pdf_exposes_computed_rates_ratio_legend_and_capture_denominators(analytical):
    root, report, artwork = analytical
    drawings = analytical_drawings(report, artwork)
    corpus = render(root / "rates.pdf", drawings["abstract-4"]).extract_text()
    repair = render(root / "repairs.pdf", drawings["abstract-3"]).extract_text()
    assert "3750.00 / 2500.00" in corpus
    assert "1/3 families" in corpus
    assert re.search(r"1\s*=\s*pooled", corpus)
    assert "equal-family / pooled" in corpus
    assert "deletion-rate / pooled" in corpus
    assert "20,480" in repair
    assert "5,120" in repair
    assert "15,360" in repair
    assert repair.count("512/4,096") == 2
    assert repair.count("1,024/4,096") == 2
    assert "2,048/4,096" in repair
    assert "40,960" in repair


def test_changed_counts_and_verse_reach_real_outputs(analytical):
    root, report, artwork = analytical
    changed = report.model_copy(
        update={
            "corpus_statistics": analyze_corpus(
                (unit("only", "states nations", "alpha"),), queries(*FOCUS)
            ),
            "quotations": tuple(
                q.model_copy(
                    update={
                        "segments": (
                            q.segments[0].model_copy(
                                update={"text": "A bounded replacement witness."}
                            ),
                        )
                    }
                )
                if q.quote_id == "Q37"
                else q
                for q in report.quotations
            ),
        }
    )
    drawings = analytical_drawings(changed, artwork)
    corpus = render(root / "changed-rates.pdf", drawings["abstract-4"]).extract_text()
    readings = render(root / "changed-verse.pdf", drawings["abstract-2"]).extract_text()
    assert "5000.00 / 5000.00" in corpus
    assert "3750.00 / 2500.00" not in corpus
    assert "1/1 families" in corpus
    assert "A bounded replacement witness." in " ".join(readings.split())
    captions = analytical_captions(changed)
    assert re.search(r"\b1 primary reading extracts", captions[3])
    assert re.search(r"\b2 Unicode", captions[3])


@pytest.mark.parametrize("text", ["...", "unrelated"])
def test_zero_hits_and_unavailable_rate_denominators_are_explicit(analytical, text):
    root, report, artwork = analytical
    changed = report.model_copy(
        update={
            "corpus_statistics": analyze_corpus((unit("empty", text, "empty"),), queries(*FOCUS))
        }
    )
    page = render(
        root / f"zero-{len(text)}.pdf", analytical_drawings(changed, artwork)["abstract-4"]
    )
    content = page.extract_text()
    assert content.count("ratio undefined") == 8
    assert ("0.00 / 0.00" in content) == (text == "unrelated")
    assert not {"nan", "inf", "-inf"}.intersection(content.lower().split())
    assert "N/A" in content
    assert len(analytical_captions(changed)) == 4


@pytest.mark.parametrize("quote_id", ["Q37", "Q38", "Q39", "Q40"])
@pytest.mark.parametrize("shorten", [False, True])
def test_missing_or_shortened_new_quotes_fail_before_rendering(analytical, quote_id, shorten):
    _, report, artwork = analytical
    quotations = tuple(
        q.model_copy(update={"segments": q.segments[:-1]}) if q.quote_id == quote_id else q
        for q in report.quotations
        if shorten or q.quote_id != quote_id
    )
    with pytest.raises(ResearchError, match="figure_quotation"):
        analytical_drawings(report.model_copy(update={"quotations": quotations}), artwork)


def test_alternative_minimal_bundles_keep_overlap_and_essential_semantics(analytical):
    root, report, artwork = analytical
    a, b, c = Intervention.NONCAPTURE, Intervention.CHARTER, Intervention.CONTESTATION
    alternative = experiment((a, b, c), ((a,), (b, c)))
    changed = report.model_copy(update={"institutional_experiments": alternative})
    page = render(root / "alternatives.pdf", analytical_drawings(changed, artwork)["abstract-3"])
    content = page.extract_text()
    assert re.findall(r"\d+", " ".join(content.splitlines()[:2])) == ["1", "3"]
    assert "5/8" in content
    assert re.search(r"\b8 labelled subsets", content)
    # The two alternative generators have empty intersection; no essential dots may be drawn.
    assert not any(op == b"c" for _, op in page.get_contents().operations)
    caption = analytical_captions(changed)[2]
    assert "2^{" not in caption
    assert "alternative minimal bundles" in caption
    assert re.search(r"\b3 declared field interventions", caption)


def test_more_than_five_valid_failing_cases_refuses_layout(analytical):
    _, report, artwork = analytical
    six = experiment((Intervention.NONCAPTURE,), ((Intervention.NONCAPTURE,),))
    case = six.decisions[0]
    six = six.model_copy(
        update={
            "decisions": tuple(
                case.model_copy(update={"decision_id": f"case-{i}"}) for i in range(6)
            ),
            "total_subsets": 12,
            "total_distinct_states": 12,
            "total_admissible_subsets": 6,
            "baseline_active_checks": 6,
            "baseline_inactive_checks": 0,
            "baseline_failed_checks": 6,
        }
    )
    with pytest.raises(ResearchError, match="figure_case_layout"):
        analytical_drawings(report.model_copy(update={"institutional_experiments": six}), artwork)


def test_four_captions_keep_structured_refs_and_computed_partition_counts(analytical):
    _, report, _ = analytical
    captions = analytical_captions(report)
    assert len(captions) == 4
    assert set(re.findall(r"\[@([\w-]+)", captions[1])) >= {
        "damrosch1980",
        "fallon2015",
        "simpson2007",
    }
    assert "20,480" in captions[2]
    assert "5,120" in captions[2]
    assert "40,960" in captions[2]
    assert "31 distinct" in captions[2]
    assert re.search(r"\b4 primary reading extracts", captions[3])
    assert re.search(r"\b8 Unicode", captions[3])


def test_relation_symbols_use_a_font_with_real_glyphs(analytical):
    root, report, artwork = analytical
    page = render(root / "symbols.pdf", analytical_drawings(report, artwork)["abstract-1"])
    symbols = []

    def collect(text, _cm, _tm, font_dict, _font_size) -> None:
        if any(symbol in text for symbol in ("⊆", "\u00d7")):
            assert font_dict is not None
            symbols.append((text, font_dict["/BaseFont"]))

    content = page.extract_text(visitor_text=collect)
    assert content.count("⊆") == content.count("\u00d7") == 3
    assert symbols
    assert all("DejaVuSerif" in font for _, font in symbols)
    face = pdfmetrics.getFont("BF-Serif").face
    assert all(face.charToGlyph[ord(symbol)] > 0 for symbol in ("⊆", "\u00d7"))


def test_unrepairable_case_preserves_zero_admissions_and_missing_minimum(analytical):
    root, report, artwork = analytical
    changed = report.model_copy(update={"institutional_experiments": experiment((), ())})
    page = render(root / "unrepairable.pdf", analytical_drawings(changed, artwork)["abstract-3"])
    content = page.extract_text()
    assert "0/1" in content
    assert "N/A" in content
    assert "2^{" not in analytical_captions(changed)[2]


@pytest.mark.parametrize("field", ["corpus_statistics", "institutional_experiments"])
def test_missing_analytical_inputs_fail_for_figures_and_captions(analytical, field):
    _, report, artwork = analytical
    changed = report.model_copy(update={field: None})
    with pytest.raises(ResearchError, match="publication_statistics"):
        analytical_drawings(changed, artwork)
    with pytest.raises(ResearchError, match="publication_statistics"):
        analytical_captions(changed)
