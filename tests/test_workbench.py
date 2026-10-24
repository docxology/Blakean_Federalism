# Copyright (c) 2026 Daniel Ari Friedman
"""Real projection and report controls; no mocked I/O or derived political score."""

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter
from typer.testing import CliRunner

from blakean_federalism.cli import app
from blakean_federalism.corpus import concordance, import_corpus, load_import
from blakean_federalism.institutions import assess
from blakean_federalism.models import Decision, QuerySpec, ResearchError
from blakean_federalism.observations import CoverageCell, reconcile_coverage
from blakean_federalism.report import build_workbench, html_document, publish_workbench
from blakean_federalism.workbench_models import CaseTrace


@pytest.fixture
def observed(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    queries = (QuerySpec(query_id="states", variants=("state", "states"), note="Test"),)
    result = concordance(dest, queries, pin)
    _, passages = load_import(dest, pin)
    return result, passages, queries, pin, dest


def test_joint_denominators_and_structural_empty_cells(observed):
    result, passages, queries, pin, _ = observed
    cells = reconcile_coverage(result, passages, queries, pin)
    primary = next(c for c in cells if c.role.value == "primary" and c.plane.value == "reading")
    assert (primary.occurrences, primary.matched_source_documents, primary.source_units) == (
        3,
        1,
        1,
    )
    assert primary.coverage_fraction == 1
    assert len([c for c in cells if c.coverage_fraction is None]) == 7


@pytest.mark.parametrize(
    "change",
    [
        "empty_units",
        "duplicate_units",
        "empty_queries",
        "duplicate_queries",
        "scanned",
        "pin",
        "query_hash",
        "missing_cell",
        "duplicate_cell",
        "aggregate",
        "duplicate_hit",
        "unknown_hit",
    ],
)
def test_reconciliation_rejects_inconsistent_membership_and_counts(observed, change):
    result, passages, queries, pin, _ = observed
    if change == "empty_units":
        passages = ()
    if change == "duplicate_units":
        passages = passages + passages[:1]
    if change == "empty_queries":
        queries = ()
    if change == "duplicate_queries":
        queries = queries + queries
    if change == "scanned":
        result = result.model_copy(update={"scanned_source_documents": 3})
    if change == "pin":
        pin = pin.model_copy(update={"upstream_commit": "other"})
    if change == "query_hash":
        result = result.model_copy(update={"query_sha256": "0" * 64})
    if change == "missing_cell":
        result = result.model_copy(update={"rows": result.rows[1:]})
    if change == "duplicate_cell":
        result = result.model_copy(update={"rows": result.rows + result.rows[:1]})
    if change == "aggregate":
        result = result.model_copy(
            update={
                "rows": (result.rows[0].model_copy(update={"occurrences": 99}), *result.rows[1:])
            }
        )
    if change == "duplicate_hit":
        result = result.model_copy(update={"hits": result.hits + result.hits[:1]})
    if change == "unknown_hit":
        result = result.model_copy(
            update={
                "hits": (
                    result.hits[0].model_copy(update={"passage_id": "absent"}),
                    *result.hits[1:],
                )
            }
        )
    with pytest.raises(ResearchError):
        reconcile_coverage(result, passages, queries, pin)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("start", -1),
        ("end", 999),
        ("text_sha256", "0" * 64),
        ("expression", "wrong"),
        ("context", "wrong"),
        ("plane", "xml"),
        ("role", "unverified"),
        ("work_id", "wrong"),
        ("title", "wrong"),
        ("edition_id", "wrong"),
        ("locator", "wrong"),
        ("source_url", "https://other.test"),
        ("query_id", "absent"),
    ],
)
def test_every_hit_binding_is_checked(observed, field, value):
    result, passages, queries, pin, _ = observed
    hit = result.hits[0].model_copy(update={field: value})
    changed = result.model_copy(update={"hits": (hit, *result.hits[1:])})
    with pytest.raises(ResearchError):
        reconcile_coverage(changed, passages, queries, pin)


@pytest.mark.parametrize(
    ("matched", "units", "occurrences", "fraction"),
    [(2, 1, 2, 1), (1, 1, 0, 1), (0, 0, 1, None), (0, 1, 0, None), (0, 0, 0, 0)],
)
def test_invalid_coverage_is_not_serialized(matched, units, occurrences, fraction):
    with pytest.raises(ResearchError):
        CoverageCell(
            query_id="x",
            plane="reading",
            role="primary",
            occurrences=occurrences,
            matched_source_documents=matched,
            source_units=units,
            coverage_fraction=fraction,
        )


@pytest.fixture
def prepared(manuscript, observed):
    root, _ = manuscript
    result, _, queries, pin, corpus = observed
    cases = Path("research/cases.json").read_text()
    (root / "research/cases.json").write_text(cases)
    (root / "research/corpus-pin.json").write_text(pin.model_dump_json())
    (root / "research/queries.json").write_bytes(
        TypeAdapter(tuple[QuerySpec, ...]).dump_json(queries)
    )
    (root / "research/scholarship-reading-0.3.0.json").write_text(
        json.dumps(
            [
                dict(
                    source="</script><script>throw 1</script>@@DATA@@",
                    reading_status="Partial",
                    locator="p1",
                )
            ]
        )
    )
    target = root / "local_data/imported"
    target.parent.mkdir()
    corpus.rename(target)
    result_path = root / "analysis_output/result.json"
    result_path.parent.mkdir()
    result_path.write_text(result.model_dump_json())
    return root, target, result_path


def test_report_is_static_escaped_and_binds_real_inputs(prepared, monkeypatch):
    root, corpus, result = prepared
    monkeypatch.chdir(root)
    report = build_workbench(root, corpus, result)
    html = html_document(report)
    assert "<script>throw 1</script>" not in html
    assert "&lt;/script&gt;" in html
    assert r"\u003c/script\u003e" in html
    assert html.count("<tr data-query=") == 9
    assert html.count('class="check"') == 150
    assert "N/A — no source units" in html
    assert "default-src" in html
    assert "font-src data:" in html
    assert all(not Path(item.path).is_absolute() for item in report.inputs)
    target = publish_workbench(report, root / "analysis_output/portable")
    assert target.is_file()
    assert json.loads((target.parent / "workbench-data.json").read_text())["source_units"] == 2
    with pytest.raises(FileExistsError):
        publish_workbench(report, target.parent)
    assert target.read_text() == html


def test_report_cli(prepared, monkeypatch):
    root, corpus, result = prepared
    monkeypatch.chdir(root)
    run = CliRunner().invoke(
        app,
        [
            "build-workbench",
            "--corpus",
            str(corpus),
            "--concordance-file",
            str(result),
            "--output",
            "analysis_output/cli",
        ],
    )
    assert run.exit_code == 0, run.output
    assert (root / "analysis_output/cli/research-workbench.html").is_file()


@pytest.mark.parametrize("kind", ["outside", "traversal", "symlink"])
def test_report_destination_boundaries(prepared, monkeypatch, kind):
    root, corpus, result = prepared
    monkeypatch.chdir(root)
    report = build_workbench(root, corpus, result)
    dest = root / "outside"
    if kind == "traversal":
        dest = root / "analysis_output/../outside"
    if kind == "symlink":
        dest = root / "analysis_output/link"
        dest.symlink_to(root, target_is_directory=True)
    with pytest.raises(ResearchError, match="report_output"):
        publish_workbench(report, dest)


def test_duplicate_decisions_are_rejected(prepared):
    root, corpus, result = prepared
    path = root / "research/cases.json"
    entries = json.loads(path.read_text())
    path.write_text(json.dumps(entries + entries[:1]))
    with pytest.raises(ResearchError, match="report_cases"):
        build_workbench(root, corpus, result)


def test_stale_case_trace_is_rejected():
    records = TypeAdapter(tuple[Decision, ...]).validate_json(
        Path("research/cases.json").read_bytes()
    )
    record = records[0]
    with pytest.raises(ResearchError, match="report_trace"):
        CaseTrace(
            record=record, assessment=assess(records[1]), poetic_label_ablation_invariant=True
        )
    with pytest.raises(ResearchError, match="report_trace"):
        CaseTrace(record=record, assessment=assess(record), poetic_label_ablation_invariant=False)


def test_reading_links_and_hashes_are_retained(prepared):
    root, corpus, result = prepared
    path = root / "research/scholarship-reading-0.3.0.json"
    path.write_text(
        json.dumps(
            [
                dict(
                    source="Reading",
                    reading_status="Selected",
                    url="https://example.test/paper",
                    sha256="a" * 64,
                )
            ]
        )
    )
    report = build_workbench(root, corpus, result)
    html = html_document(report)
    assert "https://example.test/paper" in html
    assert "a" * 64 in html
    path.write_text(
        json.dumps([dict(source="Reading", reading_status="Unread", url="javascript:alert(1)")])
    )
    report = build_workbench(root, corpus, result)
    with pytest.raises(ResearchError, match="source_url"):
        html_document(report)
