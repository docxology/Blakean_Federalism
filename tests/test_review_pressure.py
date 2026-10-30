# Copyright (c) 2026 Daniel Ari Friedman
"""Independent finite-hour and typed-domain controls for the new pressure epoch."""

from pathlib import Path
from typing import Literal, assert_never

import pytest
from pydantic import TypeAdapter

from blakean_federalism.institutional_review_models import ReviewStudy
from blakean_federalism.models import Decision, ResearchError
from blakean_federalism.review_pressure import audit_pressure
from blakean_federalism.review_pressure_models import (
    BoundaryStatus,
    PressureCase,
    PressureIssue,
    PressureStudy,
)

ROOT = Path(__file__).parents[1]


@pytest.fixture
def inputs():
    study = PressureStudy.model_validate_json(
        (ROOT / "research/review-pressure-20261029.json").read_bytes()
    )
    reference = ReviewStudy.model_validate_json(
        (ROOT / "research/institutional-review-cases.json").read_bytes()
    )
    decisions = TypeAdapter(tuple[Decision, ...]).validate_json(
        (ROOT / "research/cases.json").read_bytes()
    )
    return study, reference, decisions


def test_practical_obstruction_never_becomes_an_audit_of_independence(inputs):
    # Given identical formal inputs and distinct practical premises.
    study, reference, decisions = inputs
    # When evaluating the constructed pressure family.
    report = audit_pressure(study, reference, decisions)
    indexed = {item.case.procedure.procedure_id: item for item in report.results}
    # Then the independently stipulated obstruction remains visible beside unchanged access.
    for case_id, issue in (
        ("P05", PressureIssue.REVIEWER_CONTROL),
        ("P06", PressureIssue.COLLECTIVE_RESERVATION),
    ):
        item = indexed[case_id]
        assert item.review.conditions == report.reference.conditions
        assert item.review.declared_conditions_hold
        assert (
            next(row.status for row in item.case.boundaries if row.issue == issue)
            == BoundaryStatus.STIPULATED_OBSTRUCTION
        )


def test_support_withdrawal_preserves_the_other_persons_capacity(inputs):
    # Given the fixed support-withdrawal contrast.
    # When audited using the unchanged person-specific engine.
    report = audit_pressure(*inputs)
    item = next(x for x in report.results if x.case.procedure.procedure_id == "P02")
    people = {person.claimant_id: person for person in item.review.claimants}
    # Then one person's excess time does not cure the other's lost assistance.
    assert people["member-a"].sufficient_hours
    assert not people["resident-b"].sufficient_hours
    assert not item.review.declared_conditions_hold


@pytest.mark.parametrize(
    ("case_id", "expected"),
    [
        ("P04", set(range(3, 10))),
        ("P07", set(range(3, 6))),
        ("P08", set()),
    ],
)
def test_protection_activation_changes_the_actual_exposed_hours(inputs, case_id, expected):
    # Given a consequence at3h with absent, filing-triggered or automatic protection.
    # When the fixed cases are evaluated.
    report = audit_pressure(*inputs)
    item = next(x for x in report.results if x.case.procedure.procedure_id == case_id)
    person = next(x for x in item.review.claimants if x.claimant_id == "resident-b")
    # Then explicit integer-hour sets expose an initial gap rather than only a duration.
    actual = {hour for start, end in person.uncovered_intervals for hour in range(start, end)}
    assert actual == expected
    assert person.uncovered_wait_hours == len(expected)


def test_all_exposure_intervals_match_independent_hour_set_subtraction(inputs):
    # Given every case, person's consequence and actual activated protection.
    report = audit_pressure(*inputs)
    # When independently enumerating exposed integer hours.
    for item in report.results:
        persons = {person.claimant_id: person for person in item.case.procedure.claimants}
        for result in item.review.claimants:
            source = persons[result.claimant_id]
            expected = set(range(source.consequence_hour, item.case.procedure.response_hour))
            if result.active_protection is not None:
                expected -= set(range(*result.active_protection))
            # Then each exact component and total duration agree without reusing interval code.
            actual = {
                hour for start, end in result.uncovered_intervals for hour in range(start, end)
            }
            assert actual == expected
            assert result.uncovered_wait_hours == len(expected)


@pytest.mark.parametrize(
    "change",
    [
        "missing_reference",
        "different_baseline",
        "unknown_person",
        "changed_membership",
        "changed_required_hours",
        "changed_decision",
    ],
)
def test_domain_boundary_rejects_incompatible_reference_duties(
    inputs,
    change: Literal[
        "missing_reference",
        "different_baseline",
        "unknown_person",
        "changed_membership",
        "changed_required_hours",
        "changed_decision",
    ],
):
    # Given a valid study with one independently perturbed identity or duty.
    study, reference, decisions = inputs
    data = study.model_dump(mode="json")
    match change:
        case "missing_reference":
            data["reference_procedure_id"] = "absent"
        case "different_baseline":
            data["baseline_decisions_sha256"] = "0" * 64
        case "unknown_person":
            data["affected_person_id"] = "absent"
        case "changed_membership":
            data["cases"][0]["procedure"]["claimants"][0]["membership"] = "nonmember"
        case "changed_required_hours":
            data["cases"][0]["procedure"]["claimants"][0]["required_filing_hours"] = 3
        case "changed_decision":
            data["cases"][0]["procedure"]["baseline_decision_id"] = "other"
        case unreachable:
            assert_never(unreachable)
    changed = PressureStudy.model_validate(data)
    # When assessing against the retained reference.
    # Then the domain seam refuses rather than normalizing the mismatch.
    with pytest.raises(ResearchError):
        audit_pressure(changed, reference, decisions)


def test_duplicate_practical_issue_cannot_hide_an_omitted_issue(inputs):
    # Given four entries that repeat one issue and omit another.
    data = inputs[0].cases[0].model_dump(mode="json")
    data["boundaries"][-1] = data["boundaries"][0]
    # When parsing the case, then the incomplete boundary set is refused.
    with pytest.raises(ResearchError, match="pressure_boundary_set"):
        PressureCase.model_validate(data)


@pytest.mark.parametrize("same_as_reference", [False, True])
def test_duplicate_or_reference_case_identity_is_refused(inputs, same_as_reference):
    # Given a repeated derived identity or a derived identity colliding with its reference.
    data = inputs[0].model_dump(mode="json")
    if same_as_reference:
        data["cases"][0]["procedure"]["procedure_id"] = data["reference_procedure_id"]
    else:
        data["cases"].append(data["cases"][0])
    # When parsing the study, then the ambiguous identity is refused.
    with pytest.raises(ResearchError):
        PressureStudy.model_validate(data)
