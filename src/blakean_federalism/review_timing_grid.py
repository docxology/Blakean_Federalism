# Copyright (c) 2026 Daniel Ari Friedman
"""Enumerate two overlapping slices into unique named timing configurations."""

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import combinations
from typing import Literal, assert_never

from .institutional_review_models import ProcedureId
from .review_timing_models import (
    TimingBand,
    TimingConfiguration,
    TimingMode,
    TimingSlice,
    TimingSpec,
)


@dataclass(frozen=True, slots=True)
class TimingChoice:
    stratum_id: Literal["original-duty", "early-threat"]
    response_hour: int
    resident_ready_hour: int
    mode: TimingMode
    band: TimingBand | None

    def identifier(self) -> ProcedureId:
        """Keep exact event positions and absence in the stable logical-cell identity."""
        suffix = (
            "absent"
            if self.band is None
            else f"s{self.band.starts_hour:02}.e{self.band.ends_hour:02}"
        )
        prefix = f"T.{self.stratum_id}."
        events = f"r{self.response_hour:02}.a{self.resident_ready_hour:02}.{self.mode.value}."
        return ProcedureId(prefix + events + suffix)


def _band(mode: TimingMode, endpoints: tuple[int, int]) -> TimingBand | None:
    match mode:
        case TimingMode.NONE:
            return None
        case TimingMode.AUTOMATIC | TimingMode.ON_FILING:
            return TimingBand(starts_hour=endpoints[0], ends_hour=endpoints[1])
        case _:
            assert_never(mode)


def _slices(spec: TimingSpec) -> Iterator[tuple[TimingSlice, TimingChoice]]:
    for stratum in spec.strata:
        fixed = (stratum.resident_consequence_hour, spec.readiness_expiry_hour)
        for response in spec.response_hours:
            for ready in spec.resident_ready_hours:
                for mode in TimingMode:
                    yield (
                        TimingSlice.READINESS,
                        TimingChoice(stratum.stratum_id, response, ready, mode, _band(mode, fixed)),
                    )
            for mode in (TimingMode.AUTOMATIC, TimingMode.ON_FILING):
                for endpoints in combinations(spec.endpoint_hours, 2):
                    yield (
                        TimingSlice.GEOMETRY,
                        TimingChoice(
                            stratum.stratum_id,
                            response,
                            spec.geometry_readiness_hour,
                            mode,
                            _band(mode, endpoints),
                        ),
                    )
            yield (
                TimingSlice.GEOMETRY,
                TimingChoice(
                    stratum.stratum_id,
                    response,
                    spec.geometry_readiness_hour,
                    TimingMode.NONE,
                    None,
                ),
            )


def timing_configurations(spec: TimingSpec) -> tuple[TimingConfiguration, ...]:
    """Keep both slice memberships while evaluating each distinct configuration once."""
    choices: dict[ProcedureId, TimingChoice] = {}
    memberships: defaultdict[ProcedureId, list[TimingSlice]] = defaultdict(list)
    for family, choice in _slices(spec):
        identifier = choice.identifier()
        choices[identifier] = choice
        memberships[identifier].append(family)
    return tuple(
        TimingConfiguration(
            configuration_id=identifier,
            stratum_id=choice.stratum_id,
            response_hour=choice.response_hour,
            resident_ready_hour=choice.resident_ready_hour,
            mode=choice.mode,
            band=choice.band,
            slices=tuple(memberships[identifier]),
        )
        for identifier, choice in sorted(choices.items())
    )
