# Copyright (c) 2026 Daniel Ari Friedman
"""Observed textual comparisons and separately bounded synthetic interventions."""

from reportlab.pdfgen.canvas import Canvas

from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, GREY, MUTED, RED, circle, label, line, text
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
    text(c, "Query / extract coverage", 20, 379, 170, 9)
    text(c, "Rates per 10,000 tokens", 190, 379, 220, 9)
    circle(c, 368, 374, 3, RED, RED)
    text(c, "pooled", 376, 380, 65, 9)
    circle(c, 438, 374, 3, BLACK)
    text(c, "equal family", 446, 380, 75, 9)
    selected = tuple(
        queries.get(key) for key in ("states", "persons", "nations", "particulars", "imagination")
    )
    present_rates = [
        v
        for row in selected
        if row is not None
        for v in (row.copy_retaining.rate_per_10000_tokens, row.work_balanced_rate_per_10000_tokens)
        if v is not None
    ]
    maximum = max(8.0, *present_rates) if present_rates else 8.0
    start, width = 190, 210
    for tick in (maximum * i / 4 for i in range(5)):
        x = start + width * tick / maximum
        line(c, x, 349, x, 226, GREY, 0.4)
        label(c, f"{tick:g}", x, 354, 8, MUTED)
    for i, key in enumerate(("states", "persons", "nations", "particulars", "imagination")):
        q = queries.get(key)
        y = 336 - i * 24
        if q is None:
            text(c, key, 20, y + 6, 100, 10)
            text(c, "N/A / query absent", 190, y + 6, 330, 9, MUTED)
            continue
        text(c, key, 20, y + 6, 100, 10)
        text(
            c,
            f"{q.copy_retaining.matched_units}/{q.copy_retaining.source_units}",
            125,
            y + 6,
            60,
            9,
            MUTED,
        )
        a = q.copy_retaining.rate_per_10000_tokens
        b = q.work_balanced_rate_per_10000_tokens
        if a is None or b is None:
            text(c, "N/A / undefined rate", 190, y + 6, 330, 9, MUTED)
            continue
        xa, xb = start + width * a / maximum, start + width * b / maximum
        line(c, xa, y, xb, y, BLACK, 1)
        circle(c, xa, y, 3, RED, RED)
        circle(c, xb, y, 3, BLACK)
        text(c, f"{a:.2f} / {b:.2f}", 418, y + 6, 102, 10)
    text(
        c,
        f"Equal family: mean of {positive_families} positive-token family rates; copies retained.",
        20,
        215,
        500,
        9,
        MUTED,
    )


def _draw_repairs(c: Canvas, experiment: InstitutionalExperiment) -> None:
    line(c, 20, 195, 520, 195, BLACK, 0.8)
    text(c, "FINITE SYNTHETIC CASES", 20, 185, 270, 11, RED)
    text(c, "Minimum changes to each failed baseline", 20, 167, 300, 10)
    failed = [d for d in experiment.decisions if d.baseline_failed_rules]
    for i, row in enumerate(failed):
        x = 37 + i * 52
        label(c, row.decision_id.split("-")[0], x, 143, 10)
        if row.minimum_cardinality is None:
            text(c, "N/A", x - 15, 128, 40, 9, MUTED)
            continue
        for k in range(row.minimum_cardinality):
            circle(c, x, 128 - k * 14, 4, RED, RED)
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
        text(c, row.decision_id.split("-")[0] + " " + description, 295, 166 - i * 15, 225, 9)
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
            "Inactive operators repeat records. Counts establish finite "
            "model behavior, not political outcomes."
        ),
        20,
        31,
        500,
        9,
        MUTED,
    )
