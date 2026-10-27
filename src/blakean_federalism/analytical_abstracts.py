# Copyright (c) 2026 Daniel Ari Friedman
"""Argument and close-reading pages for the current graphical abstracts."""

from collections.abc import Callable, Mapping
from functools import partial
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .abstract_corpus_figure import corpus_page
from .abstract_layout import AbstractSources, analytical_sources, cell, footer, heading
from .abstract_results import repair_page
from .figure_style import BLACK, GREY, MUTED, RED, WHITE, circle, label, line
from .illuminated_style import plate
from .workbench_models import Workbench


def analytical_drawings(
    report: Workbench, artwork: Mapping[str, Path]
) -> dict[str, Callable[[Canvas], None]]:
    source = analytical_sources(report, artwork)
    return {
        "abstract-1": partial(relations_page, source=source),
        "abstract-2": partial(readings_page, source=source),
        "abstract-3": partial(repair_page, source=source),
        "abstract-4": partial(corpus_page, source=source),
    }


def relations_page(c: Canvas, source: AbstractSources) -> None:
    heading(
        c,
        "Persons, national formations and authority",
        (
            "Affiliation, poetic interpretation and the warrant for a public decision are "
            "different relations."
        ),
    )
    plate(c, source.artwork["J1"], (20, 432, 110, 155))
    cell(c, "Jerusalem, copy I, plate 1. Lamp, bearer and threshold.", 20, 269, 110, 38, size=9)
    for x, name in ((177, "Persons P"), (309, "Nations N"), (450, "Poetic states S")):
        label(c, name, x, 427, 9.5)
    persons = ((177, 404), (177, 368), (177, 332))
    nations = ((309, 386), (309, 350))
    states = ((450, 404), (450, 368), (450, 332))
    for first, second in ((0, 0), (1, 0), (1, 1), (2, 1)):
        line(
            c,
            persons[first][0],
            persons[first][1],
            nations[second][0],
            nations[second][1],
            BLACK,
            0.65,
        )
    c.saveState()
    c.setDash(3, 2)
    for first, second in ((0, 0), (0, 1), (1, 1), (1, 2)):
        line(
            c,
            nations[first][0],
            nations[first][1],
            states[second][0],
            states[second][1],
            MUTED,
            0.65,
        )
    c.restoreState()
    for index, (x, y) in enumerate(persons, 1):
        circle(c, x, y, 8, BLACK, width=0.65)
        label(c, f"p{index}", x, y - 3, 8.5)
    for index, (x, y) in enumerate(nations, 1):
        c.setFillColor(HexColor(WHITE))
        c.setStrokeColor(HexColor(BLACK))
        c.setLineWidth(0.65)
        c.rect(x - 10, y - 8, 20, 16, fill=1, stroke=1)
        label(c, f"n{index}", x, y - 3, 8.5)
    for index, (x, y) in enumerate(states, 1):
        circle(c, x, y, 8, BLACK, width=0.65)
        label(c, f"s{index}", x, y - 3, 8.5)
    cell(c, "Solid: A, affiliation", 166, 313, 165, 13, size=9, color=RED)
    cell(c, "Dashed: I, interpretation", 349, 313, 171, 13, size=9, color=RED)
    cell(c, source.verse("Q03", 1, 2), 150, 288, 370, 32, size=10.5, font="BF-Serif-Italic")
    cell(
        c,
        "Milton 32:23, E132; Q03. Nodes illustrate possible relations, not measured populations.",
        150,
        251,
        370,
        24,
        size=8.8,
        color=MUTED,
    )
    line(c, 20, 223, 520, 223, BLACK, 0.6)
    rows = (
        (
            207,
            "A ⊆ P \u00d7 N",
            ("Participation: one person may belong to several national formations."),
        ),
        (
            174,
            "I ⊆ N \u00d7 S",
            "Interpretation: a national formation can articulate several poetic states.",
        ),
        (
            141,
            "C ⊆ J \u00d7 D",
            "Claimed competence: an institution needs a warrant for a specified decision.",
        ),
    )
    for top, symbol, detail in rows:
        cell(c, symbol, 20, top, 128, 25, size=11, font="BF-Serif")
        cell(c, detail, 158, top, 362, 27, size=9.5)
        line(c, 20, top - 29, 520, top - 29, GREY, 0.4)
    cell(c, source.verse("Q13"), 20, 99, 500, 18, size=11, font="BF-Serif-Italic")
    cell(
        c,
        (
            "Marriage 7, E36; Q13. Historical production matters within an enduring imaginative "
            "horizon."
        ),
        20,
        78,
        500,
        15,
        size=9,
        color=MUTED,
    )
    cell(
        c,
        (
            "Translation: accessible reasons. Passage: supported change. Non-exhaustion: no total "
            "identity claim."
        ),
        20,
        57,
        500,
        15,
        size=9.1,
        color=RED,
    )
    footer(
        c,
        (
            "Institutional sorts J and D remain separate from P, N and S. Art: LOC, Rosenwald "
            "Collection, item 48038103; posthumous impression, c. 1832?; whole image retained."
        ),
    )


def readings_page(c: Canvas, source: AbstractSources) -> None:
    heading(
        c,
        "Passages, rival readings and institutional tests",
        (
            "Selected lines connect poetic scenes to specific questions of classification, power "
            "and provision."
        ),
    )
    columns = (
        (20, 151, "BLAKE PASSAGE"),
        (184, 178, "CONTEXT AND SCHOLARSHIP"),
        (375, 145, "INSTITUTIONAL TEST"),
    )
    for x, width, title in columns:
        cell(c, title, x, 432, width, 16, size=9, color=RED)
    rows = (
        (
            source.verse("Q03", 0, 1),
            "Milton 32:22 / E132 (Q03)",
            (
                "Damrosch, pp. 15-21; Lee, pp. 1-10. Particularity and persistent identity "
                "complicate a fixed repertoire of states."
            ),
            "Can affiliation change while personhood and standing continue?",
        ),
        (
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            (
                "Fallon ms. 10-12; Mellor, pp. 148-153; Kaplan, p. 82,n. 27. National opening and "
                "reciprocal imagery can coexist with unequal agency."
            ),
            "Who speaks, interprets, refuses a role and authorizes a decision?",
        ),
        (
            source.verse("Q37"),
            "Marriage 24 / E44 (Q37)",
            (
                "Heppner, pp. 55-56,59; Frosch, p. 44. Relevant differences matter; a peaceful "
                "intention cannot excuse an oppressive rule."
            ),
            "Compare actual burdens; require reasons for differentiated treatment.",
        ),
        (
            source.verse("Q40"),
            "Marriage 20 / E42 (Q40)",
            (
                "The narrator compels the Angel's vision. Simpson, pp. 67-78; Fraser, pp. "
                "122-124: refusal and organized opposition retain force."
            ),
            "Can a challenge revise the framing without requiring conversion or disclosure?",
        ),
        (
            source.verse("Q38", 1, 2),
            "Jerusalem 45:34 / E194 (Q38)",
            (
                "Los cannot locate the authors of visible injury. Shachar, pp. 75-77 relocates "
                "the burden of initiating protection."
            ),
            "Who bears a remedy's force, and who keeps essentials available during review?",
        ),
        (
            source.verse("Q39", 2, 3),
            "America 6:12 / E53 (Q39)",
            (
                "The released family still looks back. Moyer, paras. 3-10,14-16 follows labor, "
                "dependence and control of production."
            ),
            "Name the means, provider, timetable and protection against retaliation.",
        ),
    )
    for index, (verse, locator, reading, question) in enumerate(rows):
        top = 406 - index * 59
        cell(c, verse, 20, top, 151, 40, size=9.4, font="BF-Serif-Italic")
        cell(c, locator, 20, top - 42, 151, 14, size=8.6, color=MUTED)
        cell(c, reading, 184, top, 178, 55, size=9)
        cell(c, question, 375, top, 145, 55, size=9.3)
        if index < len(rows) - 1:
            line(c, 20, top - 56, 520, top - 56, GREY, 0.4)
    footer(
        c,
        (
            "Locators identify the article's cited versions; Q38-Q39 show selected lines. The "
            "right column states this article's institutional constructions. Primary text: ASU "
            "electronic Erdman edition."
        ),
    )
