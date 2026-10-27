# Copyright (c) 2026 Daniel Ari Friedman
# Independent arithmetic examples and corrupt-input controls.

from itertools import combinations

import pytest

from blakean_federalism.abstract_analysis import corpus_diagnostics, repair_diagnostics
from blakean_federalism.corpus_statistics import analyze_corpus
from blakean_federalism.institutional_experiment_models import (
    DecisionExperiment,
    InstitutionalExperiment,
    Intervention,
    RuleState,
)
from blakean_federalism.institutional_interventions import selected_catalog
from blakean_federalism.models import ResearchError

from .test_corpus_statistics import queries, unit


@pytest.fixture
def corpus():
    return analyze_corpus(
        (
            unit("a", "state state", "large"),
            unit("b", "other " * 8, "large"),
            unit("c", "state", "small"),
            unit("d", "...", "empty"),
        ),
        queries("state", "absent"),
    )


def test_weighting_and_omission_when_family_sizes_differ(corpus):
    (result,) = corpus_diagnostics(corpus, ("state",))
    assert (result.source_units, result.tokens, result.occurrences, result.matched_units) == (
        4,
        11,
        3,
        2,
    )
    assert (result.positive_token_families, result.matched_families) == (2, 2)
    assert result.pooled_rate == pytest.approx(30000 / 11)
    assert result.equal_family_rate == 6000
    assert (result.top_family_ids, result.top_family_occurrences) == (("large",), 2)
    assert result.top_family_share == pytest.approx(2 / 3)
    assert (result.loo_min_rate, result.loo_min_family_ids) == (2000, ("small",))
    assert (result.loo_max_rate, result.loo_max_family_ids) == (10000, ("large",))


def test_absent_query_has_zero_rate_and_no_top_family(corpus):
    (result,) = corpus_diagnostics(corpus, ("absent",))
    assert result.pooled_rate == result.equal_family_rate == 0
    assert result.top_family_share is None
    assert result.top_family_ids == ()
    assert result.loo_min_family_ids == result.loo_max_family_ids == ("empty", "large", "small")


@pytest.mark.parametrize("text", ["...", "state"])
def test_single_family_has_no_omission_denominator(text):
    report = analyze_corpus((unit("a", text),), queries("state"))
    (result,) = corpus_diagnostics(report, ("state",))
    assert result.loo_min_rate is result.loo_max_rate is None
    assert result.loo_min_family_ids == result.loo_max_family_ids == ()
    if text == "...":
        assert result.pooled_rate is result.equal_family_rate is result.top_family_share is None


def test_equal_count_ties_retain_all_family_ids():
    report = analyze_corpus((unit("a", "state", "z"), unit("b", "state", "a")), queries("state"))
    (result,) = corpus_diagnostics(report, ("state",))
    assert (
        result.top_family_ids
        == result.loo_min_family_ids
        == result.loo_max_family_ids
        == ("a", "z")
    )


@pytest.mark.parametrize("selected", [("missing",), ("state", "state")])
def test_query_selection_rejects_missing_or_duplicate_ids(corpus, selected):
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        corpus_diagnostics(corpus, selected)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("primary_tokens", 12),
        ("primary_source_units", 5),
        ("primary_work_groups", 4),
        ("total_source_units", 5),
    ],
)
def test_corpus_rejects_census_corruption(corpus, field, value):
    altered = corpus.model_copy(update={field: value})
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        corpus_diagnostics(altered, ("state",))


@pytest.mark.parametrize(
    "changes",
    [
        {"tokens": -1},
        {"occurrences": {"state": -1, "absent": 0}},
        {"occurrences": {"state": 3, "absent": 0}},
        {"occurrences": {"state": 2}},
        {"work_id": " "},
    ],
)
def test_corpus_rejects_impossible_source_units(corpus, changes):
    altered = corpus.model_copy(
        update={"units": (corpus.units[0].model_copy(update=changes), *corpus.units[1:])}
    )
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        corpus_diagnostics(altered, ("state",))


@pytest.mark.parametrize(
    "changes",
    [
        {"rate_work_groups": 3},
        {"work_balanced_rate_per_10000_tokens": 4000},
        {"work_balanced_coverage_fraction": 0},
        {"maximum_work_occurrence_share": 1},
        {"work_occurrence_hhi": 1},
        {"leave_one_work_out": ()},
    ],
)
def test_corpus_rejects_summary_corruption(corpus, changes):
    summaries = tuple(
        q.model_copy(update=changes) if q.query_id == "state" else q for q in corpus.queries
    )
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        corpus_diagnostics(corpus.model_copy(update={"queries": summaries}), ("state",))


def experiment(catalog, bundles):
    # Combinations provide a separate oracle from production bit-mask enumeration.
    accepted = [
        sum(any(set(b) <= set(s) for b in bundles) for s in combinations(catalog, size))
        for size in range(len(catalog) + 1)
    ]
    subset_sizes = tuple(
        len(tuple(combinations(catalog, size))) for size in range(len(catalog) + 1)
    )
    baseline_failed = () if () in bundles else ("fixture_rule",)
    decision = DecisionExperiment(
        decision_id="fixture",
        baseline_action="synthetic",
        baseline_failed_rules=baseline_failed,
        baseline_rule_states=(
            RuleState(code="fixture_rule", triggered=True, passed=not baseline_failed),
        ),
        subset_count=sum(subset_sizes),
        distinct_states=sum(subset_sizes),
        admissible_subsets=sum(accepted),
        minimum_cardinality=min(map(len, bundles), default=None),
        minimal_bundles=bundles,
        essential_interventions=tuple(
            op for op in catalog if bundles and all(op in b for b in bundles)
        ),
        irreparable_rules=(),
        subsets_by_size=subset_sizes,
        admissible_by_size=tuple(accepted),
        singleton_effects=(),
        pair_interactions=(),
        rule_failures_in_family=(),
        protected_context_unchanged=True,
        failure_monotone=True,
    )
    return InstitutionalExperiment(
        catalog=selected_catalog(catalog),
        decisions=(decision,),
        total_subsets=decision.subset_count,
        total_distinct_states=decision.distinct_states,
        total_admissible_subsets=sum(accepted),
        baseline_active_checks=1,
        baseline_inactive_checks=0,
        baseline_failed_checks=len(baseline_failed),
    )


@pytest.fixture
def alternatives():
    a, b, c = Intervention.NONCAPTURE, Intervention.CHARTER, Intervention.CONTESTATION
    return experiment((a, b, c), ((a,), (b, c)))


def test_alternative_antichain_counts_overlap_once(alternatives):
    result = repair_diagnostics(alternatives)
    (row,) = result.cases
    assert row.admissible_by_size == (0, 1, 3, 1)
    assert row.admission_fraction == 5 / 8
    assert row.minimum_cardinality == 1
    assert row.essential_interventions == ()
    assert not row.unique_minimal_bundle
    assert result.baseline_failing.admissible_subsets == 5
    assert result.baseline_admissible.admission_fraction is None


@pytest.mark.parametrize(
    ("catalog", "bundles", "expected"),
    [
        ((), (), 0),
        ((), ((),), 1),
        ((Intervention.CHARTER,), (), 0),
        ((Intervention.CHARTER,), ((),), 2),
        ((Intervention.CHARTER,), ((Intervention.CHARTER,),), 1),
    ],
)
def test_empty_and_single_operator_cases(catalog, bundles, expected):
    result = repair_diagnostics(experiment(catalog, bundles))
    assert result.total_admissible_subsets == expected
    assert result.cases[0].unique_minimal_bundle == bool(bundles)


@pytest.mark.parametrize(
    "changes",
    [
        {"failure_monotone": False},
        {"subset_count": 9},
        {"subsets_by_size": (1, 3, 2, 1)},
        {"admissible_by_size": (0, 2, 2, 1)},
        {"admissible_subsets": 6},
        {"minimum_cardinality": 2},
        {"essential_interventions": (Intervention.CHARTER,)},
        {"distinct_states": 0},
        {"distinct_states": 9},
        {"distinct_states": 1},
        {"baseline_failed_rules": ()},
        {
            "minimal_bundles": (
                (Intervention.NONCAPTURE,),
                (Intervention.NONCAPTURE, Intervention.CHARTER),
            )
        },
        {"minimal_bundles": ((Intervention.NONCAPTURE,), (Intervention.NONCAPTURE,))},
        {"minimal_bundles": ((Intervention.NONCAPTURE, Intervention.NONCAPTURE),)},
        {"minimal_bundles": ((Intervention.SUPPORTED_EXIT,),)},
    ],
)
def test_repairs_reject_corrupt_counts_and_nonminimal_bundles(alternatives, changes):
    altered = alternatives.model_copy(
        update={"decisions": (alternatives.decisions[0].model_copy(update=changes),)}
    )
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        repair_diagnostics(altered)


@pytest.mark.parametrize(
    "field",
    [
        "total_subsets",
        "total_admissible_subsets",
        "total_distinct_states",
        "baseline_active_checks",
        "baseline_failed_checks",
    ],
)
def test_repairs_reject_corrupt_aggregate(alternatives, field):
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        repair_diagnostics(alternatives.model_copy(update={field: -1}))


def test_repairs_reject_duplicate_catalog_operator(alternatives):
    altered = alternatives.model_copy(
        update={"catalog": (*alternatives.catalog, alternatives.catalog[0])}
    )
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        repair_diagnostics(altered)


def test_omission_rejects_valid_but_wrong_remaining_measure(corpus):
    summary = next(q for q in corpus.queries if q.query_id == "state")
    omission = summary.leave_one_work_out[0].model_copy(
        update={"remaining": summary.copy_retaining}
    )
    altered_summary = summary.model_copy(
        update={"leave_one_work_out": (omission, *summary.leave_one_work_out[1:])}
    )
    altered = corpus.model_copy(
        update={
            "queries": tuple(
                altered_summary if q.query_id == "state" else q for q in corpus.queries
            )
        }
    )
    with pytest.raises(ResearchError, match="abstract_diagnostics"):
        corpus_diagnostics(altered, ("state",))
