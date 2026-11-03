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
    rows = (
        (
            source.verse("Q31"),
            "Jerusalem 11:5 / E154 (Q31)",
            (
                "Los also compels labor: Clark (pp. 69-70) and White (pp. 116-117) "
                "read his system-making declaration differently."
            ),
            "Can people within a system challenge its maker?",
        ),
        (
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            (
                "Fallon (ms. 10-12) reads national openness; Mellor (148-153) and "
                "Kaplan (82 n. 27) question unequal agency."
            ),
            "Who can speak, create, revise and refuse?",
        ),
        (
            source.verse("Q37"),
            "Marriage 24 / E44 (Q37)",
            (
                "One rule can impose unequal burdens: Heppner (55-56, 59) and "
                "Frosch (44) separate a person from claims made for them."
            ),
            "Who bears a rule's costs, and whose needs does it meet?",
        ),
        (
            source.verse("Q40"),
            "Marriage 20 / E42 (Q40)",
            (
                "The narrator compels the Angel's vision. Simpson (67-78) and Fraser "
                "(122-124) give refusal and organized opposition political force."
            ),
            "Can dissent change a decision while dissenters retain their rights?",
        ),
        (
            source.verse("Q38", 2, 3),
            "Jerusalem 45:35 / E194 (Q38)",
            (
                "Los restrains vengeance against the injured; Shachar (75-77) asks "
                "who bears the burden of obtaining protection."
            ),
            "Who receives protection and material support during review?",
        ),
        (
            source.verse("Q39", 2, 3),
            "America 6:12 / E53 (Q39)",
            (
                "Release can leave dependence intact. Moyer (paras. 3-10, 14-16) "
                "follows labor, provision and control of production."
            ),
            "What makes leaving possible without losing home, livelihood or standing?",
        ),
    )
    for index, (verse, locator, reading, question) in enumerate(rows):
        top = 432 - (index // 2) * 124
        left = 20 + (index % 2) * 255
        c.setFillColor(HexColor(WHITE))
        c.setStrokeColor(HexColor(GREY))
        c.setLineWidth(0.5)
        c.rect(left, top - 118, 245, 118, fill=1, stroke=1)
        cell(c, verse, left + 9, top - 7, 227, 28, size=9, font="BF-Serif-Italic")
        cell(c, locator, left + 9, top - 37, 227, 12, size=8, color=MUTED)
        cell(c, reading, left + 9, top - 52, 227, 37, size=8.4)
        cell(c, question, left + 9, top - 91, 227, 24, size=9, font="BF-Serif-Bold", color=RED)
    footer(
        c,
        (
            "Locators identify the article's cited versions; Q38-Q39 show selected lines. The "
            "right column states this article's institutional constructions. Primary text: ASU "
            "electronic Erdman edition."
        ),
    )
