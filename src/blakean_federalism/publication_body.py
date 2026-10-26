# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound body figures and deterministic vector/raster output."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import (
    BLACK as INK,
)
from .figure_style import (
    GREY,
    MUTED,
)
from .figure_style import (
    RED as RUST,
)
from .figure_style import (
    WHITE as PAPER,
)
from .figure_style import (
    circle as _circle,
)
from .figure_style import (
    curve as _curve,
)
from .figure_style import (
    footer as _footer,
)
from .figure_style import (
    header as _header,
)
from .figure_style import (
    label as _label,
)
from .figure_style import (
    line as _line,
)
from .figure_style import (
    text as _text,
)
from .institutional_interventions import rule_is_triggered
from .models import ResearchError
from .workbench_models import Workbench


def draw_agreement_routes(c: Canvas) -> None:
    _header(
        c,
        "R",
        "Two routes to agreement",
        "Compare coordination with the conditions under which people can dissent",
    )
    _circle(c, 65, 172, 22, INK)
    _label(c, "Public", 65, 168, 10)
    _curve(c, (87, 177, 170, 184, 145, 238, 220, 238), INK, 4)
    _curve(c, (87, 167, 170, 158, 145, 110, 220, 110), RUST, 4)
    _text(c, "TRANSLATION + REVISION", 175, 271, 310, 12, INK)
    _text(c, "DEPENDENCY + GATEKEEPING", 175, 145, 335, 12, RUST)
    for dy in (-18, 0, 18):
        _curve(c, (220, 238, 280, 238 + dy, 327, 238 + dy, 380, 238 + dy), INK)
        _circle(c, 380, 238 + dy, 4, INK)
        _curve(c, (220, 110 + dy, 285, 110 + dy, 292, 110, 326, 110), RUST)
    _line(c, 326, 90, 326, 131, RUST, 5)
    _line(c, 326, 110, 380, 110, RUST, 2)
    _circle(c, 380, 110, 4, RUST)
    for y in (238, 110):
        _text(c, "Agreement", 403, y + 6, 110, 11)
    _text(c, "Challenge stays open", 260, 207, 250, 10, INK)
    _text(c, "Challenge becomes costly", 260, 77, 250, 10, RUST)
    _footer(
        c, "Conceptual contrast prompted by Rahman's profile and Pettit's account of domination."
    )


def draw_relations(c: Canvas) -> None:
    _header(
        c,
        "A I C",
        "Affiliation is not authorization",
        "Solid lines: affiliation A / dashed lines: interpretation I / separate relation C",
    )
    persons = ((80, 222), (196, 222), (312, 222))
    nations = ((106, 150), (272, 150))
    states = ((80, 78), (196, 78), (312, 78))
    for p, n in ((0, 0), (1, 0), (1, 1), (2, 1)):
        x, y = persons[p]
        end, ey = nations[n]
        _curve(c, (x, y - 12, x, y - 35, end, ey + 35, end, ey + 12), INK, 1.5)
    for n, s in ((0, 0), (0, 1), (1, 1), (1, 2)):
        x, y = nations[n]
        end, ey = states[s]
        c.setDash(3, 2)
        _curve(c, (x, y - 12, x, y - 35, end, ey + 35, end, ey + 12), INK)
        c.setDash()
    for points, prefix, color in ((persons, "P", INK), (nations, "N", INK), (states, "S", INK)):
        for index, (x, y) in enumerate(points, 1):
            _circle(c, x, y, 12, color)
            _label(c, prefix + str(index), x, y - 3, 8, color)
    _text(c, "Persons", 22, 258, 130, 10)
    _text(c, "A / affiliation", 156, 258, 180, 10, INK)
    _line(c, 355, 61, 355, 272, GREY)
    _label(c, "C / claimed competence", 444, 252, 9, RUST)
    _circle(c, 444, 208, 20, RUST)
    _label(c, "J1", 444, 204, 12, RUST)
    _line(c, 444, 187, 444, 137, RUST, 2)
    _circle(c, 444, 116, 20, RUST)
    _label(c, "d1", 444, 112, 12, RUST)
    _text(c, "Institution / decision", 376, 78, 150, 10, RUST)
    _footer(c, "Illustrative relations. C can change while A and I remain fixed (Proposition 1).")


def draw_census(c: Canvas, report: Workbench) -> None:
    census = {(x.plane.value, x.role.value): x.source_units for x in report.coverage}
    _header(
        c,
        "n",
        "Count the source units first",
        "Copies, retained pages and XML units / roles from the pinned index",
    )
    colors = {"primary": RUST, "editorial": INK, "unverified": "#bbbbbb"}
    maximum = max(
        sum(census.get((p, role), 0) for role in colors) for p in ("reading", "erdman", "xml")
    )
    for index, plane in enumerate(("reading", "erdman", "xml")):
        y = 243 - index * 65
        _text(c, plane.upper(), 20, y + 3, 85, 10)
        x = 116.0
        total = 0
        for role, color in colors.items():
            count = census.get((plane, role), 0)
            width = count / maximum * 338 if maximum else 0
            c.setFillColor(HexColor(color))
            c.rect(x, y - 20, width, 27, stroke=0, fill=1)
            if width > 32:
                _label(
                    c, str(count), x + width / 2, y - 11, 10, INK if role == "unverified" else PAPER
                )
            x += width
            total += count
        _text(c, str(total), 468, y, 56, 12)
    _text(c, "XML includes 4 editorial units", 116, 140, 310, 9, MUTED)
    for index, (role, color) in enumerate(colors.items()):
        x = 116 + index * 131
        _circle(c, x + 4, 72, 4, color, color)
        _text(c, role, x + 15, 79, 112, 9)
    _footer(
        c,
        f"{report.source_units:,} units across planes; copies and pages are not unique works.",
    )


def draw_rule_matrix(c: Canvas, report: Workbench) -> None:
    if not report.cases:
        raise ResearchError("publication_cases", "A case matrix needs recorded checks")
    codes = [x.code for x in report.cases[0].assessment.checks]
    if any([x.code for x in case.assessment.checks] != codes for case in report.cases):
        raise ResearchError("publication_checks", "Case check orders differ")
    _text(c, "FIFTEEN RULES / TEN ALTERNATIVES", 20, 431, 500, 17)
    _text(c, "Each case pairs a bounded record (+) with a capture record (-).", 20, 406, 500, 10)
    for index, case in enumerate(report.cases):
        label = case.record.decision_id.replace("-bounded", "+").replace("-capture", "-")
        x = 231 + 29 * index
        if index % 2 == 0:
            c.setFillColor(HexColor("#f2f2f2"))
            c.rect(x - 12, 60, 53, 327, fill=1, stroke=0)
        _label(c, label, x, 372, 9)
    failures = 0
    for row, code in enumerate(codes):
        y = 346 - row * 19
        _text(c, code.replace("_", " "), 20, y + 5, 192, 9)
        _line(c, 20, y - 7, 520, y - 7, "#dddddd", 0.4)
        for column, case in enumerate(report.cases):
            x = 231 + 29 * column
            passed = case.assessment.checks[row].passed
            if not rule_is_triggered(case.record, code):
                _line(c, x - 4, y, x + 4, y, "#888888", 1)
            elif passed:
                _circle(c, x, y, 4.5, INK, PAPER, 1)
            else:
                failures += 1
                _circle(c, x, y, 6.4, RUST, RUST)
                _line(c, x - 2, y - 2, x + 2, y + 2, PAPER, 1)
                _line(c, x - 2, y + 2, x + 2, y - 2, PAPER, 1)
    _circle(c, 26, 51, 4.5, INK)
    _text(c, "Active / satisfied", 37, 57, 133, 9)
    _circle(c, 183, 51, 6, RUST, RUST)
    _label(c, "x", 183, 48, 8, PAPER)
    _text(c, "Active / violated", 196, 57, 129, 9)
    _text(c, f"{failures} recorded violations", 346, 57, 173, 9)
    _line(c, 20, 36, 520, 36)
    _text(
        c,
        (
            "Grey dash: condition not triggered. Every mark retains "
            "the same fixed rule and case order."
        ),
        20,
        28,
        500,
        9,
        MUTED,
    )


def draw_watershed(c: Canvas) -> None:
    _header(
        c,
        "E",
        "Who decides about the water?",
        "Three institutional arrangements for the same hypothetical scarcity",
    )
    headings = (
        (181, "E1 / ASSOCIATIONS", INK),
        (302, "E2 / TERRITORY", INK),
        (423, "E3 / WATERSHED", INK),
    )
    rows = (
        ("Voice", "Recognized bodies", "Resident franchise", "Residents + workers"),
        (
            "Treaty relation",
            "Folded into membership",
            "Subject to general rule",
            "Separate negotiation",
        ),
        ("Decision scope", "Association mandate", "Territorial mandate", "Limited water task"),
        (
            "Hard question",
            "Who is left off rolls?",
            "Whose title is assumed?",
            "Who reviews the forum?",
        ),
    )
    for x, title, color in headings:
        _text(c, title, x, 264, 114, 9, color)
        _line(c, x, 243, x + 111, 243, color, 2)
    for index, row in enumerate(rows):
        top = 225 - index * 40
        _text(c, row[0], 20, top, 149, 10, MUTED)
        for column, value in enumerate(row[1:]):
            _text(c, value, 181 + 121 * column, top, 111, 9)
        _line(c, 20, top - 30, 520, top - 30, GREY, 0.5)
    _footer(
        c,
        "Compare water access, costs, effective challenge and revision at the same scarcity.",
    )
