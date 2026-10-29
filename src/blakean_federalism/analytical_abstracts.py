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

_OVERLAP_NODE = 2


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
        "Belonging alone does not authorize rule",
        (
            "A person may share several national histories; an institution still needs a warrant "
            "for each decision."
        ),
    )
    plate(c, source.artwork["J1"], (20, 432, 110, 155))
    cell(c, "Jerusalem, copy I, plate 1. Lamp, bearer and threshold.", 20, 269, 110, 38, size=9)
    for x, name in ((177, "Persons P"), (309, "Nations N"), (450, "State readings S")):
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
        circle(c, x, y, 8, RED if index == _OVERLAP_NODE else BLACK, width=0.9)
        label(c, f"p{index}", x, y - 3, 8.5)
    for index, (x, y) in enumerate(nations, 1):
        c.setFillColor(HexColor(WHITE))
        c.setStrokeColor(HexColor(BLACK))
        c.setLineWidth(0.65)
        c.rect(x - 10, y - 8, 20, 16, fill=1, stroke=1)
        label(c, f"n{index}", x, y - 3, 8.5)
    for index, (x, y) in enumerate(states, 1):
        circle(c, x, y, 8, RED if index == _OVERLAP_NODE else BLACK, width=0.9)
        label(c, f"s{index}", x, y - 3, 8.5)
    cell(c, "A: participates in", 166, 313, 165, 13, size=9, color=RED)
    cell(c, "I: interprets through", 349, 313, 171, 13, size=9, color=RED)
    cell(c, "p2 participates in n1 and n2", 166, 300, 165, 12, size=8.5)
    cell(c, "Both n1 and n2 draw on s2", 349, 300, 171, 12, size=8.5)
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
            (
                "Claimed competence: sharing an identity does not authorize this institution to "
                "impose this decision."
            ),
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
        ("Accessible reasons; supported changes of affiliation; no claim to a whole person."),
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
            "J means institutions; D means proposed decisions. Art: LOC, Rosenwald "
            "Collection, item 48038103; posthumous impression, c. 1832?; whole image retained."
        ),
    )


def readings_page(c: Canvas, source: AbstractSources) -> None:
    heading(
        c,
        "A shared order must answer six questions",
        (
            "Read a scene, its unresolved tension, and the question it raises for collective "
            "authority."
        ),
    )
    columns = (
        (20, 151, "BLAKE'S SCENE"),
        (184, 178, "WHAT MAKES IT CONTESTED"),
        (375, 145, "THIS ARTICLE ASKS"),
    )
    for x, width, title in columns:
        cell(c, title, x, 432, width, 16, size=9, color=RED)
    rows = (
        (
            source.verse("Q31"),
            "Jerusalem 11:5 / E154 (Q31)",
            (
                "Los also compels labor. Clark and White offer different readings of his "
                "system-making "
                "declaration."
            ),
            "Can people within a system challenge its maker?",
        ),
        (
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            (
                "Fallon's national openness confronts Mellor's and Kaplan's objections "
                "concerning unequal agency."
            ),
            "Who can speak, create, revise and refuse?",
        ),
        (
            source.verse("Q37"),
            "Marriage 24 / E44 (Q37)",
            (
                "One rule can impose unequal burdens. Heppner and Frosch distinguish the "
                "person from the claim made for them."
            ),
            "Who bears a rule's costs, and whose needs does it meet?",
        ),
        (
            source.verse("Q40"),
            "Marriage 20 / E42 (Q40)",
            (
                "The narrator also compels the Angel's vision. Simpson and Fraser give refusal "
                "and organized opposition political force."
            ),
            "Can dissent change a decision while dissenters retain their rights?",
        ),
        (
            source.verse("Q38", 2, 3),
            "Jerusalem 45:35 / E194 (Q38)",
            (
                "Los restrains vengeance against the already injured. Shachar asks where the "
                "burden of obtaining protection falls."
            ),
            "Who receives protection and material support during review?",
        ),
        (
            source.verse("Q39", 2, 3),
            "America 6:12 / E53 (Q39)",
            (
                "Release can leave dependence intact. Moyer follows labor, material provision "
                "and control of production."
            ),
            "What makes leaving possible without losing home, livelihood or standing?",
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
