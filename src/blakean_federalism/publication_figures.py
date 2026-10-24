# Copyright (c) 2026 Daniel Ari Friedman
"Source-bound explanatory figures; schematic arrows never assign political rights."

import io
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, cast
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from .models import ResearchError
from .workbench_models import Workbench


class _FontRegistry(Protocol):
    registerFont: Callable[[TTFont], None]  # noqa: N815 -- ReportLab API name.


def _registry(module: object) -> _FontRegistry:
    """Narrow the untyped third-party module at its documented registration API."""
    return cast("_FontRegistry", module)


INK = "#202c30"
TEAL = "#276b65"
RUST = "#9b482f"
PAPER = "#faf7ef"
GREY = "#dbe1df"


def _paragraph(c: Canvas, value: str, x: float, y: float, width: float, size: float = 11) -> None:
    p = Paragraph(
        escape(value),
        ParagraphStyle(
            "figure",
            fontName="BF-Vera",
            fontSize=size,
            leading=size * 1.32,
            textColor=HexColor(INK),
        ),
    )
    _, h = p.wrap(width, 500)
    p.drawOn(c, x, y - h)


def _box(
    c: Canvas, title: str, detail: str, x: float, y: float, width: float, height: float
) -> None:
    c.setStrokeColor(HexColor(TEAL))
    c.setFillColor(HexColor(PAPER))
    c.roundRect(x, y - height, width, height, 6, fill=1, stroke=1)
    _paragraph(c, title, x + 12, y - 11, width - 24, 12)
    _paragraph(c, detail, x + 12, y - 34, width - 24, 10)


def _arrow(c: Canvas, x: float, y: float, end_x: float, end_y: float) -> None:
    c.setStrokeColor(HexColor(TEAL))
    c.setFillColor(HexColor(TEAL))
    c.line(x, y, end_x, end_y)
    c.circle(end_x, end_y, 2.3, stroke=0, fill=1)


def _schematic(c: Canvas, number: int) -> None:
    if number == 1:
        _box(c, "PERSONS", "Affiliations are plural and revisable.", 12, 320, 158, 83)
        _box(
            c,
            "TEMPORAL NATIONS",
            "Situated productions; no final ownership of persons.",
            191,
            320,
            158,
            83,
        )
        _box(
            c,
            "POETIC STATES",
            "Interpreted possibilities; Imagination is not a state.",
            370,
            320,
            158,
            83,
        )
        _arrow(c, 170, 280, 191, 280)
        _arrow(c, 349, 280, 370, 280)
        _box(
            c,
            "INSTITUTION / PROPOSED DECISION",
            "Competence, affected reach and enforcement require separate warrants.",
            65,
            197,
            410,
            83,
        )
        _paragraph(
            c, "Neither affiliation nor interpretation establishes authorization.", 65, 88, 410, 12
        )
        _paragraph(
            c,
            (
                "Composition without capture is the proposed construction, not a "
                "constitutional code found in Blake."
            ),
            65,
            52,
            410,
        )
    elif number == 2:
        rows = [
            ("TEXTUAL WARRANT", "Plate, line, edition, copy and dramatic speaker."),
            ("RECONSTRUCTION", "Defend the bridge; preserve contrary passages and rival readings."),
            (
                "INSTITUTIONAL WARRANT",
                "Justify competence, rights, costs and accessible challenge.",
            ),
        ]
        for i, (title, detail) in enumerate(rows):
            y = 324 - i * 102
            _box(c, title, detail, 24, y, 492, 80)
            if i < 2:
                _arrow(c, 270, y - 83, 270, y - 99)
        _paragraph(c, "Success at one level does not discharge the next burden.", 24, 32, 492)
    elif number == 3:
        _box(
            c,
            "CLASSIFICATION",
            "Keep entity, assigned role, asserting institution and consequence distinct.",
            24,
            324,
            492,
            83,
        )
        _box(
            c,
            "AUTHORITY",
            "Issuer is not competence; competence is not reach; reach is not enforcement.",
            24,
            213,
            492,
            83,
        )
        _box(
            c,
            "CHALLENGE",
            "Voice, practical exit, representation limits, public reasons and revision.",
            24,
            102,
            492,
            75,
        )
        _arrow(c, 270, 238, 270, 216)
        _arrow(c, 270, 127, 270, 105)
    else:
        _box(
            c,
            "BROADER CULTURAL IDENTIFICATION",
            "Rahman's speculative counter-model, not an observed causal result.",
            24,
            324,
            492,
            78,
        )
        _box(
            c,
            "COORDINATION MAY IMPROVE",
            "Translation can make reasons accessible.",
            24,
            205,
            235,
            88,
        )
        _box(
            c,
            "CONFORMITY MAY INCREASE",
            "Gatekeepers can increase the cost of dissent.",
            281,
            205,
            235,
            88,
        )
        _arrow(c, 160, 243, 140, 208)
        _arrow(c, 380, 243, 398, 208)
        _box(
            c,
            "MATERIAL TEST",
            "Water, work, land, unequal power, affected nonmembers, treaties and refusal.",
            24,
            79,
            492,
            70,
        )


def _relations(c: Canvas) -> None:
    _paragraph(c, "PERSONS", 26, 333, 110, 12)
    _paragraph(c, "NATIONS", 216, 333, 110, 12)
    _paragraph(c, "STATE READINGS", 405, 333, 130, 12)
    persons = [(74, y) for y in (275, 205, 135)]
    nations = [(264, y) for y in (275, 205, 135)]
    states = [(454, y) for y in (250, 160)]
    for p, n in ((0, 0), (0, 1), (1, 1), (2, 1), (2, 2)):
        _arrow(c, persons[p][0] + 18, persons[p][1], nations[n][0] - 18, nations[n][1])
    for n, s in ((0, 0), (1, 0), (1, 1), (2, 1)):
        _arrow(c, nations[n][0] + 18, nations[n][1], states[s][0] - 18, states[s][1])
    for nodes, prefix in ((persons, "P"), (nations, "N"), (states, "S")):
        for index, (x, y) in enumerate(nodes, start=1):
            c.setFillColor(HexColor(PAPER))
            c.setStrokeColor(HexColor(TEAL))
            c.circle(x, y, 18, fill=1, stroke=1)
            c.setFillColor(HexColor(INK))
            c.setFont("BF-Vera", 12)
            c.drawCentredString(x, y - 4, prefix + str(index))
    _box(
        c,
        "CLAIMED COMPETENCE: J1 / decision d1",
        ("A separate warrant is required. No social network or authority has been observed here."),
        24,
        83,
        492,
        70,
    )


def _census(c: Canvas, report: Workbench) -> None:
    census = {(x.plane.value, x.role.value): x.source_units for x in report.coverage}
    colors = {"primary": TEAL, "editorial": "#848c8d", "unverified": "#b66f49"}
    _paragraph(c, "SOURCE UNITS BEFORE THEMATIC COUNTS", 18, 330, 504, 14)
    maximum = max(sum(census.get((p, r), 0) for r in colors) for p in ("reading", "erdman", "xml"))
    for i, plane in enumerate(("reading", "erdman", "xml")):
        y = 251 - i * 66
        _paragraph(c, plane.upper(), 18, y + 2, 85, 11)
        x = 112.0
        total = 0
        for role, color in colors.items():
            count = census.get((plane, role), 0)
            w = count / maximum * 340 if maximum else 0
            c.setFillColor(HexColor(color))
            c.rect(x, y - 24, w, 29, fill=1, stroke=0)
            x += w
            total += count
        _paragraph(c, f"n = {total}", 463, y - 1, 72, 10)
        detail = "; ".join(f"{role}: {census.get((plane, role), 0)}" for role in colors)
        _paragraph(c, detail, 112, y - 31, 410, 8)
    for i, (role, color) in enumerate(colors.items()):
        c.setFillColor(HexColor(color))
        c.rect(18 + 171 * i, 45, 12, 12, fill=1, stroke=0)
        _paragraph(c, role, 36 + 171 * i, 59, 130, 10)
    _paragraph(
        c,
        (
            f"{report.source_units:,} retained units: copies, editorial pages and XML, "
            "not unique works."
        ),
        18,
        38,
        504,
        10,
    )


def _matrix(c: Canvas, report: Workbench) -> None:
    if not report.cases:
        raise ResearchError("publication_cases", "A case matrix needs recorded checks")
    codes = [x.code for x in report.cases[0].assessment.checks]
    if any([x.code for x in case.assessment.checks] != codes for case in report.cases):
        raise ResearchError("publication_checks", "Case check orders differ")
    _paragraph(c, "STIPULATED SAFEGUARDS / FULL TRACE", 12, 424, 516, 14)
    width = 30
    for i, case in enumerate(report.cases):
        _paragraph(
            c,
            case.record.decision_id.replace("-bounded", "+").replace("-capture", "-"),
            215 + i * width,
            388,
            width,
            9,
        )
    for j, code in enumerate(codes):
        y = 356 - j * 20
        _paragraph(c, code.replace("_", " "), 12, y + 3, 193, 9)
        for i, case in enumerate(report.cases):
            passed = case.assessment.checks[j].passed
            c.setFillColor(HexColor("#d5e5de" if passed else "#9b482f"))
            c.rect(215 + i * width, y - 11, 22, 15, fill=1, stroke=0)
            c.setFillColor(HexColor(INK if passed else "#ffffff"))
            c.setFont("BF-Vera", 9)
            c.drawCentredString(226 + i * width, y - 8, "+" if passed else "x")
    _paragraph(
        c,
        (
            "+ pass (including untriggered conditions); x stipulated failure."
            " No empirical or legal verdict."
        ),
        12,
        35,
        516,
        10,
    )


def generate_figures(report: Workbench, output: Path, rasterizer: str) -> dict[str, str]:
    "Write new vector masters and PNG derivatives; fail on any rasterizer error."
    directory = Path(__file__).parent / "resources/fonts"
    _registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(directory / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    results: dict[str, str] = {}
    for name in (
        "abstract-1",
        "abstract-2",
        "abstract-3",
        "abstract-4",
        "typed-relations",
        "source-census",
        "case-traces",
    ):
        stream = io.BytesIO()
        c = Canvas(stream, pagesize=(540, 445 if name == "case-traces" else 345), invariant=1)
        c.setFillColor(HexColor(PAPER))
        c.rect(0, 0, 540, 445 if name == "case-traces" else 345, fill=1, stroke=0)
        if name.startswith("abstract-"):
            _schematic(c, int(name[-1]))
        elif name == "typed-relations":
            _relations(c)
        elif name == "source-census":
            _census(c, report)
        else:
            _matrix(c, report)
        c.showPage()
        c.save()
        pdf = output / (name + ".pdf")
        _ = pdf.write_bytes(stream.getvalue())
        _ = subprocess.run(  # noqa: S603 -- Explicit caller-selected rasterizer argv; no shell.
            [rasterizer, "-singlefile", "-scale-to", "2200", "-png", str(pdf), str(output / name)],
            check=True,
            capture_output=True,
        )
        results[name] = name + ".png"
    return results
