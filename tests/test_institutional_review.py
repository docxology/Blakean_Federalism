# Copyright (c) 2026 Daniel Ari Friedman
"""Finite controls for person-specific review access and temporal protection."""

import pytest
from pydantic import ValidationError

from blakean_federalism.institutional_review import audit_review
from blakean_federalism.institutional_review_models import ReviewProcedure, ReviewStudy


@pytest.fixture
def procedure():
    return ReviewProcedure.model_validate(
        {
            "procedure_id": "oracle",
            "label": "Synthetic review oracle",
            "baseline_decision_id": "E-bounded",
            "issuing_office_id": "issuer",
            "reviewing_office_id": "reviewer",
            "filing_opens_hour": 0,
            "filing_closes_hour": 10,
            "response_hour": 20,
            "admitted_claimant_ids": ["person"],
            "powers": ["suspend_act", "revise_act"],
            "claimants": [
                {
                    "claimant_id": "person",
                    "membership": "nonmember",
                    "affiliation_exit_required": False,
                    "available_filing_hours": 2,
                    "support_enabled_filing_hours": 1,
                    "required_filing_hours": 3,
                    "ready_to_file_hour": 2,
                    "consequence_hour": 8,
                    "protection": {
                        "provider_office_id": "protector",
                        "starts_hour": 8,
                        "ends_hour": 20,
                        "trigger": "automatic",
                    },
                }
            ],
        }
    )


def result_for(procedure: ReviewProcedure):
    return audit_review(
        ReviewStudy(
            schema_version=1,
            baseline_decisions_sha256="0" * 64,
            procedures=(procedure,),
        )
    ).results[0]


def test_all_seven_conditions_hold_at_exact_protection_boundary(procedure):
    # Given exact coverage [8,20), when audited, then equality at response closes every gap.
    result = result_for(procedure)
    assert result.conditions == (True,) * 7
    assert result.declared_conditions_hold
    assert result.claimants[0].uncovered_wait_hours == 0


@pytest.mark.parametrize(
    ("field", "value", "expected_gap"),
    [("ends_hour", 19, ((19, 20),)), ("starts_hour", 9, ((8, 9),))],
)
def test_one_hour_protection_gap_is_exposed(procedure, field, value, expected_gap):
    # Given an interval missing one endpoint hour, when audited, then retain that exact gap.
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["protection"][field] = value
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.claimants[0].uncovered_intervals == expected_gap
    assert result.claimants[0].uncovered_wait_hours == 1
    assert not result.declared_conditions_hold


@pytest.mark.parametrize("consequence", [20, 21])
def test_response_at_or_before_consequence_needs_no_protection(procedure, consequence):
    # Given response no later than consequence, when audited, then no wait is uncovered.
    data = procedure.model_dump(mode="json")
    data["claimants"][0].update(consequence_hour=consequence, protection=None)
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.declared_conditions_hold
    assert result.claimants[0].uncovered_intervals == ()


@pytest.mark.parametrize(("ready", "passes"), [(10, True), (11, False)])
def test_readiness_deadline_is_inclusive(procedure, ready, passes):
    # Given completed prerequisites at or after closing, when audited, then test the deadline.
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["ready_to_file_hour"] = ready
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.claimants[0].filing_ready is passes
    assert result.declared_conditions_hold is passes


def test_hours_are_not_pooled_between_people(procedure):
    # Given enough aggregate capacity but one person's deficit, when audited, then it fails.
    data = procedure.model_dump(mode="json")
    person = data["claimants"][0]
    person["support_enabled_filing_hours"] = 0
    second = person | {"claimant_id": "other", "available_filing_hours": 4}
    data["claimants"].append(second)
    data["admitted_claimant_ids"].append("other")
    result = result_for(ReviewProcedure.model_validate(data))
    assert sum(p.available_filing_hours for p in result.procedure.claimants) == 6
    assert [p.sufficient_hours for p in result.claimants] == [False, True]
    assert not result.declared_conditions_hold


@pytest.mark.parametrize(("trigger", "active"), [("automatic", (8, 20)), ("on_filing", None)])
@pytest.mark.parametrize("barrier", ["hours", "standing", "remain", "ready"])
def test_filing_trigger_requires_actual_access(procedure, trigger, active, barrier):
    # Given a barrier to filing, when audited, then filing cannot activate protection.
    data = procedure.model_dump(mode="json")
    match barrier:
        case "hours":
            data["claimants"][0]["available_filing_hours"] = 0
        case "standing":
            data["admitted_claimant_ids"] = []
        case "remain":
            data["claimants"][0]["affiliation_exit_required"] = True
        case "ready":
            data["claimants"][0]["ready_to_file_hour"] = 11
    data["claimants"][0]["protection"]["trigger"] = trigger
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.claimants[0].active_protection == active
    assert result.claimants[0].timely_response_or_protection is (active is not None)


def test_filing_protection_starts_at_earliest_actual_filing(procedure):
    # Given readiness after consequence, when filed, then early declared protection cannot backdate.
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["ready_to_file_hour"] = 9
    data["claimants"][0]["protection"]["trigger"] = "on_filing"
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.claimants[0].active_protection == (9, 20)
    assert result.claimants[0].uncovered_intervals == ((8, 9),)


def test_protection_expired_before_filing_has_no_active_interval(procedure):
    # Given protection ending before filing is possible, when audited, then none activates.
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["ready_to_file_hour"] = 9
    data["claimants"][0]["protection"].update(starts_hour=1, ends_hour=8, trigger="on_filing")
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.claimants[0].active_protection is None
    assert result.claimants[0].uncovered_intervals == ((8, 20),)


@pytest.mark.parametrize(
    ("start", "end", "gaps"),
    [(0, 8, ((8, 20),)), (20, 22, ((8, 20),)), (9, 19, ((8, 9), (19, 20)))],
)
def test_protection_outside_or_inside_wait_preserves_exact_components(procedure, start, end, gaps):
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["protection"].update(starts_hour=start, ends_hour=end)
    audit = result_for(ReviewProcedure.model_validate(data)).claimants[0]
    assert audit.uncovered_intervals == gaps
    assert audit.uncovered_wait_hours == sum(b - a for a, b in gaps)


@pytest.mark.parametrize(
    "condition", ["excluded_nonmember", "exit_required", "same_office", "advisory"]
)
def test_procedural_controls_fail_their_specific_condition(procedure, condition):
    # Given one deliberate procedural failure, when audited, then exactly its condition fails.
    data = procedure.model_dump(mode="json")
    indexes = {"excluded_nonmember": 0, "exit_required": 1, "same_office": 5, "advisory": 6}
    match condition:
        case "excluded_nonmember":
            data["admitted_claimant_ids"] = []
        case "exit_required":
            data["claimants"][0]["affiliation_exit_required"] = True
        case "same_office":
            data["reviewing_office_id"] = data["issuing_office_id"]
        case "advisory":
            data["powers"] = ["suspend_act"]
    result = result_for(ReviewProcedure.model_validate(data))
    assert [i for i, value in enumerate(result.conditions) if not value] == [indexes[condition]]


def test_revision_power_does_not_require_suspension_power(procedure):
    # Given revision and independent interim protection, when audited, then all conditions hold.
    data = procedure.model_dump(mode="json")
    data["powers"] = ["revise_act"]
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.declared_conditions_hold
    assert not result.suspension_power


def test_unassessed_issue_survives_all_conditions_holding(procedure):
    # Given retaliation outside the seven predicates, when audited, then no conclusion erases it.
    data = procedure.model_dump(mode="json")
    data["unassessed_issues"] = ["retaliation"]
    result = result_for(ReviewProcedure.model_validate(data))
    assert result.declared_conditions_hold
    assert tuple(result.procedure.unassessed_issues) == ("retaliation",)


@pytest.mark.parametrize("value", [-1, True, 1.5, "1"])
def test_hours_require_strict_nonnegative_integers(procedure, value):
    # Given a non-hour input, when parsed at the boundary, then reject it.
    data = procedure.model_dump(mode="json")
    data["claimants"][0]["available_filing_hours"] = value
    with pytest.raises(ValidationError):
        ReviewProcedure.model_validate(data)


@pytest.mark.parametrize(
    "failure", ["identity", "admitted", "dangling", "order", "interval", "capacity"]
)
def test_incoherent_procedure_is_rejected(procedure, failure):
    # Given an incoherent declaration, when parsed, then no audit can consume it.
    data = procedure.model_dump(mode="json")
    match failure:
        case "identity":
            data["claimants"].append(data["claimants"][0])
        case "admitted":
            data["admitted_claimant_ids"].append("person")
        case "dangling":
            data["admitted_claimant_ids"] = ["missing"]
        case "order":
            data["response_hour"] = 9
        case "interval":
            data["claimants"][0]["protection"]["ends_hour"] = 8
        case "capacity":
            data["claimants"][0]["available_filing_hours"] = 10
    with pytest.raises(ValidationError):
        ReviewProcedure.model_validate(data)


@pytest.mark.parametrize(
    "failure",
    ["duplicate_procedure", "duplicate_selection", "missing_procedure", "missing_person"],
)
def test_study_identity_links_are_validated(procedure, failure):
    # Given duplicate or dangling study links, when parsed, then reject ambiguous identities.
    data = {
        "schema_version": 1,
        "baseline_decisions_sha256": "0" * 64,
        "procedures": [procedure.model_dump(mode="json")],
        "timeline_selections": [{"procedure_id": "oracle", "claimant_id": "person"}],
    }
    match failure:
        case "duplicate_procedure":
            data["procedures"].append(data["procedures"][0])
        case "duplicate_selection":
            data["timeline_selections"].append(data["timeline_selections"][0])
        case "missing_procedure":
            data["timeline_selections"][0]["procedure_id"] = "missing"
        case "missing_person":
            data["timeline_selections"][0]["claimant_id"] = "missing"
    with pytest.raises(ValidationError):
        ReviewStudy.model_validate(data)
