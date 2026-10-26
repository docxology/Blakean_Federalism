# Copyright (c) 2026 Daniel Ari Friedman
"""Quantitative abstract linking corpus comparisons to finite safeguard experiments."""

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import number
from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, GREY, MUTED, RED, line, text
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
            y = 322 - i * 18
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
        224,
        504,
        9,
        MUTED,
    )
    line(c, 18, 207, 522, 207, BLACK)
    if stats is not None:
        _comparisons(c, stats)
    line(c, 18, 159, 522, 159, BLACK)
    experiment = report.institutional_experiments
    text(c, "FINITE REPAIRS / MINIMUM OPERATOR BUNDLES", 18, 150, 504, 10, RED)
    if experiment is not None:
        rows = [d for d in experiment.decisions if d.baseline_failed_rules]
        for i, row in enumerate(rows):
            bundles = [
                " + ".join(op.value for op in b)
                for b in row.minimal_bundles
                if len(b) == row.minimum_cardinality
            ]
            text(c, row.decision_id.split("-")[0], 18, 132 - i * 13, 22, 8.5, RED)
            text(c, " OR ".join(bundles) if bundles else "None", 40, 132 - i * 13, 482, 8)
        text(
            c,
            "".join(
                (
                    f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                    "admissible subsets / ",
                    f"{experiment.total_distinct_states} distinct records",
                )
            ),
            18,
            61,
            504,
            9,
        )
        active = experiment.baseline_active_checks - experiment.baseline_failed_checks
        text(
            c,
            "".join(
                (
                    f"Baseline: {active} active satisfied / ",
                    f"{experiment.baseline_failed_checks} failed / ",
                    f"{experiment.baseline_inactive_checks} inactive",
                )
            ),
            18,
            46,
            504,
            8,
            RED,
        )
    line(c, 18, 31, 522, 31, GREY)
    text(
        c,
        (
            "Source-family counts guide close reading; synthetic records expose the "
            "exact safeguards changed."
        ),
        18,
        24,
        504,
        8,
        MUTED,
    )


def _comparisons(c: Canvas, stats: CorpusStatistics) -> None:
    row = next((q for q in stats.queries if q.query_id == "particulars"), None)
    if row is not None:
        defined = [
            (o.remaining.rate_per_10000_tokens, o.omitted_work_id)
            for o in row.leave_one_work_out
            if o.remaining.rate_per_10000_tokens is not None
        ]
        if defined:
            low, high = min(defined), max(defined)
            text(
                c,
                "".join(
                    (
                        f"Particulars deletion range: {number(low[0])} (omit {low[1]}) to ",
                        f"{number(high[0])} (omit {high[1]}).",
                    )
                ),
                18,
                197,
                504,
                9,
            )
        else:
            text(c, "Particulars: N/A: no defined deletion rate", 18, 197, 504, 9)
    pair = next(
        (
            p
            for p in stats.cooccurrences
            if p.universe == "work_presence"
            and {p.left_query, p.right_query} == {"liberty", "particulars"}
        ),
        None,
    )
    if pair is not None:
        text(
            c,
            "".join(
                (
                    f"Liberty / particulars: Jaccard {number(pair.jaccard)}; ",
                    f"shared {pair.both_matches}/{pair.either_matches} families; ",
                    f"lift {number(pair.lift)}.",
                )
            ),
            18,
            180,
            504,
            9,
        )
