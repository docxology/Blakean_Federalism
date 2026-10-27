# Copyright (c) 2026 Daniel Ari Friedman
"""Typed countermodels, source strata and accountable decision paths as vector diagrams."""

from math import ceil, hypot

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, WHITE, circle, curve, label, line, text
from .institutional_interventions import rule_is_triggered
from .models import ResearchError
from .workbench_models import Workbench


def _heading(c: Canvas, title: str, subtitle: str) -> None:
    text(c, title, 20, 428, 500, 19)
    text(c, subtitle, 20, 400, 500, 9.5, MUTED)
    line(c, 20, 375, 520, 375, RED, 1.5)


def record_arrow(c: Canvas, x: float, y: float, xx: float, yy: float, color: str = BLACK) -> None:
    line(c, x, y, xx, yy, color, 1.2)
    dx, dy = xx - x, yy - y
    length = hypot(dx, dy)
    if length:
        ux, uy = dx / length, dy / length
        line(c, xx, yy, xx - 6 * ux + 3 * uy, yy - 6 * uy - 3 * ux, color, 1.2)
        line(c, xx, yy, xx - 6 * ux - 3 * uy, yy - 6 * uy + 3 * ux, color, 1.2)


def _foot(c: Canvas, value: str) -> None:
    line(c, 20, 38, 520, 38)
    text(c, value, 20, 29, 500, 8.5, MUTED)


def draw_relations(c: Canvas) -> None:
    _heading(
        c,
        "Same social relations; C absent or present",
        "Countermodel to automatic authorization / identical affiliations A and interpretations I",
    )
    for left, title, claimed in (
        (20, "WORLD 0 / C is empty", False),
        (280, "WORLD 1 / C contains (j,d)", True),
    ):
        text(c, title, left, 361, 240, 10, RED)
        persons = [(left + 42, 307), (left + 118, 307), (left + 194, 307)]
        nations = [(left + 69, 235), (left + 168, 235)]
        states = [(left + 42, 163), (left + 118, 163), (left + 194, 163)]
        for pi, ni in ((0, 0), (1, 0), (1, 1), (2, 1)):
            x, y = persons[pi]
            xx, yy = nations[ni]
            curve(c, (x, y - 13, x, y - 37, xx, yy + 37, xx, yy + 13), BLACK, 1)
        c.setDash(3, 3)
        for ni, si in ((0, 0), (0, 1), (1, 1), (1, 2)):
            x, y = nations[ni]
            xx, yy = states[si]
            curve(c, (x, y - 13, x, y - 37, xx, yy + 37, xx, yy + 13), BLACK, 1)
        c.setDash()
        for nodes, prefix in ((persons, "p"), (nations, "n"), (states, "s")):
            for i, (x, y) in enumerate(nodes, 1):
                circle(c, x, y, 13, BLACK)
                label(c, prefix + str(i), x, y - 3, 9)
        circle(c, left + 65, 91, 14, RED)
        circle(c, left + 173, 91, 14, RED)
        label(c, "j", left + 65, 88, 10, RED)
        label(c, "d", left + 173, 88, 10, RED)
        if claimed:
            record_arrow(c, left + 80, 91, left + 158, 91, RED)
            label(c, "claim C ≠ warrant", left + 119, 111, 8, RED)
        else:
            label(c, "no claim", left + 119, 111, 8, MUTED)
        label(c, "Persons P", left + 118, 335, 9)
        label(c, "Nations N", left + 118, 261, 9)
        label(c, "State readings S", left + 118, 137, 9)
        text(c, "Institution j / proposed decision d", left + 22, 61, 218, 8, RED)
    line(c, 268, 58, 268, 360, GREY, 0.6)
    _foot(c, "Solid: A. Dashed: I. Both worlds satisfy the typing; only C changes (Proposition 1).")


def draw_census(c: Canvas, report: Workbench) -> None:
    census = {(x.plane.value, x.role.value): x.source_units for x in report.coverage}
    planes = ("reading", "erdman", "xml")
    roles = ("primary", "editorial", "unverified")
    total = sum(census.get((p, role), 0) for p in planes for role in roles)
    if total != report.source_units:
        raise ResearchError("publication_census", "Source strata do not sum to the imported units")
    _heading(
        c,
        "One index, three source layers",
        "".join(
            (
                f"{report.source_units:,} indexed units / common zero-based scale / ",
                "source roles remain separate",
            )
        ),
    )
    maximum = max((sum(census.get((p, role), 0) for role in roles) for p in planes), default=0)
    maximum = ceil(maximum / 100) * 100 if maximum > 100 else maximum
    colors = (RED, BLACK, "#c8c8c8")
    for i, plane in enumerate(planes):
        y = 325 - i * 76
        text(c, plane.upper(), 20, y + 11, 88, 11)
        x = 119.0
        counts = [census.get((plane, role), 0) for role in roles]
        for count, color in zip(counts, colors, strict=True):
            width = 330 * count / maximum if maximum else 0
            c.setFillColor(HexColor(color))
            c.rect(x, y - 14, width, 27, fill=1, stroke=0)
            if width > 33:
                label(
                    c, str(count), x + width / 2, y - 5, 10, BLACK if color == colors[2] else WHITE
                )
            x += width
        text(c, f"{sum(counts):,}", 468, y + 10, 52, 15)
        text(
            c,
            " / ".join(f"{count} {role}" for count, role in zip(counts, roles, strict=True)),
            119,
            y - 24,
            390,
            8.5,
            MUTED,
        )
    for value in (maximum * i / 4 for i in range(5)):
        if maximum and value <= maximum:
            x = 119 + 330 * value / maximum
            line(c, x, 132, x, 127, BLACK, 0.7)
            label(c, f"{value:g}", x, 114, 8, MUTED)
    line(c, 119, 132, 449, 132, BLACK, 0.7)
    for i, (role, color) in enumerate(zip(roles, colors, strict=True)):
        x = 20 + i * 170
        n = sum(census.get((p, role), 0) for p in planes)
        c.setFillColor(HexColor(color))
        c.rect(x, 85, 9, 9, fill=1, stroke=0)
        text(c, role.upper(), x + 15, 99, 148, 8.5)
        text(c, f"{n:,}", x + 15, 83, 148, 18, RED if role == "primary" else BLACK)
        text(c, f"{n / total:.1%} of indexed units", x + 15, 58, 148, 9, MUTED)
    _foot(
        c,
        (
            f"{total:,} retained units. Small editorial XML segment: "
            f"{census.get(('xml', 'editorial'), 0)} units. Copies are not "
            f"unique works."
        ),
    )


def draw_rule_matrix(c: Canvas, report: Workbench) -> None:
    if not report.cases:
        raise ResearchError("publication_cases", "A case matrix needs recorded checks")
    codes = [x.code for x in report.cases[0].assessment.checks]
    if any([x.code for x in case.assessment.checks] != codes for case in report.cases):
        raise ResearchError("publication_checks", "Case check orders differ")
    _heading(
        c,
        "Where the ten records fail",
        "".join(
            (
                f"{len(codes)} predicates × {len(report.cases)} records / ",  # noqa: RUF001 -- Cartesian count.
                f"{sum(c.assessment.admissible_under_proposed_rules for c in report.cases)} ",
                "admissible under stipulated rules",
            )
        ),
    )
    counts = {"satisfied": 0, "violated": 0, "absent": 0}
    for column, case in enumerate(report.cases):
        x = 231 + 27 * column
        if column % 2 == 0:
            c.setFillColor(HexColor("#f3f3f3"))
            c.rect(x - 12, 61, 52, 293, fill=1, stroke=0)
        name = case.record.decision_id.replace("-bounded", "+").replace("-capture", "-")
        label(c, name, x, 356, 9)
    text(c, "RULE", 20, 365, 190, 8, MUTED)
    label(c, "V / active", 507, 356, 7, RED)
    for row, code in enumerate(codes):
        y = 334 - row * 18
        text(c, code.replace("_", " "), 20, y + 6, 192, 8.6)
        line(c, 20, y - 7, 520, y - 7, GREY, 0.45)
        failures = 0
        active = 0
        for column, case in enumerate(report.cases):
            x = 231 + 27 * column
            if not rule_is_triggered(case.record, code):
                line(c, x - 4, y, x + 4, y, "#888888", 1)
                counts["absent"] += 1
            elif case.assessment.checks[row].passed:
                active += 1
                circle(c, x, y, 3.8, BLACK)
                counts["satisfied"] += 1
            else:
                active += 1
                failures += 1
                counts["violated"] += 1
                circle(c, x, y, 5.5, RED, RED)
                line(c, x - 2, y - 2, x + 2, y + 2, WHITE, 1)
                line(c, x - 2, y + 2, x + 2, y - 2, WHITE, 1)
        label(
            c,
            f"{failures}/{active}" if active else "N/A",
            507,
            y - 3,
            8,
            RED if failures else MUTED,
        )
    for column, case in enumerate(report.cases):
        active = sum(rule_is_triggered(case.record, code) for code in codes)
        violated = sum(
            rule_is_triggered(case.record, check.code) and not check.passed
            for check in case.assessment.checks
        )
        label(
            c,
            f"{active - violated}/{violated}/{len(codes) - active}",
            231 + 27 * column,
            66,
            7,
            MUTED,
        )
    text(c, "Satisfied / violated / absent", 20, 73, 190, 8, MUTED)
    circle(c, 24, 51, 3.8, BLACK)
    text(c, f"{counts['satisfied']} active / satisfied", 34, 57, 157, 8.5)
    circle(c, 204, 51, 5, RED, RED)
    line(c, 202, 49, 206, 53, WHITE, 1)
    line(c, 202, 53, 206, 49, WHITE, 1)
    text(c, f"{counts['violated']} active / violated", 214, 57, 145, 8.5, RED)
    line(c, 387, 51, 395, 51, MUTED)
    text(c, f"{counts['absent']} condition absent", 402, 57, 118, 8.5)
    _foot(
        c,
        (
            "150 checks. + bounded / - capture; right margin: violated / active. "
            "Absent conditions stay distinct."
        ),
    )


def draw_watershed(c: Canvas) -> None:
    _heading(
        c,
        "One scarcity, three ways to authorize action",
        "Hypothetical water dispute / the affected parties and resource baseline stay fixed",
    )
    text(c, "COMMON BASELINE / arrows: storage and supply", 20, 359, 500, 9, RED)
    text(c, "Storage owner", 20, 333, 110, 10)
    record_arrow(c, 114, 321, 169, 321)
    text(c, "Supplier", 181, 333, 75, 10)
    record_arrow(c, 245, 321, 300, 321)
    text(c, "Residents / workers / nonmembers", 310, 333, 210, 10)
    text(c, "Property control", 20, 312, 130, 8.5, MUTED)
    text(c, "Service duties", 181, 312, 105, 8.5, MUTED)
    text(c, "Drinking water, wages, ecological harm", 310, 312, 210, 8.5, MUTED)
    line(c, 20, 286, 520, 286, BLACK, 0.6)
    options = (
        (
            20,
            "E1",
            "Associations",
            "Recognized bodies",
            "Association mandate",
            "Membership absorbs treaty claim",
            "Who remains off the rolls?",
        ),
        (
            192,
            "E2",
            "Territory",
            "Resident franchise",
            "Territorial mandate",
            "General rule assumes shared title",
            "Whose prior title is assumed?",
        ),
        (
            364,
            "E3",
            "Watershed",
            "Residents + workers",
            "Limited water competence",
            "Separate treaty negotiation",
            "Who can challenge the forum?",
        ),
    )
    for x, code, title, voice, mandate, treaty, question in options:
        text(c, code, x, 272, 35, 15, RED)
        text(c, title, x + 33, 270, 123, 12)
        record_arrow(c, x + 78, 241, x + 78, 219, RED)
        text(c, voice, x, 211, 156, 10)
        text(c, mandate, x, 184, 156, 9, MUTED)
        line(c, x, 157, x + 156, 157, GREY, 0.6)
        text(c, "TREATY TREATMENT", x, 149, 156, 7.5, MUTED)
        text(c, treaty, x, 134, 156, 9)
        text(c, question, x, 108, 156, 9, RED)
    line(c, 20, 76, 520, 76, BLACK, 0.6)
    text(c, "IN EVERY ROUTE", 20, 66, 108, 8.5, RED)
    text(
        c,
        "Allocate compliance costs; fund hearings; preserve interim supply and review.",
        131,
        66,
        389,
        9,
    )
    _foot(
        c,
        (
            "Owner, supplier, deciding body and enforcer have distinct "
            "roles. Water urgency does not settle jurisdiction."
        ),
    )


def draw_agreement_routes(c: Canvas) -> None:
    _heading(
        c,
        "The same assent can follow different routes",
        "Conceptual identification problem / compare the means to contest agreement",
    )
    text(c, "TRANSLATION + REVISION", 20, 359, 375, 11)
    text(c, "Public reasons", 20, 324, 125, 10)
    text(c, "Open to challenge", 20, 303, 125, 9, MUTED)
    record_arrow(c, 141, 310, 178, 310)
    text(c, "Participation", 190, 324, 125, 10)
    text(c, "Funded hearing; plural accounts", 190, 303, 145, 9, MUTED)
    record_arrow(c, 326, 310, 364, 310)
    text(c, "Effective review", 376, 324, 144, 10)
    text(c, "Forum can change the act", 376, 303, 144, 9, MUTED)
    curve(c, (445, 286, 445, 250, 370, 250, 335, 222), BLACK, 1.2)
    text(c, "DEPENDENCY + GATEKEEPING", 20, 175, 375, 11, RED)
    text(c, "Controlled account", 20, 140, 150, 10, RED)
    text(c, "Gatekeeper defines credibility", 20, 119, 150, 9, MUTED)
    record_arrow(c, 161, 126, 190, 126, RED)
    text(c, "Conditional access", 202, 140, 143, 10, RED)
    text(c, "Wages or services need compliance", 202, 119, 143, 9, MUTED)
    record_arrow(c, 346, 126, 374, 126, RED)
    text(c, "Power persists", 386, 140, 134, 10, RED)
    text(c, "Appeal cannot alter exposure", 386, 119, 134, 9, MUTED)
    curve(c, (445, 157, 445, 190, 370, 190, 335, 206), RED, 1.2)
    text(c, "may produce", 427, 244, 93, 8)
    text(c, "may produce", 427, 194, 93, 8, RED)
    c.setFillColor(HexColor(WHITE))
    c.setStrokeColor(HexColor(BLACK))
    c.ellipse(176, 197, 336, 234, fill=1, stroke=1)
    label(c, "OBSERVED AGREEMENT", 256, 211, 10)
    text(c, "Assent does not identify the route", 20, 228, 145, 9, RED)
    line(c, 20, 82, 520, 82, GREY, 0.6)
    text(c, "DISCRIMINATING TEST", 20, 71, 145, 9, RED)
    text(
        c,
        "Can participants retain provision, challenge a decision and revise its mandate?",
        174,
        71,
        346,
        9,
    )
    _foot(
        c,
        (
            "Rahman supplies the conformity question; Pettit directs "
            "attention to actual control over public power."
        ),
    )
