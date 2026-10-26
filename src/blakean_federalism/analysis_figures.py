# Copyright (c) 2026 Daniel Ari Friedman
"""Vector comparisons with explicit estimands and finite enumeration denominators."""

import math

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, GREY, MUTED, RED, WHITE, circle, label, line, text
from .workbench_models import Workbench

FOCUS = ("states", "persons", "nations", "eternity", "liberty", "law", "particulars", "imagination")


def number(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def _heading(c: Canvas, title: str, subtitle: str) -> None:
    text(c, title, 20, 431, 500, 19)
    text(c, subtitle, 20, 402, 500, 9)
    line(c, 20, 379, 520, 379, RED, 1.5)


def _ceiling(values: list[float]) -> float:
    maximum = max(values, default=1) or 1
    step = math.pow(10, math.floor(math.log10(maximum))) / 2
    return math.ceil(maximum / step) * step


def _axis(c: Canvas, maximum: float, x: float, width: float, bottom: float, top: float) -> None:
    for i in range(5):
        value = maximum * i / 4
        at = x + width * i / 4
        line(c, at, bottom, at, top, GREY, 0.45)
        label(c, f"{value:g}", at, top + 7, 8, MUTED)
    line(c, x, bottom, x, top, MUTED, 0.7)


def rates(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Copies change the statistical emphasis",
        "Occurrences per 10,000 tokens · pooled copies in red / equal-family mean in black",
    )
    rows = {q.query_id: q for q in stats.queries}
    maximum = _ceiling(
        [
            v
            for q in FOCUS
            for v in (
                rows[q].copy_retaining.rate_per_10000_tokens,
                rows[q].work_balanced_rate_per_10000_tokens,
            )
            if v is not None
        ]
    )
    _axis(c, maximum, 128, 280, 69, 349)
    text(c, "POOLED / EQUAL", 422, 367, 98, 8, MUTED)
    for i, query in enumerate(FOCUS):
        y = 329 - 34 * i
        row = rows[query]
        families = sum(
            any(m.query_id == query and m.measure.occurrences > 0 for m in st.queries)
            for st in stats.strata
            if st.dimension == "work"
        )
        text(c, query, 20, y + 9, 104, 10)
        text(c, f"{row.copy_retaining.occurrences:,} occurrences", 20, y - 6, 104, 8, MUTED)
        pooled = row.copy_retaining.rate_per_10000_tokens
        equal = row.work_balanced_rate_per_10000_tokens
        for value, dy, color in ((pooled, 3, RED), (equal, -3, BLACK)):
            if value is not None:
                end = 128 + 280 * value / maximum
                line(c, 128, y + dy, end, y + dy, color, 1.6)
                circle(c, end, y + dy, 2.5, color, color)
        text(c, f"{number(pooled)} / {number(equal)}", 422, y + 10, 98, 9)
        text(
            c,
            "".join(
                (
                    f"{families}/{stats.primary_work_groups} families · ",
                    f"{row.copy_retaining.matched_units}/{stats.primary_source_units} units",
                )
            ),
            128,
            y - 10,
            280,
            7.8,
            MUTED,
        )
    line(c, 20, 60, 520, 60)
    text(
        c,
        "".join(
            (
                f"Pooled denominator: {stats.primary_tokens:,} tokens. Equal mean: ",
                "positive-token families only.",
            )
        ),
        20,
        51,
        500,
        8.5,
    )
    text(
        c,
        "Presence counts families and individual extracts; occurrences count every match.",
        20,
        34,
        500,
        8,
        MUTED,
    )


def sensitivity(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which omissions change the pooled rate?",
        "Rates per 10,000 tokens · finite deletion range in grey / complete collection in red",
    )
    rows = {q.query_id: q for q in stats.queries}
    ranges = {
        q: [
            (o.remaining.rate_per_10000_tokens, o.omitted_work_id)
            for o in rows[q].leave_one_work_out
            if o.remaining.rate_per_10000_tokens is not None
        ]
        for q in FOCUS
    }
    maximum = _ceiling(
        [v for series in ranges.values() for v, _ in series]
        + [
            value
            for q in FOCUS
            for value in (rows[q].copy_retaining.rate_per_10000_tokens,)
            if value is not None
        ]
    )
    _axis(c, maximum, 128, 280, 70, 349)
    text(c, "MAX HIT SHARE", 431, 367, 89, 8, MUTED)
    for i, query in enumerate(FOCUS):
        y = 330 - i * 34
        row = rows[query]
        text(c, query, 20, y + 6, 104, 10)
        share = row.maximum_work_occurrence_share
        text(c, "N/A" if share is None else f"{share:.0%}", 448, y + 6, 70, 12)
        if ranges[query]:
            lower, upper = min(v for v, _ in ranges[query]), max(v for v, _ in ranges[query])
            lo, hi = 128 + 280 * lower / maximum, 128 + 280 * upper / maximum
            line(c, lo, y, hi, y, MUTED, 4)
            for at in (lo, hi):
                line(c, at, y - 4, at, y + 4, MUTED, 1)
            endpoints: list[str] = []
            for value in (lower, upper):
                ids = sorted(k for v, k in ranges[query] if v == value)
                endpoints.append(
                    f"{number(value)} omit {ids[0]}"
                    + (f" (+{len(ids) - 1} tied)" if len(ids) > 1 else "")
                )
            text(c, "  /  ".join(endpoints), 128, y - 9, 390, 7.8, MUTED)
        else:
            text(
                c,
                "N/A: no defined deletion rate; pooled "
                + number(row.copy_retaining.rate_per_10000_tokens),
                128,
                y - 9,
                390,
                8,
                MUTED,
            )
        pooled = row.copy_retaining.rate_per_10000_tokens
        if pooled is not None:
            circle(c, 128 + 280 * pooled / maximum, y, 3, RED, WHITE)
    line(c, 20, 59, 520, 59)
    text(
        c,
        "Each omission removes hits and tokens. Finite ranges are not confidence intervals.",
        20,
        50,
        500,
        8.5,
    )
    text(
        c,
        "Endpoints: first omitted ID + tie count. Max hit share: largest family share.",
        20,
        33,
        500,
        8,
        MUTED,
    )


def cooccurrence(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which vocabularies share source families?",
        "Jaccard = shared / either source families · 0 disjoint, 1 identical presence",
    )
    pairs = {
        (p.left_query, p.right_query): p
        for p in stats.cooccurrences
        if p.universe == "work_presence"
    }
    matches = {q.query_id: q.copy_retaining.matched_units for q in stats.queries}
    left, bottom, width, height = 116, 143, 50, 23
    for i, query in enumerate(FOCUS):
        c.saveState()
        c.translate(left + width * i + 16, 334)
        c.rotate(40)
        c.setFillColor(HexColor(BLACK))
        c.setFont("BF-Vera", 9)
        c.drawString(0, 0, query)
        c.restoreState()
        text(c, query, 20, bottom + height * (8 - i) - 6, 92, 9)
        for j, other in enumerate(FOCUS):
            value = (
                (1.0 if matches[query] else None)
                if i == j
                else (pairs.get((query, other)) or pairs[(other, query)]).jaccard
            )
            shade = 255 if value is None else round(255 - 195 * value)
            c.setFillColor(HexColor(f"#{shade:02x}{shade:02x}{shade:02x}"))
            x, y = left + j * width, bottom + (7 - i) * height
            c.rect(x, y, width - 1, height - 1, fill=1, stroke=0)
            label(
                c,
                number(value),
                x + (width - 1) / 2,
                y + 7,
                9,
                WHITE if value is not None and value > 0.7 else BLACK,
            )
    line(c, 20, 132, 520, 132, RED)
    text(c, "DIRECTION MATTERS", 20, 124, 500, 9, RED)
    for i, (left_query, right_query) in enumerate(
        (("states", "nations"), ("liberty", "particulars"))
    ):
        p = pairs.get((left_query, right_query)) or pairs[(right_query, left_query)]
        forward = p.right_given_left if p.left_query == left_query else p.left_given_right
        backward = p.left_given_right if p.left_query == left_query else p.right_given_left
        text(
            c,
            "".join(
                (
                    f"Pr({right_query}|{left_query}) {number(forward)}; ",
                    f"Pr({left_query}|{right_query}) {number(backward)}; lift {number(p.lift)}",
                )
            ),
            20,
            105 - i * 25,
            500,
            9,
        )
        text(c, f"{p.both_matches} shared families", 20, 93 - i * 25, 500, 7.5, MUTED)
    text(
        c,
        "".join(
            (
                "Conditional = shared / conditioning families. Lift uses ",
                f"{stats.primary_work_groups} families and marginal presence.",
            )
        ),
        20,
        46,
        500,
        8,
        MUTED,
    )
    text(
        c,
        "Family presence can join distant or opposed passages; it does not establish agreement.",
        20,
        29,
        500,
        8,
        MUTED,
    )


def repairs(c: Canvas, report: Workbench) -> None:
    experiment = report.institutional_experiments
    if experiment is None:
        return
    _heading(
        c,
        "Minimum safeguards for failed records",
        "Synthetic finite enumeration · fixed actions, populations, coercion and material duties",
    )
    rows = [d for d in experiment.decisions if d.baseline_failed_rules]
    text(c, "BASELINE / FAILED RULES", 20, 366, 145, 8, MUTED)
    text(c, "MINIMUM OPERATOR BUNDLE", 175, 366, 224, 8, MUTED)
    text(c, "ADMISSIBLE / TESTED", 407, 366, 113, 8, MUTED)
    for i, row in enumerate(rows):
        y = 345 - i * 49
        text(c, row.decision_id, 20, y, 140, 10)
        text(
            c,
            ", ".join(code.replace("_", " ").lower() for code in row.baseline_failed_rules),
            20,
            y - 15,
            140,
            8,
            MUTED,
        )
        bundles = [
            " + ".join(op.value for op in bundle)
            for bundle in row.minimal_bundles
            if len(bundle) == row.minimum_cardinality
        ]
        text(
            c,
            "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality),
            175,
            y,
            25,
            18,
            RED,
        )
        text(c, " OR ".join(bundles) if bundles else "None", 204, y, 195, 8.3)
        text(
            c,
            f"minimum {row.minimum_cardinality}; {len(bundles)} bundle(s)",
            204,
            y - 31,
            195,
            7.5,
            MUTED,
        )
        text(c, f"{row.admissible_subsets:,}/{row.subset_count:,}", 407, y, 113, 10)
        line(c, 407, y - 19, 520, y - 19, GREY, 4)
        if row.subset_count:
            line(
                c,
                407,
                y - 19,
                407 + 113 * row.admissible_subsets / row.subset_count,
                y - 19,
                BLACK,
                4,
            )
        text(c, f"{row.distinct_states} distinct records", 407, y - 28, 113, 8, MUTED)
        line(c, 20, y - 44, 520, y - 44, GREY, 0.5)
    text(
        c,
        "".join(
            (
                f"ALL {len(experiment.decisions)} RECORDS: ",
                f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                f"admissible subsets; {experiment.total_distinct_states} distinct records",
            )
        ),
        20,
        89,
        500,
        10,
        RED,
    )
    text(
        c,
        "Bars: admissible fraction (0 to 1); inactive operators repeat unchanged outcomes.",
        20,
        63,
        500,
        8,
    )
    text(
        c,
        "Failed baselines shown; bounded cases have empty bundles. No empirical efficacy claim.",
        20,
        44,
        500,
        8,
        MUTED,
    )
