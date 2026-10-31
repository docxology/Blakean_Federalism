# Copyright (c) 2026 Daniel Ari Friedman
"""Typed commands for request-pinned private review batches."""

from pathlib import Path
from typing import Annotated

import typer
from blake.methods.models import ResearchError

from .review_planning import (
    PinnedReviewBatch,
    PinnedReviewFile,
    publish_planning_request,
    verify_planning_request,
)


def plan_review_command(
    request: Annotated[Path, typer.Option(help="Independently pinned planning request")],
    request_sha256: Annotated[str, typer.Option(help="Caller-held request SHA256")],
    output: Annotated[Path, typer.Option(help="New directory below analysis_output")],
) -> None:
    """Plan blank review work without authoring any political reading."""
    try:
        receipt = publish_planning_request(
            PinnedReviewFile(path=request, sha256=request_sha256), output
        )
    except (OSError, ValueError, ResearchError) as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(receipt.model_dump_json(indent=2))


def verify_review_command(
    request: Annotated[Path, typer.Option(help="Independently pinned planning request")],
    request_sha256: Annotated[str, typer.Option(help="Caller-held request SHA256")],
    batch: Annotated[Path, typer.Option(help="Private review batch directory")],
    batch_sha256: Annotated[str, typer.Option(help="Caller-held batch run.json SHA256")],
) -> None:
    """Four explicit options hold two independent request and batch custody pairs."""
    try:
        verified = verify_planning_request(
            PinnedReviewFile(path=request, sha256=request_sha256),
            PinnedReviewBatch(directory=batch, receipt_sha256=batch_sha256),
        )
    except (OSError, ValueError, ResearchError) as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(verified.plan.model_dump_json(indent=2))


def register_review_planning_commands(app: typer.Typer) -> None:
    """Register two finite commands while retaining the existing CLI surface."""
    _ = app.command("plan-review")(plan_review_command)
    _ = app.command("verify-review")(verify_review_command)
