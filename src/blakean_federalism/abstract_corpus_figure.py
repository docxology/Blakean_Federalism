# Copyright (c) 2026 Daniel Ari Friedman
"""Literal word counts, visible denominators and two explicit weighting choices."""

from reportlab.pdfgen.canvas import Canvas

from .abstract_explanation import display_frequency
from .abstract_layout import AbstractSources, cell, footer, heading
from .figure_style import GREY, MUTED, RED, line


def corpus_page(c: Canvas, source: AbstractSources) -> None:
    heading(
        c,
        "Matching words per 10,000 words",
        "Which spellings were counted, where do they occur, and how does source weighting matter?",
    )
    stats = source.statistics
    variants = {query.query_id: query.variants for query in stats.query_specs}
    lookup = {q.query_id: q for q in source.corpus}
    states = lookup["states"]
    example = (
        (
            f"Example ({', '.join(variants['states'])}): {states.occurrences:,} matches "
            f"÷ {states.tokens:,} words \u00d7 10,000 = {display_frequency(states.pooled_rate)}"
        )
        if states.pooled_rate is not None
        else "No counted words: the frequency is N/A because its denominator is empty."
    )
    cell(
        c,
        example,
        20,
        433,
        500,
        18,
        size=10.3,
        font="BF-Serif-Bold",
    )
    cell(
        c,
        (
            f"{stats.primary_source_units} primary extracts; {stats.primary_work_groups} recorded "
            "source families; all their copies retained."
        ),
        20,
        413,
        500,
        16,
        size=9.2,
        color=MUTED,
    )
    cell(
        c,
        "All words together: combine all matches and all words, then calculate the frequency.",
        20,
        393,
        245,
        33,
        size=9.2,
    )
    cell(
        c,
        (
            "Each family equally: calculate a frequency for each family with words, then average, "
            "including zero-hit families."
        ),
        275,
        393,
        245,
        33,
        size=9.2,
        color=RED,
    )
    for x, width, text in (
        (20, 174, "LITERAL WORDS SEARCHED"),
        (198, 46, "MATCHES"),
        (244, 49, "ALL WORDS"),
        (302, 49, "EACH FAMILY"),
        (359, 62, "FAMILIES WITH MATCHES"),
        (430, 90, "LEADING FAMILY: SHARE OF MATCHES"),
    ):
        cell(c, text, x, 351, width, 34, size=8.6, color=RED)
    for index, q in enumerate(source.corpus):
        top = 310 - index * 26
        cell(c, ", ".join(variants[q.query_id]), 20, top, 174, 24, size=9)
        cell(c, f"{q.occurrences:,}", 198, top, 40, 20, size=9.2)
        cell(c, display_frequency(q.pooled_rate), 244, top, 49, 20, size=9.4)
        cell(
            c,
            display_frequency(q.equal_family_rate),
            302,
            top,
            49,
            20,
            size=9.4,
            color=RED,
        )
        cell(
            c,
            f"{q.matched_families}/{q.positive_token_families}"
            if q.positive_token_families
            else "N/A",
            359,
            top,
            62,
            20,
            size=9.2,
        )
        family = ", ".join(key.replace("-", " ").title() for key in q.top_family_ids)
        leading = (
            f"{family}: {q.top_family_occurrences}/{q.occurrences}"
            if q.top_family_share is not None
            else "N/A: no matches"
        )
        cell(c, leading, 430, top, 90, 24, size=8.8)
        line(c, 20, top - 25, 520, top - 25, GREY, 0.4)
    particulars, imagination = lookup["particulars"], lookup["imagination"]
    concentration = (
        (
            f"{particulars.top_family_occurrences} of {particulars.occurrences} matches "
            "in the leading family"
        )
        if particulars.top_family_share is not None
        else "no matching words in this group"
    )
    cell(
        c,
        (
            f"{', '.join(variants['particulars'])}: {concentration}; equal weighting gives "
            f"{display_frequency(particulars.equal_family_rate)}, versus "
            f"{display_frequency(particulars.pooled_rate)} with all words together."
        ),
        20,
        96,
        500,
        25,
        size=9.1,
    )
    cell(
        c,
        (
            f"Imagination: {display_frequency(imagination.pooled_rate)} becomes "
            f"{display_frequency(imagination.equal_family_rate)} when every source family has "
            "equal weight. Shorter texts can have higher word frequencies; see the caption."
        ),
        20,
        67,
        500,
        25,
        size=9.1,
    )
    footer(
        c,
        (
            "Literal, case-insensitive whole words. 'Words' means Unicode word tokens. "
            "A family groups "
            "extracts and copies with the same recorded work ID; labels do not determine meaning."
        ),
    )
