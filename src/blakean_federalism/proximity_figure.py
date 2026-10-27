# Copyright (c) 2026 Daniel Ari Friedman
"""A six-query matrix distinguishes local windows from document-level conjunction."""

from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, MUTED, RED, label, line, text
from .proximity_study import BUDGETS, PAIRS, ProximityStudy


def draw_proximity_study(c: Canvas, study: ProximityStudy) -> None:
    """Draw on the publication's 540 by 445 point page using its registered font."""
    text(c, "Near words, narrower evidence", 20, 433, 500, 20)
    text(c, "Six fixed literal pairs · primary text only · whole-word ALL", 20, 403, 500, 11)
    first = study.rows[0]
    text(
        c,
        " / ".join(
            (
                f"{first.eligible_source_units:,} eligible units",
                f"{first.eligible_source_families:,} source families",
                f"{first.eligible_word_tokens:,} original word tokens",
            )
        ),
        20,
        382,
        500,
        10,
        MUTED,
    )
    line(c, 20, 363, 520, 363, RED, 1.5)
    text(c, "LITERAL PAIR", 20, 351, 140, 9, MUTED)
    for index, budget in enumerate(BUDGETS):
        label(
            c,
            f"≤ {budget} words" if budget else "Whole unit",
            196 + index * 71,
            342,
            9,
            RED if budget else BLACK,
        )
    for query_index, pair in enumerate(PAIRS):
        y = 320 - query_index * 36
        text(c, pair[0] + " +", 20, y, 140, 11)
        text(c, pair[1], 20, y - 14, 140, 11)
        seen_match = False
        for column in range(len(BUDGETS)):
            row = study.rows[query_index * len(BUDGETS) + column]
            x = 196 + column * 71
            color = RED if row.request.window_words else BLACK
            if row.matched_source_units and not seen_match:
                line(c, x - 31, y + 2, x + 31, y + 2, MUTED, 0.6)
                line(c, x - 31, y - 28, x + 31, y - 28, MUTED, 0.6)
                line(c, x - 31, y + 2, x - 31, y - 28, MUTED, 0.6)
                line(c, x + 31, y + 2, x + 31, y - 28, MUTED, 0.6)
                seen_match = True
            label(
                c,
                f"{row.matched_source_units} | {row.matched_source_families}",
                x,
                y - 10,
                12,
                color,
            )
            label(c, f"({row.total_occurrences:,})", x, y - 24, 9, MUTED)
        line(c, 20, y - 32, 520, y - 32)
    text(c, "Cells: units | families; (participating term-labeled occurrences).", 20, 97, 500, 10)
    text(
        c,
        "Zero means no qualifying match, not missing data. All counts precede caps.",
        20,
        80,
        500,
        9,
        MUTED,
    )
    text(
        c,
        "Windows include phrase tokens; Whole unit = document-wide ALL.",
        20,
        64,
        500,
        9,
        MUTED,
    )
    text(
        c,
        "Outline: first nonzero budget. Occurrences are not combination counts.",
        20,
        48,
        500,
        9,
        MUTED,
    )
    text(
        c,
        "Rates use full eligible-token denominators; stored copies remain separate.",
        20,
        32,
        500,
        8.5,
        MUTED,
    )
