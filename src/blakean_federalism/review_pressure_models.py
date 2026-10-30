# Copyright (c) 2026 Daniel Ari Friedman
"""A fixed practical-pressure study, separate from the seven-condition audit."""

from enum import StrEnum
from typing import Annotated, NewType, Self

from pydantic import Field, StringConstraints, model_validator

from .institutional_review_models import (
    ClaimantKey,
    ProcedureKey,
    ReviewInput,
    ReviewProcedure,
)
from .models import Digest, ResearchError

CollectivePartyId = NewType("CollectivePartyId", str)
PartyKey = Annotated[CollectivePartyId, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")]
Note = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1400)]


class PressureIssue(StrEnum):
    MATERIAL_SUPPORT = "material_support"
    REPRISAL = "reprisal"
    REVIEWER_CONTROL = "reviewer_control"
    COLLECTIVE_RESERVATION = "collective_reservation"


class BoundaryStatus(StrEnum):
    STIPULATED_PROTECTION = "stipulated_protection"
    STIPULATED_OBSTRUCTION = "stipulated_obstruction"
    UNASSESSED = "unassessed"


class PressureBoundary(ReviewInput):
    issue: PressureIssue
    status: BoundaryStatus
    rationale: Note


class PressureCase(ReviewInput):
    procedure: ReviewProcedure
    mechanism: Note
    boundaries: Annotated[tuple[PressureBoundary, ...], Field(min_length=4, max_length=4)]

    @model_validator(mode="after")
    def complete_boundaries(self) -> Self:
        if {entry.issue for entry in self.boundaries} != set(PressureIssue):
            raise ResearchError("pressure_boundary_set", "Each distinct pressure issue is required")
        return self


class PressureStudy(ReviewInput):
    schema_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    reference_study_sha256: Digest
    baseline_decisions_sha256: Digest
    reference_procedure_id: ProcedureKey
    affected_person_id: ClaimantKey
    collective_party_id: PartyKey
    cases: Annotated[tuple[PressureCase, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_case_ids(self) -> Self:
        ids = tuple(item.procedure.procedure_id for item in self.cases)
        if len(ids) != len(set(ids)):
            raise ResearchError("duplicate_pressure_case", "Pressure procedure IDs must be unique")
        if self.reference_procedure_id in ids:
            raise ResearchError(
                "pressure_reference_overwrite", "Reference and derived IDs must differ"
            )
        return self
