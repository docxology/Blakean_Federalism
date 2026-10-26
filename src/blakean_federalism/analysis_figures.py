# Copyright (c) 2026 Daniel Ari Friedman
"""Source-family comparisons and finite intervention results as vector figures."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, GREY, MUTED, RED, WHITE, circle, label, line, text
from .workbench_models import Workbench

FOCUS = ("states", "persons", "nations", "eternity", "liberty", "law", "particulars", "imagination")


def number(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def _heading(c: Canvas, title: str, subtitle: str) -> None:
    text(c, title, 20, 430, 500, 19)
    text(c, subtitle, 20, 401, 500, 10, MUTED)
    line(c, 20, 375, 520, 375, RED, 1.5)


def rates(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Copies change the statistical emphasis",
        "Occurrences per 10,000 tokens / red: all copies pooled / black: equal source-family mean",
    )
    rows = {q.query_id: q for q in stats.queries}
    maximum = (
        max(
            max(
                rows[q].copy_retaining.rate_per_10000_tokens or 0,
                rows[q].work_balanced_rate_per_10000_tokens or 0,
            )
            for q in FOCUS
        )
        or 1
    )
    for i, q in enumerate(FOCUS):
        y = 345 - i * 34
        row = rows[q]
        text(c, q, 20, y + 5, 102, 10)
        for rate, dy, color in (
            (row.copy_retaining.rate_per_10000_tokens, 0, RED),
            (row.work_balanced_rate_per_10000_tokens, -8, BLACK),
        ):
            if rate is not None:
                x = 137 + 283 * rate / maximum
                line(c, 137, y + dy, x, y + dy, color, 2)
                circle(c, x, y + dy, 2.7, color, color)
        text(
            c,
            (
                f"{number(row.copy_retaining.rate_per_10000_tokens)} "
                f"/ {number(row.work_balanced_rate_per_10000_tokens)}"
            ),
            435,
            y + 5,
            85,
            10,
        )
    line(c, 137, 73, 420, 73, GREY)
    for value in (0, maximum / 2, maximum):
        x = 137 + 283 * value / maximum
        label(c, f"{value:.1f}", x, 57, 9, MUTED)
    text(
        c,
        (
            f"{stats.primary_source_units} units / {stats.primary_work_groups} "
            f"source-family groups / {stats.primary_tokens:,} tokens"
        ),
        20,
        35,
        500,
        9,
        MUTED,
    )


def sensitivity(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which rates depend on one source family?",
        "Grey interval: leave-one-family-out range / red dot: all-copy pooled rate",
    )
    rows = {q.query_id: q for q in stats.queries}
    ranges = {
        q: [
            o.remaining.rate_per_10000_tokens
            for o in rows[q].leave_one_work_out
            if o.remaining.rate_per_10000_tokens is not None
        ]
        for q in FOCUS
    }
    values = [v for series in ranges.values() for v in series]
    values.extend(
        q.copy_retaining.rate_per_10000_tokens
        for q in rows.values()
        if q.copy_retaining.rate_per_10000_tokens is not None
    )
    maximum = max(values, default=1) or 1
    text(c, "QUERY GROUP", 20, 361, 110, 9, MUTED)
    text(c, "RATE PER 10,000 TOKENS", 137, 361, 283, 9, MUTED)
    text(c, "MAX HIT SHARE", 435, 361, 85, 9, MUTED)
    for i, q in enumerate(FOCUS):
        y = 329 - i * 32
        row = rows[q]
        text(c, q, 20, y + 5, 108, 10)
        if ranges[q]:
            lower, upper = min(ranges[q]), max(ranges[q])
            line(c, 137 + 283 * lower / maximum, y, 137 + 283 * upper / maximum, y, "#777777", 4)
        else:
            text(c, "N/A: no defined deletion rate", 137, y + 5, 283, 9, MUTED)
        pooled = row.copy_retaining.rate_per_10000_tokens
        if pooled is not None:
            circle(c, 137 + 283 * pooled / maximum, y, 4, RED, WHITE)
        share = row.maximum_work_occurrence_share
        value = "N/A" if share is None else f"{share:.0%}"
        text(c, value, 450, y + 5, 70, 10)

    line(c, 137, 73, 420, 73, GREY)
    for value in (0, maximum / 2, maximum):
        label(c, f"{value:.1f}", 137 + 283 * value / maximum, 57, 9, MUTED)
    text(
        c,
        (
            "Max hit share = largest family's share of occurrences; "
            "each omission recomputes tokens too."
        ),
        20,
        35,
        500,
        9,
        MUTED,
    )


def cooccurrence(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which vocabularies share source families?",
        "Work-ID presence / Jaccard = shared groups divided by groups containing either query",
    )
    pairs = {
        (p.left_query, p.right_query): p
        for p in stats.cooccurrences
        if p.universe == "work_presence"
    }
    matches = {q.query_id: q.copy_retaining.matched_units for q in stats.queries}
    for i, q in enumerate(FOCUS):
        text(c, f"{i + 1}  {q}", 20, 347 - i * 32, 128, 10)
        label(c, str(i + 1), 175 + i * 37, 361, 10)
        for j, other in enumerate(FOCUS):
            x, y = 158 + j * 37, 322 - i * 32
            if i == j:
                c.setFillColor(HexColor(BLACK))
                c.rect(x, y, 34, 28, fill=1, stroke=0)
                label(c, "1.00" if matches[q] else "N/A", x + 17, y + 10, 8, WHITE)
            else:
                p = pairs.get((q, other)) or pairs[(other, q)]
                value = p.jaccard
                shade = WHITE
                if value is not None:
                    green, blue = round(255 - 175 * value), round(255 - 140 * value)
                    shade = f"#ff{green:02x}{blue:02x}"
                c.setFillColor(HexColor(shade))
                c.rect(x, y, 34, 28, fill=1, stroke=0)
                label(c, "N/A" if value is None else f"{value:.2f}", x + 17, y + 10, 8)
    text(c, "0.00 = disjoint / 1.00 = the same groups contain both vocabularies", 20, 57, 500, 9)
    text(
        c,
        (
            f"{stats.primary_work_groups} groups; a full extraction "
            f"can contain distant, opposed or differently spoken "
            f"passages."
        ),
        20,
        35,
        500,
        9,
        MUTED,
    )


def repairs(c: Canvas, report: Workbench) -> None:
    experiment = report.institutional_experiments
    if experiment is None:
        return
    _heading(
        c,
        "Repair the safeguard, preserve the dispute",
        (
            "Minimum intervention bundles / affected populations, "
            "coercion and material duties stay fixed"
        ),
    )
    rows = [d for d in experiment.decisions if d.baseline_failed_rules]
    text(c, "CASE / FAILED RULES", 20, 355, 300, 9, MUTED)
    text(c, "MINIMUM CHANGES", 350, 355, 170, 9, MUTED)
    for i, row in enumerate(rows):
        y = 327 - i * 47
        text(c, row.decision_id, 20, y, 140, 11)
        text(
            c,
            ", ".join(code.replace("_", " ").lower() for code in row.baseline_failed_rules),
            164,
            y,
            173,
            9,
        )
        if row.minimum_cardinality is not None:
            for j in range(row.minimum_cardinality):
                circle(c, 368 + j * 24, y - 9, 7, RED, RED)
            text(c, str(row.minimum_cardinality), 464, y, 56, 12, RED)
        else:
            text(c, "None", 350, y, 170, 10, RED)
        line(c, 20, y - 35, 520, y - 35, GREY, 0.5)
    text(
        c,
        (
            f"{experiment.total_subsets:,} declared subsets / {experiment.total_distinct_states} "
            f"distinct resulting records"
        ),
        20,
        70,
        500,
        11,
        RED,
    )
    text(
        c,
        (
            "Inactive operators leave a record unchanged. Bundles "
            "satisfy the programmed predicates; action labels "
            "and protected context remain visible."
        ),
        20,
        44,
        500,
        9,
        MUTED,
    )
