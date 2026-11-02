# Copyright (c) 2026 Daniel Ari Friedman
"""Real timing preparation keeps the complete run and both person-specific figures."""

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfReader

from blakean_federalism.comparison_publication import prepare_domain_figures
from blakean_federalism.models import ResearchError
from blakean_federalism.review_timing_inputs import INPUT_NAMES
from blakean_federalism.review_timing_run import verify_timing_output
from blakean_federalism.storage import digest
from blakean_federalism.timing_publication import TIMING_FIGURES, TIMING_LABELS, require_timing_pair

ROOT = Path(__file__).parents[1]


def ast_nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from ast_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from ast_nodes(child)


@pytest.fixture
def timing_stage(tmp_path):
    for name in INPUT_NAMES:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    stage = tmp_path / "analysis_output/publication"
    (stage / "output/figures").mkdir(parents=True)
    return tmp_path, stage


def test_real_timing_preparation_retains_full_run_and_data_captions(timing_stage):
    root, stage = timing_stage
    before = {name: digest(root / name) for name in INPUT_NAMES}
    result = prepare_domain_figures(root, stage, tuple(sorted(TIMING_LABELS)))
    assert result.figures == {name: name + ".png" for name in TIMING_FIGURES}
    assert set(result.captions) == {"TIMING_READINESS_CAPTION", "TIMING_PROTECTION_CAPTION"}
    assert "21,454" in result.captions["TIMING_READINESS_CAPTION"]
    assert "42,908" in result.captions["TIMING_READINESS_CAPTION"]
    pandoc = shutil.which("pandoc")
    assert pandoc is not None, "The native manuscript regression requires actual Pandoc"
    for token, caption in result.captions.items():
        rendered = subprocess.run(  # noqa: S603 -- Resolved Pandoc, fixed options and literal stdin.
            [pandoc, "--from=markdown", "--to=json"],
            input=f"![{caption}](example.png){{#fig:timing}}\n",
            text=True,
            capture_output=True,
            check=False,
        )
        assert rendered.returncode == 0, rendered.stderr
        ast = json.loads(rendered.stdout)
        kinds = [node.get("t") for node in ast_nodes(ast)]
        assert kinds.count("Image") == 1, token
        assert kinds.count("Link") == 0, token
    run = stage / "review-timing"
    receipt = verify_timing_output(run, digest(run / "atlas-receipt.json"))
    assert receipt.configurations == 21454
    assert receipt.person_records == 42908
    with (run / "atlas-claimants.csv").open(newline="") as stream:
        rows = tuple(csv.DictReader(stream))
    assert len(rows) == 42908
    assert {row["claimant_id"] for row in rows} == {"resident-b", "member-a"}
    for name in TIMING_FIGURES:
        for suffix in (".pdf", ".png"):
            source = run / "figures" / (name + suffix)
            target = stage / "output/figures" / (name + suffix)
            assert digest(source) == digest(target)
            assert source.stat().st_ino != target.stat().st_ino
        assert len(PdfReader(stage / "output/figures" / (name + ".pdf")).pages) == 1
        with Image.open(stage / "output/figures" / (name + ".png")) as image:
            image.load()
            assert max(image.size) == 3200
    assert {name: digest(root / name) for name in INPUT_NAMES} == before
    marker = (run / "atlas-receipt.json").read_bytes()
    with pytest.raises(ResearchError, match="occupied_output"):
        prepare_domain_figures(root, stage, tuple(TIMING_LABELS))
    assert (run / "atlas-receipt.json").read_bytes() == marker


def test_partial_timing_pair_refuses_before_any_output(timing_stage):
    root, stage = timing_stage
    with pytest.raises(ResearchError, match="timing_figure_pair"):
        prepare_domain_figures(root, stage, ("fig:review-timing-readiness",))
    assert not (stage / "review-timing").exists()
    assert not tuple((stage / "output/figures").iterdir())
    assert not require_timing_pair(())


def test_changed_timing_input_refuses_before_atlas_output(timing_stage):
    root, stage = timing_stage
    path = root / INPUT_NAMES[1]
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ResearchError, match="timing_input_hash"):
        prepare_domain_figures(root, stage, tuple(TIMING_LABELS))
    assert not (stage / "review-timing").exists()
    assert not tuple((stage / "output/figures").iterdir())


def test_registered_real_cli_help_and_occupied_output_control(timing_stage):
    root, stage = timing_stage
    base = [sys.executable, "-m", "blakean_federalism.cli", "timing-atlas"]
    help_result = subprocess.run(  # noqa: S603 -- Fixed real Python module.
        [*base, "--help"], capture_output=True, text=True, check=False
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "--root" in help_result.stdout
    assert "--figures" in help_result.stdout
    sentinel = stage / "keep.json"
    sentinel.write_text(json.dumps({"preserved": True}))
    refused = subprocess.run(  # noqa: S603 -- Fixed module and test-owned output.
        [*base, "--root", str(root), "--output", str(stage)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert refused.returncode == 1
    assert "occupied_output" in refused.stderr
    assert json.loads(sentinel.read_text()) == {"preserved": True}
    assert not (stage / "atlas-receipt.json").exists()
