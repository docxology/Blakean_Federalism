# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound composition and scholarship pages for illuminated abstracts."""

from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, MUTED, RED, circle, curve, label, line
from .illuminated_sources import IlluminatedSources
from .illuminated_style import footer, heading, plate, prose


def draw_composition(c: Canvas, source: IlluminatedSources) -> None:
    heading(
        c,
        "01",
        "Composition without capture",
        "Persons endure; affiliations change; authority answers for its acts.",
    )
    plate(c, source.artwork["J1"], (20, 434, 184, 258))
    # A pointed red arch echoes the depicted threshold without painting over the plate.
    line(c, 14, 176, 14, 435, RED, 0.6)
    curve(c, (14, 435, 52, 436, 86, 441, 112, 441), RED, 0.6)
    curve(c, (112, 441, 138, 441, 172, 436, 210, 435), RED, 0.6)
    line(c, 210, 435, 210, 176, RED, 0.6)
    prose(c, "Jerusalem I, plate 1. Lamp, figure and threshold.", (20, 168, 184, 27), size=9)
    prose(c, source.verse("Q13"), (20, 133, 184, 49), size=13, font="BF-Serif-Italic")
    prose(c, "Marriage 7 / E36 (Q13)", (20, 85, 184, 12), size=9, color=MUTED)
    rows = (
        (
            434,
            "PERSONS / P",
            source.verse("Q03", 1, 2),
            "Milton 32:23 / E132 (Q03)",
            "A person exceeds every assigned role and collective label.",
        ),
        (
            326,
            "POETIC STATES / S",
            source.verse("Q05", 0, 2),
            "Jerusalem 52 / E200 (Q05)",
            "Enduring possibilities become intelligible through particular lives.",
        ),
        (
            218,
            "NATIONAL FORMATIONS / N",
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            "Plural histories and exchanges compose a common world.",
        ),
    )
    for top, title, verse, locator, interpretation in rows:
        prose(c, title, (229, top, 291, 14), size=10, color=RED)
        prose(c, verse, (229, top - 19, 291, 38), size=14, font="BF-Serif-Italic")
        prose(c, locator, (229, top - 59, 291, 12), size=9, color=MUTED)
        prose(c, interpretation, (229, top - 75, 291, 26), size=9.5)
    line(c, 229, 105, 520, 105, RED, 0.7)
    _relations(c)
    prose(
        c,
        "C: J to D / claimed competence; require warrant, reach and review.",
        (229, 66, 291, 26),
        size=9,
        color=RED,
    )
    footer(
        c,
        "".join(
            (
                f"{source.report.source_units:,} imported units; ",
                f"{source.statistics.primary_source_units:,} primary extracts. Art: Library ",
                "of Congress, Jerusalem I, c.1832?, item 48038103; uncropped.",
            ),
        ),
    )


def _relations(c: Canvas) -> None:
    for x, text_value in ((245, "P"), (367, "N"), (500, "S")):
        label(c, text_value, x, 91, 9)
    for x, y, end_x, end_y, dashed in (
        (237, 82, 359, 82, False),
        (253, 72, 359, 82, False),
        (253, 72, 375, 72, False),
        (359, 82, 492, 82, True),
        (375, 72, 492, 82, True),
        (375, 72, 508, 72, True),
    ):
        c.saveState()
        if dashed:
            c.setDash(2, 2)
        line(c, x, y, end_x, end_y, BLACK, 0.6)
        c.restoreState()
    for x, y in ((237, 82), (253, 72), (359, 82), (375, 72), (492, 82), (508, 72)):
        circle(c, x, y, 3, BLACK)
    label(c, "A / affiliation", 305, 91, 9, RED)
    label(c, "I / interpretation", 436, 91, 9, RED)


def draw_scholarship(c: Canvas, source: IlluminatedSources) -> None:
    heading(
        c,
        "02",
        "Read the tension; specify the claim",
        "Poetic assertions, scholarly disagreements and institutional questions stay connected.",
    )
    plate(c, source.artwork["J52"], (20, 433, 133, 187))
    prose(c, source.verse("Q05", 2, 4), (20, 237, 133, 61), size=13, font="BF-Serif-Italic")
    prose(c, "Jerusalem 52 / E200 (Q05)", (20, 173, 133, 24), size=9, color=MUTED)
    prose(
        c,
        """State is not person. Interpretation is not jurisdiction. A represented
identity does not authorize its interpreter to rule.""",
        (20, 132, 133, 80),
        size=10,
        font="BF-Serif",
    )
    panels = (
        (
            433,
            source.verse("Q03", 0, 1),
            "Milton 32:22 / E132 (Q03)",
            "Damrosch, pp.15-21: universality in particular forms.",
            "Lee, pp.1-10: identity resists compulsory remaking.",
            "What changes while a person's standing persists?",
        ),
        (
            304,
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            "Fallon, ms.pp.10-12: national opening and incorporation.",
            "Mellor, pp.148-153: creative reciprocity retains hierarchy.",
            "Who interprets, refuses an assigned role and governs?",
        ),
        (
            175,
            source.verse("Q31"),
            "Jerusalem 11:5 / E154 (Q31)",
            "Simpson, pp.67-78: refusal limits compulsory disclosure.",
            "Shachar, pp.75-77: review before enforceability.",
            "Who can contest the protective forum itself?",
        ),
    )
    for index, (top, verse, locator, first, second, question) in enumerate(panels):
        prose(c, verse, (173, top, 347, 36), size=13, font="BF-Serif-Italic")
        prose(c, locator, (173, top - 37, 347, 12), size=9, color=MUTED)
        prose(c, first, (173, top - 55, 166, 34), size=9)
        prose(c, second, (354, top - 55, 166, 34), size=9)
        prose(c, question, (173, top - 95, 347, 25), size=10, color=RED)
        if index < len(panels) - 1:
            line(c, 173, top - 124, 520, top - 124, BLACK, 0.4)
    footer(
        c,
        """Arguments guide the questions below each pair. Art: Jerusalem I, plate 52,
Library of Congress, c.1832?, item 48038103; uncropped.""",
    )
