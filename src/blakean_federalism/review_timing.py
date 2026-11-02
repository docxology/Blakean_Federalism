# Copyright (c) 2026 Daniel Ari Friedman
"""Evaluate person-specific activation and keep timing topologies inspectable."""

from collections import Counter
from pathlib import Path
from typing import Final, assert_never

from .institutional_review import audit_review
from .institutional_review_models import (
    ClaimantId,
    InterimProtection,
    OfficeId,
    ProcedureId,
    ProtectionTrigger,
    ReviewClaimant,
    ReviewStudy,
)
from .review_inputs import linked_assessments
from .review_timing_grid import timing_configurations
from .review_timing_inputs import TimingInputs, load_timing_inputs
from .review_timing_models import (
    GapTopology,
    TimingAtlas,
    TimingCell,
    TimingConfiguration,
    TimingFigureData,
    TimingGroup,
    TimingMode,
    TimingSlice,
    TimingSummary,
)

MEMBER: Final = ClaimantId("member-a")
RESIDENT: Final = ClaimantId("resident-b")
_SLICE_COUNT: Final = len(TimingSlice)


def _person(
    original: ReviewClaimant, config: TimingConfiguration, inputs: TimingInputs
) -> ReviewClaimant:
    band = config.band
    protection: InterimProtection | None = None
    if band is not None:
        match config.mode:
            case TimingMode.AUTOMATIC:
                trigger = ProtectionTrigger.AUTOMATIC
            case TimingMode.ON_FILING:
                trigger = ProtectionTrigger.ON_FILING
            case TimingMode.NONE:
                # TimingConfiguration rejects a band in this mode at admission.
                raise AssertionError(config.mode)
            case _:
                assert_never(config.mode)
        protection = InterimProtection(
            provider_office_id=OfficeId(inputs.specification.provider_office_id),
            starts_hour=band.starts_hour,
            ends_hour=band.ends_hour,
            trigger=trigger,
        )
    ready, consequence = original.ready_to_file_hour, original.consequence_hour
    if original.claimant_id == inputs.specification.affected_person_id:
        ready = config.resident_ready_hour
        consequence = next(
            s.resident_consequence_hour
            for s in inputs.specification.strata
            if s.stratum_id == config.stratum_id
        )
    return original.model_copy(
        update={
            "ready_to_file_hour": ready,
            "consequence_hour": consequence,
            "protection": protection,
        }
    )


def evaluate_timing(config: TimingConfiguration, inputs: TimingInputs) -> TimingCell:
    """Reuse the declared access audit; never pool capacities or infer practical safety."""
    procedure = inputs.reference.model_copy(
        update={
            "procedure_id": ProcedureId(config.configuration_id),
            "label": "Stipulated timing configuration",
            "response_hour": config.response_hour,
            "claimants": tuple(_person(p, config, inputs) for p in inputs.reference.claimants),
        }
    )
    study = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256=inputs.specification.baseline_decisions_sha256,
        procedures=(procedure,),
    )
    return TimingCell(configuration=config, review=audit_review(study).results[0])


def build_timing_atlas(root: Path) -> TimingAtlas:
    """Read the four pinned sources and evaluate the complete fixed two-slice family."""
    return atlas_from_inputs(load_timing_inputs(root))


def atlas_from_inputs(inputs: TimingInputs) -> TimingAtlas:
    study = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256=inputs.specification.baseline_decisions_sha256,
        procedures=(inputs.reference,),
    )
    return TimingAtlas(
        specification=inputs.specification,
        baseline_assessments=linked_assessments(study, inputs.decisions),
        cells=tuple(
            evaluate_timing(c, inputs) for c in timing_configurations(inputs.specification)
        ),
    )


def gap_topology(cell: TimingCell, claimant: str) -> GapTopology:
    audit = next(p for p in cell.review.claimants if p.claimant_id == claimant)
    person = next(p for p in cell.review.procedure.claimants if p.claimant_id == claimant)
    gaps = audit.uncovered_intervals
    if not gaps:
        return GapTopology.EMPTY
    if gaps == ((person.consequence_hour, cell.review.procedure.response_hour),):
        return GapTopology.WHOLE_WAIT
    if len(gaps) > 1:
        return GapTopology.TWO_COMPONENTS
    if next(iter(gaps))[0] == person.consequence_hour:
        return GapTopology.INITIAL
    return GapTopology.TERMINAL


def timing_summary(atlas: TimingAtlas) -> TimingSummary:
    """Report descriptive denominators per duty and activation, with no scalar objective."""
    groups: list[TimingGroup] = []
    for stratum in atlas.specification.strata:
        for mode in TimingMode:
            cells = tuple(
                c
                for c in atlas.cells
                if c.configuration.stratum_id == stratum.stratum_id and c.configuration.mode == mode
            )
            zeros = Counter(
                p.claimant_id
                for c in cells
                for p in c.review.claimants
                if not p.uncovered_intervals
            )
            groups.append(
                TimingGroup(
                    stratum_id=stratum.stratum_id,
                    mode=mode,
                    configurations=len(cells),
                    resident_zero_gap=zeros[RESIDENT],
                    member_zero_gap=zeros[MEMBER],
                    all_formal_conditions=sum(c.review.declared_conditions_hold for c in cells),
                    resident_topologies=dict(Counter(gap_topology(c, RESIDENT) for c in cells)),
                )
            )
    return TimingSummary(
        configurations=len(atlas.cells),
        person_records=sum(len(c.review.claimants) for c in atlas.cells),
        readiness_memberships=sum(
            TimingSlice.READINESS in c.configuration.slices for c in atlas.cells
        ),
        geometry_memberships=sum(
            TimingSlice.GEOMETRY in c.configuration.slices for c in atlas.cells
        ),
        shared_memberships=sum(len(c.configuration.slices) == _SLICE_COUNT for c in atlas.cells),
        groups=tuple(groups),
    )


def timing_figure_data(atlas: TimingAtlas) -> TimingFigureData:
    """Retain named source cells and both people's vectors for each figure selection."""
    selected = {
        "T.original-duty.r20.a06.automatic.s13.e20",
        "T.original-duty.r20.a06.automatic.s12.e19",
        "T.early-threat.r20.a06.automatic.s03.e20",
        "T.early-threat.r20.a06.on_filing.s03.e20",
    }
    return TimingFigureData(
        readiness=tuple(c for c in atlas.cells if TimingSlice.READINESS in c.configuration.slices),
        geometry=tuple(
            c
            for c in atlas.cells
            if TimingSlice.GEOMETRY in c.configuration.slices
            and c.configuration.response_hour == atlas.specification.readiness_expiry_hour
            and c.configuration.band is not None
        ),
        timeline_cells=tuple(
            c for c in atlas.cells if c.configuration.configuration_id in selected
        ),
    )
