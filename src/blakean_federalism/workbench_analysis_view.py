# Copyright (c) 2026 Daniel Ari Friedman
"""Escaped analytical summaries for the portable workbench."""

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workbench_models import Workbench


def text(value: object) -> str:
    return escape(str(value), quote=True)


def disclosure(label: str, body: str) -> str:
    return f'<details><summary>{text(label)}</summary><div class="stack">{body}</div></details>'


def statistics_records(report: "Workbench") -> str:
    stats = report.corpus_statistics
    if stats is None:
        return "<p>No statistics attached to this historical report.</p>"
    rows: list[str] = []
    for query in stats.queries:
        pooled = query.copy_retaining.rate_per_10000_tokens
        balanced = query.work_balanced_rate_per_10000_tokens
        rate = "N/A" if pooled is None else f"{pooled:.3f}"
        mean = "N/A" if balanced is None else f"{balanced:.3f}"
        rows.append(
            "".join(
                (
                    f"<p><strong>{text(query.query_id)}</strong>: {rate} ",
                    f"pooled / {mean} equal-family; {query.copy_retaining.occurrences} ",
                    f"occurrences in {query.copy_retaining.matched_units} ",
                    "units.</p>",
                )
            )
        )
    intro = "".join(
        (
            f"<h3>Copy-sensitive corpus statistics</h3><p>{stats.primary_source_units} ",
            f"primary units; {stats.primary_work_groups} source-family ",
            f"groups; {stats.primary_tokens:,} Unicode word tokens. ",
            "Both rates are per 10,000 tokens. Equal-family rates ",
            "give each positive-token work-ID group the same weight.</p>",
        )
    )
    return intro + disclosure("Compare all query rates", "".join(rows))


def experiment_records(report: "Workbench") -> str:
    result = report.institutional_experiments
    if result is None:
        return "<p>No counterfactual experiment attached to this historical report.</p>"
    rows: list[str] = []
    for case in result.decisions:
        minimum = (
            "No admissible bundle"
            if case.minimum_cardinality is None
            else str(case.minimum_cardinality)
        )
        bundles = "; ".join(
            ", ".join(op.value for op in bundle) or "empty bundle"
            for bundle in case.minimal_bundles
        )
        rows.append(
            "".join(
                (
                    f"<p><strong>{text(case.decision_id)}</strong>: minimum ",
                    f"{minimum}; {case.distinct_states} distinct records; ",
                    f"bundles: {text(bundles)}.</p>",
                )
            )
        )
    return (
        "".join(
            (
                f"<h3>Finite safeguard interventions</h3><p>{result.total_subsets:,} ",
                f"declared subsets produce {result.total_distinct_states} ",
                "distinct records. Coercion, resource duties, treaty ",
                "implications and affected populations stay fixed. ",
                "Interventions change the recorded safeguards; the ",
                "action label remains visible.</p>",
            )
        )
    ) + disclosure("Inspect minimum bundles for all alternatives", "".join(rows))
