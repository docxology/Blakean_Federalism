# Copyright (c) 2026 Daniel Ari Friedman
"""Source-weighting ratios and finite family-deletion sensitivity for the abstract."""

from math import ceil

from reportlab.pdfgen.canvas import Canvas

from .abstract_layout import AbstractSources, cell, footer, heading
from .figure_style import BLACK, GREY, MUTED, RED, circle, label, line


def corpus_page(c: Canvas, source: AbstractSources) -> None:
    heading(
        c,
        "Lexical rates and dependence on source families",
        (
            "Copies retained; red points change family weighting, grey spans delete one family at "
            "a time."
        ),
    )
    stats = source.statistics
    for x, number, detail in (
        (20, f"{source.report.source_units:,}", "imported units, all source roles"),
        (
            189,
            f"{stats.primary_source_units} / {stats.primary_work_groups}",
            "primary extracts / source families",
        ),
        (358, f"{stats.primary_tokens:,}", "primary Unicode word tokens"),
    ):
        cell(c, number, x, 431, 162, 22, size=13, font="BF-Serif-Bold")
        cell(c, detail, x, 408, 162, 23, size=8.6, color=MUTED)
    cell(c, "QUERY / HITS", 20, 371, 90, 15, size=8.8, color=RED)
    cell(c, "RELATIVE TO POOLED", 117, 371, 190, 15, size=8.8, color=RED)
    cell(c, "POOLED / EQUAL", 326, 371, 91, 15, size=8.8, color=RED)
    cell(c, "LEADING FAMILY", 422, 371, 98, 15, size=8.8, color=RED)
    ratios = [
        q.equal_family_rate / q.pooled_rate
        for q in source.corpus
        if q.equal_family_rate is not None and q.pooled_rate not in (None, 0)
    ]
    ratios.extend(
        q.loo_max_rate / q.pooled_rate
        for q in source.corpus
        if q.loo_max_rate is not None and q.pooled_rate not in (None, 0)
    )
    upper = max(1.5, ceil(max(ratios, default=1) * 2) / 2)
    left, width = 117.0, 190.0
    scale = width / upper
    for tick in range(int(upper * 2) + 1):
        value = tick / 2
        x = left + value * scale
        line(c, x, 341, x, 159, GREY, 0.35)
        label(c, f"{value:g}", x, 348, 8.4, MUTED)
    line(c, left + scale, 341, left + scale, 159, BLACK, 0.8)
    for index, q in enumerate(source.corpus):
        top = 333 - index * 23.5
        y = top - 6
        cell(c, f"{q.query_id} {q.occurrences:,}", 20, top, 91, 13, size=9.1)
        cell(
            c,
            f"{q.matched_families}/{q.positive_token_families} families",
            20,
            top - 12,
            91,
            12,
            size=8.6,
            color=MUTED,
        )
        if q.pooled_rate not in (None, 0) and q.equal_family_rate is not None:
            if q.loo_min_rate is not None and q.loo_max_rate is not None:
                low = left + q.loo_min_rate / q.pooled_rate * scale
                high = left + q.loo_max_rate / q.pooled_rate * scale
                line(c, low, y, high, y, MUTED, 0.7)
                line(c, low, y - 2, low, y + 2, MUTED, 0.6)
                line(c, high, y - 2, high, y + 2, MUTED, 0.6)
            circle(
                c,
                left + q.equal_family_rate / q.pooled_rate * scale,
                y,
                2.6,
                RED,
                fill=RED,
                width=0.6,
            )
        else:
            cell(c, "ratio undefined", 121, top, 178, 12, size=8.7, color=MUTED)
        rates = (
            "N/A"
            if q.pooled_rate is None or q.equal_family_rate is None
            else f"{q.pooled_rate:.2f} / {q.equal_family_rate:.2f}"
        )
        cell(c, rates, 326, top, 91, 15, size=9.2)
        share = "N/A" if q.top_family_share is None else f"{100 * q.top_family_share:.1f}%"
        family = ", ".join(key.replace("-", " ").title() for key in q.top_family_ids) or "none"
        cell(c, f"{family}: {share}", 422, top, 98, 24, size=8.6)
    line(c, 20, 141, 520, 141, BLACK, 0.5)
    cell(
        c,
        "1 = pooled baseline. Red = equal-family / pooled. Grey = deletion-rate / pooled.",
        20,
        134,
        500,
        16,
        size=8.8,
    )
    lookup = {q.query_id: q for q in source.corpus}
    states = lookup["states"]
    particulars = lookup["particulars"]
    imagination = lookup["imagination"]
    deletion = "N/A" if states.loo_min_rate is None else f"{states.loo_min_rate:.3f}"
    cell(
        c,
        (
            f"States: largest count in {', '.join(key.title() for key in states.top_family_ids)}; "
            "lowest deletion rate "
            f"follows omitting {', '.join(key.title() for key in states.loo_min_family_ids)} "
            f"({deletion}/10,000)."
        ),
        20,
        120,
        500,
        28,
        size=9.1,
    )
    cell(
        c,
        (
            f"Particulars: {particulars.top_family_occurrences}/{particulars.occurrences} hits in "
            f"the leading family; matched families "
            f"{particulars.matched_families}/{particulars.positive_token_families}. Compare "
            f"pooled and equal-family weighting to inspect this concentration."
        ),
        20,
        91,
        500,
        28,
        size=9.1,
    )
    direction = (
        "N/A"
        if imagination.pooled_rate is None or imagination.equal_family_rate is None
        else f"{imagination.pooled_rate:.2f} to {imagination.equal_family_rate:.2f}"
    )
    cell(
        c,
        (
            f"Imagination: the rate moves {direction} per 10,000 under equal-family weighting. "
            f"Short and long source families contribute differently."
        ),
        20,
        62,
        500,
        25,
        size=9.1,
    )
    footer(
        c,
        (
            "Rates use whole-word query groups per 10,000 tokens. Equal-family means include "
            "positive-token families with zero hits. Deletion spans describe this finite "
            "collection; they are not confidence intervals."
        ),
    )
