# Copyright (c) 2026 Daniel Ari Friedman
"""Adverse premises stay outside the atlas and do not disappear into a zero gap."""

from dataclasses import replace
from pathlib import Path
from typing import assert_never

import pytest
from pydantic import ValidationError

from blakean_federalism.institutional_review import ReviewReport
from blakean_federalism.institutional_review_models import ReviewPower, ReviewStudy
from blakean_federalism.models import ResearchError
from blakean_federalism.review_comparison import RepairRelation, compare_review
from blakean_federalism.review_timing import evaluate_timing
from blakean_federalism.review_timing_grid import timing_configurations
from blakean_federalism.review_timing_inputs import load_timing_inputs
from blakean_federalism.review_timing_models import TimingBand, TimingConfiguration, TimingSpec

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def sources():
    return load_timing_inputs(ROOT)


@pytest.fixture(scope="module")
def selected(sources):
    wanted = {
        "T.early-threat.r20.a06.on_filing.s03.e20",
        "T.early-threat.r20.a06.automatic.s03.e20",
        "T.original-duty.r20.a06.automatic.s13.e20",
        "T.original-duty.r20.a06.automatic.s12.e19",
    }
    return {
        c.configuration_id: c
        for c in timing_configurations(sources.specification)
        if c.configuration_id in wanted
    }


@pytest.mark.parametrize("mode", ["automatic", "on_filing"])
@pytest.mark.parametrize("barrier", ["capacity", "admission", "exit", "deadline"])
def test_each_filing_barrier_blocks_only_filing_activation(sources, selected, mode, barrier):
    # Given a distinct adverse premise outside the grid, evaluate the same raw timing cell.
    original = sources.reference
    resident = next(p for p in original.claimants if p.claimant_id == "resident-b")
    changes = {}
    config = selected[f"T.early-threat.r20.a06.{mode}.s03.e20"]
    match barrier:
        case "capacity":
            resident = resident.model_copy(update={"support_enabled_filing_hours": 0})
        case "admission":
            changes["admitted_claimant_ids"] = tuple(
                p for p in original.admitted_claimant_ids if p != "resident-b"
            )
        case "exit":
            resident = resident.model_copy(update={"affiliation_exit_required": True})
        case "deadline":
            config = config.model_copy(update={"resident_ready_hour": 9})
        case unreachable:
            assert_never(unreachable)
    changes["claimants"] = tuple(
        resident if p.claimant_id == "resident-b" else p for p in original.claimants
    )
    inputs = replace(sources, reference=original.model_copy(update=changes))
    result = evaluate_timing(config, inputs).review
    person = next(p for p in result.claimants if p.claimant_id == "resident-b")
    assert not all(person.conditions[:4])
    assert not result.declared_conditions_hold
    assert person.uncovered_intervals == (() if mode == "automatic" else ((3, 20),))
    assert {p.claimant_id for p in result.claimants} == {"resident-b", "member-a"}


@pytest.mark.parametrize("forum", ["same-office", "suspension-only"])
def test_zero_exposure_does_not_establish_forum_predicates(sources, selected, forum):
    # Given full automatic coverage, when a forum premise fails, the conjunction still fails.
    match forum:
        case "same-office":
            updates = {"reviewing_office_id": sources.reference.issuing_office_id}
        case "suspension-only":
            updates = {"powers": (ReviewPower.SUSPEND_ACT,)}
        case unreachable:
            assert_never(unreachable)
    inputs = replace(sources, reference=sources.reference.model_copy(update=updates))
    result = evaluate_timing(selected["T.early-threat.r20.a06.automatic.s03.e20"], inputs).review
    assert all(not p.uncovered_intervals for p in result.claimants)
    assert not all(result.conditions[-2:])
    assert not result.declared_conditions_hold


def test_reordered_people_keep_their_own_events(sources, selected):
    # Given reversed roster order, when evaluated, every named person's result remains the same.
    config = selected["T.early-threat.r20.a06.on_filing.s03.e20"]
    inputs = replace(
        sources,
        reference=sources.reference.model_copy(
            update={"claimants": tuple(reversed(sources.reference.claimants))}
        ),
    )
    normal = evaluate_timing(config, sources).review
    reordered = evaluate_timing(config, inputs).review
    assert {p.claimant_id: p for p in normal.claimants} == {
        p.claimant_id: p for p in reordered.claimants
    }


def test_equal_resident_duration_keeps_different_gap_locations(sources, selected):
    # Given two same-duty one-hour resident gaps, exact residual inclusion is incomparable.
    cells = tuple(
        evaluate_timing(selected[name], sources).review
        for name in (
            "T.original-duty.r20.a06.automatic.s13.e20",
            "T.original-duty.r20.a06.automatic.s12.e19",
        )
    )
    study = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256=sources.specification.baseline_decisions_sha256,
        procedures=tuple(c.procedure for c in cells),
    )
    result = compare_review(ReviewReport(schema_version=1, study=study, results=cells))
    assert result.comparisons[0].relation == RepairRelation.INCOMPARABLE
    residents = [next(p for p in c.claimants if p.claimant_id == "resident-b") for c in cells]
    assert [p.uncovered_wait_hours for p in residents] == [1, 1]
    assert [p.uncovered_intervals for p in residents] == [((12, 13),), ((19, 20),)]


def test_changed_consequence_refuses_cross_stratum_comparison(sources, selected):
    # Given distinct threat times, the existing fixed-duty comparator refuses the pair.
    cells = tuple(
        evaluate_timing(config, sources).review
        for config in (
            selected["T.original-duty.r20.a06.automatic.s12.e19"],
            selected["T.early-threat.r20.a06.automatic.s03.e20"],
        )
    )
    study = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256=sources.specification.baseline_decisions_sha256,
        procedures=tuple(c.procedure for c in cells),
    )
    with pytest.raises(ResearchError, match="review_comparison_duties"):
        compare_review(ReviewReport(schema_version=1, study=study, results=cells))


@pytest.mark.parametrize(
    "edit", ["axes", "strata", "duplicate-boundary", "obstruction", "schema-bool"]
)
def test_fixed_spec_refuses_relabelled_family_or_practical_claim(edit):
    # Given a material alteration, parsing must refuse rather than adopt it under schema 1.
    data = TimingSpec.model_validate_json(
        (ROOT / "research/review-timing-atlas-v1.json").read_bytes()
    ).model_dump(mode="json")
    match edit:
        case "axes":
            data["response_hours"] = data["response_hours"][:-1]
        case "strata":
            data["strata"][1]["resident_consequence_hour"] = 4
        case "duplicate-boundary":
            data["practical_boundaries"][0] = data["practical_boundaries"][1]
        case "obstruction":
            data["practical_boundaries"][0]["status"] = "stipulated_obstruction"
        case "schema-bool":
            data["schema_version"] = True
        case unreachable:
            assert_never(unreachable)
    with pytest.raises((ResearchError, ValidationError)):
        TimingSpec.model_validate(data)


@pytest.mark.parametrize("band", [(3, 3), (4, 3), (-1, 5), (0, 25), (True, 3)])
def test_protection_band_refuses_invalid_endpoints(band):
    # Given invalid endpoints, admission refuses before timing evaluation.
    with pytest.raises((ResearchError, ValidationError)):
        TimingBand(starts_hour=band[0], ends_hour=band[1])


@pytest.mark.parametrize(
    ("mode", "band"), [("none", {"starts_hour": 3, "ends_hour": 20}), ("automatic", None)]
)
def test_absence_and_activation_are_consistent(mode, band):
    # Given contradictory activation, the model must refuse the proposed cell.
    with pytest.raises(ResearchError, match="timing_activation_band"):
        TimingConfiguration.model_validate(
            {
                "configuration_id": "control",
                "stratum_id": "early-threat",
                "response_hour": 20,
                "resident_ready_hour": 6,
                "mode": mode,
                "band": band,
                "slices": ["geometry"],
            }
        )
