# Copyright (c) 2026 Daniel Ari Friedman
"""Person-specific inputs for a stipulated institutional review-access audit."""

from enum import StrEnum
from typing import Annotated, ClassVar, NewType, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

ClaimantId = NewType("ClaimantId", str)
OfficeId = NewType("OfficeId", str)
ProcedureId = NewType("ProcedureId", str)
_KEY = StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
ClaimantKey = Annotated[ClaimantId, _KEY]
OfficeKey = Annotated[OfficeId, _KEY]
ProcedureKey = Annotated[ProcedureId, _KEY]
Hour = Annotated[int, Field(strict=True, ge=0)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class ReviewInput(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")


class Membership(StrEnum):
    MEMBER = "member"
    NONMEMBER = "nonmember"


class ReviewPower(StrEnum):
    SUSPEND_ACT = "suspend_act"
    REVISE_ACT = "revise_act"


class ProtectionTrigger(StrEnum):
    AUTOMATIC = "automatic"
    ON_FILING = "on_filing"


class UnassessedIssue(StrEnum):
    RETALIATION = "retaliation"
    FORUM_COMPETENCE = "disputed_forum_competence"


class InterimProtection(ReviewInput):
    provider_office_id: OfficeKey
    starts_hour: Hour
    ends_hour: Hour
    trigger: ProtectionTrigger

    @model_validator(mode="after")
    def ordered_interval(self) -> Self:
        if self.starts_hour >= self.ends_hour:
            raise ValueError("protection_interval_empty_or_reversed")
        return self


class ReviewClaimant(ReviewInput):
    claimant_id: ClaimantKey
    membership: Membership
    affiliation_exit_required: Annotated[bool, Field(strict=True)]
    available_filing_hours: Hour
    support_enabled_filing_hours: Hour
    required_filing_hours: Hour
    ready_to_file_hour: Hour
    consequence_hour: Hour
    protection: InterimProtection | None = None


class ReviewProcedure(ReviewInput):
    procedure_id: ProcedureKey
    label: Label
    baseline_decision_id: Annotated[str, _KEY]
    issuing_office_id: OfficeKey
    reviewing_office_id: OfficeKey
    filing_opens_hour: Hour
    filing_closes_hour: Hour
    response_hour: Hour
    admitted_claimant_ids: tuple[ClaimantKey, ...]
    powers: tuple[ReviewPower, ...]
    claimants: Annotated[tuple[ReviewClaimant, ...], Field(min_length=1)]
    unassessed_issues: tuple[UnassessedIssue, ...] = ()

    @model_validator(mode="after")
    def coherent_procedure(self) -> Self:
        if not self.filing_opens_hour <= self.filing_closes_hour <= self.response_hour:
            raise ValueError("review_events_out_of_order")
        identities = tuple(person.claimant_id for person in self.claimants)
        for values in (identities, self.admitted_claimant_ids, self.powers, self.unassessed_issues):
            if len(values) != len(set(values)):
                raise ValueError("duplicate_review_identity_or_enum")
        if not set(self.admitted_claimant_ids).issubset(identities):
            raise ValueError("admitted_claimant_not_listed")
        window_hours = self.filing_closes_hour - self.filing_opens_hour
        if any(
            person.available_filing_hours + person.support_enabled_filing_hours > window_hours
            for person in self.claimants
        ):
            raise ValueError("declared_hours_exceed_filing_window")
        return self


class TimelineSelection(ReviewInput):
    procedure_id: ProcedureKey
    claimant_id: ClaimantKey


class ReviewStudy(ReviewInput):
    schema_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    baseline_decisions_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    procedures: Annotated[tuple[ReviewProcedure, ...], Field(min_length=1)]
    timeline_selections: tuple[TimelineSelection, ...] = ()

    @model_validator(mode="after")
    def linked_selections(self) -> Self:
        procedures = {item.procedure_id: item for item in self.procedures}
        if len(procedures) != len(self.procedures):
            raise ValueError("duplicate_procedure_id")
        selections = tuple((x.procedure_id, x.claimant_id) for x in self.timeline_selections)
        if len(selections) != len(set(selections)):
            raise ValueError("duplicate_timeline_selection")
        for procedure_id, claimant_id in selections:
            if procedure_id not in procedures or claimant_id not in {
                person.claimant_id for person in procedures[procedure_id].claimants
            }:
                raise ValueError("timeline_selection_not_listed")
        return self
