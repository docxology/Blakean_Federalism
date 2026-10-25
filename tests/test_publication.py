# Copyright (c) 2026 Daniel Ari Friedman
"Real source, archive, process, and rendered-byte controls for the native route."

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas
from typer.testing import CliRunner

from blakean_federalism.cli import app
from blakean_federalism.manuscript import validate_manuscript
from blakean_federalism.models import ResearchError
from blakean_federalism.publication import SOURCE_NAMES, manuscript_variables, prepare_publication
from blakean_federalism.publication_contract import manuscript_contract
from blakean_federalism.publication_figures import generate_figures
from blakean_federalism.publication_models import NativeReceipt, PreparedPublication
from blakean_federalism.publication_verification import (
    NumberedBlocks,
    verify_opening,
    verify_publication,
    verify_references,
)
from blakean_federalism.report import build_workbench
from blakean_federalism.storage import digest

from .test_workbench import observed as observations_fixture
from .test_workbench import prepared as workbench_fixture

observed = observations_fixture
prepared = workbench_fixture

BIB = "@article{a,author={A, Test},title={A real citation},year={2026}}\n"
FORMAL = '::: {.definition #def:trial title="Trial"}\nA typed statement.\n:::\n\n[@def:trial; @a]\n'


def test_per_kind_numbering_and_reference_inventory():
    source = FORMAL + '\n::: {.proposition #prop:one title="Countermodel"}\nProof.\n:::\n'
    source += '\n::: {.definition #def:later title="Later"}\nStatement.\n:::\n'
    result = manuscript_contract(source, BIB)
    assert result.formalism_numbers == {
        "def:trial": "Definition 1",
        "prop:one": "Proposition 1",
        "def:later": "Definition 2",
    }
    assert result.cited_bibliography_keys == ("a",)


@pytest.mark.parametrize(
    "change",
    [
        "no_blocks",
        "duplicate",
        "unlabeled",
        "unclosed",
        "manual",
        "unknown_kind",
        "missing_citation",
        "missing_formalism",
        "missing_equation",
        "duplicate_bib",
        "duplicate_equation",
        "single_dollar",
    ],
)
def test_source_controls_reject_broken_numbering_and_citations(change):
    source, bib = FORMAL, BIB
    if change == "no_blocks":
        source = "Text [@a]."
    if change == "duplicate":
        source += FORMAL
    if change == "unlabeled":
        source += "\n::: {.definition}\nHidden.\n:::\n"
    if change == "unclosed":
        source = source.replace("\n:::\n", "\n")
    if change == "manual":
        source = source.replace('title="Trial"', 'title="Definition 7 Trial"')
    if change == "unknown_kind":
        source = source.replace(".definition", ".invented")
    if change == "missing_citation":
        source += "\n[@absent]\n"
    if change == "missing_formalism":
        source += "\n[@def:absent]\n"
    if change == "missing_equation":
        source += "\n[@eq:absent]\n"
    if change == "duplicate_bib":
        bib += BIB
    if change == "duplicate_equation":
        source += "\n$$x$$ {#eq:x}\n\n$$y$$ {#eq:x}\n"
    if change == "single_dollar":
        source += "\n$\nx\n$ {#eq:x}\n"
    with pytest.raises(ResearchError):
        manuscript_contract(source, bib)


def test_verse_hardbreak_is_syntax_not_a_spelling_normalization(manuscript):
    root, spec = manuscript
    text = "> Persons &\\\n> states\n\n" * 4
    assert validate_manuscript(root, spec, text)
    with pytest.raises(ResearchError, match="manuscript_quotation"):
        validate_manuscript(root, spec, text.replace("states", "sta\\tes", 1))


@pytest.fixture
def publication_source(prepared):
    root, corpus, result = prepared
    original = Path(__file__).parents[1]
    for name in (n for n in SOURCE_NAMES[2:] if n != "research/manuscript-inputs.json"):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    (root / "tools").mkdir()
    shutil.copyfile(original / "tools/template_render.py", root / "tools/template_render.py")
    article = root / "docs/manuscript/states-change.md"
    article.write_text(article.read_text() + "\n" + FORMAL)
    (root / "docs/manuscript/references.bib").write_text(BIB)
    report = build_workbench(root, corpus, result)
    rasterizer = shutil.which("pdftoppm")
    assert rasterizer is not None, "Install the documented Poppler toolchain"
    return root, report, rasterizer


def test_prepared_stage_binds_inputs_and_real_vector_and_png_outputs(publication_source):
    root, report, rasterizer = publication_source
    target = root / "analysis_output/publication"
    prepare_publication(root, target, report, rasterizer)
    receipt = PreparedPublication.model_validate_json(
        (target / "prepared-publication.json").read_bytes()
    )
    assert len(receipt.figures) == 22
    assert all(
        digest(target / "output/figures" / name) == value for name, value in receipt.figures.items()
    )
    assert receipt.variables["SOURCE_UNITS"] == "2"
    assert receipt.variables["CASE_CHECKS"] == "150"
    assert receipt.variables["STATES_PRIMARY_PERCENT"] == "100.0"
    before = (target / "prepared-publication.json").read_bytes()
    with pytest.raises(ResearchError, match="occupied_output"):
        prepare_publication(root, target, report, rasterizer)
    assert (target / "prepared-publication.json").read_bytes() == before


@pytest.mark.parametrize("change", ["outside", "traversal", "symlink", "stale_input"])
def test_preparation_refuses_unsafe_or_stale_input(publication_source, change):
    root, report, rasterizer = publication_source
    target = root / "analysis_output/not-written"
    if change == "outside":
        target = root / "tracked-output"
    if change == "traversal":
        target = root / "analysis_output/../escape"
    if change == "symlink":
        target.symlink_to(root / "elsewhere", target_is_directory=True)
    if change == "stale_input":
        (root / "docs/manuscript/states-change.md").write_text("Changed source")
    with pytest.raises(ResearchError):
        prepare_publication(root, target, report, rasterizer)
    assert not (target / "prepared-publication.json").exists()


def test_rasterizer_failure_is_real_and_cannot_publish_a_complete_stage(publication_source):
    root, report, _ = publication_source
    failing_executable = shutil.which("false")
    assert failing_executable is not None
    target = root / "analysis_output/rasterizer-failure"
    with pytest.raises(subprocess.CalledProcessError, match="non-zero exit status"):
        prepare_publication(root, target, report, failing_executable)
    assert not (target / "prepared-publication.json").exists()


def test_census_rejects_disagreement_and_absent_state_is_not_zero(publication_source):
    _, report, _ = publication_source
    cell = report.coverage[0].model_copy(update={"source_units": 300})
    with pytest.raises(ResearchError, match="publication_census"):
        manuscript_variables(report.model_copy(update={"coverage": (*report.coverage, cell)}))
    with pytest.raises(ResearchError, match="publication_census"):
        manuscript_variables(report.model_copy(update={"source_units": 300}))
    other = tuple(x.model_copy(update={"query_id": "another"}) for x in report.coverage)
    assert (
        manuscript_variables(report.model_copy(update={"coverage": other}))[
            "STATES_PRIMARY_PERCENT"
        ]
        == "N/A"
    )


@pytest.mark.parametrize("change", ["no_cases", "wrong_check_order"])
def test_matrix_rejects_incomplete_or_misaligned_traces(publication_source, change):
    root, report, rasterizer = publication_source
    if change == "no_cases":
        report = report.model_copy(update={"cases": ()})
    else:
        case = report.cases[0]
        wrong = case.assessment.model_copy(
            update={"checks": tuple(reversed(case.assessment.checks))}
        )
        changed = case.model_copy(update={"assessment": wrong})
        report = report.model_copy(update={"cases": (changed, *report.cases[1:])})
    with pytest.raises(ResearchError):
        generate_figures(report, root / change, rasterizer)


def html_fixture():
    return (
        '<div id="def:trial"><strong>Definition 1 (Trial).</strong> A '
        'statement.</div><div id="ref-a">A citation</div><span '
        'id="eq:x">(1)</span>'
    )


@pytest.mark.parametrize(
    "change",
    ["positive", "wrong_number", "duplicate_id", "missing_bib", "missing_equation", "unresolved"],
)
def test_actual_html_reference_controls(change):
    contract = manuscript_contract(FORMAL + "\n$$x$$ {#eq:x}\n", BIB)
    html = html_fixture()
    if change == "wrong_number":
        html = html.replace("Definition 1", "Definition 2")
    if change == "duplicate_id":
        html += '<div id="ref-a">Repeated</div>'
    if change == "missing_bib":
        html = html.replace('id="ref-a"', 'id="ref-b"')
    if change == "missing_equation":
        html = html.replace('id="eq:x"', 'id="eq:absent"')
    if change == "unresolved":
        html += "[?]"
    document = NumberedBlocks()
    document.feed(html)
    if change == "positive":
        verify_references(contract, document, html, "Definition 1")
    else:
        with pytest.raises(ResearchError):
            verify_references(contract, document, html, "Definition 1")


@pytest.mark.parametrize("change", ["positive", "short", "cover", "page_four"])
def test_opening_is_checked_by_physical_page(change):
    pages = [
        "States Change",
        "Graphical abstract 2",
        "Graphical abstract 3",
        "Graphical abstract 4",
        "Body",
    ]
    if change == "short":
        pages = pages[:4]
    if change == "cover":
        pages[0] = "Wrong cover"
    if change == "page_four":
        pages[3] = "Wrong page"
    if change == "positive":
        verify_opening(pages)
    else:
        with pytest.raises(ResearchError):
            verify_opening(pages)


@pytest.fixture
def serialized_editions(publication_source):
    # Synthetic serialization controls, not evidence of a native template execution.
    root, report, rasterizer = publication_source
    stage = root / "analysis_output/serialized-control"
    prepare_publication(root, stage, report, rasterizer)
    pdf = stage / "output/pdf/test.pdf"
    pdf.parent.mkdir()
    canvas = Canvas(str(pdf))
    for text in [
        "States Change",
        "Graphical abstract 2",
        "Graphical abstract 3",
        "Graphical abstract 4",
        "Definition 1 (Trial).",
    ]:
        canvas.drawString(50, 700, text)
        if text.startswith("Definition"):
            for i in range(4):
                canvas.drawString(50, 650 - 25 * i, "Persons & states")
        canvas.showPage()
    canvas.save()
    html = stage / "output/web/index.html"
    html.parent.mkdir()
    html.write_text(html_fixture())
    (pdf.parent / "_combined_manuscript.aux").write_text(r"\bibcite{a}{1}")
    prepared = PreparedPublication.model_validate_json(
        (stage / "prepared-publication.json").read_bytes()
    )
    native = NativeReceipt(
        template_repository=prepared.template.repository,
        template_commit=prepared.template.commit,
        template_sources={"synthetic.py": "0" * 64},
        template_gitlinks={},
        template_sources_unchanged=True,
        runtime={"scope": "Synthetic serialization test only; never native-execution evidence"},
        pdf=pdf.relative_to(stage).as_posix(),
        html=html.relative_to(stage).as_posix(),
        outputs={
            pdf.relative_to(stage).as_posix(): digest(pdf),
            html.relative_to(stage).as_posix(): digest(html),
        },
        resolved_inputs={},
        writer_calls=prepared.template.writers,
        scope="Synthetic control",
    )
    (stage / "native-render-receipt.json").write_text(native.model_dump_json())
    return root, stage, native


@pytest.mark.parametrize(
    "change",
    [
        "positive",
        "source",
        "engine",
        "hydrated_input",
        "figure",
        "output",
        "bibliography",
        "quotation",
    ],
)
def test_complete_verifier_detects_changed_source_and_output(serialized_editions, change):
    root, stage, native = serialized_editions
    if change == "source":
        (root / "docs/manuscript/states-change.md").write_text("Changed")
    if change == "engine":
        native = native.model_copy(update={"template_commit": "f" * 40})
    if change == "hydrated_input":
        native = native.model_copy(
            update={"resolved_inputs": {"manuscript/states-change.md": "0" * 64}}
        )
    if change == "figure":
        (stage / "output/figures/abstract-1.png").write_bytes(b"Changed")
    if change == "output":
        (stage / native.html).write_text("Changed")
    if change == "bibliography":
        (stage / "output/pdf/_combined_manuscript.aux").write_text("")
    if change == "quotation":
        canvas = Canvas(str(stage / native.pdf))
        for text in [
            "States Change",
            "Graphical abstract 2",
            "Graphical abstract 3",
            "Graphical abstract 4",
            "Definition 1 (Trial).",
        ]:
            canvas.drawString(50, 700, text)
            canvas.showPage()
        canvas.save()
        native = native.model_copy(
            update={"outputs": native.outputs | {native.pdf: digest(stage / native.pdf)}}
        )
    (stage / "native-render-receipt.json").write_text(native.model_dump_json())
    if change == "positive":
        assert verify_publication(root, stage)["verified_quotations"] == 4
    else:
        with pytest.raises(ResearchError):
            verify_publication(root, stage)


def test_native_receipt_cannot_collapse_two_editions(serialized_editions):
    _, _, native = serialized_editions
    with pytest.raises(ResearchError, match="native_receipt"):
        NativeReceipt.model_validate(
            native.model_dump() | {"html": native.pdf, "outputs": {native.pdf: "0" * 64}}
        )


def test_cli_retains_failed_real_native_invocation(publication_source, monkeypatch):
    root, _, _ = publication_source
    monkeypatch.chdir(root)
    run = CliRunner().invoke(
        app,
        [
            "render-manuscript",
            "--template-root",
            str(root / "missing-template"),
            "--template-python",
            sys.executable,
            "--output",
            "analysis_output/failed-native",
            "--corpus",
            "local_data/imported",
            "--concordance-file",
            "analysis_output/result.json",
        ],
    )
    assert run.exit_code != 0
    log = root / "analysis_output/failed-native/native-render.log"
    assert log.is_file()
    assert log.stat().st_size > 0
    assert not (log.parent / "native-render-receipt.json").exists()


def test_evidence_abstract_distinguishes_absent_state_query_from_measured_zero(publication_source):
    root, report, rasterizer = publication_source
    other = tuple(x.model_copy(update={"query_id": "another"}) for x in report.coverage)
    absent = report.model_copy(update={"coverage": other})
    generate_figures(absent, root / "absent-state", rasterizer)
    assert (
        "N/A / query absent"
        in PdfReader(root / "absent-state/abstract-4.pdf").pages[0].extract_text()
    )
    zero = tuple(
        x.model_copy(
            update={"occurrences": 0, "matched_source_documents": 0, "coverage_fraction": 0.0}
        )
        for x in report.coverage
    )
    generate_figures(report.model_copy(update={"coverage": zero}), root / "zero-state", rasterizer)
    content = PdfReader(root / "zero-state/abstract-4.pdf").pages[0].extract_text()
    assert "0.0% unit coverage" in content
    assert "0 occurrences" in content
    assert "N/A / query absent" not in content
