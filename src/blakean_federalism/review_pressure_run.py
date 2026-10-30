# Copyright (c) 2026 Daniel Ari Friedman
"""Publish the dated domain pressure experiment with exact input and output custody."""

import csv
import io
import json
from hashlib import sha256
from pathlib import Path
from typing import Final

from blake.methods.producer import SourceBinding, source_hashes
from pydantic import TypeAdapter

from . import __version__
from .institutional_review_models import ReviewStudy
from .models import Decision, ResearchError
from .review_comparison_run import SHARED
from .review_pressure import PressureReport, audit_pressure
from .review_pressure_models import PressureIssue, PressureStudy
from .storage import digest, safe_path, write_new

STUDY: Final = "research/review-pressure-20261029.json"
REFERENCE: Final = "research/institutional-review-cases.json"
DECISIONS: Final = "research/cases.json"


def pressure_caption(report: PressureReport) -> str:
    """Generate source-bound quantities without assuming a particular pressure contrast."""
    passes = sum(item.review.declared_conditions_hold for item in report.results)
    total = len(report.results)
    affected = report.study.affected_person_id
    waiting: list[str] = []
    for item in report.results:
        person = next(
            claimant for claimant in item.review.claimants if claimant.claimant_id == affected
        )
        waiting.append(f"{item.case.procedure.procedure_id}: {person.uncovered_wait_hours} h")
    return (
        f"{total} stipulated pressure cases retain the same E-bounded decision record and "
        f"fifteen safeguard fields; {passes} satisfy all seven declared review conditions. "
        "The first seven columns are computed by the unchanged person-specific audit. "
        "The final four columns retain separately declared practical premises: an open "
        "circle means stipulated protection, a red cross stipulated obstruction, and a "
        "question mark unassessed. "
        f"Uncovered waiting time for {affected}: {'; '.join(waiting)}. "
        "These are constructed contrasts, not measured institutional effects, "
        "independence findings or legitimacy scores."
    )


def _csv(report: PressureReport) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        (
            "procedure_id",
            "claimant_id",
            "standing",
            "may_remain",
            "sufficient_hours",
            "filing_ready",
            "uncovered_wait_hours",
            "uncovered_intervals",
            "issuer_separated",
            "revision_power",
            *[issue.value for issue in PressureIssue],
        )
    )
    for item in report.results:
        statuses = {row.issue: row.status.value for row in item.case.boundaries}
        for person in item.review.claimants:
            writer.writerow(
                (
                    item.case.procedure.procedure_id,
                    person.claimant_id,
                    int(person.standing),
                    int(person.may_remain),
                    int(person.sufficient_hours),
                    int(person.filing_ready),
                    person.uncovered_wait_hours,
                    json.dumps(person.uncovered_intervals),
                    int(item.review.issuer_separated_forum),
                    int(item.review.revision_power),
                    *[statuses[issue] for issue in PressureIssue],
                )
            )
    return stream.getvalue()


def pressure_producers(*, figures: bool) -> dict[str, str]:
    """Use the shared producer binder for the actual selected source closure."""
    return source_hashes(
        (
            SourceBinding(
                "blakean_federalism",
                (
                    "__init__.py",
                    "review_pressure_models.py",
                    "review_pressure.py",
                    "review_pressure_run.py",
                    "review_comparison_run.py",
                    "review_inputs.py",
                    "institutional_review.py",
                    "institutional_review_models.py",
                    "institutions.py",
                    "models.py",
                    "storage.py",
                )
                + (
                    (
                        "review_pressure_figure.py",
                        "figure_style.py",
                        "resources/fonts/Vera.ttf",
                        "resources/fonts/bitstream-vera-license.txt",
                    )
                    if figures
                    else ()
                ),
            ),
            SourceBinding("blake", SHARED),
        )
    )


def publish_pressure(root: Path, output: Path, *, figures: bool = False) -> PressureReport:
    """Validate the complete fixed study before reserving an exclusive new destination."""
    if not output.resolve().is_relative_to((root / "analysis_output").resolve()):
        raise ResearchError("private_output_required", "analysis_output")
    sources = {name: safe_path(root, name) for name in (STUDY, REFERENCE, DECISIONS)}
    if output.exists() or output.is_symlink():
        raise ResearchError("occupied_output", str(output))
    payloads = {name: path.read_bytes() for name, path in sources.items()}
    before = {name: sha256(raw).hexdigest() for name, raw in payloads.items()}
    producers = pressure_producers(figures=figures)
    study = PressureStudy.model_validate_json(payloads[STUDY])
    if before[REFERENCE] != study.reference_study_sha256:
        raise ResearchError("pressure_reference_hash", "Reference study bytes differ")
    if before[DECISIONS] != study.baseline_decisions_sha256:
        raise ResearchError("pressure_baseline_hash", "Baseline decision bytes differ")
    reference = ReviewStudy.model_validate_json(payloads[REFERENCE])
    decisions = TypeAdapter(tuple[Decision, ...]).validate_json(payloads[DECISIONS])
    report = audit_pressure(study, reference, decisions)
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "pressure-report.json", report.model_dump_json(indent=2) + "\n")
    write_new(output / "pressure-claimants.csv", _csv(report))
    if figures:
        from .review_pressure_figure import render_pressure_figure  # noqa: PLC0415

        _ = render_pressure_figure(report, output / "figures")
    if any(digest(path) != before[name] for name, path in sources.items()):
        raise ResearchError("pressure_changed_inputs", "Inputs changed during publication")
    if producers != pressure_producers(figures=figures):
        raise ResearchError(
            "pressure_changed_producer", "Producer bytes changed during publication"
        )
    files = {
        path.relative_to(output).as_posix(): digest(path)
        for path in sorted(output.rglob("*"))
        if path.is_file()
    }
    receipt = {
        "schema_version": 1,
        "producer_version": __version__,
        "inputs": before,
        "outputs": files,
        "producers": producers,
        "procedures": len(report.results),
        "claimants": sum(len(item.review.claimants) for item in report.results),
        "formal_passes": sum(item.review.declared_conditions_hold for item in report.results),
        "scope": (
            "Constructed pressure cases; practical boundary declarations "
            "are not scored or conjoined into legitimacy."
        ),
    }
    write_new(output / "pressure-receipt.json", json.dumps(receipt, indent=2) + "\n")
    return report
