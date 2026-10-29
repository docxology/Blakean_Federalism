# Copyright (c) 2026 Daniel Ari Friedman
"""Expose the person-specific review comparison through the existing orchestrator."""

from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated, Final

import typer

from .models import ResearchError
from .review_comparison import RepairRelation
from .review_comparison_run import publish_comparison

DEFAULT_REVIEW_CASES: Final = Path("research/institutional-review-cases.json")
DEFAULT_DECISIONS: Final = Path("research/cases.json")


def _require_private_output(output: Path) -> None:
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ResearchError("symlink_output", str(output))
    if not output.resolve().is_relative_to((Path.cwd() / "analysis_output").resolve()):
        raise ResearchError("private_output_required", "analysis_output")


def compare_review_command(
    output: Annotated[Path, typer.Option(help="New directory under analysis_output")],
    cases: Path = DEFAULT_REVIEW_CASES,
    decisions: Path = DEFAULT_DECISIONS,
    *,
    figures: Annotated[bool, typer.Option(help="Add source-derived PDF/PNG figures")] = False,
) -> None:
    """Export exact person-indexed requirements, partial-order pairs and a repair frontier."""
    try:
        _require_private_output(output)
        report = publish_comparison(cases, decisions, output, figures=figures)
    except (OSError, ValueError, ResearchError, ImportError, CalledProcessError) as error:
        typer.echo(f"review_comparison_failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    incomparable = sum(p.relation == RepairRelation.INCOMPARABLE for p in report.comparisons)
    typer.echo(
        "".join(
            (
                f"Compared {len(report.requirements)} procedures / ",
                f"{sum(len(p.claimants) for p in report.requirements)} claimant records; ",
                f"{len(report.comparisons)} pairs, {incomparable} incomparable.",
            )
        )
    )
    typer.echo("Minimal residual profiles: " + ", ".join(report.frontier_procedure_ids))
    typer.echo(
        "Exact requirements and intervals retained; unassessed issues remain outside the order."
    )
