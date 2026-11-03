# Copyright (c) 2026 Daniel Ari Friedman
"""Real worker processes refuse unqualified input before importing native writers."""

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, assert_never

import pytest

ROOT: Final = Path(__file__).parents[1]


def invoke(
    arguments: list[str], environment: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 -- Fixed worker; all arguments are test-owned paths/options.
        [sys.executable, "-m", "tools.template_render", *arguments],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )


def test_worker_help_needs_no_stage_or_native_writer() -> None:
    # Given no prepared input, when help is requested, then expose the actual parser.
    result = invoke(["--help"])
    assert result.returncode == 0, result.stderr
    assert "--template-root" in result.stdout
    assert "--stage" in result.stdout


def test_missing_preparation_never_creates_native_output(tmp_path: Path) -> None:
    # Given an empty stage, when the real worker runs, then fail before native imports.
    stage = tmp_path / "stage"
    stage.mkdir()
    result = invoke(["--template-root", str(tmp_path / "template"), "--stage", str(stage)])
    assert result.returncode != 0
    assert "prepared-publication.json" in result.stderr
    assert not tuple(stage.iterdir())


@pytest.mark.parametrize(
    "gate", ["git_missing", "template_pin", "template_dirty", "unsupported_template_source_mode"]
)
def test_unqualified_template_is_refused_before_native_import(
    tmp_path: Path,
    gate: Literal[
        "git_missing", "template_pin", "template_dirty", "unsupported_template_source_mode"
    ],
) -> None:
    # Given a real fixture repository, when one admission premise fails, then emit that refusal.
    template = tmp_path / "template"
    stage = tmp_path / "stage"
    template.mkdir()
    stage.mkdir()
    git = shutil.which("git")
    assert git is not None
    tracked = template / "fixture.txt"
    tracked.write_text("original\n")
    for arguments in (
        ["init", "--initial-branch=main"],
        ["add", "fixture.txt"],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-m",
            "Fixture",
        ],
    ):
        subprocess.run(  # noqa: S603 -- Resolved Git and fixed fixture-only argv.
            [git, *arguments], cwd=template, capture_output=True, check=True, text=True
        )
    actual = subprocess.check_output(  # noqa: S603 -- Resolved Git and fixed read-only argv.
        [git, "rev-parse", "HEAD"], cwd=template, text=True
    ).strip()
    selected = actual
    environment = dict(os.environ)
    match gate:
        case "git_missing":
            environment["PATH"] = ""
        case "template_pin":
            selected = "0" * 40
        case "template_dirty":
            tracked.write_text("changed\n")
        case "unsupported_template_source_mode":
            unsafe = template / "infrastructure" / "unsafe.py"
            unsafe.parent.mkdir()
            unsafe.symlink_to(tracked)
            for arguments in (
                ["add", "infrastructure/unsafe.py"],
                [
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "-c",
                    "commit.gpgsign=false",
                    "commit",
                    "-m",
                    "Symlink fixture",
                ],
            ):
                subprocess.run(  # noqa: S603 -- Fixed operations on the fixture repository.
                    [git, *arguments], cwd=template, capture_output=True, check=True, text=True
                )
            selected = subprocess.check_output(  # noqa: S603 -- Fixed read-only fixture argv.
                [git, "rev-parse", "HEAD"], cwd=template, text=True
            ).strip()
        case unreachable:
            assert_never(unreachable)
    (stage / "prepared-publication.json").write_text(
        json.dumps({"template": {"commit": selected, "source_date_epoch": 0}})
    )

    result = invoke(
        ["--template-root", str(template), "--stage", str(stage)],
        environment,
    )

    assert result.returncode != 0
    assert gate in result.stderr
    assert not (stage / "native-render-receipt.json").exists()
    assert not (stage / "output").exists()
