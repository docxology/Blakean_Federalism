# Copyright (c) 2026 Daniel Ari Friedman
"""Rendered-PDF oracles for new density encodings, including changed and missing inputs."""

import shutil
from functools import partial
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.analysis_figures import FOCUS, cooccurrence, rates, repairs, sensitivity
from blakean_federalism.corpus_statistics import analyze_corpus
from blakean_federalism.proximity_figure import draw_proximity_study
from blakean_federalism.proximity_study import ProximityStudy
from blakean_federalism.publication_body import draw_rule_matrix
from blakean_federalism.publication_figures import generate_figures

from .test_corpus_statistics import queries, unit
from .test_illuminated_abstracts import illuminated as illuminated_fixture
from .test_illuminated_abstracts import observed as observations_fixture
from .test_illuminated_abstracts import prepared as prepared_fixture

illuminated = illuminated_fixture
observed = observations_fixture
prepared = prepared_fixture


def pdf_page(tmp_path, name, draw):
    font = Path(__file__).parents[1] / "src/blakean_federalism/resources/fonts/Vera.ttf"
    pdfmetrics.registerFont(TTFont("BF-Vera", str(font)))
    path = tmp_path / (name + ".pdf")
    canvas = Canvas(str(path), pagesize=(540, 445), invariant=1)
    draw(canvas)
    canvas.save()
    return PdfReader(path).pages[0]


def test_identical_text_changes_exact_denominator_but_not_pooled(tmp_path):
    stats = analyze_corpus(
        (
            unit("a", "states", "alpha"),
            unit("b", "states", "alpha"),
            unit("c", "unrelated unrelated", "beta"),
        ),
        queries(*FOCUS),
    )
    content = pdf_page(tmp_path, "duplicate-rates", partial(rates, stats=stats)).extract_text()
    assert "Pooled denominator: 4 tokens / 3 units" in content
    assert "Exact-text denominator: 3 tokens / 2 units" in content
    assert "3333.33" in content
    assert "5000.00 / 5000.00" in content
    empty = analyze_corpus((unit("empty", "", "alpha"),), queries(*FOCUS))
    missing = pdf_page(tmp_path, "undefined-rates", partial(rates, stats=empty)).extract_text()
    assert "N/A / N/A" in missing
    assert "0 occurrences" in missing
    deletion = pdf_page(
        tmp_path, "undefined-delete", partial(sensitivity, stats=empty)
    ).extract_text()
    assert "N/A: no defined deletion rate" in deletion


def test_family_identity_margins_and_concentration_follow_changed_sources(tmp_path):
    stats = analyze_corpus(
        (unit("a", "liberty particulars", "alpha"), unit("b", "liberty liberty", "beta")),
        queries(*FOCUS),
    )
    overlap = pdf_page(
        tmp_path, "family-overlap", partial(cooccurrence, stats=stats)
    ).extract_text()
    assert "liberty 2/2" in overlap
    assert "particulars 1/2" in overlap
    assert "1 shared / 2 either: alpha" in overlap
    concentration = pdf_page(
        tmp_path, "concentration", partial(sensitivity, stats=stats)
    ).extract_text()
    assert "beta" in concentration
    assert "2/3 (67%)" in concentration


def test_saved_cardinality_profile_changes_real_vector_bar(illuminated, tmp_path):
    _, report, _ = illuminated
    experiment = report.institutional_experiments
    row = next(d for d in experiment.decisions if d.baseline_failed_rules)
    admitted = list(row.admissible_by_size)
    admitted[0] = row.subsets_by_size[0]
    changed = experiment.model_copy(
        update={
            "decisions": tuple(
                d.model_copy(update={"admissible_by_size": tuple(admitted)}) if d == row else d
                for d in experiment.decisions
            )
        }
    )
    first = pdf_page(tmp_path, "repair-profile", partial(repairs, report=report))
    other = pdf_page(
        tmp_path,
        "repair-profile-perturbed",
        partial(repairs, report=report.model_copy(update={"institutional_experiments": changed})),
    )

    def filled_bars(page) -> int:
        return sum(
            operator == b"re" and tuple(args[-2:]) == (14, 20)
            for args, operator in page.get_contents().operations
        )

    assert filled_bars(other) == filled_bars(first) + 1
    assert "Distinct resulting records include admissible and inadmissible" in first.extract_text()
    assert str(experiment.total_distinct_states) in first.extract_text()


def test_active_fraction_and_record_reconciliation_are_rendered(illuminated, tmp_path):
    _, report, _ = illuminated
    content = pdf_page(
        tmp_path, "active-matrix", partial(draw_rule_matrix, report=report)
    ).extract_text()
    assert "1/2" in content
    assert "Satisfied / violated / absent" in content
    assert "condition absent" in content


def test_proximity_families_are_independent_of_units_and_hits(tmp_path):
    path = Path(__file__).parents[1] / "research/proximity-study-0.10.0.json"
    study = ProximityStudy.model_validate_json(path.read_bytes())
    first = pdf_page(
        tmp_path, "proximity", partial(draw_proximity_study, study=study)
    ).extract_text()
    assert "6 | 2" in first
    assert "(38)" in first
    changed = study.model_copy(
        update={
            "rows": (
                study.rows[0].model_copy(
                    update={
                        "matched_source_units": 7,
                        "matched_source_families": 3,
                        "total_occurrences": 19,
                    }
                ),
                *study.rows[1:],
            )
        }
    )
    other = pdf_page(
        tmp_path, "proximity-perturbed", partial(draw_proximity_study, study=changed)
    ).extract_text()
    assert "7 | 3" in other
    assert "(19)" in other
    assert "7 | 3" not in first


def test_concept_registration_requires_current_version_and_artwork(illuminated, tmp_path):
    _, report, artwork = illuminated
    rasterizer = shutil.which("pdftoppm")
    assert rasterizer is not None
    for name, version, art, expected in (
        ("legacy", "0.11.0", artwork, False),
        ("no-art", "0.12.0", None, False),
        ("prior", "0.12.0", artwork, True),
        ("prior13", "0.13.0", artwork, True),
        ("current", "0.14.0", artwork, True),
    ):
        output = tmp_path / name
        figures = generate_figures(
            report.model_copy(update={"producer_version": version}), output, rasterizer, artwork=art
        )
        assert ("federated-inference-authority" in figures) is expected
        assert (output / "federated-inference-authority.png").exists() is expected
        if expected:
            page = PdfReader(output / "federated-inference-authority.pdf").pages[0]
            assert tuple(page.mediabox) == (0, 0, 540, 445)
            assert "must not erase a person's standing" in page.extract_text()
