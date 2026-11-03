# Copyright (c) 2026 Daniel Ari Friedman
"""Source-family omission intervals for the corpus graphical abstract."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .abstract_explanation import display_frequency
from .abstract_layout import AbstractSources, cell
from .figure_style import BLACK, GREY, MUTED, RED, line


def source_sensitivity(c: Canvas, source: AbstractSources) -> None:
    """Draw two exact deletion ranges and pooled points on a common frequency scale."""
    lookup = {row.query_id: row for row in source.corpus}
    rows = (lookup["states"], lookup["imagination"])
    rates = tuple(
        value
        for row in rows
        for value in (row.loo_min_rate, row.loo_max_rate, row.pooled_rate)
        if value is not None
    )
    ceiling = max(rates, default=0.0) or 1.0
    cell(
        c,
        "OMIT ONE FAMILY: range + pooled point, per 10,000 remaining words",
        20,
        96,
        500,
        13,
        size=8.8,
        color=RED,
    )
    for index, row in enumerate(rows):
        left = 20 + 255 * index
        cell(c, row.query_id.capitalize(), left, 79, 245, 12, size=8.8)
        start = left + 65
        line(c, start, 61, start + 170, 61, GREY, 0.5)
        low, high, pooled = row.loo_min_rate, row.loo_max_rate, row.pooled_rate
        if low is not None and high is not None:
            lo = start + 170 * low / ceiling
            hi = start + 170 * high / ceiling
            line(c, lo, 61, hi, 61, RED, 2)
            line(c, lo, 58, lo, 64, RED, 0.8)
            line(c, hi, 58, hi, 64, RED, 0.8)
        if pooled is not None:
            point = start + 170 * pooled / ceiling
            c.setFillColor(HexColor(BLACK))
            c.circle(point, 61, 2.2, fill=1, stroke=0)
        low_text, high_text = display_frequency(low), display_frequency(high)
        pooled_text = display_frequency(pooled)
        cell(
            c,
            f"Range {low_text}-{high_text}; pooled {pooled_text}",
            left,
            49,
            245,
            11,
            size=8.1,
            color=MUTED,
        )
