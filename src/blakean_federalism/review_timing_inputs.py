# Copyright (c) 2026 Daniel Ari Friedman
"""Pin the declared atlas to the retained H12, pressure and decision sources."""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Final

from pydantic import TypeAdapter

from .institutional_review_models import ProcedureId, ReviewProcedure, ReviewStudy
from .models import Decision, ResearchError
from .review_pressure import audit_pressure
from .review_pressure_models import PressureStudy
from .review_timing_models import TimingSpec
from .storage import safe_path

SPEC: Final = "research/review-timing-atlas-v1.json"
REFERENCE: Final = "research/institutional-review-cases.json"
PRESSURE: Final = "research/review-pressure-20261029.json"
DECISIONS: Final = "research/cases.json"
INPUT_NAMES: Final = (SPEC, REFERENCE, PRESSURE, DECISIONS)


@dataclass(frozen=True, slots=True)
class TimingInputBytes:
    name: str
    content: bytes


@dataclass(frozen=True, slots=True)
class TimingInputs:
    specification: TimingSpec
    reference: ReviewProcedure
    decisions: tuple[Decision, ...]
    files: tuple[TimingInputBytes, ...]


def load_timing_inputs(root: Path) -> TimingInputs:
    """Parse all inputs and verify the H12/pressure linkage before reserving output."""
    payloads = {name: safe_path(root, name).read_bytes() for name in INPUT_NAMES}
    spec = TimingSpec.model_validate_json(payloads[SPEC])
    for name, expected in (
        (REFERENCE, spec.reference_study_sha256),
        (PRESSURE, spec.pressure_study_sha256),
        (DECISIONS, spec.baseline_decisions_sha256),
    ):
        if sha256(payloads[name]).hexdigest() != expected:
            raise ResearchError("timing_input_hash", name)
    reference = ReviewStudy.model_validate_json(payloads[REFERENCE])
    pressure = PressureStudy.model_validate_json(payloads[PRESSURE])
    decisions = TypeAdapter(tuple[Decision, ...]).validate_json(payloads[DECISIONS])
    if (
        reference.baseline_decisions_sha256 != spec.baseline_decisions_sha256
        or pressure.baseline_decisions_sha256 != spec.baseline_decisions_sha256
        or pressure.reference_study_sha256 != spec.reference_study_sha256
        or pressure.reference_procedure_id != spec.reference_procedure_id
        or pressure.affected_person_id != spec.affected_person_id
        or pressure.collective_party_id != spec.collective_party_id
    ):
        raise ResearchError(
            "timing_anchor_bindings", "Retained anchors must agree with actual inputs"
        )
    _ = audit_pressure(pressure, reference, decisions)
    derived = {c.procedure.procedure_id: c.procedure for c in pressure.cases}
    early_threat = next(
        s.resident_consequence_hour for s in spec.strata if s.stratum_id == "early-threat"
    )
    for identifier in (ProcedureId("P04"), ProcedureId("P07"), ProcedureId("P08")):
        if identifier not in derived or not any(
            p.claimant_id == spec.affected_person_id and p.consequence_hour == early_threat
            for p in derived[identifier].claimants
        ):
            raise ResearchError("timing_pressure_anchor", "The early threat retains P04/P07/P08")
    original = next(
        p for p in reference.procedures if p.procedure_id == spec.reference_procedure_id
    )
    _require_reference(original)
    return TimingInputs(
        spec,
        original,
        decisions,
        tuple(TimingInputBytes(name, payloads[name]) for name in INPUT_NAMES),
    )


def _require_reference(procedure: ReviewProcedure) -> None:
    """Keep the named capacities/duties fixed even if input hashes are intentionally repinned."""
    people = sorted(
        (
            p.claimant_id,
            p.membership.value,
            p.affiliation_exit_required,
            p.available_filing_hours,
            p.support_enabled_filing_hours,
            p.required_filing_hours,
            p.ready_to_file_hour,
            p.consequence_hour,
            p.protection,
        )
        for p in procedure.claimants
    )
    if people != [
        ("member-a", "member", False, 6, 0, 4, 4, 18, None),
        ("resident-b", "nonmember", False, 1, 3, 4, 6, 12, None),
    ] or (
        procedure.baseline_decision_id != "E-bounded"
        or procedure.issuing_office_id != "water-board"
        or procedure.reviewing_office_id != "review-panel"
        or (procedure.filing_opens_hour, procedure.filing_closes_hour) != (2, 8)
        or set(procedure.admitted_claimant_ids) != {"member-a", "resident-b"}
        or tuple(p.value for p in procedure.powers) != ("revise_act",)
    ):
        raise ResearchError("timing_reference_contract", "Schema 1 fixes the H12 roster and duties")
