# Copyright (c) 2026 Daniel Ari Friedman
"""Quantitative abstract linking corpus comparisons to finite safeguard experiments."""

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import number
from .figure_style import BLACK, GREY, MUTED, RED, circle, line, text
from .workbench_models import Workbench


def evidence(c: Canvas, report: Workbench) -> None:
    text(c, "04", 18, 503, 34, 11, RED)
    text(c, "From retrieval to comparative tests", 58, 505, 464, 19)
    text(
        c,
        "Normalize copies, retain particulars and inspect the minimum safeguard bundle",
        58,
        477,
        464,
        10,
        MUTED,
    )
    line(c, 18, 452, 522, 452, RED, 2)
    stats = report.corpus_statistics
    metrics = (
        (f"{report.source_units:,}", "PINNED SOURCE UNITS"),
        (str(stats.primary_source_units) if stats else "N/A", "PRIMARY EXTRACTS"),
        (str(stats.primary_work_groups) if stats else "N/A", "SOURCE FAMILIES"),
        (f"{stats.primary_tokens:,}" if stats else "N/A", "PRIMARY WORD TOKENS"),
    )
    for index, (value, title) in enumerate(metrics):
        x = 18 + index * 131
        text(c, value, x, 431, 119, 21, RED)
        text(c, title, x, 402, 119, 8)
    line(c, 18, 378, 522, 378, BLACK)
    text(c, "COPY BALANCE CHANGES THE EMPHASIS", 18, 366, 504, 11, RED)
    for x, value, width in (
        (18, "QUERY", 120),
        (160, "HITS", 70),
        (244, "POOLED", 90),
        (354, "EQUAL FAMILY", 120),
    ):
        text(c, value, x, 343, width, 9, MUTED)
    if stats is not None:
        queries = {q.query_id: q for q in stats.queries}
        for i, query in enumerate(("states", "persons", "nations", "particulars", "imagination")):
            row = queries.get(query)
            y = 322 - i * 23
            text(c, query, 18, y, 120, 10)
            if row is None:
                text(c, "N/A / query absent", 160, y, 320, 10, MUTED)
            else:
                text(c, str(row.copy_retaining.occurrences), 160, y, 70, 10)
                text(c, number(row.copy_retaining.rate_per_10000_tokens), 244, y, 90, 10, RED)
                text(c, number(row.work_balanced_rate_per_10000_tokens), 354, y, 120, 10)
    text(
        c,
        "Rates per 10,000 tokens. Source families retain the archive's work-ID grouping.",
        18,
        202,
        504,
        9,
        MUTED,
    )
    line(c, 18, 181, 522, 181, BLACK)
    experiment = report.institutional_experiments
    text(c, "MINIMUM SAFEGUARD REPAIRS", 18, 170, 300, 11, RED)
    if experiment is not None:
        active_satisfied = experiment.baseline_active_checks - experiment.baseline_failed_checks
        rows = [d for d in experiment.decisions if d.baseline_failed_rules]
        for i, row in enumerate(rows):
            x = 18 + i * 104
            text(c, row.decision_id.split("-")[0], x, 145, 94, 11)
            for j in range(row.minimum_cardinality or 0):
                circle(c, x + 7 + j * 17, 117, 5, RED, RED)
        text(
            c,
            "".join(
                (
                    f"{experiment.total_subsets:,} subsets / {experiment.total_distinct_states} ",
                    "distinct records",
                )
            ),
            18,
            95,
            504,
            11,
        )
        text(
            c,
            "".join(
                (
                    f"Baseline: {active_satisfied} ",
                    f"active satisfied / {experiment.baseline_failed_checks} ",
                    f"failed / {experiment.baseline_inactive_checks} ",
                    "inactive",
                )
            ),
            18,
            74,
            504,
            10,
            RED,
        )
    line(c, 18, 47, 522, 47, GREY)
    text(
        c,
        "Results retain source identity, denominators, declared operations and protected context.",
        18,
        35,
        504,
        9,
        MUTED,
    )
