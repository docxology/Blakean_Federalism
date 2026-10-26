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
        "Rates per 10,000 tokens / red: pooled copies / black: equal source-family mean",
    )
    rows = {q.query_id: q for q in stats.queries}
    maximum = (
        max(
            (
                v
                for q in FOCUS
                for v in (
                    rows[q].copy_retaining.rate_per_10000_tokens,
                    rows[q].work_balanced_rate_per_10000_tokens,
                )
                if v is not None
            ),
            default=1,
        )
        or 1
    )
    for x, title, width in (
        (20, "QUERY / HITS", 110),
        (140, "RATE", 160),
        (325, "POOLED / EQUAL", 100),
        (435, "MATCHED", 85),
    ):
        text(c, title, x, 363, width, 8, MUTED)
    for i, q in enumerate(FOCUS):
        y = 338 - i * 33
        row = rows[q]
        families = sum(
            any(m.query_id == q and m.measure.occurrences > 0 for m in st.queries)
            for st in stats.strata
            if st.dimension == "work"
        )
        text(c, q, 20, y + 6, 112, 10)
        text(c, f"{row.copy_retaining.occurrences:,} occurrences", 20, y - 8, 112, 8, MUTED)
        for rate, dy, color in (
            (row.copy_retaining.rate_per_10000_tokens, 0, RED),
            (row.work_balanced_rate_per_10000_tokens, -8, BLACK),
        ):
            if rate is not None:
                x = 140 + 160 * rate / maximum
                line(c, 140, y + dy, x, y + dy, color, 2)
                circle(c, x, y + dy, 2.5, color, color)
        text(
            c,
            "".join(
                (
                    f"{number(row.copy_retaining.rate_per_10000_tokens)} / ",
                    f"{number(row.work_balanced_rate_per_10000_tokens)}",
                )
            ),
            325,
            y + 5,
            105,
            9,
        )
        text(c, f"{families}/{stats.primary_work_groups} families", 435, y + 5, 85, 8)
        text(
            c,
            f"{row.copy_retaining.matched_units}/{stats.primary_source_units} units",
            435,
            y - 8,
            85,
            8,
            MUTED,
        )
    line(c, 140, 68, 300, 68)
    for v in (0, maximum / 2, maximum):
        label(c, f"{v:.1f}", 140 + 160 * v / maximum, 54, 8, MUTED)
    text(
        c,
        "".join(
            (
                f"Pooled denominator: {stats.primary_tokens:,} tokens; equal-family mean: ",
                "positive-token families only.",
            )
        ),
        20,
        37,
        500,
        9,
        MUTED,
    )
    text(
        c,
        "Source-family IDs; matched columns count family and extract presence.",
        20,
        22,
        500,
        8,
        MUTED,
    )


def sensitivity(c: Canvas, stats: CorpusStatistics) -> None:
    _heading(
        c,
        "Which family omissions change the rate?",
        "Grey: deletion range / red: pooled rate / endpoints name the omitted source-family ID",
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
    values = [v for series in ranges.values() for v, _ in series]
    values.extend(
        q.copy_retaining.rate_per_10000_tokens
        for q in rows.values()
        if q.copy_retaining.rate_per_10000_tokens is not None
    )
    maximum = max(values, default=1) or 1
    for x, title, width in (
        (20, "QUERY", 110),
        (140, "RATE / 10,000", 155),
        (310, "LOW / OMIT", 100),
        (417, "HIGH / OMIT", 103),
    ):
        text(c, title, x, 362, width, 8, MUTED)
    for i, q in enumerate(FOCUS):
        y = 336 - i * 33
        row = rows[q]
        text(c, q, 20, y + 5, 115, 10)
        share = row.maximum_work_occurrence_share
        text(
            c,
            "max hit share " + ("N/A" if share is None else f"{share:.0%}"),
            20,
            y - 9,
            115,
            8,
            MUTED,
        )
        if ranges[q]:
            lower = min(v for v, _ in ranges[q])
            upper = max(v for v, _ in ranges[q])
            line(c, 140 + 155 * lower / maximum, y, 140 + 155 * upper / maximum, y, MUTED, 3)
            for x, value in ((310, lower), (417, upper)):
                ids = sorted(k for v, k in ranges[q] if v == value)
                text(c, number(value), x, y + 7, 100, 9)
                text(
                    c,
                    ids[0] + (f" (+{len(ids) - 1} tied)" if len(ids) > 1 else ""),
                    x,
                    y - 7,
                    100,
                    8,
                    MUTED,
                )
        else:
            text(c, "N/A: no defined deletion rate", 310, y + 5, 210, 8, MUTED)
        pooled = row.copy_retaining.rate_per_10000_tokens
        if pooled is not None:
            circle(c, 140 + 155 * pooled / maximum, y, 3, RED, WHITE)
    line(c, 140, 68, 295, 68)
    for value in (0, maximum / 2, maximum):
        label(c, f"{value:.1f}", 140 + 155 * value / maximum, 54, 8, MUTED)
    text(
        c,
        "Each omission removes its tokens too. Max hit share = largest family's share of hits.",
        20,
        37,
        500,
        8.5,
        MUTED,
    )
    text(
        c,
        (
            "Exhaustive family omissions recompute both hits and tokens. Ties show first "
            "ID + tie count."
        ),
        20,
        22,
        500,
        8,
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
        text(c, f"{i + 1}  {q}", 20, 347 - i * 27, 128, 10)
        label(c, str(i + 1), 175 + i * 37, 361, 10)
        for j, other in enumerate(FOCUS):
            x, y = 158 + j * 37, 327 - i * 27
            if i == j:
                c.setFillColor(HexColor(BLACK))
                c.rect(x, y, 34, 24, fill=1, stroke=0)
                label(c, "1.00" if matches[q] else "N/A", x + 17, y + 10, 8, WHITE)
            else:
                p = pairs.get((q, other)) or pairs[(other, q)]
                value = p.jaccard
                shade = WHITE
                if value is not None:
                    grey = round(255 - 125 * value)
                    shade = f"#{grey:02x}{grey:02x}{grey:02x}"
                c.setFillColor(HexColor(shade))
                c.rect(x, y, 34, 24, fill=1, stroke=0)
                label(c, "N/A" if value is None else f"{value:.2f}", x + 17, y + 10, 8)
    line(c, 20, 128, 520, 128, RED)
    text(c, "DIRECTIONAL PRESENCE / distinct from Jaccard", 20, 120, 500, 9, RED)
    for i, (left, right) in enumerate((("states", "nations"), ("liberty", "particulars"))):
        p = pairs.get((left, right)) or pairs[(right, left)]
        forward = p.right_given_left if p.left_query == left else p.left_given_right
        backward = p.left_given_right if p.left_query == left else p.right_given_left
        text(
            c,
            "".join(
                (
                    f"{left} / {right}: shared {p.both_matches}; ",
                    f"P({right}|{left}) {number(forward)}; ",
                    f"P({left}|{right}) {number(backward)}; lift {number(p.lift)}",
                )
            ),
            20,
            103 - i * 18,
            500,
            8.5,
        )
    text(
        c,
        "Jaccard: 0.00 disjoint; 1.00 same groups. Conditional = shared / conditioning groups.",
        20,
        59,
        500,
        8,
        MUTED,
    )
    text(
        c,
        "".join(
            (
                "Lift compares joint presence with marginal product in ",
                f"{stats.primary_work_groups} families.",
            )
        ),
        20,
        44,
        500,
        8,
        MUTED,
    )
    text(
        c,
        "Presence is evaluated across each family, including distant or opposed passages.",
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
        "Repair the safeguard, preserve the dispute",
        "Minimum operator bundles / fixed action labels, populations, coercion and material duties",
    )
    rows = [d for d in experiment.decisions if d.baseline_failed_rules]
    for x, title, width in (
        (20, "CASE / FAILED RULES", 150),
        (180, "MINIMUM BUNDLE (operator IDs)", 230),
        (430, "ENUMERATION", 90),
    ):
        text(c, title, x, 360, width, 8, MUTED)
    for i, row in enumerate(rows):
        y = 338 - i * 49
        text(c, row.decision_id, 20, y, 150, 10)
        text(
            c,
            ", ".join(code.replace("_", " ").lower() for code in row.baseline_failed_rules),
            20,
            y - 15,
            150,
            8,
            MUTED,
        )
        bundles = [
            " + ".join(op.value for op in bundle)
            for bundle in row.minimal_bundles
            if len(bundle) == row.minimum_cardinality
        ]
        text(c, " OR ".join(bundles) if bundles else "None", 180, y, 240, 9, RED)
        text(
            c,
            "".join(
                (
                    f"minimum {row.minimum_cardinality}; ",
                    f"{len(bundles)} bundle(s)",
                )
            ),
            180,
            y - 32,
            240,
            8,
            MUTED,
        )
        text(
            c, f"{row.admissible_subsets:,}/{row.subset_count:,} admissible subsets", 430, y, 90, 8
        )
        text(c, f"{row.distinct_states} distinct records", 430, y - 24, 90, 8, MUTED)
        line(c, 20, y - 44, 520, y - 44, GREY, 0.5)
    text(
        c,
        "".join(
            (
                f"ALL {len(experiment.decisions)} RECORDS: ",
                f"{experiment.total_admissible_subsets:,}/",
                f"{experiment.total_subsets:,} admissible subsets; ",
                f"{experiment.total_distinct_states} distinct records",
            )
        ),
        20,
        80,
        500,
        10,
        RED,
    )
    text(
        c,
        "Subset counts include inactive operators; distinct records collapse unchanged outcomes.",
        20,
        58,
        500,
        9,
        MUTED,
    )
    text(
        c,
        (
            "Displayed cases failed at baseline. Bundles change safeguards while retaining "
            "action labels, affected populations and material obligations."
        ),
        20,
        39,
        500,
        9,
        MUTED,
    )
