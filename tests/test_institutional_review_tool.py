# Copyright (c) 2026 Daniel Ari Friedman
"""Real subprocess audits preserve inputs and refuse invalid publication destinations."""

import json
import os
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import pytest
from PIL import Image
from pydantic import TypeAdapter
from pypdf import PdfReader

from blakean_federalism.institutional_review_models import ReviewStudy
from blakean_federalism.models import Decision
from tools.audit_institutional_review import ReviewAuditReceipt

ROOT = Path(__file__).parents[1]


@pytest.fixture
def inputs(tmp_path):
    cases = tmp_path / "review.json"
    decisions = tmp_path / "decisions.json"
    cases.write_bytes((ROOT / "research/institutional-review-cases.json").read_bytes())
    decisions.write_bytes((ROOT / "research/cases.json").read_bytes())
    return cases, decisions, tmp_path / "output"


def invoke(inputs, *, figures=False, empty_path=False):
    cases, decisions, output = inputs
    options = ["--figures"] if figures else []
    child_environment = dict(os.environ)
    if empty_path:
        child_environment["PATH"] = ""
    return subprocess.run(  # noqa: S603 - Fixed Python module; paths are test-owned inputs.
        [
            sys.executable,
            "-m",
            "tools.audit_institutional_review",
            "--cases",
            str(cases),
            "--decisions",
            str(decisions),
            "--output",
            str(output),
            *options,
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        env=child_environment,
    )


def test_missing_rasterizer_fails_before_creating_output(inputs):
    result = invoke(inputs, figures=True, empty_path=True)
    assert result.returncode == 1
    assert "pdftoppm_missing" in result.stderr
    assert not inputs[2].exists()


def test_real_command_emits_hash_bound_domain_report_without_figures(inputs):
    # Given the complete stipulated study, when the real CLI runs, then retain its predicates.
    cases, decisions, output = inputs
    result = invoke(inputs)
    assert result.returncode == 0, result.stderr
    assert "Audited 14 procedures" in result.stdout
    assert result.stderr == ""
    receipt = ReviewAuditReceipt.model_validate_json((output / "review-receipt.json").read_bytes())
    report_bytes = (output / "review-report.json").read_bytes()
    report = json.loads(report_bytes)
    assert receipt.review_cases_sha256 == sha256(cases.read_bytes()).hexdigest()
    assert receipt.baseline_decisions_sha256 == sha256(decisions.read_bytes()).hexdigest()
    assert receipt.review_report_sha256 == sha256(report_bytes).hexdigest()
    assert receipt.procedure_count == len(report["results"]) == 14
    assert receipt.claimant_count == 28
    assert receipt.declared_conditions_hold_count == 4
    assert receipt.unassessed_issue_count == 2
    assert receipt.claimant_count == sum(len(r["claimants"]) for r in report["results"])
    assert receipt.declared_conditions_hold_count == sum(
        r["declared_conditions_hold"] for r in report["results"]
    )
    assert all(a.admissible_under_proposed_rules for a in receipt.linked_baseline_assessments)
    assert {a.decision_id for a in receipt.linked_baseline_assessments} == {"E-bounded"}
    assert receipt.figures == ()
    assert {p.name for p in output.iterdir()} == {
        "review-report.json",
        "review-receipt.json",
        "review-producer-receipt.json",
    }
    assert all("conditions" in r for r in report["results"])
    assert all("uncovered_wait_hours" in p for r in report["results"] for p in r["claimants"])
    assert {
        r["procedure"]["procedure_id"] for r in report["results"] if r["declared_conditions_hold"]
    } == {"H01", "H05", "H12", "H13"}
    residents = {
        row["procedure"]["procedure_id"]: next(
            person for person in row["claimants"] if person["claimant_id"] == "resident-b"
        )
        for row in report["results"]
    }
    assert {
        identifier: residents[identifier]["uncovered_wait_hours"]
        for identifier in ("H04", "H06", "H07", "H14")
    } == {"H04": 8, "H06": 1, "H07": 1, "H14": 2}


def test_real_figure_command_renders_report_labels_and_exact_gaps(inputs):
    # Given the real curated matrix and selections, when rendered, then read both native formats.
    result = invoke(inputs, figures=True)
    assert result.returncode == 0, result.stderr
    output = inputs[2]
    receipt = ReviewAuditReceipt.model_validate_json((output / "review-receipt.json").read_bytes())
    report = json.loads((output / "review-report.json").read_bytes())
    assert len(receipt.figures) == 4
    assert sum(figure.relative_path.endswith(".pdf") for figure in receipt.figures) == 2
    assert sum(figure.relative_path.endswith(".png") for figure in receipt.figures) == 2
    for figure in receipt.figures:
        path = output / figure.relative_path
        assert sha256(path.read_bytes()).hexdigest() == figure.sha256
        if path.suffix == ".png":
            with Image.open(path) as image:
                image.load()
                assert max(image.size) == 2400
        else:
            reader = PdfReader(path)
            assert len(reader.pages) == 1
            assert "/XObject" not in reader.pages[0]["/Resources"]
    matrix = PdfReader(output / "figures/institutional-review.pdf").pages[0].extract_text()
    timeline = " ".join(
        PdfReader(output / "figures/review-continuity.pdf").pages[0].extract_text().split()
    )
    for row in report["results"]:
        assert row["procedure"]["procedure_id"] in matrix
        assert row["procedure"]["label"] in matrix
    by_procedure = {row["procedure"]["procedure_id"]: row for row in report["results"]}
    selections = report["study"]["timeline_selections"]
    for index, selection in enumerate(selections):
        row = by_procedure[selection["procedure_id"]]
        person = next(p for p in row["claimants"] if p["claimant_id"] == selection["claimant_id"])
        label = f"{selection['procedure_id']} {row['procedure']['label']}"
        start = timeline.index(label)
        end = (
            timeline.index(selections[index + 1]["procedure_id"])
            if index + 1 < len(selections)
            else len(timeline)
        )
        assert f"{person['uncovered_wait_hours']} h uncovered" in timeline[start:end]


@pytest.mark.parametrize(
    ("failure", "code"),
    [
        ("hash", "baseline_hash_mismatch"),
        ("missing", "missing_baseline_decision"),
        ("inadmissible", "inadmissible_baseline_decision"),
        ("duplicate", "duplicate_baseline_decision"),
        ("malformed", "review_audit_failed"),
    ],
)
def test_invalid_inputs_fail_before_creating_output(inputs, failure, code):
    # Given mismatched or invalid baseline links, when invoked, then publish no partial audit.
    cases, decisions, output = inputs
    study = ReviewStudy.model_validate_json(cases.read_bytes())
    data = study.model_dump(mode="json")
    baseline = TypeAdapter(tuple[Decision, ...]).validate_json(decisions.read_bytes())
    match failure:
        case "hash":
            data["baseline_decisions_sha256"] = "0" * 64
        case "missing":
            data["procedures"][0]["baseline_decision_id"] = "absent"
        case "inadmissible":
            data["procedures"][0]["baseline_decision_id"] = "E-capture"
        case "duplicate":
            decisions.write_bytes(
                TypeAdapter(tuple[Decision, ...]).dump_json((*baseline, baseline[0]))
            )
            data["baseline_decisions_sha256"] = sha256(decisions.read_bytes()).hexdigest()
        case "malformed":
            data["procedures"][0]["claimants"][0]["available_filing_hours"] = True
    cases.write_text(json.dumps(data), encoding="utf-8")
    result = invoke(inputs)
    assert result.returncode != 0
    assert code in result.stderr
    assert result.stdout == ""
    assert not output.exists()


def test_occupied_output_preserves_every_existing_byte(inputs):
    # Given an occupied directory, when invoked, then refuse it without touching the occupant.
    output = inputs[2]
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_bytes(b"original bytes\x00")
    result = invoke(inputs)
    assert result.returncode != 0
    assert "occupied_output" in result.stderr
    assert sentinel.read_bytes() == b"original bytes\x00"
    assert tuple(output.iterdir()) == (sentinel,)


def test_missing_baseline_file_creates_no_output(inputs):
    # Given a missing decisions file, when invoked, then retain a stable command failure.
    cases, decisions, output = inputs
    result = invoke((cases, decisions.with_name("absent.json"), output))
    assert result.returncode != 0
    assert "review_audit_failed" in result.stderr
    assert not output.exists()


def test_input_nested_under_new_output_is_rejected(inputs):
    # Given an input path below the new destination, when invoked, then reject before mkdir.
    _, decisions, output = inputs
    result = invoke((output / "review.json", decisions, output))
    assert result.returncode != 0
    assert "input_inside_output" in result.stderr
    assert not output.exists()


def test_figure_layout_rejection_creates_no_partial_output(inputs):
    # Given a valid but unsupported layout, when figures are requested, then reject before mkdir.
    cases, _, output = inputs
    data = ReviewStudy.model_validate_json(cases.read_bytes()).model_dump(mode="json")
    data["procedures"] = data["procedures"][:1]
    data["timeline_selections"] = []
    cases.write_text(ReviewStudy.model_validate(data).model_dump_json(), encoding="utf-8")
    result = invoke(inputs, figures=True)
    assert result.returncode != 0
    assert "review_figure_requires_fixed_14_by_7_study" in result.stderr
    assert not output.exists()
