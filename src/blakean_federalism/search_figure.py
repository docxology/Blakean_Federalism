# Copyright (c) 2026 Daniel Ari Friedman
"""Source-stratum retrieval map for the literal-search study."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, MUTED, RED, line, text
from .models import Role
from .search_study import SearchStudy


def draw_search_study(c: Canvas, study: SearchStudy) -> None:
    text(c, "Literal search separates the source layers", 20, 430, 500, 19)
    text(
        c,
        "Exact phrases and words / full counts before display limits / stored copies retained",
        20,
        399,
        500,
        9,
        MUTED,
    )
    line(c, 20, 375, 520, 375, RED, 1.5)
    roles = (Role.PRIMARY, Role.EDITORIAL, Role.UNVERIFIED)
    rows = [q for q in study.queries if q.query_id != "negative_control"]
    for column, role in enumerate(roles):
        x = 171 + column * 116
        denominator = sum(f.source_units for f in study.queries[0].facets if f.role == role)
        text(c, role.value.upper(), x, 362, 112, 9, RED if role == Role.PRIMARY else BLACK)
        text(c, f"{denominator:,} eligible units", x, 346, 112, 8, MUTED)
    maximum = (
        max(
            (
                sum(f.occurrences for f in q.facets if f.role == role)
                for q in rows
                for role in roles
            ),
            default=1,
        )
        or 1
    )
    for row, query in enumerate(rows):
        y = 316 - row * 39
        text(c, query.terms[0], 20, y + 3, 142, 10)
        for column, role in enumerate(roles):
            x = 171 + column * 116
            facets = [f for f in query.facets if f.role == role]
            hits = sum(f.occurrences for f in facets)
            units = sum(f.matched_units for f in facets)
            c.setFillColor(HexColor(RED if role == Role.PRIMARY else BLACK))
            c.rect(x, y - 7, 100 * hits / maximum, 3, fill=1, stroke=0)
            text(c, f"{hits:,} hits / {units:,} units", x, y + 10, 113, 8)
    line(c, 20, 73, 520, 73)
    control = next(q for q in study.queries if q.query_id == "negative_control")
    text(
        c,
        (
            f"{study.source_units:,} units. Nonsense control: {control.total_occurrences} hits. "
            "Bars share one zero-based count scale."
        ),
        20,
        63,
        500,
        9,
    )
    text(
        c,
        (
            "Editorial includes mixed Erdman pages; unverified text retains its source label. "
            "Exact phrases preserve spaces and line breaks."
        ),
        20,
        35,
        500,
        8,
        MUTED,
    )
