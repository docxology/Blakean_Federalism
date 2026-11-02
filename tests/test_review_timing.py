# Copyright (c) 2026 Daniel Ari Friedman
"""Finite-grid oracles derive activation from raw inputs, never from audited gaps."""

import json
from pathlib import Path
from typing import assert_never

import pytest
from pydantic import ValidationError

from blakean_federalism.institutional_review_models import ProtectionTrigger
from blakean_federalism.review_timing import build_timing_atlas, timing_figure_data
from blakean_federalism.review_timing_models import TimingMode, TimingSpec

ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def atlas():
    # Given the pinned project-authored study, evaluate the complete declared grid once.
    return build_timing_atlas(ROOT)


def test_union_of_slices_retains_duplicate_membership_once(atlas):
    # When two complete slices intersect, then every logical configuration appears once.
    configurations = [item.configuration for item in atlas.cells]
    assert len(configurations) == len({item.configuration_id for item in configurations}) == 21454
    assert sum("readiness" in item.slices for item in configurations) == 1122
    assert sum("geometry" in item.slices for item in configurations) == 20434
    assert sum(len(item.slices) == 2 for item in configurations) == 102
    assert sum(len(item.review.claimants) for item in atlas.cells) == 42908


def test_every_logical_coordinate_and_slice_membership_matches_input_grid(atlas):
    # Given independent Cartesian sets from raw JSON, compare the entire generated union.
    spec = json.loads((ROOT / "research/review-timing-atlas-v1.json").read_bytes())
    readiness = set()
    for stratum in spec["strata"]:
        bands = {
            "none": None,
            "automatic": (stratum["resident_consequence_hour"], 20),
            "on_filing": (stratum["resident_consequence_hour"], 20),
        }
        readiness.update(
            (stratum["stratum_id"], r, a, mode, band)
            for r in spec["response_hours"]
            for a in spec["resident_ready_hours"]
            for mode, band in bands.items()
        )
    geometry = {
        (s["stratum_id"], r, 6, mode, (a, b))
        for s in spec["strata"]
        for r in spec["response_hours"]
        for mode in ("automatic", "on_filing")
        for a in spec["endpoint_hours"]
        for b in spec["endpoint_hours"]
        if a < b
    } | {
        (s["stratum_id"], r, 6, "none", None)
        for s in spec["strata"]
        for r in spec["response_hours"]
    }
    actual = set()
    for cell in atlas.cells:
        c = cell.configuration
        band = None if c.band is None else (c.band.starts_hour, c.band.ends_hour)
        key = (c.stratum_id, c.response_hour, c.resident_ready_hour, c.mode.value, band)
        actual.add(key)
        assert {s.value for s in c.slices} == ({"readiness"} if key in readiness else set()) | (
            {"geometry"} if key in geometry else set()
        )
    assert actual == readiness | geometry


def test_every_person_matches_raw_activation_hour_set_oracle(atlas):
    # Given original anchor/spec JSON, derive events independently of the produced procedure.
    reference = json.loads((ROOT / "research/institutional-review-cases.json").read_bytes())
    base = next(p for p in reference["procedures"] if p["procedure_id"] == "H12")
    people = {p["claimant_id"]: p for p in base["claimants"]}
    spec = json.loads((ROOT / "research/review-timing-atlas-v1.json").read_bytes())
    threats = {s["stratum_id"]: s["resident_consequence_hour"] for s in spec["strata"]}
    for cell in atlas.cells:
        config = cell.configuration
        audits = {p.claimant_id: p for p in cell.review.claimants}
        expected_predicates = []
        for identity, person in people.items():
            ready = (
                config.resident_ready_hour
                if identity == "resident-b"
                else person["ready_to_file_hour"]
            )
            consequence = (
                threats[config.stratum_id]
                if identity == "resident-b"
                else person["consequence_hour"]
            )
            first = max(base["filing_opens_hour"], ready)
            access = (
                identity in base["admitted_claimant_ids"],
                not person["affiliation_exit_required"],
                person["available_filing_hours"] + person["support_enabled_filing_hours"]
                >= person["required_filing_hours"],
                first <= base["filing_closes_hour"],
            )
            active = set()
            if config.band is not None:
                band = config.band
                start = band.starts_hour
                match config.mode:
                    case TimingMode.AUTOMATIC:
                        pass
                    case TimingMode.ON_FILING:
                        start = max(start, first) if all(access) else band.ends_hour
                    case TimingMode.NONE:
                        raise AssertionError(config.mode)
                    case _:
                        assert_never(config.mode)
                active = set(range(start, band.ends_hour))
            expected = set(range(consequence, config.response_hour)) - active
            actual = audits[identity]
            represented = {h for a, b in actual.uncovered_intervals for h in range(a, b)}
            assert represented == expected
            assert actual.uncovered_wait_hours == len(expected)
            assert actual.conditions == (*access, not expected)
            expected_predicates.append((*access, not expected))
        expected_vector = (
            *(all(p[i] for p in expected_predicates) for i in range(5)),
            base["issuing_office_id"] != base["reviewing_office_id"],
            "revise_act" in base["powers"],
        )
        assert cell.review.conditions == expected_vector
        assert cell.review.declared_conditions_hold == all(expected_vector)


def test_boundary_lemma_is_necessary_and_sufficient(atlas):
    # Given one declared band, then zero exposure has the exact scoped endpoint condition.
    for cell in atlas.cells:
        procedure = cell.review.procedure
        for person, audit in zip(procedure.claimants, cell.review.claimants, strict=True):
            first = max(procedure.filing_opens_hour, person.ready_to_file_hour)
            feasible = (
                person.claimant_id in procedure.admitted_claimant_ids
                and not person.affiliation_exit_required
                and person.available_filing_hours + person.support_enabled_filing_hours
                >= person.required_filing_hours
                and first <= procedure.filing_closes_hour
            )
            predicted = procedure.response_hour <= person.consequence_hour
            band = person.protection
            if band is not None and person.consequence_hour < procedure.response_hour:
                start = band.starts_hour
                available = True
                match band.trigger:
                    case ProtectionTrigger.AUTOMATIC:
                        pass
                    case ProtectionTrigger.ON_FILING:
                        start = max(start, first)
                        available = feasible
                    case unreachable:
                        assert_never(unreachable)
                predicted = (
                    available
                    and start <= person.consequence_hour
                    and procedure.response_hour <= band.ends_hour
                )
            assert (not audit.uncovered_intervals) is predicted


def test_figures_keep_named_people_and_source_cell_membership(atlas):
    # When selecting figure views, then retain both people and each full condition vector.
    data = timing_figure_data(atlas)
    assert len(data.readiness) == 1122
    assert len(data.geometry) == 1200
    assert len(data.timeline_cells) == 4
    assert all(len(item.review.claimants) == 2 for item in data.readiness + data.geometry)
    assert all(len(item.review.conditions) == 7 for item in data.readiness + data.geometry)


@pytest.mark.parametrize("field", ["response_hours", "resident_ready_hours", "endpoint_hours"])
@pytest.mark.parametrize("bad", [True, 2.0, "2", -1])
def test_axes_reject_coercion_and_changed_fixed_grid(field, bad):
    # Given an altered axis, when parsing, then refuse rather than silently change the family.
    data = TimingSpec.model_validate_json(
        (ROOT / "research/review-timing-atlas-v1.json").read_bytes()
    ).model_dump(mode="json")
    data[field][0] = bad
    with pytest.raises(ValidationError):
        TimingSpec.model_validate(data)
