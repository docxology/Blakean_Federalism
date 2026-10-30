# Copyright (c) 2026 Daniel Ari Friedman
"""Quantitative caption and figure metadata follow admitted pressure-study inputs."""

import json
import re
import shutil
from pathlib import Path
from typing import Literal, assert_never

import pytest
from pypdf import PdfReader

from blakean_federalism.review_pressure_figure import render_pressure_figure
from blakean_federalism.review_pressure_run import (
    DECISIONS,
    REFERENCE,
    STUDY,
    pressure_caption,
    publish_pressure,
)

ROOT = Path(__file__).parents[1]
CaptionChange = Literal["later_filing", "shorter_protection", "same_office", "required_exit"]


@pytest.fixture
def source_root(tmp_path):
    for name in (STUDY, REFERENCE, DECISIONS):
        target = tmp_path / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return tmp_path


@pytest.mark.parametrize(
    "change", ["later_filing", "shorter_protection", "same_office", "required_exit"]
)
def test_caption_measurements_follow_admitted_input_changes(source_root, change: CaptionChange):
    # Given a valid study with one adverse change and independently fixed expectations.
    data = json.loads((source_root / STUDY).read_bytes())
    cases = {item["procedure"]["procedure_id"]: item["procedure"] for item in data["cases"]}
    expected_gaps = {"P01": 0, "P02": 0, "P03": 0, "P04": 7, "P05": 0, "P06": 0, "P07": 3, "P08": 0}
    expected_passes = 4
    match change:
        case "later_filing":
            cases["P07"]["claimants"][1]["ready_to_file_hour"] = 7
            expected_gaps["P07"] = 4
        case "shorter_protection":
            cases["P08"]["claimants"][1]["protection"]["ends_hour"] = 9
            expected_gaps["P08"] = 1
            expected_passes = 3
        case "same_office":
            cases["P05"]["reviewing_office_id"] = cases["P05"]["issuing_office_id"]
            expected_passes = 3
        case "required_exit":
            cases["P06"]["claimants"][1]["affiliation_exit_required"] = True
            expected_passes = 3
        case unreachable:
            assert_never(unreachable)
    (source_root / STUDY).write_text(json.dumps(data))
    # When the admitted analytical result supplies its publication caption.
    report = publish_pressure(source_root, source_root / "analysis_output/result")
    caption = pressure_caption(report)
    # Then the exposed quantities retain case IDs, units and explicit zeros.
    counts = re.match(r"^(\d+).*?; (\d+)\s", caption)
    assert counts is not None
    assert tuple(map(int, counts.groups())) == (8, expected_passes)
    quantities = {key: int(hours) for key, hours in re.findall(r"\b(P\d{2}): (\d+) h\b", caption)}
    assert quantities == expected_gaps


def test_caption_uses_the_selected_person_and_retains_zero_exposures(source_root):
    # Given the same valid procedures with the other listed person selected.
    data = json.loads((source_root / STUDY).read_bytes())
    data["affected_person_id"] = "member-a"
    (source_root / STUDY).write_text(json.dumps(data))
    # When publishing the caption from the real report.
    report = publish_pressure(source_root, source_root / "analysis_output/member")
    caption = pressure_caption(report)
    # Then the selected identity and every zero measurement remain visible.
    assert "member-a" in caption
    quantities = {key: int(hours) for key, hours in re.findall(r"\b(P\d{2}): (\d+) h\b", caption)}
    assert quantities == {f"P{index:02}": 0 for index in range(1, 9)}


def test_caption_supports_an_admitted_case_subset_without_unnamed_contrasts(source_root):
    # Given a one-case analytical family admitted independently of the eight-row figure.
    data = json.loads((source_root / STUDY).read_bytes())
    data["cases"] = data["cases"][-1:]
    (source_root / STUDY).write_text(json.dumps(data))
    # When publishing its caption through the same report seam.
    report = publish_pressure(source_root, source_root / "analysis_output/subset")
    caption = pressure_caption(report)
    # Then its quantities include only the actual single result.
    counts = re.match(r"^(\d+).*?; (\d+)\s", caption)
    assert counts is not None
    assert tuple(map(int, counts.groups())) == (1, 1)
    assert re.findall(r"\b(P\d{2}): (\d+) h\b", caption) == [("P08", "0")]


def test_vector_figure_uses_the_actual_reference_and_practical_subject_ids(source_root):
    # Given valid changed metadata, all distinct from the original fixed labels.
    data = json.loads((source_root / STUDY).read_bytes())
    data["reference_procedure_id"] = "H01"
    data["affected_person_id"] = "member-a"
    data["collective_party_id"] = "council-z"
    (source_root / STUDY).write_text(json.dumps(data))
    report = publish_pressure(source_root, source_root / "analysis_output/metadata")
    # When rendering a real vector master.
    pdf, _ = render_pressure_figure(report, source_root / "analysis_output/figure")
    rendered = " ".join((page.extract_text() or "") for page in PdfReader(pdf).pages)
    # Then source identity fields, rather than the old fixed values, reach the output.
    assert all(value in rendered for value in ("H01", "member-a", "council-z"))
    assert all(value not in rendered for value in ("H12", "resident-b", "treaty-people"))
