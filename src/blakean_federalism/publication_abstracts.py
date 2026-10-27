# Copyright (c) 2026 Daniel Ari Friedman
"""Typed relations, interpretive tensions, and accountable decisions in vector form."""

from math import atan2, cos, sin

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, MUTED, RED, WHITE, circle, label, line, text


def _heading(c: Canvas, number: str, title: str, subtitle: str) -> None:
    text(c, number, 20, 503, 32, 11, RED)
    text(c, title, 55, 505, 465, 21)
    text(c, subtitle, 55, 477, 465, 10, MUTED)
    line(c, 20, 458, 520, 458, RED, 1.5)


def _foot(c: Canvas, value: str) -> None:
    line(c, 20, 38, 520, 38, BLACK, 0.6)
    text(c, value, 20, 31, 500, 9, MUTED)


def _arrow(
    c: Canvas, x: float, y: float, ex: float, ey: float, color: str = BLACK, *, dashed: bool = False
) -> None:
    c.saveState()
    if dashed:
        c.setDash(3, 3)
    line(c, x, y, ex, ey, color, 1)
    c.setDash()
    angle = atan2(ey - y, ex - x)
    for delta in (-0.45, 0.45):
        line(c, ex, ey, ex - 5 * cos(angle + delta), ey - 5 * sin(angle + delta), color, 1)
    c.restoreState()


def _box(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    detail: str,
    color: str = BLACK,
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setFillColor(HexColor(WHITE))
    c.setLineWidth(1)
    c.rect(x, y - height, width, height, stroke=1, fill=1)
    text(c, title, x + 9, y - 8, width - 18, 10, color)
    text(c, detail, x + 9, y - 25, width - 18, 9)


def composition(c: Canvas) -> None:
    _heading(
        c,
        "01",
        "Composition without capture",
        "Different relations carry different warrants; no layer grants the next its power.",
    )
    text(c, "POETIC STATES / S", 20, 442, 160, 11)
    text(c, "Recurrent possibilities, represented through interpretations", 210, 442, 310, 9, MUTED)
    for x, name in ((135, "s1"), (270, "s2"), (405, "s3")):
        c.setStrokeColor(HexColor(BLACK))
        c.setLineWidth(1)
        c.ellipse(x - 33, 393, x + 33, 420)
        label(c, name, x, 402, 11)
    for x, ex in ((135, 185), (270, 185), (270, 355), (405, 355), (135, 355)):
        c.saveState()
        c.setDash(3, 3)
        line(c, x, 393, ex, 340, BLACK, 0.8)
        c.restoreState()
    text(c, "I: interpretation", 20, 374, 120, 9, RED)
    text(c, "I pairs N with S", 410, 374, 110, 10, MUTED)
    for x, name in ((185, "n1"), (355, "n2")):
        _box(c, x - 47, 340, 94, 33, name, "")
    text(c, "NATIONAL FORMATIONS / N", 20, 337, 110, 10)
    text(c, "Interpretation is not a competence warrant", 410, 337, 110, 9, MUTED)
    for x, ex in ((95, 185), (210, 185), (210, 355), (325, 355), (445, 355)):
        line(c, x, 246, ex, 307, BLACK, 0.85)
    for x, name in ((95, "p1"), (210, "p2"), (325, "p3"), (445, "p4")):
        circle(c, x, 235, 12, BLACK)
        label(c, name, x, 231, 9)
    text(c, "A pairs P with N", 20, 274, 100, 10, RED)
    text(c, "PERSONS / P", 20, 212, 120, 11)
    text(c, "Plural affiliation; no compulsory final identity", 155, 212, 365, 10)
    _arrow(c, 95, 179, 445, 179, RED)
    text(c, "PASSAGE: change affiliation while retaining basic standing", 65, 170, 440, 10, RED)
    line(c, 20, 145, 520, 145, BLACK, 0.7)
    text(c, "SEPARATE AUTHORITY LAYER", 20, 135, 250, 10, RED)
    _box(c, 20, 114, 145, 45, "Institution / J", "C pairs J with D")
    _arrow(c, 165, 91, 350, 91, RED)
    label(c, "C: claimed competence", 258, 102, 9, RED)
    _box(c, 350, 114, 170, 45, "Proposed decision / D", "Warrant, reach, review")
    text(
        c,
        "Same A and I, different C: affiliation and interpretation underdetermine authority.",
        20,
        61,
        500,
        9,
    )
    _foot(c, "Textual anchors: Milton 32:22-38 / E132; Jerusalem 52 / E200; 73 / E229.")


def scholarship(c: Canvas) -> None:
    _heading(
        c,
        "02",
        "Disagreement changes the design",
        "Selected arguments constrain three institutional questions; arrows mark reconstruction.",
    )
    # Each fork brings distinct arguments into one design question, not a consensus.
    blocks = (
        (
            440,
            "PERMANENCE ≠ POSSESSION",
            ("Damrosch, pp. 15-21", "Universality in particular forms"),
            ("Lee, pp. 1-10", "Identity can resist forced remaking"),
            "What may change while preserving standing?",
            "Design test: portable rights + supported affiliation change.",
        ),
        (
            317,
            "RECIPROCITY ≠ EQUAL AUTHORITY",
            ("Fallon, ms. pp. 10-12", "National opening; incorporation disputed"),
            ("Mellor, pp. 148-153", "Creative reciprocity can retain hierarchy"),
            "Who can interpret, refuse a role and govern?",
            "Design test: role ≠ person; vision confers no civic rank.",
        ),
        (
            194,
            "PROTECTION ≠ CONTROL",
            ("Simpson, pp. 67-78", "Refusal limits compulsory disclosure"),
            ("Shachar, pp. 75-77", "Review before enforceability shifts burden"),
            "Who initiates review and can contest the forum?",
            "Design test: funded challenge + separately negotiated refusal.",
        ),
    )
    for y, title, left, right, question, consequence in blocks:
        text(c, title, 20, y, 500, 11, RED)
        text(c, left[0], 20, y - 23, 230, 10)
        text(c, left[1], 20, y - 40, 230, 9, MUTED)
        text(c, right[0], 295, y - 23, 225, 10)
        text(c, right[1], 295, y - 40, 225, 9, MUTED)
        _arrow(c, 135, y - 66, 235, y - 74)
        _arrow(c, 405, y - 66, 305, y - 74)
        text(c, question, 20, y - 82, 500, 12, RED)
        text(c, consequence, 20, y - 100, 500, 9)
    _foot(
        c,
        "Read as tensions, not a unified doctrine. Primary countertexts: Jerusalem 43, 88, 92, 99.",
    )


def decision(c: Canvas) -> None:
    _heading(
        c,
        "03",
        "Who can make a water levy bind?",
        "Hypothetical accountability map: classification, authority and remedy remain distinct.",
    )
    _box(c, 20, 440, 145, 58, "ENTITY", "Affected person or collective")
    _box(c, 205, 440, 145, 58, "ASSIGNED ROLE", "User, worker, resident or treaty claimant")
    _arrow(c, 165, 411, 205, 411)
    text(c, "Classification needs a stated warrant", 367, 429, 153, 10, RED)
    _box(c, 20, 357, 145, 71, "ISSUER", "Board in J; name its issuing jurisdiction separately")
    _box(c, 205, 357, 145, 71, "PROPOSED ACT / D", "Levy, term and competence source")
    _arrow(c, 165, 325, 205, 325)
    label(c, "C", 185, 333, 10, RED)
    _arrow(c, 277, 382, 277, 357)
    _box(c, 385, 357, 135, 71, "REACH", "Upstream + downstream; affected nonmembers")
    _arrow(c, 350, 325, 385, 325)
    _box(c, 205, 258, 145, 65, "ENFORCER", "Named actor; coercive powers and limits")
    _arrow(c, 277, 286, 277, 258)
    _box(c, 385, 258, 135, 65, "CONSEQUENCE", "Access, levy, ability to pay; residual risk")
    _arrow(c, 350, 227, 385, 227)
    _arrow(c, 452, 286, 452, 258)
    text(c, "Authority to issue ≠ reach ≠ power to compel", 20, 272, 160, 10, RED)
    _box(
        c,
        20,
        164,
        330,
        69,
        "CHALLENGE + INTERIM DUTIES",
        (
            "Fund participation; maintain essential water during delay. Name "
            "reviewer, deadline and effective remedy."
        ),
        RED,
    )
    _arrow(c, 452, 193, 452, 130, RED)
    _arrow(c, 452, 130, 350, 130, RED)
    text(c, "burdens trigger scrutiny", 370, 181, 75, 9, RED)
    # Explicit feedback to the act and a separate challenge to the issuer.
    _arrow(c, 277, 164, 277, 193, RED, dashed=True)
    _arrow(c, 175, 164, 175, 301, RED, dashed=True)
    _arrow(c, 175, 301, 165, 301, RED, dashed=True)
    text(c, "contest title", 22, 190, 65, 9, RED)
    text(c, "remedy / revise", 286, 188, 65, 9, RED)
    text(c, "RECORD / CHECK / REMEDY", 20, 82, 500, 10, RED)
    text(c, "Reach: EXCLUDED_AFFECTED; costs: RESOURCE_GAP; appeal: CONTESTATION", 20, 64, 500, 9)
    _foot(
        c,
        (
            "The forum's jurisdiction remains challengeable. This diagram "
            "asserts no current legal power."
        ),
    )
