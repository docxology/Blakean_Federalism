# Copyright (c) 2026 Daniel Ari Friedman
"""Audit stipulated review access against hash-bound, admissible baseline decisions."""

from hashlib import sha256
from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated

import typer

from blakean_federalism.institutional_review_models import ReviewInput
from blakean_federalism.models import Assessment, ResearchError
from blakean_federalism.review_inputs import (
    ValidatedReviewAudit,
    linked_assessments,
    validated_report,
)

__all__ = ["ReviewAuditReceipt", "ValidatedReviewAudit", "linked_assessments", "validated_report"]

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


class ReviewFigureReceipt(ReviewInput):
    """Bind a rendered review figure's relative location to its bytes."""

    relative_path: str
    sha256: str


class ReviewAuditReceipt(ReviewInput):
    """Bind this review audit to its two inputs and linked baseline assessments."""

    schema_version: int = 1
    review_cases_sha256: str
    baseline_decisions_sha256: str
    review_report_sha256: str
    baseline_decision_count: int
    linked_baseline_assessments: tuple[Assessment, ...]
    procedure_count: int
    claimant_count: int
    declared_conditions_hold_count: int
    unassessed_issue_count: int
    figures: tuple[ReviewFigureReceipt, ...]


@app.command()
def main(
    cases: Annotated[Path, typer.Option(help="Review study JSON.")],
    decisions: Annotated[Path, typer.Option(help="Hash-bound baseline decision JSON.")],
    output: Annotated[Path, typer.Option(help="New audit output directory.")],
    *,
    figures: Annotated[bool, typer.Option(help="Render vector PDF and PNG figures.")] = False,
) -> None:
    """Evaluate declared review conditions; retain all unassessed issues explicitly."""
    try:
        audit = validated_report(cases, decisions, output)
        report = audit.report
        report_bytes = (report.model_dump_json(indent=2) + "\n").encode()
        if figures:
            # Optional rendering dependencies are needed only for the requested figure path.
            from blakean_federalism.institutional_review_figure import (  # noqa: PLC0415
                render_review_figures,
                validate_review_figure_report,
            )

            validate_review_figure_report(report)
            output.mkdir(parents=True, exist_ok=False)
            rendered = render_review_figures(report, output / "figures")
        else:
            output.mkdir(parents=True, exist_ok=False)
            rendered = ()
        _ = (output / "review-report.json").write_bytes(report_bytes)
        receipt = ReviewAuditReceipt(
            review_cases_sha256=sha256(audit.review_bytes).hexdigest(),
            baseline_decisions_sha256=sha256(audit.baseline_bytes).hexdigest(),
            review_report_sha256=sha256(report_bytes).hexdigest(),
            baseline_decision_count=audit.baseline_decision_count,
            linked_baseline_assessments=audit.assessments,
            procedure_count=len(report.results),
            claimant_count=sum(len(result.claimants) for result in report.results),
            declared_conditions_hold_count=sum(
                result.declared_conditions_hold for result in report.results
            ),
            unassessed_issue_count=sum(
                len(result.procedure.unassessed_issues) for result in report.results
            ),
            figures=tuple(
                ReviewFigureReceipt(
                    relative_path=str(path.relative_to(output)),
                    sha256=sha256(path.read_bytes()).hexdigest(),
                )
                for path in rendered
            ),
        )
        _ = (output / "review-receipt.json").write_text(
            receipt.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, ResearchError, ImportError, CalledProcessError) as error:
        typer.echo(f"review_audit_failed: {error}", err=True)
        raise typer.Exit(code=1) from error
    typer.echo(
        " ".join(
            (
                f"Audited {receipt.procedure_count} procedures",
                f"and {receipt.claimant_count} claimants;",
                "declared conditions hold for",
                f"{receipt.declared_conditions_hold_count} procedures;",
                f"{receipt.unassessed_issue_count} unassessed issues retained.",
            )
        )
    )


if __name__ == "__main__":
    app()
