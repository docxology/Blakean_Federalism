# Copyright (c) 2026 Daniel Ari Friedman
"""Typed finite-family results for explicit institutional field interventions."""

from enum import StrEnum
from typing import Literal

from pydantic import Field

from .models import FrozenModel


class Intervention(StrEnum):
    NONCAPTURE = "noncapture"
    UNRANKED_RIGHTS = "unranked_rights"
    EQUAL_PERSONHOOD = "equal_personhood"
    OPEN_AFFILIATION = "open_affiliation"
    PUBLIC_REASONS = "public_reasons"
    CHARTER = "charter"
    COMPETENCE = "competence"
    CONTESTATION = "contestation"
    SUPPORTED_EXIT = "supported_exit"
    NONMEMBER_STANDING = "nonmember_standing"
    BURDEN_ALLOCATION = "burden_allocation"
    TREATY_AND_REFUSAL = "treaty_and_refusal"


ALL_INTERVENTIONS: tuple[Intervention, ...] = tuple(Intervention)


class FieldChange(FrozenModel):
    path: tuple[str, ...] = Field(min_length=1, max_length=2)
    value: str | bool | tuple[str, ...]
    only_if_blank: bool = False


class InterventionSpec(FrozenModel):
    intervention: Intervention
    label: str
    rule: str
    changes: tuple[FieldChange, ...]


class RuleState(FrozenModel):
    code: str
    triggered: bool
    passed: bool


class InterventionEffect(FrozenModel):
    intervention: Intervention
    changed_paths: tuple[str, ...]
    resolved_rules: tuple[str, ...]
    remaining_rules: tuple[str, ...]
    predicate_admissible: bool


class PairInteraction(FrozenModel):
    first: Intervention
    second: Intervention
    admission_interaction: int
    excess_resolved_rules: int


class FamilyRule(FrozenModel):
    code: str
    triggered: bool
    baseline_passed: bool
    family_failures: int
    singleton_resolvers: tuple[Intervention, ...]


class DecisionExperiment(FrozenModel):
    decision_id: str
    baseline_action: str
    baseline_failed_rules: tuple[str, ...]
    baseline_rule_states: tuple[RuleState, ...]
    subset_count: int
    distinct_states: int
    admissible_subsets: int
    minimum_cardinality: int | None
    minimal_bundles: tuple[tuple[Intervention, ...], ...]
    essential_interventions: tuple[Intervention, ...]
    irreparable_rules: tuple[str, ...]
    subsets_by_size: tuple[int, ...]
    admissible_by_size: tuple[int, ...]
    singleton_effects: tuple[InterventionEffect, ...]
    pair_interactions: tuple[PairInteraction, ...]
    rule_failures_in_family: tuple[FamilyRule, ...]
    protected_context_unchanged: bool
    failure_monotone: bool


class InstitutionalExperiment(FrozenModel):
    schema_version: Literal[1] = 1
    catalog: tuple[InterventionSpec, ...]
    decisions: tuple[DecisionExperiment, ...]
    total_subsets: int
    total_distinct_states: int
    total_admissible_subsets: int
    baseline_active_checks: int
    baseline_inactive_checks: int
    baseline_failed_checks: int
    scope: str = (
        "Exhaustive subsets of declared synthetic field interventions under the existing fifteen "
        "predicates. Action labels identify baseline records; "
        "interventions edit the listed fields. "
        "Coercion, resource decisions, affected populations, treaty triggers, identities and "
        "interpretive content remain fixed. Counts describe this finite model."
    )
