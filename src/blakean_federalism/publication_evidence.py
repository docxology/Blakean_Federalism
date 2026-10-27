# Copyright (c) 2026 Daniel Ari Friedman
"""Observed textual comparisons and separately bounded synthetic interventions."""

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import FOCUS
from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, MUTED, RED, circle, label, line, text
from .institutional_experiment_models import InstitutionalExperiment
from .models import ResearchError
from .workbench_models import Workbench


def evidence(c: Canvas, report: Workbench) -> None:
    stats = report.corpus_statistics
    experiment = report.institutional_experiments
    if stats is None or experiment is None:
        raise ResearchError(
            "publication_statistics", "Quantitative abstract requires statistics and experiments"
        )
    text(c, "04", 20, 503, 32, 11, RED)
    text(c, "From sources to bounded tests", 55, 505, 465, 21)
    text(
        c,
        "Observed text directs reading; synthetic records expose programmed safeguards.",
        55,
        477,
        465,
        10,
        MUTED,
    )
    line(c, 20, 458, 520, 458, RED, 1.5)
    text(c, "OBSERVED TEXT", 20, 443, 180, 11, RED)
    text(c, f"{report.source_units:,} imported units", 20, 421, 175, 16)
    text(
        c,
        (
            f"{stats.primary_source_units} primary extracts / "
            f"{stats.primary_work_groups} source families"
        ),
        220,
        422,
        300,
        12,
    )
    text(c, f"Pooled denominator: {stats.primary_tokens:,} word tokens", 220, 404, 300, 10)
    _draw_rates(c, stats)
    _draw_repairs(c, experiment)


def _draw_rates(c: Canvas, stats: CorpusStatistics) -> None:
    line(c, 20, 389, 520, 389, BLACK, 0.6)
    queries = {q.query_id: q for q in stats.queries}
    positive_families = len({u.work_id for u in stats.units if u.tokens > 0})
    text(c, "QUERY", 20, 379, 100, 9)
    text(c, "HITS", 133, 379, 50, 9)
    text(c, "UNITS / FAMILIES", 191, 379, 135, 9)
    text(c, "RATES PER 10,000 TOKENS", 342, 379, 178, 9)
    text(c, "Matched / total", 191, 364, 135, 9, MUTED)
    text(c, "Pooled / equal-family mean", 342, 364, 178, 9, RED)
    for i, key in enumerate(FOCUS):
        y = 345 - i * 18
        q = queries.get(key)
        text(c, key, 20, y, 105, 10)
        if q is None:
            text(c, "N/A / query absent", 133, y, 387, 9, MUTED)
            continue
        families = sum(
            any(m.query_id == key and m.measure.occurrences > 0 for m in st.queries)
            for st in stats.strata
            if st.dimension == "work"
        )
        text(c, f"{q.copy_retaining.occurrences:,}", 133, y, 52, 10)
        text(
            c,
            "".join(
                (
                    f"{q.copy_retaining.matched_units}/{q.copy_retaining.source_units}  /  ",
                    f"{families}/{stats.primary_work_groups}",
                )
            ),
            191,
            y,
            140,
            10,
        )
        a, b = q.copy_retaining.rate_per_10000_tokens, q.work_balanced_rate_per_10000_tokens
        rate = "N/A" if a is None or b is None else f"{a:.2f} / {b:.2f}"
        text(c, rate, 342, y, 178, 10, RED)
    text(
        c,
        f"Equal mean: {positive_families} positive-token families; presence ≠ occurrences.",
        20,
        199,
        500,
        9,
        MUTED,
    )


def _draw_repairs(c: Canvas, experiment: InstitutionalExperiment) -> None:
    line(c, 20, 181, 520, 181, BLACK, 0.8)
    text(c, "FINITE SYNTHETIC CASES", 20, 172, 270, 11, RED)
    text(c, "Minimum changes to each failed baseline", 20, 155, 300, 10)
    failed = [d for d in experiment.decisions if d.baseline_failed_rules]
    for i, row in enumerate(failed):
        x = 37 + i * 52
        label(c, row.decision_id.split("-")[0], x, 133, 10)
        if row.minimum_cardinality is None:
            text(c, "N/A", x - 15, 128, 40, 9, MUTED)
            continue
        for k in range(row.minimum_cardinality):
            circle(c, x, 117 - k * 12, 4, RED, RED)
        label(c, str(row.minimum_cardinality), x, 77, 10, RED)
    names = {
        "equal_personhood": "personhood",
        "open_affiliation": "affiliation",
        "supported_exit": "exit",
        "noncapture": "non-capture",
        "contestation": "contestation",
        "charter": "competence warrant",
        "unranked_rights": "unranked rights",
        "nonmember_standing": "nonmembers",
        "burden_allocation": "burdens",
        "treaty_and_refusal": "treaty / refusal",
    }
    for i, row in enumerate(failed):
        bundles = [b for b in row.minimal_bundles if len(b) == row.minimum_cardinality]
        description = " OR ".join(
            " + ".join(names.get(op.value, op.value) for op in b) for b in bundles
        )
        text(c, row.decision_id.split("-")[0] + " " + description, 295, 155 - i * 15, 225, 9)
    text(
        c,
        (
            f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} "
            f"admissible subsets; {experiment.total_distinct_states} distinct "
            f"records"
        ),
        20,
        63,
        500,
        10,
    )
    line(c, 20, 38, 520, 38, BLACK, 0.6)
    text(
        c,
        (
            "Inactive operators repeat records; distinct resulting "
            "decision records are counted separately."
        ),
        20,
        31,
        500,
        9,
        MUTED,
    )
