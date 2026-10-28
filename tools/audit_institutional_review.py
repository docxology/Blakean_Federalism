# Copyright (c) 2026 Daniel Ari Friedman
"""Audit stipulated review access against hash-bound, admissible baseline decisions."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated

import typer
from pydantic import TypeAdapter

from blakean_federalism.institutional_review import ReviewReport, audit_review
from blakean_federalism.institutional_review_models import ReviewInput, ReviewStudy
from blakean_federalism.institutions import assess
from blakean_federalism.models import Assessment, Decision, ResearchError

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


@dataclass(frozen=True, slots=True)
class ValidatedReviewAudit:
    """Parsed review inputs with their assessed baseline linkages."""

    report: ReviewReport
    review_bytes: bytes
    baseline_bytes: bytes
    assessments: tuple[Assessment, ...]
    baseline_decision_count: int


def linked_assessments(
    study: ReviewStudy, decisions: tuple[Decision, ...]
) -> tuple[Assessment, ...]:
    """Require unique existing baseline identities and admissible linked decisions."""
    indexed = {decision.decision_id: decision for decision in decisions}
    if len(indexed) != len(decisions):
        raise ResearchError("duplicate_baseline_decision", "baseline decision IDs must be unique")
    linked = sorted({procedure.baseline_decision_id for procedure in study.procedures})
    results: list[Assessment] = []
    for identifier in linked:
        if identifier not in indexed:
            raise ResearchError("missing_baseline_decision", identifier)
        result = assess(indexed[identifier])
        if not result.admissible_under_proposed_rules:
            raise ResearchError("inadmissible_baseline_decision", identifier)
        results.append(result)
    return tuple(results)


def validated_report(cases: Path, decisions: Path, output: Path) -> ValidatedReviewAudit:
    """Finish all input and destination checks before creating an output directory."""
    if output.exists() or output.is_symlink():
        raise ResearchError("occupied_output", str(output))
    destination = output.resolve()
    for source in (cases, decisions):
        resolved = source.resolve()
        if resolved == destination or destination in resolved.parents:
            raise ResearchError("input_inside_output", str(source))
    cases_bytes = cases.read_bytes()
    baseline_bytes = decisions.read_bytes()
    study = ReviewStudy.model_validate_json(cases_bytes)
    if sha256(baseline_bytes).hexdigest() != study.baseline_decisions_sha256:
        raise ResearchError("baseline_hash_mismatch", "decision bytes differ from review study")
    parsed_decisions = TypeAdapter(tuple[Decision, ...]).validate_json(baseline_bytes)
    assessments = linked_assessments(study, parsed_decisions)
    return ValidatedReviewAudit(
        audit_review(study), cases_bytes, baseline_bytes, assessments, len(parsed_decisions)
    )


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
