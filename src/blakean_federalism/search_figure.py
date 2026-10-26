# Copyright (c) 2026 Daniel Ari Friedman
"""Literal retrieval counts with matched-unit and family denominators."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, label, line, text
from .models import Role
from .search_study import SearchStudy


def draw_search_study(c: Canvas, study: SearchStudy) -> None:
    text(c, "Literal search separates the source layers", 20, 431, 500, 19)
    text(
        c,
        "All occurrences before display limits · literal whitespace · stored copies retained",
        20,
        402,
        500,
        9,
    )
    line(c, 20, 379, 520, 379, RED, 1.5)
    roles = (Role.PRIMARY, Role.EDITORIAL, Role.UNVERIFIED)
    rows = [q for q in study.queries if q.query_id != "negative_control"]
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
    for column, role in enumerate(roles):
        x = 144 + column * 128
        facets = [f for f in study.queries[0].facets if f.role == role]
        denominator = sum(f.source_units for f in facets)
        families = len({f.work_id for f in facets})
        text(c, role.value.upper(), x, 366, 120, 10, RED if role == Role.PRIMARY else BLACK)
        text(
            c,
            f"{denominator:,} units / {families} " + ("family" if families == 1 else "families"),
            x,
            350,
            120,
            8,
            MUTED,
        )
        for i in range(3):
            at = x + 112 * i / 2
            line(c, at, 84, at, 321, GREY, 0.4)
            label(c, f"{maximum * i / 2:g}", at, 326, 7, MUTED)
    text(c, "LITERAL QUERY", 20, 330, 110, 8, MUTED)
    for row, query in enumerate(rows):
        y = 313 - row * 39
        text(c, " / ".join(query.terms), 20, y, 116, 10)
        for column, role in enumerate(roles):
            x = 144 + column * 128
            facets = [f for f in query.facets if f.role == role]
            hits = sum(f.occurrences for f in facets)
            units = sum(f.matched_units for f in facets)
            families = len({f.work_id for f in facets if f.occurrences > 0})
            color = RED if role == Role.PRIMARY else BLACK
            text(c, f"{hits:,} hits", x, y, 116, 10, color)
            c.setFillColor(HexColor(color))
            c.rect(x, y - 17, 112 * hits / maximum, 3, fill=1, stroke=0)
            text(
                c,
                f"{units:,} units · {families} " + ("family" if families == 1 else "families"),
                x,
                y - 22,
                120,
                7.5,
                MUTED,
            )
    line(c, 20, 72, 520, 72)
    control = next(q for q in study.queries if q.query_id == "negative_control")
    text(
        c,
        "".join(
            (
                f"Nonsense control: {control.total_occurrences} hits across ",
                f"{study.source_units:,} units. Bars share one zero-based count scale.",
            )
        ),
        20,
        63,
        500,
        8.5,
    )
    text(
        c,
        "Family counts use distinct IDs per role; editorial includes mixed Erdman pages.",
        20,
        43,
        500,
        8,
        MUTED,
    )

    text(
        c,
        "Unverified text keeps its source label; counts do not establish authorship.",
        20,
        30,
        500,
        8,
        MUTED,
    )
