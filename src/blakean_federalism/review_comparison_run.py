# Copyright (c) 2026 Daniel Ari Friedman
"""Exclusive, source-bound exports for the stipulated procedural comparison."""

import csv
import io
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal

from blake.methods.producer import SourceBinding, source_hashes

from .institutional_review_models import ReviewInput
from .models import Assessment, FileReceipt, ResearchError
from .review_comparison import ReviewComparison, compare_review
from .review_inputs import validated_report
from .storage import digest, safe_path, write_new

if TYPE_CHECKING:
    from collections.abc import Callable

PRODUCERS: Final = (
    "__init__.py",
    "review_comparison.py",
    "review_comparison_run.py",
    "review_inputs.py",
    "institutional_review.py",
    "institutional_review_models.py",
    "institutions.py",
    "models.py",
    "storage.py",
)
SHARED: Final = (
    "__init__.py",
    "version.py",
    "methods/__init__.py",
    "methods/models.py",
    "methods/common.py",
    "methods/projection_models.py",
    "methods/bundle_models.py",
    "text_search/models.py",
    "methods/storage.py",
    "methods/runs.py",
    "methods/producer.py",
)


class ComparisonReceipt(ReviewInput):
    schema_version: Literal[1] = 1
    review_cases_sha256: str
    baseline_decisions_sha256: str
    linked_baseline_assessments: tuple[Assessment, ...]
    producers: dict[str, str]
    outputs: tuple[FileReceipt, ...]
    scope: str = "Source-bound stipulated comparison; no native manuscript or installed SDK claim"


def comparison_producers(*, figures: bool) -> dict[str, str]:
    """Bind only the analytical closure, adding the optional figure closure when used."""
    extra = (
        (
            "review_comparison_figure.py",
            "figure_style.py",
            "resources/fonts/Vera.ttf",
            "resources/fonts/bitstream-vera-license.txt",
        )
        if figures
        else ()
    )
    return source_hashes(
        (SourceBinding("blakean_federalism", PRODUCERS + extra), SourceBinding("blake", SHARED))
    )


def _claimant_csv(report: ReviewComparison) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        (
            "procedure_id",
            "claimant_id",
            "membership",
            "standing",
            "may_remain",
            "available_hours",
            "support_hours",
            "required_hours",
            "shortfall_hours",
            "filing_opens_hour",
            "filing_closes_hour",
            "ready_to_file_hour",
            "earliest_filing_hour",
            "readiness_lateness_hours",
            "consequence_hour",
            "response_hour",
            "active_protection",
            "uncovered_intervals",
            "unmet_requirements",
            "issuer_separated",
            "revision_power",
            "suspension_power",
            "unassessed_issues",
        )
    )
    for result, requirements in zip(report.review.results, report.requirements, strict=True):
        audits = {p.claimant_id: p for p in result.claimants}
        residuals = {p.claimant_id: p for p in requirements.claimants}
        for person in result.procedure.claimants:
            audit = audits[person.claimant_id]
            residual = residuals[person.claimant_id]
            writer.writerow(
                (
                    result.procedure.procedure_id,
                    person.claimant_id,
                    person.membership.value,
                    audit.standing,
                    audit.may_remain,
                    person.available_filing_hours,
                    person.support_enabled_filing_hours,
                    person.required_filing_hours,
                    residual.preparation_shortfall_hours,
                    result.procedure.filing_opens_hour,
                    result.procedure.filing_closes_hour,
                    person.ready_to_file_hour,
                    audit.earliest_filing_hour,
                    residual.readiness_lateness_hours,
                    person.consequence_hour,
                    result.procedure.response_hour,
                    ""
                    if audit.active_protection is None
                    else _intervals((audit.active_protection,)),
                    _intervals(audit.uncovered_intervals),
                    "|".join(residual.unmet),
                    result.issuer_separated_forum,
                    result.revision_power,
                    result.suspension_power,
                    "|".join(result.procedure.unassessed_issues),
                )
            )
    return buffer.getvalue()


def _intervals(intervals: tuple[tuple[int, int], ...]) -> str:
    return "|".join(f"[{start},{end})" for start, end in intervals)


def _comparison_csv(report: ReviewComparison) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(("left_procedure_id", "right_procedure_id", "relation"))
    writer.writerows((p.left, p.right, p.relation.value) for p in report.comparisons)
    return buffer.getvalue()


def publish_comparison(
    cases: Path, decisions: Path, output: Path, *, figures: bool = False
) -> ReviewComparison:
    """Validate before reserving a new run; write the completion receipt last.

    A generator failure preserves its partial run without a completion receipt.
    Figures need ReportLab, the packaged Vera font and the actual pdftoppm binary;
    JSON/CSV export needs none of those optional rendering dependencies.
    """
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ResearchError("symlink_output", str(output))
    audit = validated_report(cases, decisions, output)
    report = compare_review(audit.report)
    producers = comparison_producers(figures=figures)
    renderer: Callable[[ReviewComparison, Path], tuple[Path, ...]] | None = None
    if figures:
        from .review_comparison_figure import (  # noqa: PLC0415 -- Optional manuscript stack.
            render_comparison_figures,
            validate_comparison_figures,
        )

        _ = validate_comparison_figures(report)
        renderer = render_comparison_figures
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "review-report.json", audit.report.model_dump_json(indent=2) + "\n")
    write_new(output / "comparison.json", report.model_dump_json(indent=2, round_trip=True) + "\n")
    write_new(output / "claimant-requirements.csv", _claimant_csv(report))
    write_new(output / "procedure-comparisons.csv", _comparison_csv(report))
    rendered = renderer(report, output / "figures") if renderer is not None else ()
    names = (
        "review-report.json",
        "comparison.json",
        "claimant-requirements.csv",
        "procedure-comparisons.csv",
    )
    paths = tuple(output / name for name in names) + rendered
    if (
        producers != comparison_producers(figures=figures)
        or digest(safe_path(cases.parent, cases.name)) != sha256(audit.review_bytes).hexdigest()
        or digest(safe_path(decisions.parent, decisions.name))
        != sha256(audit.baseline_bytes).hexdigest()
    ):
        raise ResearchError(
            "review_comparison_source_changed", "Producer or input changed during export"
        )
    receipt = ComparisonReceipt(
        review_cases_sha256=sha256(audit.review_bytes).hexdigest(),
        baseline_decisions_sha256=sha256(audit.baseline_bytes).hexdigest(),
        linked_baseline_assessments=audit.assessments,
        producers=producers,
        outputs=tuple(
            FileReceipt(
                path=path.relative_to(output).as_posix(),
                size=path.stat().st_size,
                sha256=digest(path),
            )
            for path in paths
        ),
    )
    write_new(output / "comparison-receipt.json", receipt.model_dump_json(indent=2) + "\n")
    return report
