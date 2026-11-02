# Copyright (c) 2026 Daniel Ari Friedman
"""Real CLI outputs, exact membership and refusing source/output/process controls."""

import csv
import json
import os
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import assert_never

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.review_timing_inputs import INPUT_NAMES, load_timing_inputs
from blakean_federalism.review_timing_run import publish_timing, verify_timing_output

ROOT = Path(__file__).parents[1]


def copy_inputs(destination: Path) -> Path:
    (destination / "research").mkdir(parents=True)
    for name in INPUT_NAMES:
        shutil.copyfile(ROOT / name, destination / name)
    return destination


def run_cli(root: Path, *, figures: bool = False, environment=None):
    return subprocess.run(  # noqa: S603 -- Real selected Python and test-owned explicit paths.
        [
            sys.executable,
            "-B",
            "-m",
            "tools.audit_review_timing",
            "--root",
            str(root),
            "--output",
            str(root / "analysis_output/timing"),
            *(["--figures"] if figures else []),
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


@pytest.fixture(scope="module")
def produced(tmp_path_factory):
    root = copy_inputs(tmp_path_factory.mktemp("timing-run"))
    result = run_cli(root)
    assert result.returncode == 0, result.stderr
    return root


def test_completed_cli_has_pinned_outputs_and_shared_interval_closure(produced):
    # Given a real completed run, the caller-held receipt verifies exact bytes and producer source.
    output = produced / "analysis_output/timing"
    pin = sha256((output / "atlas-receipt.json").read_bytes()).hexdigest()
    receipt = verify_timing_output(output, pin)
    assert (receipt.configurations, receipt.person_records) == (21454, 42908)
    assert "blake/methods/intervals.py" in receipt.producers
    assert {f.path for f in receipt.inputs} == set(INPUT_NAMES)
    assert receipt.producer_state == "artifacts_complete"


def test_complete_csv_retains_named_people_and_four_unassessed_relations(produced):
    # When the actual CSV is read, every logical cell retains two records and unpooled predicates.
    with (produced / "analysis_output/timing/atlas-claimants.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 42908
    people = {}
    for row in rows:
        people.setdefault(row["configuration_id"], set()).add(row["claimant_id"])
        assert all(
            row[k] == "unassessed"
            for k in ("material_support", "reprisal", "reviewer_control", "collective_reservation")
        )
    assert set(map(frozenset, people.values())) == {frozenset(("member-a", "resident-b"))}
    assert any(row["uncovered_hours"] == "0" and row["filing_ready"] == "0" for row in rows)


def test_occupied_cli_destination_preserves_the_prior_epoch(produced):
    # Given an occupied destination, invoking the actual CLI refuses without changing its receipt.
    receipt = produced / "analysis_output/timing/atlas-receipt.json"
    before = receipt.read_bytes()
    result = run_cli(produced)
    assert result.returncode == 1
    assert "occupied_output" in result.stderr
    assert receipt.read_bytes() == before


def test_wrong_input_pin_refuses_before_output(tmp_path):
    # Given changed case bytes, the real CLI refuses before reserving a run.
    root = copy_inputs(tmp_path / "case")
    with (root / "research/cases.json").open("ab") as stream:
        stream.write(b"\n")
    result = run_cli(root)
    assert result.returncode == 1
    assert "timing_input_hash" in result.stderr
    assert not (root / "analysis_output/timing").exists()


def test_missing_rasterizer_refuses_before_output(tmp_path):
    # Given an unavailable optional executable, requesting figures fails before publication.
    root = copy_inputs(tmp_path / "case")
    result = run_cli(root, figures=True, environment=dict(os.environ, PATH=""))
    assert result.returncode == 1
    assert "timing_rasterizer_missing" in result.stderr
    assert not (root / "analysis_output/timing").exists()


def test_real_failed_raster_child_keeps_partial_epoch_without_completion(tmp_path):
    # Given a real process returning 17, the parent reaps it and refuses analytical completion.
    root = copy_inputs(tmp_path / "case")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    executable = binaries / "pdftoppm"
    executable.write_text(
        f"#!{sys.executable}\n"
        "import sys\nsys.stderr.write('intentional raster failure\\n')\nsys.exit(17)\n"
    )
    executable.chmod(0o700)
    result = run_cli(root, figures=True, environment=dict(os.environ, PATH=str(binaries)))
    output = root / "analysis_output/timing"
    assert result.returncode == 1
    assert not (output / "atlas-receipt.json").exists()
    terminal = json.loads((output / "figures/review-timing-readiness.exit.json").read_text())
    assert terminal == {"returncode": 17, "reaped": True}
    assert (
        output / "figures/review-timing-readiness.stderr.log"
    ).read_text() == "intentional raster failure\n"


@pytest.mark.parametrize(
    "kind", ["extra", "changed-caption", "changed-summary", "wrong-pin", "duplicate-receipt"]
)
def test_output_verifier_refuses_invalid_complete_looking_epochs(produced, tmp_path, kind):
    # Given a copy with one defect, verification rejects actual bytes or semantic membership.
    output = tmp_path / "copy"
    shutil.copytree(produced / "analysis_output/timing", output)
    receipt_path = output / "atlas-receipt.json"
    pin = sha256(receipt_path.read_bytes()).hexdigest()
    match kind:
        case "extra":
            (output / "unreceipted.txt").write_text("extra\n")
        case "changed-caption":
            (output / "captions.json").write_text("{}\n")
        case "changed-summary":
            (output / "atlas-summary.json").write_text("{}\n")
        case "wrong-pin":
            pin = "0" * 64
        case "duplicate-receipt":
            data = json.loads(receipt_path.read_text())
            data["outputs"].append(data["outputs"][0])
            receipt_path.write_text(json.dumps(data) + "\n")
            pin = sha256(receipt_path.read_bytes()).hexdigest()
        case _:
            assert_never(kind)
    with pytest.raises(ResearchError):
        verify_timing_output(output, pin)


def test_output_must_be_private_and_not_symlinked(tmp_path):
    # Given an external destination, no run is created outside the declared private output root.
    root = copy_inputs(tmp_path / "case")
    with pytest.raises(ResearchError, match="timing_private_output"):
        publish_timing(root, tmp_path / "outside")
    (root / "analysis_output").mkdir()
    (root / "analysis_output/timing").symlink_to(
        root / "analysis_output/target", target_is_directory=True
    )
    result = run_cli(root)
    assert result.returncode == 1
    assert "timing_symlink_output" in result.stderr
    assert not (root / "analysis_output/target").exists()


@pytest.mark.parametrize("mutation", ["cross-pin", "missing-anchor", "changed-reference"])
def test_rebound_hashes_do_not_hide_anchor_contradictions(tmp_path, mutation):
    # Given individually valid JSON and updated outer hashes, inner anchor contracts still refuse.
    root = copy_inputs(tmp_path / "case")
    spec_path = root / "research/review-timing-atlas-v1.json"
    pressure_path = root / "research/review-pressure-20261029.json"
    reference_path = root / "research/institutional-review-cases.json"
    spec, pressure, reference = [
        json.loads(p.read_text()) for p in (spec_path, pressure_path, reference_path)
    ]
    match mutation:
        case "cross-pin":
            pressure["reference_study_sha256"] = "0" * 64
        case "missing-anchor":
            pressure["cases"] = [
                p for p in pressure["cases"] if p["procedure"]["procedure_id"] != "P07"
            ]
        case "changed-reference":
            item = next(p for p in reference["procedures"] if p["procedure_id"] == "H12")
            item["claimants"][0]["available_filing_hours"] = 5
            reference_path.write_text(json.dumps(reference) + "\n")
            spec["reference_study_sha256"] = sha256(reference_path.read_bytes()).hexdigest()
            pressure["reference_study_sha256"] = spec["reference_study_sha256"]
        case _:
            assert_never(mutation)
    pressure_path.write_text(json.dumps(pressure) + "\n")
    spec["pressure_study_sha256"] = sha256(pressure_path.read_bytes()).hexdigest()
    spec_path.write_text(json.dumps(spec) + "\n")
    with pytest.raises(ResearchError):
        load_timing_inputs(root)


def test_a_partial_epoch_cannot_supply_a_completion_receipt(tmp_path):
    # Given a partial output, verification fails on the absent final marker.
    output = tmp_path / "partial"
    output.mkdir()
    (output / "atlas-summary.json").write_text("{}\n")
    with pytest.raises(ResearchError, match="missing_regular_file"):
        verify_timing_output(output, "0" * 64)
