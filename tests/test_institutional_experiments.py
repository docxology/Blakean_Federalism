# Copyright (c) 2026 Daniel Ari Friedman
"""Finite numerical oracles and controls for synthetic field interventions."""

from pathlib import Path

import pytest
from pydantic import TypeAdapter

from blakean_federalism.institutional_experiments import (
    _run_serialized_decision,
    run_decision,
    run_experiment,
)
from blakean_federalism.institutional_interventions import (
    CATALOG,
    Intervention,
    apply_interventions,
    protected_context,
    rule_is_triggered,
    verify_protected_context,
)
from blakean_federalism.institutions import assess
from blakean_federalism.models import Decision, EntityKind, ResearchError, Warrant

CASES = TypeAdapter(tuple[Decision, ...]).validate_json(
    (Path(__file__).parents[1] / "research/cases.json").read_bytes()
)


def test_complete_family_has_exact_admission_and_distinct_state_counts():
    result = run_experiment(CASES)
    assert result.total_subsets == 40960
    assert result.total_distinct_states == 31
    assert result.total_admissible_subsets == 25600
    assert result.baseline_active_checks == 118
    assert result.baseline_inactive_checks == 32
    assert result.baseline_failed_checks == 11
    capture = [r for r in result.decisions if r.decision_id.endswith("-capture")]
    assert [r.minimum_cardinality for r in capture] == [3, 2, 1, 2, 3]
    assert [r.admissible_subsets for r in capture] == [512, 1024, 2048, 1024, 512]
    assert all(len(r.minimal_bundles) == 1 for r in result.decisions)
    assert sum(p.admission_interaction for r in capture for p in r.pair_interactions) == 2
    assert all(r.protected_context_unchanged and r.failure_monotone for r in result.decisions)


def test_missing_charter_operator_cannot_repair_interpretive_coercion():
    case = next(r for r in CASES if r.decision_id == "C-capture")
    available = tuple(i for i in Intervention if i != Intervention.CHARTER)
    result = run_experiment((case,), available).decisions[0]
    assert result.minimum_cardinality is None
    assert result.admissible_subsets == 0
    assert result.minimal_bundles == ()
    assert result.irreparable_rules == ("POETRY_TO_POWER",)


def case(identifier):
    return next(record for record in CASES if record.decision_id == identifier)


def test_two_obligation_oracle_has_one_joint_solution():
    result = run_decision(case("B-capture"), (Intervention.NONCAPTURE, Intervention.CONTESTATION))
    assert result.subset_count == result.distinct_states == 4
    assert result.subsets_by_size == (1, 2, 1)
    assert result.admissible_by_size == (0, 0, 1)
    assert result.minimum_cardinality == 2
    assert result.minimal_bundles == ((Intervention.NONCAPTURE, Intervention.CONTESTATION),)
    assert result.essential_interventions == result.minimal_bundles[0]
    assert result.pair_interactions[0].admission_interaction == 1
    assert result.pair_interactions[0].excess_resolved_rules == 0
    assert [effect.resolved_rules for effect in result.singleton_effects] == [
        ("CAPTURE",),
        ("CONTESTATION",),
    ]
    assert all(not effect.predicate_admissible for effect in result.singleton_effects)


def test_already_admissible_empty_family_retains_empty_bundle():
    result = run_decision(case("E-bounded"), ())
    assert result.subset_count == result.distinct_states == result.admissible_subsets == 1
    assert result.minimum_cardinality == 0
    assert result.minimal_bundles == ((),)
    assert result.essential_interventions == result.irreparable_rules == ()
    assert result.subsets_by_size == result.admissible_by_size == (1,)
    assert result.singleton_effects == result.pair_interactions == ()


def test_failed_empty_family_is_distinct_from_empty_repair():
    result = run_decision(case("C-capture"), ())
    assert result.subset_count == result.distinct_states == 1
    assert result.admissible_subsets == 0
    assert result.minimum_cardinality is None
    assert result.minimal_bundles == ()
    assert result.irreparable_rules == ("POETRY_TO_POWER",)


def test_catalog_repairs_all_twelve_mutable_predicates_without_changing_triggers():
    baseline = case("E-bounded")
    authority = baseline.asserting_authority.model_copy(
        update={
            "public_reason": "  ",
            "representation_limits": "",
            "assigned_competence": "",
            "competence_warrant": Warrant.INTERPRETIVE,
            "competence_source": "",
            "reach": (" \t ",),
            "enforcement_actor": "",
            "enforcement_limits": "",
        }
    )
    consequence = baseline.consequence.model_copy(
        update={
            "nonmember_standing": False,
            "burden_allocation": "",
        }
    )
    contest = baseline.contestation.model_copy(
        update={
            "forum": "",
            "voice": "",
            "revision": "",
            "exit": "",
            "materially_supported_exit": False,
        }
    )
    record = baseline.model_copy(
        update={
            "asserting_authority": authority,
            "consequence": consequence,
            "contestation": contest,
            "claims_exhaust_person": True,
            "vision_rank_determines_rights": True,
            "equal_personhood": False,
            "forced_exclusive_national_register": True,
            "treaty_or_refusal_addressed": False,
        }
    )
    assert len(assess(record).findings) == 12
    changed = apply_interventions(record, tuple(Intervention))
    assert assess(changed).admissible_under_proposed_rules
    assert protected_context(changed) == protected_context(record)
    assert changed.consequence.action == record.consequence.action
    assert apply_interventions(changed, tuple(Intervention)) == changed
    assert apply_interventions(record, tuple(reversed(Intervention))) == changed
    assert record.equal_personhood is False
    assert changed.consequence.affected_nonmembers == record.consequence.affected_nonmembers
    assert changed.treaty_or_refusal_implicated is record.treaty_or_refusal_implicated


def test_nonempty_existing_details_survive_other_missing_details():
    record = case("E-bounded")
    reason = record.asserting_authority.public_reason
    authority = record.asserting_authority.model_copy(update={"representation_limits": ""})
    changed = apply_interventions(
        record.model_copy(update={"asserting_authority": authority}),
        (Intervention.PUBLIC_REASONS,),
    )
    assert changed.asserting_authority.public_reason == reason
    assert changed.asserting_authority.representation_limits


def test_fixed_entity_types_remain_irreparable_with_every_operator():
    original = case("E-bounded")
    authority = original.asserting_authority.model_copy(
        update={
            "institution": original.asserting_authority.institution.model_copy(
                update={"kind": EntityKind.PERSON}
            ),
            "issuing_jurisdiction": original.asserting_authority.issuing_jurisdiction.model_copy(
                update={"kind": EntityKind.NATION}
            ),
        }
    )
    record = original.model_copy(
        update={
            "subject": original.subject.model_copy(update={"kind": EntityKind.POETIC_STATE}),
            "asserting_authority": authority,
        }
    )
    result = run_decision(record)
    assert result.admissible_subsets == 0
    assert result.minimum_cardinality is None
    assert result.irreparable_rules == ("ISSUER_TYPE", "JURISDICTION_TYPE", "SUBJECT_COLLAPSE")
    assert result.distinct_states == 1
    assert result.protected_context_unchanged


def test_inactive_obligations_are_not_counted_as_substantive_successes():
    record = case("A-bounded")
    dormant = {
        "POETRY_TO_POWER",
        "AUTHORITY_GAP",
        "EXCLUDED_AFFECTED",
        "RESOURCE_GAP",
        "FORCED_INCORPORATION",
    }
    assert {
        check.code for check in assess(record).checks if not rule_is_triggered(record, check.code)
    } == dormant
    assert all(rule_is_triggered(case("E-bounded"), code) for code in dormant)
    result = run_experiment((record,), ())
    assert result.baseline_active_checks == 10
    assert result.baseline_inactive_checks == 5
    assert result.baseline_failed_checks == 0


def test_inactive_operators_leave_even_unspecified_fields_unchanged():
    original = case("A-bounded")
    authority = original.asserting_authority.model_copy(
        update={
            "competence_source": "",
            "assigned_competence": "",
            "reach": (),
            "enforcement_actor": "",
            "enforcement_limits": "",
            "competence_warrant": Warrant.INTERPRETIVE,
        }
    )
    record = original.model_copy(update={"asserting_authority": authority})
    assert apply_interventions(record, (Intervention.CHARTER, Intervention.COMPETENCE)) == record


def test_shared_field_can_make_one_operator_resolve_two_failures():
    original = case("E-bounded")
    authority = original.asserting_authority.model_copy(
        update={
            "competence_source": "",
            "competence_warrant": Warrant.INTERPRETIVE,
        }
    )
    record = original.model_copy(update={"asserting_authority": authority})
    result = run_decision(record, (Intervention.CHARTER, Intervention.COMPETENCE))
    assert result.baseline_failed_rules == ("POETRY_TO_POWER", "AUTHORITY_GAP")
    assert result.minimal_bundles == ((Intervention.CHARTER,),)
    assert result.minimum_cardinality == 1
    assert result.admissible_subsets == 2
    assert result.pair_interactions[0].admission_interaction == 0
    assert result.pair_interactions[0].excess_resolved_rules == -1
    assert result.failure_monotone


@pytest.mark.parametrize("records", [(), (CASES[0], CASES[0])])
def test_empty_or_duplicate_decisions_are_rejected(records):
    with pytest.raises(ResearchError, match="experiment_decisions"):
        run_experiment(records)


@pytest.mark.parametrize("available", [(Intervention.CHARTER, Intervention.CHARTER), ("unknown",)])
def test_invalid_catalogs_are_rejected(available):
    with pytest.raises(ResearchError, match="intervention_catalog"):
        run_decision(CASES[0], available)


def test_unknown_rules_do_not_silently_gain_applicability():
    with pytest.raises(ResearchError, match="unknown_rule"):
        rule_is_triggered(CASES[0], "MISSING")


def test_declared_catalog_cannot_edit_any_protected_trigger_or_entity():
    paths = {change.path for spec in CATALOG for change in spec.changes}
    forbidden = {
        ("consequence", "coercive"),
        ("consequence", "resource_decision"),
        ("consequence", "affected_persons"),
        ("consequence", "affected_nonmembers"),
        ("treaty_or_refusal_implicated",),
        ("subject",),
        ("national_affiliations",),
    }
    assert paths.isdisjoint(forbidden)
    assert len({spec.rule for spec in CATALOG}) == len(Intervention) == 12


@pytest.mark.parametrize("field", ["coercive", "resource_decision", "affected_nonmembers"])
def test_changed_trigger_or_affected_population_fails_custody_guard(field):
    original = case("E-bounded")
    value = () if field == "affected_nonmembers" else False
    changed = original.model_copy(
        update={"consequence": original.consequence.model_copy(update={field: value})}
    )
    with pytest.raises(ResearchError, match="intervention_context"):
        verify_protected_context(original, changed)


def test_bounded_cache_preserves_full_record_and_catalog_identity():
    _run_serialized_decision.cache_clear()
    record = case("B-capture")
    catalog = (Intervention.NONCAPTURE, Intervention.CONTESTATION)
    first = run_decision(record, catalog)
    assert run_decision(record.model_copy(), catalog) is first
    assert _run_serialized_decision.cache_info().hits == 1
    changed = record.model_copy(update={"equal_personhood": False})
    different = run_decision(changed, catalog)
    assert different is not first
    assert different.minimum_cardinality is None
    assert different.irreparable_rules == ("RIGHTS_FLOOR",)
    expanded = run_decision(changed, (*catalog, Intervention.EQUAL_PERSONHOOD))
    assert expanded.minimum_cardinality == 3
    assert not expanded.irreparable_rules
    assert _run_serialized_decision.cache_info().maxsize == 128
    _run_serialized_decision.cache_clear()
