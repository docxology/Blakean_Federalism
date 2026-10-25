# Copyright (c) 2026 Daniel Ari Friedman
"""Four information-rich visual abstracts for the article's distinct arguments."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import (
    BLACK,
    GREY,
    MUTED,
    RED,
    WHITE,
    circle,
    curve,
    label,
    line,
    petal,
    ribbon,
    text,
)
from .workbench_models import Workbench


def _heading(c: Canvas, number: str, title: str, subtitle: str) -> None:
    text(c, number, 18, 503, 34, 11, RED)
    text(c, title, 58, 505, 464, 19)
    text(c, subtitle, 58, 477, 464, 10, MUTED)
    line(c, 18, 452, 522, 452, RED, 2)


def _foot(c: Canvas, value: str) -> None:
    line(c, 18, 38, 522, 38, BLACK, 0.6)
    text(c, value, 18, 29, 504, 9, MUTED)


def composition(c: Canvas) -> None:
    _heading(
        c,
        "01",
        "States recur. Nations compose.",
        "A federation can sustain plural nations without becoming one nation",
    )
    text(c, "STATES / S", 18, 431, 100, 10, RED)
    text(c, "Recurrent imaginative possibilities", 18, 412, 103, 9)
    for x, name, turn in ((174, "S1", 0), (311, "S2", 30), (448, "S1", 0)):
        petal(c, x, 417, BLACK, turn)
        label(c, name, x, 394, 9)
    for points in (
        (174, 386, 166, 367, 175, 354, 205, 347),
        (311, 386, 296, 369, 245, 353, 205, 347),
        (311, 386, 322, 360, 344, 343, 367, 328),
        (448, 386, 443, 364, 407, 343, 367, 328),
    ):
        c.setDash(3, 3)
        curve(c, points, BLACK, 0.9)
        c.setDash()
    text(c, "NATIONS / N", 18, 350, 100, 10, RED)
    text(c, "Historical combinations and productions", 18, 331, 100, 9)
    ribbon(c, 119, 341, BLACK)
    ribbon(c, 254, 321, RED, -1)
    label(c, "N1", 202, 329, 11)
    label(c, "N2", 431, 307, 11, RED)
    text(c, "PERSONS / P", 18, 279, 103, 10, RED)
    for x, end in ((150, 170), (246, 221), (349, 374), (473, 438)):
        curve(c, (x, 270, x - 14, 284, end + 16, 299, end, 305), BLACK)
        circle(c, x, 263, 7, BLACK)
    curve(c, (246, 270, 263, 291, 302, 297, 328, 309), BLACK)
    text(c, "Plural affiliations; standing survives a change of affiliation", 120, 247, 398, 10)
    line(c, 18, 224, 522, 224, RED, 1.5)
    text(
        c,
        "A: persons x nations   I: nations x state readings   C: institution x decision",
        18,
        214,
        504,
        10,
    )
    text(
        c,
        "Affiliation and interpretation leave the competence claim to be justified.",
        18,
        194,
        504,
        10,
        RED,
    )
    text(c, "PRIMARY TEXT", 18, 164, 240, 11, RED)
    text(c, "INSTITUTIONAL CONSEQUENCE", 285, 164, 237, 11, RED)
    pairs = (
        (
            "Milton 32:22-24 / E132",
            "Persons endure; present states change.",
            "Basic standing",
            "A person exceeds the current register.",
        ),
        (
            "Milton 32:32-38 / E132",
            "Imagination exceeds the states named.",
            "Limited representation",
            "No body speaks a member's whole identity.",
        ),
        (
            "Jerusalem 52 + 73 / E200, E229",
            "Permanent states and persons in passage.",
            "Passage, voice, revision",
            "Specify means, forums and continuing duties.",
        ),
    )
    for index, (source, claim, title, consequence) in enumerate(pairs):
        y = 143 - index * 32
        text(c, source, 18, y, 247, 9)
        text(c, claim, 18, y - 13, 247, 9, MUTED)
        text(c, title, 285, y, 237, 9)
        text(c, consequence, 285, y - 13, 237, 9, MUTED)
    _foot(c, "The reconstruction connects poetic nonidentity to accountable public decisions.")


def scholarship(c: Canvas) -> None:
    _heading(
        c,
        "02",
        "Six disputes shape the federation",
        "Textual and political interlocutors change the questions asked of a federation",
    )
    columns = (
        (18, 108, "PROBLEM"),
        (138, 188, "SCHOLARLY TENSION"),
        (340, 182, "INSTITUTIONAL QUESTION"),
    )
    for x, width, title in columns:
        text(c, title, x, 433, width, 10, RED)
    rows = (
        (
            "PERMANENCE",
            "Milton 32; Jerusalem 52",
            "Damrosch / Lee",
            "Particular forms and identity versus compulsory remaking.",
            "Which mandate can end while persons retain standing?",
        ),
        (
            "NATION",
            "Jerusalem 27, 43, 92",
            "Fallon / Clark",
            "Situated mediation versus incorporation into one authorized future.",
            "Can a people dispute the common story while remaining a participant?",
        ),
        (
            "GENDER",
            "Jerusalem 88 + 99",
            "Mellor / Kaplan",
            "Gendered creative priority; rival readings of the final embrace.",
            "Who interprets, refuses a role and helps govern the shared world?",
        ),
        (
            "REFUSAL",
            "Standing and disclosure",
            "Simpson / Pettit",
            "Access to reasons differs from compulsory cultural legibility.",
            "Can someone challenge a classification without narrating a total identity?",
        ),
        (
            "OPPOSITION",
            "Counterpublics and recognition",
            "Fraser / Tully",
            "Collective voice needs means; procedures of recognition can be reopened.",
            "Can organized dissent change both the decision and the rules of hearing?",
        ),
        (
            "REVIEW",
            "Power and remedies",
            "Shachar / Henderson",
            "Protection may require review; the reviewer's jurisdiction remains arguable.",
            "Who initiates, pays for and can contest protective intervention?",
        ),
    )
    for index, (problem, source, authors, tension, question) in enumerate(rows):
        y = 408 - index * 55
        text(c, problem, 18, y, 108, 11)
        text(c, source, 18, y - 19, 108, 9, MUTED)
        text(c, authors, 138, y, 188, 10, RED)
        text(c, tension, 138, y - 16, 188, 9)
        text(c, question, 340, y, 182, 9.5)
        line(c, 18, y - 51, 522, y - 51, GREY, 0.6)
    text(
        c,
        "Who can remain and contest the terms of combination?",
        18,
        62,
        504,
        10,
        RED,
    )
    _foot(
        c,
        "Page-specific arguments, contrary passages and reading records are developed in the text.",
    )


def decision(c: Canvas) -> None:
    _heading(
        c,
        "03",
        "A water decision in six stages",
        "Worked example: a proposed water levy amid contested membership and jurisdiction",
    )
    stages = (
        (
            "ENTITY / ROLE",
            "Resident, water user, worker and treaty claimant are separately described roles.",
        ),
        (
            "ISSUER / COMPETENCE",
            "Name the board, the proposed act and the delegation or agreement invoked.",
        ),
        (
            "REACH / ENFORCEMENT",
            "Identify affected upstream and downstream people, the enforcing actor and its limits.",
        ),
        (
            "MATERIAL BURDENS",
            "Specify water access, costs, ability to pay, wages and residual risks.",
        ),
        (
            "CHALLENGE / INTERIM DUTIES",
            "Locate review, its funding and the duty to maintain essential provision during delay.",
        ),
        (
            "REVISION / DISPUTED TITLE",
            "Record expiry, rule-change powers and a challenge to the forum's jurisdiction.",
        ),
    )
    line(c, 31, 420, 31, 118, RED, 1.5)
    for index, (title, detail) in enumerate(stages):
        y = 426 - index * 55
        circle(c, 31, y - 9, 10, RED, WHITE)
        label(c, str(index + 1), 31, y - 12, 10, RED)
        text(c, title, 54, y, 290, 10, RED)
        text(c, detail, 54, y - 17, 290, 10)
    line(c, 360, 126, 360, 435, GREY)
    for index, (title, detail) in enumerate(
        (
            ("AFFILIATION / STANDING", "A national label does not allocate every public right."),
            (
                "VOICE / AGREEMENT",
                "Representation, consent to an act and a power to reopen it differ.",
            ),
            (
                "WARRANT / EXECUTION",
                "Issuing a decision, reaching people and compelling compliance differ.",
            ),
        )
    ):
        y = 425 - index * 102
        text(c, title, 378, y, 144, 10, RED)
        text(c, detail, 378, y - 27, 144, 10)
    line(c, 18, 100, 522, 100, BLACK)
    text(c, "COMPARE AT THE SAME SCARCITY", 18, 89, 504, 10, RED)
    for x, title, detail in (
        (18, "E1 / associations", "Recognized bodies"),
        (190, "E2 / territory", "Resident franchise"),
        (362, "E3 / watershed", "Limited task + treaty negotiation"),
    ):
        text(c, title, x, 70, 160, 10)
        text(c, detail, x, 56, 160, 8.5, MUTED)
    _foot(c, "The record follows entity, role, authority, consequence, contestation and revision.")


def evidence(c: Canvas, report: Workbench) -> None:
    _heading(
        c,
        "04",
        "Corpus retrieval and rule traces",
        "Two executable operations: locate passages and inspect explicitly programmed safeguards",
    )
    for x, value, title in (
        (18, f"{report.source_units:,}", "SOURCE UNITS"),
        (149, str(len(report.query_groups)), "QUERY GROUPS"),
        (280, f"{report.stored_occurrences:,}", "STORED HITS"),
        (411, str(len(report.coverage)), "COVERAGE CELLS"),
    ):
        text(c, value, x, 433, 111, 24, RED)
        text(c, title, x, 400, 111, 9)
    line(c, 18, 376, 522, 376, BLACK)
    text(c, "KNOW THE DENOMINATOR", 18, 363, 245, 11, RED)
    census = {(x.plane.value, x.role.value): x.source_units for x in report.coverage}
    maximum = max(
        sum(census.get((p, role), 0) for role in ("primary", "editorial", "unverified"))
        for p in ("reading", "erdman", "xml")
    )
    for index, plane in enumerate(("reading", "erdman", "xml")):
        y = 333 - index * 31
        text(c, plane, 18, y, 56, 9)
        x = 81.0
        for role, color in (("primary", RED), ("editorial", BLACK), ("unverified", "#bbbbbb")):
            count = census.get((plane, role), 0)
            width = 148 * count / maximum if maximum else 0
            c.setFillColor(HexColor(color))
            c.rect(x, y - 13, width, 14, fill=1, stroke=0)
            x += width
        text(
            c,
            str(
                sum(census.get((plane, role), 0) for role in ("primary", "editorial", "unverified"))
            ),
            240,
            y,
            45,
            9,
        )
    text(c, "Red: primary / black: editorial / grey: unverified", 18, 242, 267, 8.5)
    state = next(
        (
            x
            for x in report.coverage
            if x.query_id == "states" and x.plane.value == "reading" and x.role.value == "primary"
        ),
        None,
    )
    text(c, "STATES / PRIMARY READING", 304, 363, 218, 11, RED)
    if state is not None:
        text(c, f"{state.matched_source_documents} / {state.source_units} units", 304, 335, 218, 18)
        fraction = (
            f"{100 * state.coverage_fraction:.1f}%"
            if state.coverage_fraction is not None
            else "N/A"
        )
        text(c, f"{fraction} unit coverage", 304, 306, 218, 12, RED)
        text(c, f"{state.occurrences} occurrences", 304, 281, 218, 12)
    else:
        text(c, "N/A / query absent", 304, 335, 218, 14)
    text(c, "Copies, pages and XML remain distinct source units.", 304, 255, 218, 9)
    line(c, 18, 224, 522, 224, BLACK)
    text(c, "FIVE SYNTHETIC CASE PAIRS", 18, 214, 300, 11, RED)
    text(c, "Violations: bounded / capture", 326, 214, 196, 9)
    issues = (
        "A / shared territory",
        "B / cross-border nation",
        "C / a generation becomes public",
        "D / vision ranking",
        "E / water, costs and treaty claims",
    )
    for index, title in enumerate(issues):
        y = 187 - index * 23
        text(c, title, 18, y, 312, 10)
        pair = report.cases[2 * index : 2 * index + 2]
        counts = [sum(not x.passed for x in case.assessment.checks) for case in pair]
        text(c, " / ".join(str(x) for x in counts), 411, y, 111, 11, RED)
        line(c, 18, y - 17, 522, y - 17, GREY, 0.5)
    checks = sum(len(case.assessment.checks) for case in report.cases)
    failures = sum(not x.passed for case in report.cases for x in case.assessment.checks)
    text(
        c,
        f"{checks} checks / {failures} recorded violations / full inputs and per-rule traces",
        18,
        62,
        504,
        10,
    )
    _foot(c, "Counts support passage finding; the case verdicts express the supplied safeguards.")
