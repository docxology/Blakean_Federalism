# Copyright (c) 2026 Daniel Ari Friedman
"""Evaluate seven declared review conditions without pooling people's access."""

from blake.methods.intervals import Interval as SupportInterval
from blake.methods.intervals import interval_difference
from pydantic import computed_field

from blakean_federalism.institutional_review_models import (
    ClaimantId,
    ProtectionTrigger,
    ReviewClaimant,
    ReviewInput,
    ReviewPower,
    ReviewProcedure,
    ReviewStudy,
)

Interval = tuple[int, int]


class ClaimantReview(ReviewInput):
    claimant_id: ClaimantId
    standing: bool
    may_remain: bool
    sufficient_hours: bool
    filing_ready: bool
    earliest_filing_hour: int
    active_protection: Interval | None
    uncovered_intervals: tuple[Interval, ...]

    @computed_field
    @property
    def uncovered_wait_hours(self) -> int:
        return sum(end - start for start, end in self.uncovered_intervals)

    @computed_field
    @property
    def timely_response_or_protection(self) -> bool:
        return not self.uncovered_intervals

    @computed_field
    @property
    def conditions(self) -> tuple[bool, ...]:
        return (
            self.standing,
            self.may_remain,
            self.sufficient_hours,
            self.filing_ready,
            self.timely_response_or_protection,
        )


class ProcedureReview(ReviewInput):
    procedure: ReviewProcedure
    claimants: tuple[ClaimantReview, ...]
    issuer_separated_forum: bool
    revision_power: bool
    suspension_power: bool

    @computed_field
    @property
    def conditions(self) -> tuple[bool, ...]:
        per_person = tuple(all(row.conditions[i] for row in self.claimants) for i in range(5))
        return (*per_person, self.issuer_separated_forum, self.revision_power)

    @computed_field
    @property
    def declared_conditions_hold(self) -> bool:
        return all(self.conditions)


class ReviewReport(ReviewInput):
    schema_version: int
    study: ReviewStudy
    results: tuple[ProcedureReview, ...]


def _uncovered(start: int, end: int, protection: Interval | None) -> tuple[Interval, ...]:
    """Keep the response-first policy here; delegate positive support geometry."""
    if start >= end:
        return ()
    active = (
        () if protection is None else (SupportInterval(start=protection[0], end=protection[1]),)
    )
    return tuple(
        (span.start, span.end)
        for span in interval_difference((SupportInterval(start=start, end=end),), active)
    )


def audit_claimant(procedure: ReviewProcedure, person: ReviewClaimant) -> ClaimantReview:
    standing = person.claimant_id in procedure.admitted_claimant_ids
    remain = not person.affiliation_exit_required
    hours = (
        person.available_filing_hours + person.support_enabled_filing_hours
        >= person.required_filing_hours
    )
    earliest = max(procedure.filing_opens_hour, person.ready_to_file_hour)
    ready = earliest <= procedure.filing_closes_hour
    active: Interval | None = None
    if person.protection is not None:
        protection = person.protection
        match protection.trigger:
            case ProtectionTrigger.AUTOMATIC:
                active = (protection.starts_hour, protection.ends_hour)
            case ProtectionTrigger.ON_FILING:
                if standing and remain and hours and ready:
                    start = max(protection.starts_hour, earliest)
                    if start < protection.ends_hour:
                        active = (start, protection.ends_hour)
    return ClaimantReview(
        claimant_id=person.claimant_id,
        standing=standing,
        may_remain=remain,
        sufficient_hours=hours,
        filing_ready=ready,
        earliest_filing_hour=earliest,
        active_protection=active,
        uncovered_intervals=_uncovered(person.consequence_hour, procedure.response_hour, active),
    )


def audit_review(study: ReviewStudy) -> ReviewReport:
    return ReviewReport(
        schema_version=1,
        study=study,
        results=tuple(
            ProcedureReview(
                procedure=procedure,
                claimants=tuple(
                    audit_claimant(procedure, person) for person in procedure.claimants
                ),
                issuer_separated_forum=procedure.issuing_office_id != procedure.reviewing_office_id,
                revision_power=ReviewPower.REVISE_ACT in procedure.powers,
                suspension_power=ReviewPower.SUSPEND_ACT in procedure.powers,
            )
            for procedure in study.procedures
        ),
    )
