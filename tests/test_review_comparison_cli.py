# Copyright (c) 2026 Daniel Ari Friedman
"""Real CLI exports, input rejection and native figure producer integration."""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from blakean_federalism.review_comparison import ReviewComparison
from blakean_federalism.review_comparison_run import ComparisonReceipt, publish_comparison
from blakean_federalism.storage import digest

ROOT = Path(__file__).parents[1]


@pytest.fixture
def inputs(tmp_path):
    # Given real independent copies, all destructive controls touch test-owned bytes only.
    cases, decisions = tmp_path / "cases.json", tmp_path / "decisions.json"
    cases.write_bytes((ROOT / "research/institutional-review-cases.json").read_bytes())
    decisions.write_bytes((ROOT / "research/cases.json").read_bytes())
    return cases, decisions, tmp_path / "analysis_output" / "run"


def invoke(inputs, *, figures=False, empty_path=False):
    cases, decisions, output = inputs
    environment = dict(os.environ)
    if empty_path:
        environment["PATH"] = ""
    return subprocess.run(  # noqa: S603 -- Actual package CLI, explicit test-owned paths.
        [
            sys.executable,
            "-m",
            "blakean_federalism.cli",
            "compare-review",
            "--cases",
            str(cases),
            "--decisions",
            str(decisions),
            "--output",
            str(output),
            *(["--figures"] if figures else []),
        ],
        cwd=cases.parent,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def test_real_cli_exports_deterministic_source_bound_requirements(inputs):
    # Given the fixed sources, when the command runs, then inspect actual JSON and both CSVs.
    result = invoke(inputs)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    cases, decisions, output = inputs
    report = ReviewComparison.model_validate_json((output / "comparison.json").read_bytes())
    receipt = ComparisonReceipt.model_validate_json(
        (output / "comparison-receipt.json").read_bytes()
    )
    assert receipt.review_cases_sha256 == digest(cases)
    assert receipt.baseline_decisions_sha256 == digest(decisions)
    assert all(a.admissible_under_proposed_rules for a in receipt.linked_baseline_assessments)
    assert set(receipt.producers) >= {
        "blake/methods/storage.py",
        "blakean_federalism/institutions.py",
    }
    for entry in receipt.outputs:
        assert digest(output / entry.path) == entry.sha256
    with (output / "claimant-requirements.csv").open() as stream:
        people = tuple(csv.DictReader(stream))
    with (output / "procedure-comparisons.csv").open() as stream:
        pairs = tuple(csv.DictReader(stream))
    assert len(people) == 28
    assert len(pairs) == 91
    resident = next(
        p for p in people if (p["procedure_id"], p["claimant_id"]) == ("H14", "resident-b")
    )
    assert (resident["filing_opens_hour"], resident["uncovered_intervals"]) == ("14", "[12,14)")
    # Independent replay to a fresh epoch must retain identical measurement and receipt bytes.
    second = output.with_name("second")
    publish_comparison(cases, decisions, second)
    assert {p.name: p.read_bytes() for p in output.iterdir()} == {
        p.name: p.read_bytes() for p in second.iterdir()
    }
    assert report.review.study.baseline_decisions_sha256 == digest(decisions)


@pytest.mark.parametrize(
    ("failure", "code"),
    [
        ("hash", "baseline_hash_mismatch"),
        ("empty", "too_short"),
        ("invalid", "int_type"),
        ("duties", "review_comparison_duties"),
        ("outside", "private_output_required"),
        ("occupied", "occupied_output"),
        ("symlink", "symlink_output"),
        ("source_link", "symlink_input"),
    ],
)
def test_real_cli_rejects_invalid_or_occupied_work_before_publication(inputs, failure, code):
    # Given invalid inputs or occupied destinations, when invoked, publish no completion marker.
    cases, decisions, output = inputs
    data = json.loads(cases.read_bytes())
    match failure:
        case "hash":
            data["baseline_decisions_sha256"] = "0" * 64
        case "empty":
            data["procedures"] = []
        case "invalid":
            data["procedures"][0]["response_hour"] = True
        case "duties":
            data["procedures"][1]["claimants"][1]["consequence_hour"] = 13
        case "outside":
            output = cases.parent / "outside"
        case "occupied":
            output.mkdir(parents=True)
            (output / "keep").write_bytes(b"original\x00")
        case "symlink":
            output.parent.mkdir()
            output.symlink_to(cases.parent / "absent", target_is_directory=True)
        case "source_link":
            link = cases.with_name("linked.json")
            link.symlink_to(cases)
    cases.write_text(json.dumps(data), encoding="utf-8")
    if failure == "source_link":
        cases = cases.with_name("linked.json")
    result = invoke((cases, decisions, output))
    assert result.returncode != 0
    assert code in result.stderr
    assert result.stdout == ""
    assert not (output / "comparison-receipt.json").exists()
    if failure == "occupied":
        assert (output / "keep").read_bytes() == b"original\x00"


def test_optional_native_rasterizer_rejection_leaves_no_output(inputs):
    # Given no native executable on PATH, when figures are requested, fail before mkdir.
    result = invoke(inputs, figures=True, empty_path=True)
    assert result.returncode != 0
    assert "pdftoppm_missing" in result.stderr
    assert not inputs[2].exists()


def test_small_valid_study_rejects_only_the_fixed_publication_layout(inputs):
    # Given a smaller valid study, when fixed figures are requested, retain a useful failure.
    data = json.loads(inputs[0].read_bytes())
    data["procedures"] = data["procedures"][:1]
    data["timeline_selections"] = []
    inputs[0].write_text(json.dumps(data), encoding="utf-8")
    result = invoke(inputs, figures=True)
    assert result.returncode != 0
    assert "comparison_figure_layout" in result.stderr
    assert not inputs[2].exists()


def test_real_figures_bind_exact_person_labels_and_pair_counts(inputs):
    # Given all fixed procedures, when generated, inspect both vector masters and PNG derivatives.
    result = invoke(inputs, figures=True)
    assert result.returncode == 0, result.stderr
    output = inputs[2]
    receipt = ComparisonReceipt.model_validate_json(
        (output / "comparison-receipt.json").read_bytes()
    )
    figures = [entry for entry in receipt.outputs if entry.path.startswith("figures/")]
    assert len(figures) == 4
    for entry in figures:
        path = output / entry.path
        assert digest(path) == entry.sha256
        if path.suffix == ".png":
            with Image.open(path) as image:
                image.load()
                assert max(image.size) == 2400
        else:
            pdf = PdfReader(path)
            assert len(pdf.pages) == 1
            assert "/XObject" not in pdf.pages[0]["/Resources"]
    requirements = PdfReader(output / "figures/review-requirements.pdf").pages[0].extract_text()
    assert "[12,13)" in requirements
    assert "[19,20)" in requirements
    assert "member-a" in requirements
    assert "resident-b" in requirements


def test_input_change_during_real_export_retains_partial_run_without_receipt(inputs):
    # Given a real file mutation triggered on output IO, when export finishes, custody rejects it.
    cases, decisions, output = inputs
    source = f"""
import sys
from pathlib import Path
from blakean_federalism.review_comparison_run import publish_comparison
def mutation(event, args):
    if event == "os.link" and str(args[1]) == "comparison.json":
        Path({str(cases)!r}).write_bytes(b"changed during publication")
sys.addaudithook(mutation)
publish_comparison(Path({str(cases)!r}), Path({str(decisions)!r}), Path({str(output)!r}))
"""
    result = subprocess.run(  # noqa: S603 -- Real isolated process and test-owned input mutation.
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "review_comparison_source_changed" in result.stderr
    assert (output / "comparison.json").exists()
    assert not (output / "comparison-receipt.json").exists()
