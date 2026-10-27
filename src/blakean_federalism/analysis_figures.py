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
    scale = math.pow(10, math.floor(math.log10(maximum / 4)))
    step = next(v * scale for v in (1, 2, 5, 10) if v * scale >= maximum / 4)
    return 4 * step


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
        "Pooled text and equal-family weighting",
        "Per 10,000 tokens · red circle: pooled / black square: equal-family mean",
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
    _axis(c, maximum, 128, 190, 82, 349)
    text(c, "POOLED / EQUAL", 330, 367, 110, 8, MUTED)
    text(c, "EXACT TEXT", 447, 367, 73, 8, MUTED)
    for i, query in enumerate(FOCUS):
        y = 329 - 32 * i
        row = rows[query]
        families = sum(
            any(m.query_id == query and m.measure.occurrences > 0 for m in st.queries)
            for st in stats.strata
            if st.dimension == "work"
        )
        text(c, query, 20, y + 9, 104, 10)
        text(c, f"{row.copy_retaining.occurrences:,} occurrences", 20, y - 6, 104, 8, MUTED)
        pooled, equal = (
            row.copy_retaining.rate_per_10000_tokens,
            row.work_balanced_rate_per_10000_tokens,
        )
        if pooled is not None and equal is not None:
            line(c, 128 + 190 * pooled / maximum, y, 128 + 190 * equal / maximum, y, MUTED, 1)
        if pooled is not None:
            circle(c, 128 + 190 * pooled / maximum, y, 3, RED, RED)
        if equal is not None:
            c.setFillColor(HexColor(BLACK))
            c.rect(125 + 190 * equal / maximum, y - 3, 6, 6, fill=1, stroke=0)
        text(c, f"{number(pooled)} / {number(equal)}", 330, y + 9, 110, 9)
        text(c, number(row.exact_text.rate_per_10000_tokens), 447, y + 9, 73, 9)
        text(c, f"{row.exact_text.occurrences:,} hits", 447, y - 6, 73, 8, MUTED)
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
    line(c, 20, 70, 520, 70)
    exact = rows[FOCUS[0]].exact_text
    text(
        c,
        "".join(
            (
                f"Pooled denominator: {stats.primary_tokens:,} tokens / ",
                f"{stats.primary_source_units} units.",
            )
        ),
        20,
        62,
        500,
        8.5,
    )
    text(
        c,
        "".join(
            (
                f"Exact-text denominator: {exact.tokens:,} tokens / {exact.source_units} units; ",
                f"{len(stats.exact_duplicate_groups)} identical-text groups.",
            )
        ),
        20,
        47,
        500,
        8.5,
    )
    text(
        c,
        "Equal mean: positive-token families. Rounded rates can conceal changed counts.",
        20,
        31,
        500,
        8,
        MUTED,
    )


def sensitivity(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which omissions change the pooled rate?",
        "Rates per 10,000 tokens · all deletions in grey / complete collection in red",
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
    text(c, "LARGEST FAMILY", 419, 367, 101, 8, MUTED)
    for i, query in enumerate(FOCUS):
        y = 330 - i * 34
        row = rows[query]
        text(c, query, 20, y + 6, 104, 10)
        share = row.maximum_work_occurrence_share
        contributions = [
            (m.measure.occurrences, str(st.key[0]))
            for st in stats.strata
            if st.dimension == "work"
            for m in st.queries
            if m.query_id == query
        ]
        hits, family = max(contributions, default=(0, "N/A"))
        text(c, family if share is not None else "N/A", 419, y + 12, 101, 8)
        text(
            c,
            "N/A" if share is None else f"{hits}/{row.copy_retaining.occurrences} ({share:.0%})",
            419,
            y,
            101,
            8,
        )
        if ranges[query]:
            lower, upper = min(v for v, _ in ranges[query]), max(v for v, _ in ranges[query])
            lo, hi = 128 + 280 * lower / maximum, 128 + 280 * upper / maximum
            line(c, lo, y, hi, y, GREY, 1)
            for value, _ in ranges[query]:
                at = 128 + 280 * value / maximum
                line(c, at, y - 4, at, y + 4, MUTED, 0.6)
            for at in (lo, hi):
                line(c, at, y - 4, at, y + 4, MUTED, 1)
            endpoints: list[str] = []
            for value in (lower, upper):
                ids = sorted(k for v, k in ranges[query] if v == value)
                endpoints.append(
                    "".join(
                        (
                            f"{number(value)} omit {ids[0]}",
                            (f" (+{len(ids) - 1} tied)" if len(ids) > 1 else ""),
                        )
                    ),
                )
            text(c, "  /  ".join(endpoints), 128, y - 9, 390, 7.8, MUTED)
        else:
            text(
                c,
                "".join(
                    (
                        "N/A: no defined deletion rate; pooled ",
                        number(row.copy_retaining.rate_per_10000_tokens),
                    )
                ),
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
        "Endpoints: first omitted ID + ties. Largest family: hits / all query hits.",
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
    families = {
        q: {
            str(st.key[0])
            for st in stats.strata
            if st.dimension == "work"
            and any(m.query_id == q and m.measure.occurrences for m in st.queries)
        }
        for q in FOCUS
    }
    left, bottom, width, height = 116, 143, 50, 23
    for i, query in enumerate(FOCUS):
        c.saveState()
        c.translate(left + width * i + 16, 334)
        c.rotate(40)
        c.setFillColor(HexColor(BLACK))
        c.setFont("BF-Vera", 9)
        c.drawString(0, 0, query)
        c.restoreState()
        text(
            c,
            f"{query} {len(families[query])}/{stats.primary_work_groups}",
            20,
            bottom + height * (8 - i) - 4,
            94,
            8.5,
        )
        for j, other in enumerate(FOCUS):
            value = (
                (1.0 if families[query] else None)
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
    text(c, "DIRECTION MATTERS", 20, 124, 260, 9, RED)
    for i in range(5):
        shade = 255 - round(195 * i / 4)
        c.setFillColor(HexColor(f"#{shade:02x}{shade:02x}{shade:02x}"))
        c.rect(385 + 19 * i, 113, 19, 9, fill=1, stroke=0)
    label(c, "0", 378, 114, 8)
    label(c, "1", 488, 114, 8)
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
        text(
            c,
            "".join(
                (
                    f"{p.both_matches} shared / {p.either_matches} either: ",
                    ", ".join(sorted(families[left_query] & families[right_query])),
                )
            ),
            20,
            93 - i * 25,
            500,
            7.5,
            MUTED,
        )
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
        "Repair bundles across the finite family",
        "Fixed actions, populations and material duties · exact declared operator IDs",
    )
    rows = [d for d in experiment.decisions if d.baseline_failed_rules]
    text(c, "FAILED RECORD / MINIMUM BUNDLE", 20, 367, 235, 8, MUTED)
    text(c, "ADMISSIBLE / TESTED BY BUNDLE SIZE", 274, 367, 246, 8, MUTED)
    sizes = range(len(experiment.catalog) + 1)
    for k in sizes:
        label(c, str(k), 281 + 18 * k, 342, 8, MUTED)
    for i, row in enumerate(rows):
        y = 325 - i * 44
        bundles = [
            " + ".join(op.value for op in bundle)
            for bundle in row.minimal_bundles
            if len(bundle) == row.minimum_cardinality
        ]
        minimum = "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality)
        text(
            c,
            f"{row.decision_id} · minimum {minimum} · {len(bundles)} bundle(s)",
            20,
            y + 6,
            247,
            9,
            RED,
        )
        text(c, " OR ".join(bundles) if bundles else "None", 20, y - 8, 247, 8.3)
        for k, (admitted, tested) in enumerate(
            zip(row.admissible_by_size, row.subsets_by_size, strict=True)
        ):
            x = 274 + 18 * k
            c.setFillColor(HexColor(GREY))
            c.rect(x, y - 14, 14, 20, fill=1, stroke=0)
            if tested:
                c.setFillColor(HexColor(BLACK))
                c.rect(x, y - 14, 14, 20 * admitted / tested, fill=1, stroke=0)
            else:
                label(c, "N/A", x + 7, y - 7, 6)
        text(
            c,
            "".join(
                (
                    f"{row.admissible_subsets:,}/{row.subset_count:,} subsets; ",
                    f"{row.distinct_states} distinct records",
                )
            ),
            274,
            y - 18,
            246,
            8,
        )
        line(c, 20, y - 35, 520, y - 35, GREY, 0.5)
    text(
        c,
        "Strip height: admissible / tested at each size, 0 to 1. Not success probability.",
        20,
        99,
        500,
        8,
    )
    text(
        c,
        "".join(
            (
                f"ALL {len(experiment.decisions)} RECORDS: ",
                f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                "admissible subsets; ",
                f"{experiment.total_distinct_states} distinct records",
            )
        ),
        20,
        82,
        500,
        10,
        RED,
    )
    bounded = [d for d in experiment.decisions if not d.baseline_failed_rules]
    text(
        c,
        "".join(
            (
                f"{len(bounded)} bounded baselines: minimum 0; ",
                f"{sum(d.admissible_subsets for d in bounded):,} admissible subsets.",
            )
        ),
        20,
        55,
        500,
        8,
    )
    text(
        c,
        "Distinct resulting records include admissible and inadmissible outcomes.",
        20,
        37,
        500,
        8,
        MUTED,
    )
