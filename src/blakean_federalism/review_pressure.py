# Copyright (c) 2026 Daniel Ari Friedman
"""Expose formal-access results and practical premises without combining their scores."""

from .institutional_review import ProcedureReview, audit_review
from .institutional_review_models import ReviewInput, ReviewStudy
from .models import Assessment, Decision, ResearchError
from .review_inputs import linked_assessments
from .review_pressure_models import PressureCase, PressureStudy


class PressureResult(ReviewInput):
    case: PressureCase
    review: ProcedureReview


class PressureReport(ReviewInput):
    study: PressureStudy
    reference: ProcedureReview
    baseline_assessments: tuple[Assessment, ...]
    results: tuple[PressureResult, ...]


def audit_pressure(
    study: PressureStudy, reference: ReviewStudy, decisions: tuple[Decision, ...]
) -> PressureReport:
    """Reuse the existing time/access evaluator and keep boundary declarations separate."""
    if study.baseline_decisions_sha256 != reference.baseline_decisions_sha256:
        raise ResearchError(
            "pressure_baseline_identity", "The reference must use the same decisions"
        )
    original = next(
        (
            item
            for item in reference.procedures
            if item.procedure_id == study.reference_procedure_id
        ),
        None,
    )
    if original is None:
        raise ResearchError("pressure_reference_missing", str(study.reference_procedure_id))
    roster = tuple(
        (person.claimant_id, person.membership, person.required_filing_hours)
        for person in original.claimants
    )
    if study.affected_person_id not in {person.claimant_id for person in original.claimants}:
        raise ResearchError("pressure_person_missing", str(study.affected_person_id))
    for item in study.cases:
        procedure = item.procedure
        candidate = tuple(
            (person.claimant_id, person.membership, person.required_filing_hours)
            for person in procedure.claimants
        )
        if candidate != roster or procedure.baseline_decision_id != original.baseline_decision_id:
            raise ResearchError("pressure_changed_duties", str(procedure.procedure_id))
    derived = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256=study.baseline_decisions_sha256,
        procedures=tuple(item.procedure for item in study.cases),
    )
    assessments = linked_assessments(derived, decisions)
    audited = audit_review(derived)
    return PressureReport(
        study=study,
        reference=audit_review(
            ReviewStudy(
                schema_version=1,
                baseline_decisions_sha256=reference.baseline_decisions_sha256,
                procedures=(original,),
            )
        ).results[0],
        baseline_assessments=assessments,
        results=tuple(
            PressureResult(case=case, review=result)
            for case, result in zip(study.cases, audited.results, strict=True)
        ),
    )
