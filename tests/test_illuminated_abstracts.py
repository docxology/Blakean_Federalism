# Copyright (c) 2026 Daniel Ari Friedman
"""Real vector/image/font checks and source perturbations for the four illuminated pages."""

from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.analysis_figures import FOCUS
from blakean_federalism.corpus_statistics import analyze_corpus
from blakean_federalism.illuminated_abstracts import illuminated_drawings
from blakean_federalism.illuminated_style import prose
from blakean_federalism.manuscript import ManuscriptSpec
from blakean_federalism.models import ResearchError
from blakean_federalism.report import build_workbench

from .test_corpus_statistics import queries, unit
from .test_dense_figures import unequal_families
from .test_workbench import observed as observations_fixture
from .test_workbench import prepared as workbench_fixture

observed = observations_fixture
prepared = workbench_fixture


@pytest.fixture
def illuminated(prepared):
    root, corpus, result = prepared
    report = build_workbench(root, corpus, result)
    repository = Path(__file__).parents[1]
    spec = ManuscriptSpec.model_validate_json(
        (repository / "research/manuscript-inputs.json").read_bytes()
    )
    report = report.model_copy(
        update={
            "producer_version": "0.13.0",
            "quotations": spec.quotations,
            "corpus_statistics": unequal_families(),
        }
    )
    artwork = {}
    for key in ("J1", "J52", "J55", "J91"):
        path = root / (key + ".png")
        Image.new("RGB", (32, 48), (176, 0, 32)).save(path)
        artwork[key] = path
    pdfmetrics.registerFont(
        TTFont("BF-Vera", str(repository / "src/blakean_federalism/resources/fonts/Vera.ttf"))
    )
    return root, report, artwork


def render(path, drawing):
    canvas = Canvas(str(path), pagesize=(540, 520), invariant=1)
    drawing(canvas)
    canvas.save()
    return PdfReader(path).pages[0]


def test_pages_embed_whole_images_italic_font_and_source_values(illuminated):
    root, report, artwork = illuminated
    drawings = illuminated_drawings(report, artwork)
    assert set(drawings) == {"abstract-1", "abstract-2", "abstract-3", "abstract-4"}
    pages = {key: render(root / (key + ".pdf"), draw) for key, draw in drawings.items()}
    for page in pages.values():
        assert tuple(page.mediabox) == (0, 0, 540, 520)
        assert len(page.images) == 1
        assert page.images[0].image.size == (32, 48)
        assert page.images[0].image.getpixel((0, 0)) == (176, 0, 32)
        fonts = [font.get_object() for font in page["/Resources"]["/Font"].values()]
        italic = next(font for font in fonts if "DejaVuSerif-Italic" in font["/BaseFont"])
        descriptor = italic["/FontDescriptor"]
        assert descriptor["/ItalicAngle"] < 0
        assert descriptor["/FontFile2"].get_data()
    cover = " ".join(pages["abstract-1"].extract_text().split())
    assert "States Change: but Individual Identities never change nor cease:" in cover
    assert "Eternity is in love with the productions of time." in cover
    content = pages["abstract-4"].extract_text()
    # Four unequal extracts: 3 state occurrences / 8 tokens; family mean 2500.
    assert "3750.00 / 2500.00" in content
    assert "2/4 / 1/3" in content
    assert "8 tokens / 3 source families" in content
    assert "25,600/40,960 admissible subsets; 31 distinct records." in content


def test_verse_and_denominator_changes_reach_the_real_pdf(illuminated):
    root, report, artwork = illuminated
    quote = next(q for q in report.quotations if q.quote_id == "Q13")
    changed_quote = quote.model_copy(
        update={
            "segments": (
                quote.segments[0].model_copy(update={"text": "Verified replacement witness."}),
            )
        }
    )
    changed = report.model_copy(
        update={
            "quotations": tuple(
                changed_quote if q.quote_id == "Q13" else q for q in report.quotations
            ),
            "corpus_statistics": analyze_corpus(
                (unit("only", "states nations", "alpha"),), queries(*FOCUS)
            ),
        }
    )
    drawings = illuminated_drawings(changed, artwork)
    content = render(root / "changed-cover.pdf", drawings["abstract-1"]).extract_text()
    assert "Verified replacement witness." in " ".join(content.split())
    assert "Eternity is in love" not in content
    evidence = render(root / "changed-statistics.pdf", drawings["abstract-4"]).extract_text()
    assert "5000.00 / 5000.00" in evidence
    assert "3750.00 / 2500.00" not in evidence
    assert "1/1 / 1/1" in evidence


def test_missing_inputs_are_rejected_before_any_canvas_is_created(illuminated):
    root, report, artwork = illuminated
    with pytest.raises(ResearchError, match="figure_artwork"):
        illuminated_drawings(report, {k: v for k, v in artwork.items() if k != "J1"})
    with pytest.raises(ResearchError, match="figure_artwork"):
        illuminated_drawings(report, {**artwork, "J1": root / "missing.png"})
    for quotes in (
        tuple(q for q in report.quotations if q.quote_id != "Q05"),
        tuple(
            q.model_copy(update={"segments": q.segments[:1]}) if q.quote_id == "Q05" else q
            for q in report.quotations
        ),
    ):
        with pytest.raises(ResearchError, match="figure_quotation"):
            illuminated_drawings(report.model_copy(update={"quotations": quotes}), artwork)
    for field in ("corpus_statistics", "institutional_experiments"):
        with pytest.raises(ResearchError, match="publication_statistics"):
            illuminated_drawings(report.model_copy(update={field: None}), artwork)
    stats = report.corpus_statistics
    with pytest.raises(ResearchError, match="figure_queries"):
        illuminated_drawings(
            report.model_copy(
                update={
                    "corpus_statistics": stats.model_copy(update={"queries": stats.queries[:1]})
                }
            ),
            artwork,
        )
    experiment = report.institutional_experiments
    failed = next(row for row in experiment.decisions if row.baseline_failed_rules)
    with pytest.raises(ResearchError, match="figure_case_layout"):
        illuminated_drawings(
            report.model_copy(
                update={
                    "institutional_experiments": experiment.model_copy(
                        update={"decisions": (failed,) * 6}
                    )
                }
            ),
            artwork,
        )


def test_undefined_measurements_and_unrepairable_cases_remain_explicit(illuminated):
    root, report, artwork = illuminated
    stats = analyze_corpus((unit("zero", "...", "empty"),), queries(*FOCUS))
    experiment = report.institutional_experiments
    first = next(row for row in experiment.decisions if row.baseline_failed_rules)
    changed = report.model_copy(
        update={
            "corpus_statistics": stats,
            "institutional_experiments": experiment.model_copy(
                update={"decisions": (first.model_copy(update={"minimum_cardinality": None}),)}
            ),
        }
    )
    page = render(root / "undefined.pdf", illuminated_drawings(changed, artwork)["abstract-4"])
    content = page.extract_text()
    assert content.count("N/A") == 9
    assert "0 tokens / 1 source families" in content
    canvas = Canvas(str(root / "overflow.pdf"), pagesize=(540, 520))
    with pytest.raises(ResearchError, match="figure_text_overflow"):
        prose(canvas, "Cannot fit this text into a single point", (20, 50, 100, 1))
    canvas.save()
