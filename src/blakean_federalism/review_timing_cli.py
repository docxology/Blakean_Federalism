# Copyright (c) 2026 Daniel Ari Friedman
"""The installed domain CLI for a fixed source-bound timing atlas."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 -- Typer resolves annotation globals at runtime.
from subprocess import CalledProcessError
from typing import Annotated

import typer

from blakean_federalism.models import ResearchError
from blakean_federalism.review_timing_run import publish_timing

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


@app.command()
def main(
    root: Annotated[
        Path, typer.Option(help="Source root containing the four pinned research inputs.")
    ],
    output: Annotated[Path, typer.Option(help="New child of root/analysis_output.")],
    *,
    figures: Annotated[bool, typer.Option(help="Write vector PDF and PNG timing figures.")] = False,
) -> None:
    try:
        atlas = publish_timing(root, output, figures=figures)
    except (OSError, ValueError, ResearchError, ImportError, CalledProcessError) as error:
        typer.echo(f"timing_audit_failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    people = sum(len(c.review.claimants) for c in atlas.cells)
    typer.echo(
        f"Produced {len(atlas.cells)} stipulated configurations and {people} person records."
    )


if __name__ == "__main__":
    app()
