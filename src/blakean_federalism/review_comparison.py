# Copyright (c) 2026 Daniel Ari Friedman
"""Compare person-indexed unmet review requirements without a scalar ranking."""

from enum import StrEnum
from itertools import combinations
from typing import Final, Literal

from .institutional_review import ClaimantReview, ProcedureReview, ReviewReport
from .institutional_review_models import ClaimantId, ProcedureId, ReviewInput
from .models import ResearchError


class AccessRequirement(StrEnum):
    STANDING = "standing"
    REMAIN = "remain_affiliated"
    HOURS = "filing_hours"
    DEADLINE = "filing_deadline"


class ForumRequirement(StrEnum):
    SEPARATION = "issuer_separation"
    REVISION = "revise_act"


class RepairRelation(StrEnum):
    EQUIVALENT = "equivalent"
    LEFT_SUBSET = "left_requires_subset"
    RIGHT_SUBSET = "right_requires_subset"
    INCOMPARABLE = "incomparable"


ACCESS_REQUIREMENTS: Final = tuple(AccessRequirement)


class ClaimantRequirements(ReviewInput):
    """Residual obligations for one identified person, with exact timing components."""

    claimant_id: ClaimantId
    unmet: tuple[AccessRequirement, ...]
    preparation_shortfall_hours: int
    readiness_lateness_hours: int
    uncovered_intervals: tuple[tuple[int, int], ...]


class ProcedureRequirements(ReviewInput):
    procedure_id: ProcedureId
    claimants: tuple[ClaimantRequirements, ...]
    unmet_forum: tuple[ForumRequirement, ...]


class ProcedureComparison(ReviewInput):
    left: ProcedureId
    right: ProcedureId
    relation: RepairRelation


class ReviewComparison(ReviewInput):
    schema_version: Literal[1] = 1
    review: ReviewReport
    requirements: tuple[ProcedureRequirements, ...]
    comparisons: tuple[ProcedureComparison, ...]
    frontier_procedure_ids: tuple[ProcedureId, ...]
    interpretation: str = (
        "Descriptive order on residual requirements for the same listed persons, baseline, "
        "required preparation and consequence times on one stipulated notice clock. "
        "Each person's categorical failures, hours shortfall, readiness lateness and exact "
        "uncovered intervals are retained. Equivalent residual profiles form a partial order; "
        "different source procedures can have the same profile. Minimal means inclusion-minimal "
        "among supplied profiles, not cheapest policy, empirical superiority or legitimacy. "
        "Repair requirements are conditions to discharge, not independent intervention actions. "
        "Suspension, retaliation and disputed forum competence do not enter this order."
    )


def _person_requirements(result: ProcedureReview, audit: ClaimantReview) -> ClaimantRequirements:
    person = next(p for p in result.procedure.claimants if p.claimant_id == audit.claimant_id)
    return ClaimantRequirements(
        claimant_id=audit.claimant_id,
        unmet=tuple(
            requirement
            for requirement, holds in zip(ACCESS_REQUIREMENTS, audit.conditions[:4], strict=True)
            if not holds
        ),
        preparation_shortfall_hours=max(
            0,
            person.required_filing_hours
            - person.available_filing_hours
            - person.support_enabled_filing_hours,
        ),
        readiness_lateness_hours=max(
            0, audit.earliest_filing_hour - result.procedure.filing_closes_hour
        ),
        uncovered_intervals=audit.uncovered_intervals,
    )


def _requirements(result: ProcedureReview) -> ProcedureRequirements:
    return ProcedureRequirements(
        procedure_id=result.procedure.procedure_id,
        claimants=tuple(_person_requirements(result, person) for person in result.claimants),
        unmet_forum=tuple(
            requirement
            for requirement, holds in (
                (ForumRequirement.SEPARATION, result.issuer_separated_forum),
                (ForumRequirement.REVISION, result.revision_power),
            )
            if not holds
        ),
    )


def _same_comparison_duties(report: ReviewReport) -> None:
    if not report.results:
        raise ResearchError("empty_review_comparison", "Require at least one audited procedure")
    first = report.results[0].procedure
    roster = {
        p.claimant_id: (p.membership, p.required_filing_hours, p.consequence_hour)
        for p in first.claimants
    }
    for result in report.results:
        current = result.procedure
        duties = {
            p.claimant_id: (p.membership, p.required_filing_hours, p.consequence_hour)
            for p in current.claimants
        }
        if current.baseline_decision_id != first.baseline_decision_id or duties != roster:
            raise ResearchError(
                "review_comparison_duties",
                "Require identical baseline, claimant roster and duties on one notice clock",
            )


def requirements_contained(left: ProcedureRequirements, right: ProcedureRequirements) -> bool:
    """Test the review-specific product order; canonical gaps come from audit_review.

    Each gap list has at most two separated components after removing one active
    protection interval. Thus a left component is contained in the right union
    exactly when a right component contains it. No duration comparison substitutes
    for that inclusion, and no person's improvement offsets another person's loss.
    """
    indexed = {p.claimant_id: p for p in right.claimants}
    return set(left.unmet_forum) <= set(right.unmet_forum) and all(
        set(person.unmet) <= set(indexed[person.claimant_id].unmet)
        and person.preparation_shortfall_hours
        <= indexed[person.claimant_id].preparation_shortfall_hours
        and person.readiness_lateness_hours <= indexed[person.claimant_id].readiness_lateness_hours
        and all(
            any(a <= start and end <= b for a, b in indexed[person.claimant_id].uncovered_intervals)
            for start, end in person.uncovered_intervals
        )
        for person in left.claimants
    )


def _relation(left: ProcedureRequirements, right: ProcedureRequirements) -> RepairRelation:
    forward = requirements_contained(left, right)
    reverse = requirements_contained(right, left)
    if forward and reverse:
        return RepairRelation.EQUIVALENT
    if forward:
        return RepairRelation.LEFT_SUBSET
    if reverse:
        return RepairRelation.RIGHT_SUBSET
    return RepairRelation.INCOMPARABLE


def compare_review(report: ReviewReport) -> ReviewComparison:
    """Derive residual profiles from the existing audit, preserving its complete inputs."""
    _same_comparison_duties(report)
    requirements = tuple(_requirements(result) for result in report.results)
    pairs = tuple(
        ProcedureComparison(
            left=left.procedure_id, right=right.procedure_id, relation=_relation(left, right)
        )
        for left, right in combinations(requirements, 2)
    )
    dominated = {
        pair.right if pair.relation == RepairRelation.LEFT_SUBSET else pair.left
        for pair in pairs
        if pair.relation in (RepairRelation.LEFT_SUBSET, RepairRelation.RIGHT_SUBSET)
    }
    return ReviewComparison(
        review=report,
        requirements=requirements,
        comparisons=pairs,
        frontier_procedure_ids=tuple(
            p.procedure_id for p in requirements if p.procedure_id not in dominated
        ),
    )
