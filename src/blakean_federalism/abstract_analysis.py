# Copyright (c) 2026 Daniel Ari Friedman
"""Text-free finite-collection diagnostics; rates are per 10,000 word tokens."""

from math import comb, isclose
from statistics import fmean

from .abstract_analysis_models import (
    QueryDiagnostic,
    RepairCase,
    RepairDiagnostics,
    RepairPartition,
)
from .corpus_statistics_models import CorpusStatistics, Measure, SourceUnit
from .institutional_experiment_models import InstitutionalExperiment, Intervention
from .models import ResearchError, Role


def _require(*, condition: bool, detail: str) -> None:
    if not condition:
        raise ResearchError("abstract_diagnostics", detail)


def _equal_rate(left: float | None, right: float | None) -> bool:
    return (
        left is right
        if left is None or right is None
        else isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
    )


def _measure(units: tuple[SourceUnit, ...], query: str) -> Measure:
    tokens = sum(unit.tokens for unit in units)
    occurrences = sum(unit.occurrences[query] for unit in units)
    matched = sum(unit.occurrences[query] > 0 for unit in units)
    return Measure(
        source_units=len(units),
        tokens=tokens,
        occurrences=occurrences,
        matched_units=matched,
        rate_per_10000_tokens=(10000 * occurrences / tokens if tokens else None),
        coverage_fraction=matched / len(units) if units else None,
    )


def corpus_diagnostics(
    stats: CorpusStatistics, query_ids: tuple[str, ...]
) -> tuple[QueryDiagnostic, ...]:
    """Reconcile unit-derived family weighting and leave-one-family-out sensitivity.

    Exact-text, strata and co-occurrence outputs are outside this reconciliation.
    Ties retain every family ID; no matches have no top family or occurrence share.
    """
    specs = {q.query_id for q in stats.query_specs}
    summaries = {q.query_id: q for q in stats.queries}
    groups = {
        w: tuple(u for u in stats.units if u.work_id == w)
        for w in sorted({u.work_id for u in stats.units})
    }
    _require(
        condition=len(specs) == len(stats.query_specs)
        and len(summaries) == len(stats.queries)
        and specs == summaries.keys()
        and len(set(query_ids)) == len(query_ids)
        and set(query_ids) <= specs,
        detail="Query identifiers are missing or duplicated",
    )
    _require(
        condition=bool(stats.units)
        and len({u.passage_id for u in stats.units}) == len(stats.units)
        and all(
            u.passage_id.strip()
            and u.work_id.strip()
            and u.tokens >= 0
            and u.occurrences.keys() == specs
            and all(0 <= n <= u.tokens for n in u.occurrences.values())
            for u in stats.units
        ),
        detail="Invalid source units or occurrence counts",
    )
    _require(
        condition=(len(stats.units), len(groups), sum(u.tokens for u in stats.units))
        == (stats.primary_source_units, stats.primary_work_groups, stats.primary_tokens)
        and all(c.units >= 0 for c in stats.source_census)
        and sum(c.units for c in stats.source_census) == stats.total_source_units
        and sum(c.units for c in stats.source_census if c.role == Role.PRIMARY)
        == stats.primary_source_units,
        detail="Source census differs from units",
    )
    result: list[QueryDiagnostic] = []
    for query in query_ids:
        summary = summaries[query]
        pooled = _measure(stats.units, query)
        family = {w: _measure(units, query) for w, units in groups.items()}
        rates = [
            m.rate_per_10000_tokens for m in family.values() if m.rate_per_10000_tokens is not None
        ]
        equal = fmean(rates) if rates else None
        top = max(m.occurrences for m in family.values())
        shares = (
            [m.occurrences / pooled.occurrences for m in family.values()]
            if pooled.occurrences
            else []
        )
        _require(
            condition=pooled == summary.copy_retaining
            and len(rates) == summary.rate_work_groups
            and _equal_rate(equal, summary.work_balanced_rate_per_10000_tokens)
            and _equal_rate(
                fmean(m.matched_units / m.source_units for m in family.values()),
                summary.work_balanced_coverage_fraction,
            )
            and _equal_rate(max(shares) if shares else None, summary.maximum_work_occurrence_share)
            and _equal_rate(
                sum(s * s for s in shares) if shares else None, summary.work_occurrence_hhi
            ),
            detail=f"Summary mismatch: {query}",
        )
        omissions = {o.omitted_work_id: o.remaining for o in summary.leave_one_work_out}
        _require(
            condition=len(omissions) == len(summary.leave_one_work_out)
            and omissions.keys() == family.keys(),
            detail=f"Omission membership: {query}",
        )
        for work, remaining in omissions.items():
            _require(
                condition=remaining
                == _measure(tuple(u for u in stats.units if u.work_id != work), query),
                detail=f"Omission counts: {query}/{work}",
            )
        loo = {
            w: m.rate_per_10000_tokens
            for w, m in omissions.items()
            if m.rate_per_10000_tokens is not None
        }
        low, high = min(loo.values(), default=None), max(loo.values(), default=None)
        result.append(
            QueryDiagnostic(
                query_id=query,
                source_units=pooled.source_units,
                tokens=pooled.tokens,
                occurrences=pooled.occurrences,
                matched_units=pooled.matched_units,
                positive_token_families=len(rates),
                matched_families=sum(m.occurrences > 0 for m in family.values()),
                pooled_rate=pooled.rate_per_10000_tokens,
                equal_family_rate=equal,
                top_family_ids=tuple(w for w, m in family.items() if top and m.occurrences == top),
                top_family_occurrences=top,
                top_family_share=max(shares) if shares else None,
                loo_min_rate=low,
                loo_min_family_ids=tuple(sorted(w for w, r in loo.items() if r == low)),
                loo_max_rate=high,
                loo_max_family_ids=tuple(sorted(w for w, r in loo.items() if r == high)),
            )
        )
    return tuple(result)


def repair_diagnostics(experiment: InstitutionalExperiment) -> RepairDiagnostics:
    """Reconstruct upper sets of minimal bundles, independently of predicate evaluation.

    Distinct state counts are reported and bounded, not rederived from absent records.
    Mask fractions describe combinatorics, not probabilities of social success.
    """
    catalog = tuple(spec.intervention for spec in experiment.catalog)
    _require(
        condition=len(set(catalog)) == len(catalog) and set(catalog) <= set(Intervention),
        detail="Unknown or duplicate catalog operators",
    )
    _require(
        condition=bool(experiment.decisions)
        and len({d.decision_id for d in experiment.decisions}) == len(experiment.decisions),
        detail="Missing or duplicate decisions",
    )
    subset_count = 1 << len(catalog)
    rows: list[RepairCase] = []
    for decision in experiment.decisions:
        bundles = tuple(frozenset(bundle) for bundle in decision.minimal_bundles)
        _require(
            condition=all(
                len(b) == len(original) and b <= set(catalog)
                for b, original in zip(bundles, decision.minimal_bundles, strict=True)
            )
            and all(
                not (a <= b) for i, a in enumerate(bundles) for j, b in enumerate(bundles) if i != j
            ),
            detail=f"Invalid minimal antichain: {decision.decision_id}",
        )
        admitted = [0] * (len(catalog) + 1)
        for mask in range(subset_count):
            selected = {op for bit, op in enumerate(catalog) if mask & (1 << bit)}
            admitted[mask.bit_count()] += any(bundle <= selected for bundle in bundles)
        count = sum(admitted)
        minimum = min((len(b) for b in bundles), default=None)
        essentials = {op for op in catalog if bundles and all(op in b for b in bundles)}
        _require(
            condition=decision.failure_monotone
            and decision.subset_count == subset_count
            and decision.subsets_by_size
            == tuple(comb(len(catalog), k) for k in range(len(catalog) + 1))
            and decision.admissible_by_size == tuple(admitted)
            and decision.admissible_subsets == count
            and decision.minimum_cardinality == minimum
            and len(set(decision.essential_interventions)) == len(decision.essential_interventions)
            and set(decision.essential_interventions) == essentials
            and bool(admitted[0]) == (not decision.baseline_failed_rules)
            and 1 <= decision.distinct_states <= subset_count
            and (decision.distinct_states > 1 or count in (0, subset_count)),
            detail=f"Repair counts or monotonicity: {decision.decision_id}",
        )
        _require(
            condition=len(set(decision.baseline_failed_rules))
            == len(decision.baseline_failed_rules)
            and set(decision.baseline_failed_rules)
            == {r.code for r in decision.baseline_rule_states if not r.passed},
            detail=f"Baseline rule mismatch: {decision.decision_id}",
        )
        rows.append(
            RepairCase(
                decision_id=decision.decision_id,
                baseline_failed_rules=decision.baseline_failed_rules,
                minimal_bundles=decision.minimal_bundles,
                essential_interventions=tuple(op for op in catalog if op in essentials),
                minimum_cardinality=minimum,
                subset_count=subset_count,
                admissible_subsets=count,
                distinct_states=decision.distinct_states,
                admissible_by_size=tuple(admitted),
                admission_fraction=count / subset_count,
                unique_minimal_bundle=len(bundles) == 1,
            )
        )
    states = [s for d in experiment.decisions for s in d.baseline_rule_states]
    _require(
        condition=sum(r.subset_count for r in rows) == experiment.total_subsets
        and sum(r.admissible_subsets for r in rows) == experiment.total_admissible_subsets
        and sum(r.distinct_states for r in rows) == experiment.total_distinct_states
        and sum(s.triggered for s in states) == experiment.baseline_active_checks
        and sum(not s.triggered for s in states) == experiment.baseline_inactive_checks
        and sum(not s.passed for s in states) == experiment.baseline_failed_checks,
        detail="Experiment totals mismatch",
    )
    partitions: list[RepairPartition] = []
    for baseline_failing in (False, True):
        members = [r for r in rows if bool(r.baseline_failed_rules) == baseline_failing]
        masks = sum(r.subset_count for r in members)
        admissions = sum(r.admissible_subsets for r in members)
        partitions.append(
            RepairPartition(
                decisions=len(members),
                subset_count=masks,
                admissible_subsets=admissions,
                distinct_states=sum(r.distinct_states for r in members),
                admission_fraction=admissions / masks if masks else None,
            )
        )
    return RepairDiagnostics(
        cases=tuple(rows),
        baseline_admissible=partitions[0],
        baseline_failing=partitions[1],
        total_subsets=experiment.total_subsets,
        total_admissible_subsets=experiment.total_admissible_subsets,
        total_distinct_states=experiment.total_distinct_states,
    )
