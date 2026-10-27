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
            f"≤ {budget} words" if budget else "Doc ALL",
            196 + index * 71,
            342,
            9,
            RED if budget else BLACK,
        )
    for query_index, pair in enumerate(PAIRS):
        y = 320 - query_index * 36
        text(c, pair[0] + " +", 20, y, 140, 11)
        text(c, pair[1], 20, y - 14, 140, 11)
        for column in range(len(BUDGETS)):
            row = study.rows[query_index * len(BUDGETS) + column]
            x = 196 + column * 71
            color = RED if row.request.window_words else BLACK
            label(c, str(row.matched_source_units), x, y - 10, 13, color)
            label(c, f"({row.total_occurrences:,})", x, y - 24, 9, MUTED)
        line(c, 20, y - 32, 520, y - 32)
    text(c, "Cells: matched units; (participating literal occurrences).", 20, 97, 500, 10)
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
        "Windows include phrase tokens; Doc ALL can span an entire stored poem.",
        20,
        64,
        500,
        9,
        MUTED,
    )
    text(
        c,
        "Per-term counts, matched families and rates per 10,000 tokens are in the JSON.",
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
