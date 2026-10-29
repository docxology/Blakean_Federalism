# Copyright (c) 2026 Daniel Ari Friedman
"""Independent finite examples for exact person-indexed requirement inclusion."""

from itertools import product
from pathlib import Path

import pytest
from pydantic import JsonValue, ValidationError

from blakean_federalism.institutional_review import audit_review
from blakean_federalism.institutional_review_models import ReviewProcedure, ReviewStudy
from blakean_federalism.models import ResearchError
from blakean_federalism.review_comparison import RepairRelation, compare_review

ROOT = Path(__file__).parents[1]


@pytest.fixture
def example():
    # Given a small independent clock, both people can file and have [5,12) protection.
    return {
        "procedure_id": "A",
        "label": "Independent numerical example",
        "baseline_decision_id": "fixed",
        "issuing_office_id": "issuer",
        "reviewing_office_id": "reviewer",
        "filing_opens_hour": 0,
        "filing_closes_hour": 4,
        "response_hour": 12,
        "admitted_claimant_ids": ["one", "two"],
        "powers": ["revise_act"],
        "claimants": [
            {
                "claimant_id": name,
                "membership": membership,
                "affiliation_exit_required": False,
                "available_filing_hours": 2,
                "support_enabled_filing_hours": 1,
                "required_filing_hours": 3,
                "ready_to_file_hour": 2,
                "consequence_hour": 5,
                "protection": {
                    "provider_office_id": "provider",
                    "starts_hour": 5,
                    "ends_hour": 12,
                    "trigger": "automatic",
                },
            }
            for name, membership in (("one", "member"), ("two", "nonmember"))
        ],
    }


def compare(*procedures: dict[str, JsonValue]):
    study = ReviewStudy(
        schema_version=1,
        baseline_decisions_sha256="0" * 64,
        procedures=tuple(ReviewProcedure.model_validate(p) for p in procedures),
    )
    return compare_review(audit_review(study))


def test_timing_only_changes_preserve_unequal_gaps_at_equal_duration(example):
    # Given equal one-hour exposures at opposite ends, when compared, neither contains the other.
    left = ReviewProcedure.model_validate(example).model_dump(mode="json")
    right = ReviewProcedure.model_validate(example).model_dump(mode="json")
    left["claimants"][1]["protection"]["starts_hour"] = 6
    right["procedure_id"] = "B"
    right["claimants"][1]["protection"]["ends_hour"] = 11
    result = compare(left, right)
    assert result.comparisons[0].relation == RepairRelation.INCOMPARABLE
    assert result.requirements[0].claimants[1].uncovered_intervals == ((5, 6),)
    assert result.requirements[1].claimants[1].uncovered_intervals == ((11, 12),)
    assert result.frontier_procedure_ids == ("A", "B")


def test_people_cannot_trade_standing_against_each_other(example):
    # Given a different excluded person in each procedure, when compared, retain the tradeoff.
    left = example | {"admitted_claimant_ids": ["one"]}
    right = example | {"procedure_id": "B", "admitted_claimant_ids": ["two"]}
    result = compare(left, right)
    assert result.comparisons[0].relation == RepairRelation.INCOMPARABLE


def test_nested_gaps_have_a_strict_requirement_frontier(example):
    # Given [5,6) versus [5,12), when compared, the smaller gap is the unique frontier.
    left = ReviewProcedure.model_validate(example).model_dump(mode="json")
    right = ReviewProcedure.model_validate(example).model_dump(mode="json")
    left["claimants"][1]["protection"]["starts_hour"] = 6
    right["procedure_id"] = "B"
    right["claimants"][1]["protection"] = None
    result = compare(right, left)
    assert result.comparisons[0].relation == RepairRelation.RIGHT_SUBSET
    assert result.frontier_procedure_ids == ("A",)


def test_numeric_shortfalls_remain_distinct_when_boolean_failures_match(example):
    # Given one versus two missing hours, when compared, categorical equality is insufficient.
    left = ReviewProcedure.model_validate(example).model_dump(mode="json")
    right = ReviewProcedure.model_validate(example).model_dump(mode="json")
    left["claimants"][1]["support_enabled_filing_hours"] = 0
    right["procedure_id"] = "B"
    right["claimants"][1].update(available_filing_hours=1, support_enabled_filing_hours=0)
    result = compare(left, right)
    assert result.comparisons[0].relation == RepairRelation.LEFT_SUBSET
    assert [r.claimants[1].preparation_shortfall_hours for r in result.requirements] == [1, 2]


def test_suspension_and_unassessed_issues_do_not_become_modeled_repair_requirements(example):
    # Given suspension and retaliation differences, when compared, preserve the flags separately.
    right = example | {
        "procedure_id": "B",
        "powers": ["revise_act", "suspend_act"],
        "unassessed_issues": ["retaliation", "disputed_forum_competence"],
    }
    result = compare(example, right)
    assert result.comparisons[0].relation == RepairRelation.EQUIVALENT
    assert len(result.review.results[1].procedure.unassessed_issues) == 2


def test_separation_and_revision_are_incomparable_requirements(example):
    # Given distinct forum defects, when compared, one power cannot compensate for the other.
    left = example | {"reviewing_office_id": "issuer"}
    right = example | {"procedure_id": "B", "powers": ["suspend_act"]}
    result = compare(left, right)
    assert result.comparisons[0].relation == RepairRelation.INCOMPARABLE


def test_removing_filing_barrier_also_activates_protection_on_reassessment(example):
    # Given filing-triggered protection, when capacity is restored, both failures disappear.
    blocked = ReviewProcedure.model_validate(example).model_dump(mode="json")
    blocked["claimants"][1]["available_filing_hours"] = 0
    blocked["claimants"][1]["protection"]["trigger"] = "on_filing"
    repaired = ReviewProcedure.model_validate(blocked).model_dump(mode="json")
    repaired["procedure_id"] = "B"
    repaired["claimants"][1]["support_enabled_filing_hours"] = 3
    result = compare(blocked, repaired)
    assert result.requirements[0].claimants[1].uncovered_intervals == ((5, 12),)
    assert result.requirements[1].claimants[1].uncovered_intervals == ()
    assert result.requirements[1].claimants[1].unmet == ()
    assert result.comparisons[0].relation == RepairRelation.RIGHT_SUBSET


@pytest.mark.parametrize(
    "field",
    [
        "claimant_id",
        "membership",
        "consequence_hour",
        "required_filing_hours",
        "baseline_decision_id",
    ],
)
def test_changed_comparison_duties_are_rejected(example, field):
    # Given different people or duties, when compared, no misleading cross-case order is emitted.
    right = ReviewProcedure.model_validate(example).model_dump(mode="json")
    right["procedure_id"] = "B"
    if field == "baseline_decision_id":
        right[field] = "other"
    else:
        right["claimants"][1][field] = {
            "claimant_id": "three",
            "membership": "member",
            "consequence_hour": 6,
            "required_filing_hours": 4,
        }[field]
        if field == "claimant_id":
            right["admitted_claimant_ids"] = ["one", "three"]
    with pytest.raises(ResearchError, match="review_comparison_duties"):
        compare(example, right)


def test_claimant_order_does_not_change_identity_matching(example):
    # Given reordered records of the same people, when compared, profiles remain equivalent.
    right = example | {"procedure_id": "B", "claimants": list(reversed(example["claimants"]))}
    assert compare(example, right).comparisons[0].relation == RepairRelation.EQUIVALENT


def test_single_procedure_has_an_empty_pair_set_and_a_frontier(example):
    # Given one valid procedure, when compared, it is its own minimal supplied profile.
    result = compare(example)
    assert result.comparisons == ()
    assert result.frontier_procedure_ids == ("A",)


def test_empty_study_is_rejected():
    # Given no procedures, when parsed, reject the empty scientific comparison.
    with pytest.raises(ValidationError):
        ReviewStudy(schema_version=1, baseline_decisions_sha256="0" * 64, procedures=())


def test_empty_audit_is_rejected(example):
    # Given an empty internal report, when compared, fail explicitly.
    audit = compare(example).review.model_copy(update={"results": ()})
    with pytest.raises(ResearchError, match="empty_review_comparison"):
        compare_review(audit)


def test_small_profiles_match_independent_integer_atom_enumeration(example):
    # Given independent capacity, deadline and protection changes, use unit-hour atoms as an oracle.
    procedures = []
    expected = {}
    for i, (capacity, ready, start) in enumerate(product((1, 3), (2, 6), (5, 7))):
        row = ReviewProcedure.model_validate(example).model_dump(mode="json")
        row["procedure_id"] = f"C{i}"
        row["claimants"][1].update(
            available_filing_hours=capacity,
            support_enabled_filing_hours=0,
            ready_to_file_hour=ready,
        )
        row["claimants"][1]["protection"]["starts_hour"] = start
        procedures.append(row)
        expected[f"C{i}"] = (
            {("capacity", n) for n in range(3 - capacity)}
            | {("deadline", n) for n in range(max(0, ready - 4))}
            | {("gap", n) for n in range(5, start)}
        )
    # When the real evaluator compares every pair, then all pair relations match set inclusion.
    report = compare(*procedures)
    for pair in report.comparisons:
        left, right = expected[pair.left], expected[pair.right]
        relation = (
            RepairRelation.EQUIVALENT
            if left == right
            else RepairRelation.LEFT_SUBSET
            if left < right
            else RepairRelation.RIGHT_SUBSET
            if right < left
            else RepairRelation.INCOMPARABLE
        )
        assert pair.relation == relation


def test_fixed_study_retains_all_people_and_the_h12_limitations():
    # Given all fourteen procedures, when compared, preserve all twenty-eight source records.
    study = ReviewStudy.model_validate_json(
        (ROOT / "research/institutional-review-cases.json").read_bytes()
    )
    report = compare_review(audit_review(study))
    assert len(report.comparisons) == 91
    assert sum(len(r.claimants) for r in report.requirements) == 28
    assert report.frontier_procedure_ids == ("H01", "H05", "H12", "H13")
    assert (
        next(p for p in report.comparisons if (p.left, p.right) == ("H06", "H07")).relation
        == RepairRelation.INCOMPARABLE
    )
    assert len(report.review.results[11].procedure.unassessed_issues) == 2
