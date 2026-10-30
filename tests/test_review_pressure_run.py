# Copyright (c) 2026 Daniel Ari Friedman
"""Real files, CLI execution, figure output and refusing publication controls."""

import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.pressure_publication import prepare_pressure_figure
from blakean_federalism.review_pressure_figure import render_pressure_figure
from blakean_federalism.review_pressure_run import DECISIONS, REFERENCE, STUDY, publish_pressure

ROOT = Path(__file__).parents[1]


@pytest.fixture
def source_root(tmp_path):
    for name in (STUDY, REFERENCE, DECISIONS):
        target = tmp_path / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


def test_real_export_receipt_binds_all_claimants_and_producer_bytes(source_root):
    # Given three exact immutable study inputs.
    before = {name: (source_root / name).read_bytes() for name in (STUDY, REFERENCE, DECISIONS)}
    output = source_root / "analysis_output/plain"
    # When publishing the analytical epoch.
    result = publish_pressure(source_root, output)
    # Then JSON/CSV preserve every individual and the receipt binds the real payload bytes.
    parsed = json.loads((output / "pressure-report.json").read_bytes())
    rows = list(csv.DictReader(io.StringIO((output / "pressure-claimants.csv").read_text())))
    assert len(rows) == 16
    assert len(result.results) == 8
    pairs = {
        (item["case"]["procedure"]["procedure_id"], person["claimant_id"])
        for item in parsed["results"]
        for person in item["review"]["claimants"]
    }
    assert pairs == {
        (f"P{index:02}", claimant)
        for index in range(1, 9)
        for claimant in ("member-a", "resident-b")
    }
    assert pairs == {(row["procedure_id"], row["claimant_id"]) for row in rows}
    assert sum(item["review"]["declared_conditions_hold"] for item in parsed["results"]) == 4
    resident = {row["procedure_id"]: row for row in rows if row["claimant_id"] == "resident-b"}
    assert [int(resident[key]["uncovered_wait_hours"]) for key in ("P04", "P07", "P08")] == [
        7,
        3,
        0,
    ]
    receipt = json.loads((output / "pressure-receipt.json").read_bytes())
    assert receipt["producers"]
    for name, expected in receipt["outputs"].items():
        assert hashlib.sha256((output / name).read_bytes()).hexdigest() == expected
    assert before == {name: (source_root / name).read_bytes() for name in before}


@pytest.mark.parametrize("source_name", [STUDY, REFERENCE, DECISIONS])
def test_changed_or_invalid_input_refuses_before_reserving_output(source_root, source_name):
    # Given either malformed study data or byte-changed retained reference/decisions.
    source = source_root / source_name
    original = source.read_bytes()
    source.write_bytes(b"{}" if source_name == STUDY else original + b" ")
    output = source_root / "analysis_output/rejected"
    # When publishing, then the input boundary refuses without creating the destination.
    with pytest.raises((ValueError, ResearchError)):
        publish_pressure(source_root, output)
    assert not output.exists()


def test_an_occupied_output_is_preserved(source_root):
    # Given an existing caller-owned output tree.
    output = source_root / "analysis_output/occupied"
    output.mkdir(parents=True)
    marker = output / "keep.bin"
    marker.write_bytes(b"retained caller output")
    # When attempting publication, then no old byte is overwritten.
    with pytest.raises(ResearchError, match="occupied_output"):
        publish_pressure(source_root, output)
    assert marker.read_bytes() == b"retained caller output"
    assert list(output.iterdir()) == [marker]


def test_outside_private_output_is_refused(source_root):
    # Given a destination outside the declared ignored result root.
    output = source_root / "outside"
    # When publishing through the actual seam, then it refuses before output creation.
    with pytest.raises(ResearchError, match="private_output_required"):
        publish_pressure(source_root, output)
    assert not output.exists()


def test_native_adapter_copies_figure_masters_as_independent_files(source_root):
    # Given the real eight-case study and a native preparation stage.
    stage = source_root / "analysis_output/stage"
    (stage / "output/figures").mkdir(parents=True)
    # When the adapter runs, then both native figure derivatives match the bound source run.
    caption = prepare_pressure_figure(source_root, stage)
    assert caption
    for suffix in (".pdf", ".png"):
        original = stage / "review-pressure/figures" / ("review-pressure" + suffix)
        copied = stage / "output/figures" / ("review-pressure" + suffix)
        assert original.read_bytes() == copied.read_bytes()
        assert original.stat().st_ino != copied.stat().st_ino
    receipt = json.loads((stage / "review-pressure/pressure-receipt.json").read_bytes())
    assert set(receipt["outputs"]) == {
        "pressure-report.json",
        "pressure-claimants.csv",
        "figures/review-pressure.pdf",
        "figures/review-pressure.png",
    }


def test_figure_refuses_a_different_case_family(source_root):
    # Given a valid analytical study restricted to one case, outside this fixed layout.
    data = json.loads((source_root / STUDY).read_bytes())
    data["cases"] = data["cases"][:1]
    (source_root / STUDY).write_text(json.dumps(data))
    result = publish_pressure(source_root, source_root / "analysis_output/one")
    output = source_root / "analysis_output/not-eight"
    # When using the eight-case figure, then it refuses before creating the figure directory.
    with pytest.raises(ResearchError, match="pressure_figure_scope"):
        render_pressure_figure(result, output)
    assert not output.exists()


@pytest.mark.parametrize("figures", [False, True])
def test_real_cli_succeeds_then_rejects_the_occupied_destination(source_root, figures):
    # Given exact inputs and the actual installed command module.
    output = source_root / "analysis_output/cli"
    command = [
        sys.executable,
        "-B",
        "-m",
        "blakean_federalism.review_pressure_cli",
        "--root",
        str(source_root),
        "--output",
        str(output),
    ]
    if figures:
        command.append("--figures")
    # When invoked as a real subprocess, then success closes a complete immutable tree.
    first = subprocess.run(  # noqa: S603 -- Absolute Python and fixed module in a tmp fixture.
        command, stdin=subprocess.DEVNULL, capture_output=True, check=False
    )
    assert first.returncode == 0, first.stderr
    before = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    second = subprocess.run(  # noqa: S603 -- Repeat the exact fixed local CLI control.
        command, stdin=subprocess.DEVNULL, capture_output=True, check=False
    )
    assert second.returncode == 1
    assert before == {
        p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()
    }


def test_missing_real_rasterizer_retains_partial_output_without_a_completion_receipt(source_root):
    # Given a real child environment where no external rasterizer can be discovered.
    output = source_root / "analysis_output/missing-rasterizer"
    environment = dict(os.environ, PATH="")
    command = [
        sys.executable,
        "-B",
        "-m",
        "blakean_federalism.review_pressure_cli",
        "--root",
        str(source_root),
        "--output",
        str(output),
        "--figures",
    ]
    # When the actual CLI runs, then it fails explicitly and preserves its partial evidence.
    result = subprocess.run(  # noqa: S603 -- Absolute Python; empty PATH is the real control.
        command, env=environment, stdin=subprocess.DEVNULL, capture_output=True, check=False
    )
    assert result.returncode == 1
    assert (output / "pressure-report.json").is_file()
    assert not (output / "pressure-receipt.json").exists()
