# Copyright (c) 2026 Daniel Ari Friedman
"""Admit one declared timing family without changing historical H/P studies."""

from enum import StrEnum
from typing import Annotated, Literal, Self, assert_never

from pydantic import Field, model_validator

from .institutional_review import ProcedureReview
from .institutional_review_models import Hour, ProcedureKey, ReviewInput
from .models import Assessment, Digest, ResearchError
from .review_pressure_models import BoundaryStatus, PressureBoundary, PressureIssue


class TimingMode(StrEnum):
    NONE = "none"
    AUTOMATIC = "automatic"
    ON_FILING = "on_filing"


class TimingSlice(StrEnum):
    READINESS = "readiness"
    GEOMETRY = "geometry"


class GapTopology(StrEnum):
    EMPTY = "empty"
    INITIAL = "initial"
    TERMINAL = "terminal"
    TWO_COMPONENTS = "two_components"
    WHOLE_WAIT = "whole_wait"


class TimingStratum(ReviewInput):
    stratum_id: Literal["original-duty", "early-threat"]
    resident_consequence_hour: Hour


class TimingSpec(ReviewInput):
    """Schema 1 fixes the two ratified slices; another grid requires a new schema."""

    schema_version: Annotated[int, Field(strict=True, ge=1, le=1)]
    study_id: Literal["review-timing-atlas-v1"]
    reference_study_sha256: Digest
    pressure_study_sha256: Digest
    baseline_decisions_sha256: Digest
    reference_procedure_id: Literal["H12"]
    affected_person_id: Literal["resident-b"]
    collective_party_id: Literal["treaty-people"]
    clock_origin: Literal["notice at hour zero"]
    provider_office_id: Literal["supply-guarantor"]
    response_hours: tuple[Hour, ...]
    resident_ready_hours: tuple[Hour, ...]
    endpoint_hours: tuple[Hour, ...]
    geometry_readiness_hour: Hour
    readiness_expiry_hour: Hour
    strata: Annotated[tuple[TimingStratum, ...], Field(min_length=2, max_length=2)]
    practical_boundaries: Annotated[tuple[PressureBoundary, ...], Field(min_length=4, max_length=4)]

    @model_validator(mode="after")
    def fixed_family(self) -> Self:
        for actual, expected in (
            (self.response_hours, tuple(range(8, 25))),
            (self.resident_ready_hours, tuple(range(11))),
            (self.endpoint_hours, tuple(range(25))),
            ((self.geometry_readiness_hour, self.readiness_expiry_hour), (6, 20)),
        ):
            if actual != expected:
                raise ResearchError("timing_fixed_axes", "Schema 1 requires the declared slices")
        strata = tuple((s.stratum_id, s.resident_consequence_hour) for s in self.strata)
        if strata != (("original-duty", 12), ("early-threat", 3)):
            raise ResearchError("timing_duty_strata", "Keep the two named duties separate")
        if {b.issue for b in self.practical_boundaries} != set(PressureIssue) or any(
            b.status != BoundaryStatus.UNASSESSED for b in self.practical_boundaries
        ):
            raise ResearchError("timing_practical_premises", "All four relations remain unassessed")
        return self


class TimingBand(ReviewInput):
    starts_hour: Annotated[int, Field(strict=True, ge=0, le=24)]
    ends_hour: Annotated[int, Field(strict=True, ge=0, le=24)]

    @model_validator(mode="after")
    def positive(self) -> Self:
        if self.starts_hour >= self.ends_hour:
            raise ResearchError("timing_empty_band", "Require strict half-open protection")
        return self


class TimingConfiguration(ReviewInput):
    configuration_id: ProcedureKey
    stratum_id: Literal["original-duty", "early-threat"]
    response_hour: Annotated[int, Field(strict=True, ge=8, le=24)]
    resident_ready_hour: Annotated[int, Field(strict=True, ge=0, le=10)]
    mode: TimingMode
    band: TimingBand | None
    slices: Annotated[tuple[TimingSlice, ...], Field(min_length=1, max_length=2)]

    @model_validator(mode="after")
    def coherent(self) -> Self:
        match self.mode:
            case TimingMode.NONE:
                if self.band is not None:
                    raise ResearchError("timing_activation_band", "Absence requires no band")
            case TimingMode.AUTOMATIC | TimingMode.ON_FILING:
                if self.band is None:
                    raise ResearchError("timing_activation_band", "Activation requires a band")
            case _:
                assert_never(self.mode)
        if len(self.slices) != len(set(self.slices)):
            raise ResearchError("timing_duplicate_slice", "Retain membership once per slice")
        return self


class TimingCell(ReviewInput):
    configuration: TimingConfiguration
    review: ProcedureReview


class TimingAtlas(ReviewInput):
    specification: TimingSpec
    baseline_assessments: tuple[Assessment, ...]
    cells: tuple[TimingCell, ...]


class TimingGroup(ReviewInput):
    stratum_id: str
    mode: TimingMode
    configurations: int
    resident_zero_gap: int
    member_zero_gap: int
    all_formal_conditions: int
    resident_topologies: dict[GapTopology, int]


class TimingSummary(ReviewInput):
    configurations: int
    person_records: int
    readiness_memberships: int
    geometry_memberships: int
    shared_memberships: int
    groups: tuple[TimingGroup, ...]
    meaning: str = (
        "Two finite stipulated slices, not a joint full grid, institutional population, "
        "probability, pooled-person score or finding of legitimacy."
    )


class TimingFigureData(ReviewInput):
    readiness: tuple[TimingCell, ...]
    geometry: tuple[TimingCell, ...]
    timeline_cells: tuple[TimingCell, ...]
