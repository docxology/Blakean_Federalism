# Copyright (c) 2026 Daniel Ari Friedman
"""Explicit private candidate preparation and authored review commands."""

from pathlib import Path
from typing import Annotated, Final

import typer
from pydantic import TypeAdapter

from .evidence_review import prepare_review, review_evidence
from .models import CorpusPin, QuerySpec

QUERIES: Final = TypeAdapter(tuple[QuerySpec, ...])


def prepare_evidence_command(
    corpus: Annotated[Path, typer.Option(help="Verified imported corpus directory")],
    pin: Annotated[Path, typer.Option(help="Explicit corpus pin JSON")],
    queries: Annotated[Path, typer.Option(help="Explicit query specifications JSON")],
    output: Annotated[Path, typer.Option(help="New directory below analysis_output")],
) -> None:
    receipt = prepare_review(
        corpus,
        CorpusPin.model_validate_json(pin.read_bytes()),
        QUERIES.validate_json(queries.read_bytes()),
        output,
    )
    typer.echo(receipt.model_dump_json())


def review_evidence_command(
    run: Annotated[Path, typer.Option(help="Candidate run directory")],
    run_sha256: Annotated[str, typer.Option(help="Externally retained run.json SHA256")],
    decisions: Annotated[Path, typer.Option(help="Authored unchanged CSV or decision JSONL")],
    output: Annotated[Path, typer.Option(help="New review directory below analysis_output")],
) -> None:
    summary = review_evidence(run, run_sha256, decisions, output)
    typer.echo(summary.model_dump_json())


def register_review_commands(app: typer.Typer) -> None:
    """Attach explicit commands without changing existing application registration."""
    _ = app.command("prepare-evidence-review")(prepare_evidence_command)
    _ = app.command("review-evidence")(review_evidence_command)
