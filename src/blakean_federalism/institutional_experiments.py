# Copyright (c) 2026 Daniel Ari Friedman
"""Exhaustive finite interventions, trigger accounting and minimal predicate repair."""

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from typing import cast

from .institutional_experiment_models import (
    ALL_INTERVENTIONS,
    DecisionExperiment,
    FamilyRule,
    InstitutionalExperiment,
    Intervention,
    InterventionEffect,
    InterventionSpec,
    PairInteraction,
    RuleState,
)
from .institutional_interventions import (
    apply_interventions,
    protected_context,
    rule_is_triggered,
    selected_catalog,
)
from .institutions import assess
from .models import Decision, ResearchError


def _members(mask: int, catalog: tuple[InterventionSpec, ...]) -> tuple[Intervention, ...]:
    return tuple(spec.intervention for bit, spec in enumerate(catalog) if mask & (1 << bit))


def _singleton_effect(record: Decision, spec: InterventionSpec) -> InterventionEffect:
    changed = apply_interventions(record, (spec.intervention,))
    before: dict[str, object] = record.model_dump(mode="json")
    after: dict[str, object] = changed.model_dump(mode="json")
    # Each declared path has at most one nested model component.
    paths = tuple(
        ".".join(change.path)
        for change in spec.changes
        if _path_value(before, change.path) != _path_value(after, change.path)
    )
    failed = {finding.code for finding in assess(record).findings}
    remaining = tuple(finding.code for finding in assess(changed).findings)
    return InterventionEffect(
        intervention=spec.intervention,
        changed_paths=paths,
        resolved_rules=tuple(sorted(failed - set(remaining))),
        remaining_rules=remaining,
        predicate_admissible=not remaining,
    )


def _path_value(payload: dict[str, object], path: tuple[str, ...]) -> object:
    if len(path) == 1:
        return payload[path[0]]
    return cast("dict[str, object]", payload[path[0]])[path[1]]


def _interactions(
    failures: dict[int, frozenset[str]], catalog: tuple[InterventionSpec, ...]
) -> tuple[PairInteraction, ...]:
    baseline = failures[0]
    return tuple(
        PairInteraction(
            first=catalog[first].intervention,
            second=catalog[second].intervention,
            admission_interaction=(
                int(not failures[(1 << first) | (1 << second)])
                - int(not failures[1 << first])
                - int(not failures[1 << second])
                + int(not baseline)
            ),
            excess_resolved_rules=(
                len(baseline - failures[(1 << first) | (1 << second)])
                - len(baseline - failures[1 << first])
                - len(baseline - failures[1 << second])
            ),
        )
        for first, second in combinations(range(len(catalog)), 2)
    )


def run_decision(
    record: Decision, available: tuple[Intervention, ...] = ALL_INTERVENTIONS
) -> DecisionExperiment:
    """Key bounded reuse by every serialized field and the complete operator selection."""
    return _run_serialized_decision(record.model_dump_json(), available)


@lru_cache(maxsize=128)
def _run_serialized_decision(
    serialized: str, available: tuple[Intervention, ...]
) -> DecisionExperiment:
    record = Decision.model_validate_json(serialized)
    catalog = selected_catalog(available)
    family: dict[int, frozenset[str]] = {}
    states: set[str] = set()
    protected = protected_context(record)
    unchanged = True
    subsets_by_size = [0] * (len(catalog) + 1)
    admitted_by_size = [0] * (len(catalog) + 1)
    family_failures: Counter[str] = Counter()
    for mask in range(1 << len(catalog)):
        changed = apply_interventions(record, _members(mask, catalog))
        failed = frozenset(finding.code for finding in assess(changed).findings)
        family[mask] = failed
        family_failures.update(failed)
        subsets_by_size[mask.bit_count()] += 1
        admitted_by_size[mask.bit_count()] += int(not failed)
        states.add(sha256(changed.model_dump_json().encode()).hexdigest())
        unchanged = unchanged and protected_context(changed) == protected
    admitted = tuple(mask for mask, failed in family.items() if not failed)
    minimal = tuple(
        mask
        for mask in admitted
        if all(family[mask ^ (1 << bit)] for bit in range(len(catalog)) if mask & (1 << bit))
    )
    essential_mask = (1 << len(catalog)) - 1 if admitted else 0
    for mask in admitted:
        essential_mask &= mask
    baseline = assess(record)
    effects = tuple(_singleton_effect(record, spec) for spec in catalog)
    irreparable = set(family[0]).intersection(*family.values())
    return DecisionExperiment(
        decision_id=record.decision_id,
        baseline_action=record.consequence.action,
        baseline_failed_rules=tuple(finding.code for finding in baseline.findings),
        baseline_rule_states=tuple(
            RuleState(
                code=check.code,
                triggered=rule_is_triggered(record, check.code),
                passed=check.passed,
            )
            for check in baseline.checks
        ),
        subset_count=len(family),
        distinct_states=len(states),
        admissible_subsets=len(admitted),
        minimum_cardinality=min((mask.bit_count() for mask in admitted), default=None),
        minimal_bundles=tuple(_members(mask, catalog) for mask in minimal),
        essential_interventions=_members(essential_mask, catalog),
        irreparable_rules=tuple(sorted(irreparable)),
        subsets_by_size=tuple(subsets_by_size),
        admissible_by_size=tuple(admitted_by_size),
        singleton_effects=effects,
        pair_interactions=_interactions(family, catalog),
        rule_failures_in_family=tuple(
            FamilyRule(
                code=check.code,
                triggered=rule_is_triggered(record, check.code),
                baseline_passed=check.passed,
                family_failures=family_failures[check.code],
                singleton_resolvers=tuple(
                    effect.intervention for effect in effects if check.code in effect.resolved_rules
                ),
            )
            for check in baseline.checks
        ),
        protected_context_unchanged=unchanged,
        failure_monotone=all(
            family[mask | (1 << bit)] <= failed
            for mask, failed in family.items()
            for bit in range(len(catalog))
        ),
    )


def run_experiment(
    records: tuple[Decision, ...], available: tuple[Intervention, ...] = ALL_INTERVENTIONS
) -> InstitutionalExperiment:
    if not records or len({record.decision_id for record in records}) != len(records):
        raise ResearchError(
            "experiment_decisions", "Require nonempty records with distinct identifiers"
        )
    catalog = selected_catalog(available)
    results = tuple(run_decision(record, available) for record in records)
    rule_states = tuple(state for result in results for state in result.baseline_rule_states)
    return InstitutionalExperiment(
        catalog=catalog,
        decisions=results,
        total_subsets=sum(result.subset_count for result in results),
        total_distinct_states=sum(result.distinct_states for result in results),
        total_admissible_subsets=sum(result.admissible_subsets for result in results),
        baseline_active_checks=sum(state.triggered for state in rule_states),
        baseline_inactive_checks=sum(not state.triggered for state in rule_states),
        baseline_failed_checks=sum(not state.passed for state in rule_states),
    )
