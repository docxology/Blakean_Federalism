# Copyright (c) 2026 Daniel Ari Friedman
"""Actual renderer controls and the source-only dependency-light production route."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import assert_never

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.review_timing import build_timing_atlas
from blakean_federalism.review_timing_figure import validate_timing_figures
from tests.test_review_timing_run import copy_inputs, run_cli

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def complete_atlas():
    return build_timing_atlas(ROOT)


def test_incomplete_figure_selection_refuses_before_output(complete_atlas):
    # Given a missing selected cell, the fixed-layout boundary refuses the truncated view.
    partial = complete_atlas.model_copy(update={"cells": complete_atlas.cells[1:]})
    with pytest.raises(ResearchError, match="timing_figure_scope"):
        validate_timing_figures(partial)


def test_no_figure_route_imports_no_optional_render_stack(tmp_path):
    # Given a fresh process and no figure request, the actual producer stays dependency-light.
    root = copy_inputs(tmp_path / "case")
    script = (
        "import sys\nfrom pathlib import Path\n"
        "from blakean_federalism.review_timing_run import publish_timing\n"
        "root=Path(sys.argv[1])\n"
        "publish_timing(root,root/'analysis_output/light')\n"
        "assert not any(n.split('.')[0] in {'reportlab','PIL','pypdf'} for n in sys.modules)\n"
    )
    result = subprocess.run(  # noqa: S603 -- Real selected Python and a fixed pure-data production script.
        [sys.executable, "-B", "-c", script, str(root)],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (root / "analysis_output/light/atlas-receipt.json").is_file()


@pytest.mark.parametrize("changed", ["input", "producer"])
def test_real_raster_child_source_drift_refuses_completion(tmp_path, changed):
    # Given an actual child changing test-owned bytes during export, both post-checks refuse.
    root = copy_inputs(tmp_path / "case")
    actual = shutil.which("pdftoppm")
    assert actual is not None
    binaries = tmp_path / "bin"
    binaries.mkdir()
    environment = dict(os.environ)
    target = root / "research/review-timing-atlas-v1.json"
    match changed:
        case "input":
            pass
        case "producer":
            overlay = tmp_path / "overlay"
            shutil.copytree(ROOT / "src/blakean_federalism", overlay / "blakean_federalism")
            inherited = environment.get("PYTHONPATH", "")
            environment["PYTHONPATH"] = str(overlay) + (os.pathsep + inherited if inherited else "")
            target = overlay / "blakean_federalism/review_timing_models.py"
        case _:
            assert_never(changed)
    script = (
        f"#!{sys.executable}\nimport subprocess,sys\nfrom pathlib import Path\n"
        f"with Path({str(target)!r}).open('ab') as stream: stream.write(b'\\n')\n"
        f"child=subprocess.Popen([{actual!r},*sys.argv[1:]],stdin=subprocess.DEVNULL)\n"
        "status=child.wait()\n"
        f"Path({str(root / 'raster-grandchild.json')!r}).write_text("
        "__import__('json').dumps({'pid':child.pid,'returncode':status,'reaped':True}))\n"
        "sys.exit(status)\n"
    )
    executable = binaries / "pdftoppm"
    executable.write_text(script)
    executable.chmod(0o700)
    environment["PATH"] = str(binaries) + os.pathsep + environment["PATH"]
    result = run_cli(root, figures=True, environment=environment)
    assert result.returncode == 1
    assert f"timing_changed_{changed}" in result.stderr
    assert not (root / "analysis_output/timing/atlas-receipt.json").exists()
    terminal = json.loads((root / "raster-grandchild.json").read_text())
    assert terminal["returncode"] == 0
    assert terminal["reaped"] is True
