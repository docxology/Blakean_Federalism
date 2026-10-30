# Copyright (c) 2026 Daniel Ari Friedman
"""Run the fixed review-pressure extension without changing historical procedures."""

from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated, Final

import typer

from blakean_federalism.models import ResearchError
from blakean_federalism.review_pressure_run import publish_pressure

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)
_DEFAULT_ROOT: Final = Path()


@app.command()
def main(
    output: Annotated[Path, typer.Option(help="New ignored output directory.")],
    *,
    root: Annotated[Path, typer.Option(help="Application source root.")] = _DEFAULT_ROOT,
    figures: Annotated[bool, typer.Option(help="Render vector/raster pressure figure.")] = False,
) -> None:
    """Keep modeled access and practical-pressure declarations distinct."""
    try:
        report = publish_pressure(root, output, figures=figures)
    except (OSError, ValueError, ResearchError, ImportError, CalledProcessError) as error:
        typer.echo(f"review_pressure_failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(f"Audited {len(report.results)} pressure cases; practical premises remain separate.")


if __name__ == "__main__":
    app()
