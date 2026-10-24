# Copyright (c) 2026 Daniel Ari Friedman
"""Hypothetical records expose failures without claiming political validity."""

from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from blakean_federalism.institutions import assess
from blakean_federalism.models import Decision, EntityKind, EntityRef

CASES = TypeAdapter(tuple[Decision, ...]).validate_json(
    (Path(__file__).parents[1] / "research/cases.json").read_bytes(),
)


@pytest.mark.parametrize("record", CASES, ids=lambda record: record.decision_id)
def test_case_outcome_follows_declared_safeguards(record):
    # Given each curated pair, when assessed, then only the bounded option passes.
    assert assess(record).admissible_under_proposed_rules == record.decision_id.endswith("-bounded")


@pytest.mark.parametrize(
    ("case_id", "code"),
    [
        ("A-capture", "FORCED_REGISTER"),
        ("B-capture", "CAPTURE"),
        ("C-capture", "POETRY_TO_POWER"),
        ("D-capture", "VISION_HIERARCHY"),
        ("E-capture", "EXCLUDED_AFFECTED"),
        ("E-capture", "RESOURCE_GAP"),
        ("E-capture", "FORCED_INCORPORATION"),
    ],
)
def test_named_counterexample_is_exposed(case_id, code):
    record = next(r for r in CASES if r.decision_id == case_id)
    # When a prohibited move is present, then the corresponding rule fails.
    assert code in {f.code for f in assess(record).findings}


@pytest.mark.parametrize("lenses", [3, 4, 6])
def test_lens_count_carries_no_authority(lenses):
    original = CASES[0]
    transformed = original.model_copy(
        update={
            "poetic_state_interpretation": f"{lenses} proposed interpretive lenses",
        }
    )
    # When lens count changes, then civic admissibility remains identical.
    assert assess(transformed) == assess(original)


def test_more_affiliations_do_not_establish_more_freedom():
    original = CASES[0]
    transformed = original.model_copy(
        update={
            "national_affiliations": (*original.national_affiliations, "n-federation-scale"),
        }
    )
    # When cultural reach grows, then no freedom score is inferred.
    assert assess(transformed) == assess(original)


@pytest.mark.parametrize("field", ["institution", "issuing_jurisdiction"])
def test_authority_types_are_not_interchangeable(field):
    original = CASES[0]
    authority = original.asserting_authority.model_copy(
        update={
            field: EntityRef(entity_id="wrong", kind=EntityKind.PERSON, label="A person"),
        }
    )
    # When person and authority types collapse, then flag the record.
    assert not assess(
        original.model_copy(update={"asserting_authority": authority})
    ).admissible_under_proposed_rules


def test_unknown_fields_do_not_silently_become_theory():
    data = CASES[0].model_dump(mode="json") | {"eternal_mandate": True}
    # When a schema gains an unauthorized field, then parsing rejects it.
    with pytest.raises(ValidationError):
        Decision.model_validate(data)


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("public_reason", "TRANSLATION_OBLIGATION"),
        ("representation_limits", "TRANSLATION_OBLIGATION"),
        ("enforcement_actor", "AUTHORITY_GAP"),
    ],
)
def test_missing_authority_details_are_exposed(field, code):
    record = next(r for r in CASES if r.decision_id == "E-bounded")
    authority = record.asserting_authority.model_copy(update={field: ""})
    result = assess(record.model_copy(update={"asserting_authority": authority}))
    assert code in {f.code for f in result.findings}


def test_poetic_state_cannot_be_the_rights_bearing_subject():
    record = CASES[0].model_copy(
        update={
            "subject": EntityRef(
                entity_id="s-poetic", kind=EntityKind.POETIC_STATE, label="A descriptor"
            ),
        }
    )
    assert "SUBJECT_COLLAPSE" in {f.code for f in assess(record).findings}


@pytest.mark.parametrize(
    "field",
    [
        "public_reason",
        "representation_limits",
        "assigned_competence",
        "competence_source",
        "enforcement_actor",
        "enforcement_limits",
        "reach",
    ],
)
def test_whitespace_is_an_exposed_authority_gap(field):
    record = next(r for r in CASES if r.decision_id == "E-bounded")
    value = (" ",) if field == "reach" else " \t "
    authority = record.asserting_authority.model_copy(update={field: value})
    result = assess(record.model_copy(update={"asserting_authority": authority}))
    assert not result.admissible_under_proposed_rules
    assert {f.code for f in result.findings} <= {"AUTHORITY_GAP", "TRANSLATION_OBLIGATION"}


@pytest.mark.parametrize("record", CASES, ids=lambda r: r.decision_id)
def test_every_stipulated_rule_has_an_inspectable_outcome(record):
    result = assess(record)
    assert result.schema_version == 2
    assert len(result.checks) == len({c.code for c in result.checks}) == 15
    assert {c.code for c in result.checks if not c.passed} == {f.code for f in result.findings}
    assert result.admissible_under_proposed_rules == all(c.passed for c in result.checks)
