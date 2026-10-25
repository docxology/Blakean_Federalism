# Copyright (c) 2026 Daniel Ari Friedman
"""Vector essays: relational diagrams and source-bound analytical figures."""

import io
import math
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


class _BezierPath(Protocol):
    def moveTo(self, x: float, y: float) -> None: ...  # noqa: N802 -- ReportLab API.
    def lineTo(self, x: float, y: float) -> None: ...  # noqa: N802 -- ReportLab API.
    def curveTo(  # noqa: N802 -- ReportLab API.
        self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float
    ) -> None: ...
    def close(self) -> None: ...


class _PathWriter(Protocol):
    def drawPath(  # noqa: N802 -- ReportLab API.
        self, path: _BezierPath, stroke: int = 1, fill: int = 0
    ) -> None: ...


class _FontRegistry(Protocol):
    registerFont: Callable[[TTFont], None]  # noqa: N815 -- ReportLab API name.


def _path_writer(canvas: object) -> _PathWriter:
    "Narrow the ReportLab path writer where its third-party stubs omit coordinates."
    return cast("_PathWriter", canvas)


def _registry(module: object) -> _FontRegistry:
    return cast("_FontRegistry", module)


INK = "#193440"
TEAL = "#167b80"
RUST = "#ad4932"
GOLD = "#b08029"
VIOLET = "#74547d"
PAPER = "#fbf8f0"
GREY = "#d5dcd8"
MUTED = "#50656b"


def _text(
    c: Canvas,
    value: str,
    x: float,
    y: float,
    width: float,
    size: float = 11,
    color: str = INK,
) -> None:
    p = Paragraph(
        escape(value),
        ParagraphStyle(
            "figure",
            fontName="BF-Vera",
            fontSize=size,
            leading=size * 1.27,
            textColor=HexColor(color),
        ),
    )
    _, height = p.wrap(width, 500)
    p.drawOn(c, x, y - height)


def _line(
    c: Canvas, x: float, y: float, end_x: float, end_y: float, color: str = GREY, width: float = 1
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x, y, end_x, end_y)


def _curve(
    c: Canvas,
    points: tuple[float, float, float, float, float, float, float, float],
    color: str,
    width: float = 1.3,
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    p = cast("_BezierPath", c.beginPath())
    p.moveTo(points[0], points[1])
    p.curveTo(*points[2:])
    _path_writer(c).drawPath(p)


def _circle(
    c: Canvas, x: float, y: float, radius: float, color: str, fill: str = PAPER, width: float = 1.3
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setFillColor(HexColor(fill))
    c.setLineWidth(width)
    c.circle(x, y, radius, stroke=1, fill=1)


def _label(c: Canvas, value: str, x: float, y: float, size: float = 10, color: str = INK) -> None:
    c.setFillColor(HexColor(color))
    c.setFont("BF-Vera", size)
    c.drawCentredString(x, y, value)


def _header(c: Canvas, index: str, title: str, subtitle: str) -> None:
    _text(c, index, 20, 328, 38, 10, TEAL)
    _text(c, title, 63, 331, 458, 19)
    _text(c, subtitle, 63, 304, 458, 9, MUTED)
    _line(c, 20, 286, 520, 286)


def _footer(c: Canvas, value: str) -> None:
    _line(c, 20, 40, 520, 40)
    _text(c, value, 20, 31, 500, 9, MUTED)


def _petal(c: Canvas, x: float, y: float, color: str, turn: float = 0) -> None:
    c.saveState()
    c.translate(x, y)
    c.rotate(turn)
    for angle in (0, 60, 120):
        c.saveState()
        c.rotate(angle)
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(1.1)
        c.ellipse(-16, -5, 16, 5, fill=0, stroke=1)
        c.restoreState()
    c.restoreState()


def _ribbon(c: Canvas, x: float, y: float, color: str, flip: float = 1) -> None:
    c.saveState()
    c.setFillColor(HexColor(color))
    c.setFillAlpha(0.12)
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(1.4)
    p = cast("_BezierPath", c.beginPath())
    p.moveTo(x, y)
    p.curveTo(x + 80, y + 65 * flip, x + 142, y - 44 * flip, x + 250, y + 16)
    p.curveTo(x + 152, y - 86 * flip, x + 75, y + 12 * flip, x, y - 41)
    p.close()
    _path_writer(c).drawPath(p, fill=1, stroke=1)
    c.restoreState()


def _composition(c: Canvas) -> None:
    _header(
        c,
        "01",
        "Composition without capture",
        "Enduring possibilities / historical formations / persons in passage",
    )
    _text(c, "STATES", 20, 265, 83, 10, VIOLET)
    _text(c, "Recurring\npossibilities", 20, 247, 83, 9, MUTED)
    for x, color, turn, name in (
        (151, TEAL, 0, "S1"),
        (298, VIOLET, 30, "S2"),
        (444, TEAL, 0, "S1"),
    ):
        _petal(c, x, 245, color, turn)
        _label(c, name, x, 220, 9, color)
    for points in (
        (151, 214, 145, 198, 170, 190, 205, 185),
        (298, 214, 289, 196, 244, 191, 205, 185),
        (298, 214, 313, 196, 335, 183, 359, 160),
        (444, 214, 441, 194, 404, 172, 359, 160),
    ):
        c.setDash(3, 3)
        _curve(c, points, VIOLET, 0.9)
        c.setDash()
    _text(c, "NATIONS", 20, 187, 83, 10, TEAL)
    _ribbon(c, 116, 180, TEAL)
    _ribbon(c, 251, 156, RUST, -1)
    _label(c, "N1", 194, 173, 12, TEAL)
    _label(c, "N2", 421, 143, 12, RUST)
    _text(c, "PERSONS", 20, 109, 83, 10, INK)
    for x, target in ((142, 170), (247, 220), (349, 370), (470, 434)):
        _curve(c, (x, 100, x - 18, 117, target + 18, 130, target, 147), MUTED)
        _circle(c, x, 91, 8, INK)
    _curve(c, (247, 100, 259, 125, 303, 126, 326, 148), MUTED)
    _text(c, "Plural affiliations", 120, 70, 167, 10)
    _text(c, "Persons exceed every membership", 296, 70, 215, 10)
    _footer(
        c, "Interpretation links nations to states; political authority requires its own warrant."
    )


def _book(c: Canvas, x: float, y: float) -> None:
    for direction in (-1, 1):
        p = cast("_BezierPath", c.beginPath())
        p.moveTo(x, y - 25)
        p.curveTo(
            x + direction * 12, y - 12, x + direction * 32, y - 18, x + direction * 43, y - 22
        )
        p.lineTo(x + direction * 43, y + 27)
        p.curveTo(x + direction * 26, y + 34, x + direction * 13, y + 31, x, y + 20)
        p.close()
        c.setStrokeColor(HexColor(TEAL))
        c.setFillColor(HexColor("#e8eeDE"))
        _path_writer(c).drawPath(p, stroke=1, fill=1)
        for offset in (-7, 3, 13):
            _line(c, x + direction * 10, y + offset, x + direction * 32, y + offset + 4, TEAL, 0.8)


def _warrants(c: Canvas) -> None:
    _header(
        c,
        "02",
        "Three acts of argument",
        "Read the passage. Defend the interpretation. Justify the institution.",
    )
    _curve(c, (72, 185, 167, 282, 365, 101, 478, 189), GOLD, 3)
    for x in (101, 270, 439):
        _circle(c, x, 193, 58, GREY, PAPER, 0.8)
    _book(c, 101, 193)
    # A bridge: the middle act constructs a relation between distinct banks.
    _line(c, 229, 172, 311, 172, VIOLET, 2)
    _curve(c, (231, 175, 240, 219, 301, 219, 309, 175), VIOLET, 2)
    for x in range(239, 308, 17):
        _line(c, x, 174, x, 191, VIOLET)
    # A public forum: several seats face a decision rather than one sovereign eye.
    for angle in (30, 90, 150, 210, 270, 330):
        radians = math.radians(angle)
        _circle(c, 439 + 33 * math.cos(radians), 193 + 33 * math.sin(radians), 5, RUST)
    _circle(c, 439, 193, 13, RUST)
    _label(c, "d", 439, 189, 12, RUST)
    for x, title, detail, color in (
        (26, "READ", "Plate, line, speaker, copy", TEAL),
        (195, "RECONSTRUCT", "State, person, generation", VIOLET),
        (364, "INSTITUTE", "Power, costs, review", RUST),
    ):
        _text(c, title, x, 111, 150, 12, color)
        _text(c, detail, x, 89, 150, 10)
    _footer(
        c,
        "Close reading, political reconstruction and institutional comparison.",
    )


def _authority(c: Canvas) -> None:
    _header(
        c,
        "03",
        "Unpack the decision",
        "A water-allocation example separates four questions about authority",
    )
    positions = (
        (114, 222, "ISSUER", "Who asserts?", TEAL),
        (416, 222, "COMPETENCE", "Under which warrant?", VIOLET),
        (114, 115, "REACH", "Who is affected?", GOLD),
        (416, 115, "ENFORCEMENT", "Who can compel?", RUST),
    )
    for x, y, title, detail, color in positions:
        _line(c, 270, 176, x, y, color, 1.6)
        _circle(c, x, y, 7, color, color)
        _label(c, title, x, y + 22, 10, color)
        _label(c, detail, x, y - 25, 9)
    _circle(c, 270, 176, 43, INK, PAPER, 1.7)
    _label(c, "DECISION", 270, 184, 10)
    _label(c, "Water levy", 270, 165, 11)
    _line(c, 170, 67, 370, 67, TEAL, 2)
    _label(c, "Reasons  /  standing  /  review  /  revision", 270, 51, 10)
    _footer(
        c,
        "Record the entity, assigned role and consequence alongside these four distinct warrants.",
    )


def _scale(c: Canvas) -> None:
    _header(
        c,
        "04",
        "Two routes to agreement",
        "Compare coordination with the conditions under which people can dissent",
    )
    _circle(c, 65, 172, 22, INK)
    _label(c, "Public", 65, 168, 10)
    _curve(c, (87, 177, 170, 184, 145, 238, 220, 238), TEAL, 4)
    _curve(c, (87, 167, 170, 158, 145, 110, 220, 110), RUST, 4)
    _text(c, "TRANSLATION + REVISION", 175, 271, 310, 12, TEAL)
    _text(c, "DEPENDENCY + GATEKEEPING", 175, 145, 335, 12, RUST)
    for dy in (-18, 0, 18):
        _curve(c, (220, 238, 280, 238 + dy, 327, 238 + dy, 380, 238 + dy), TEAL)
        _circle(c, 380, 238 + dy, 4, TEAL)
        _curve(c, (220, 110 + dy, 285, 110 + dy, 292, 110, 326, 110), RUST)
    _line(c, 326, 90, 326, 131, RUST, 5)
    _line(c, 326, 110, 380, 110, RUST, 2)
    _circle(c, 380, 110, 4, RUST)
    for y in (238, 110):
        _text(c, "Agreement", 403, y + 6, 110, 11)
    _text(c, "Challenge stays open", 260, 207, 250, 10, TEAL)
    _text(c, "Challenge becomes costly", 260, 77, 250, 10, RUST)
    _footer(
        c, "Conceptual contrast prompted by Rahman's profile and Pettit's account of domination."
    )


def _relations(c: Canvas) -> None:
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
        _curve(c, (x, y - 12, x, y - 35, end, ey + 35, end, ey + 12), TEAL, 1.5)
    for n, s in ((0, 0), (0, 1), (1, 1), (1, 2)):
        x, y = nations[n]
        end, ey = states[s]
        c.setDash(3, 2)
        _curve(c, (x, y - 12, x, y - 35, end, ey + 35, end, ey + 12), VIOLET)
        c.setDash()
    for points, prefix, color in ((persons, "P", INK), (nations, "N", TEAL), (states, "S", VIOLET)):
        for index, (x, y) in enumerate(points, 1):
            _circle(c, x, y, 12, color)
            _label(c, prefix + str(index), x, y - 3, 8, color)
    _text(c, "Persons", 22, 258, 130, 10)
    _text(c, "A / affiliation", 156, 258, 180, 10, TEAL)
    _line(c, 355, 61, 355, 272, GREY)
    _label(c, "C / claimed competence", 444, 252, 9, RUST)
    _circle(c, 444, 208, 20, RUST)
    _label(c, "J1", 444, 204, 12, RUST)
    _line(c, 444, 187, 444, 137, RUST, 2)
    _circle(c, 444, 116, 20, RUST)
    _label(c, "d1", 444, 112, 12, RUST)
    _text(c, "Institution / decision", 376, 78, 150, 10, RUST)
    _footer(c, "Illustrative relations. C can change while A and I remain fixed (Proposition 1).")


def _census(c: Canvas, report: Workbench) -> None:
    census = {(x.plane.value, x.role.value): x.source_units for x in report.coverage}
    _header(
        c,
        "n",
        "Count the source units first",
        "Copies, retained pages and XML units / roles from the pinned index",
    )
    colors = {"primary": TEAL, "editorial": "#586f75", "unverified": "#966a22"}
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
                _label(c, str(count), x + width / 2, y - 11, 10, "#ffffff")
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


def _matrix(c: Canvas, report: Workbench) -> None:
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
            c.setFillColor(HexColor("#ebece4"))
            c.rect(x - 12, 60, 53, 327, fill=1, stroke=0)
        _label(c, label, x, 372, 9)
    failures = 0
    for row, code in enumerate(codes):
        y = 346 - row * 19
        _text(c, code.replace("_", " "), 20, y + 5, 192, 9)
        _line(c, 20, y - 7, 520, y - 7, "#e1e4df", 0.4)
        for column, case in enumerate(report.cases):
            x = 231 + 29 * column
            passed = case.assessment.checks[row].passed
            if passed:
                _circle(c, x, y, 4.5, TEAL, PAPER, 1)
            else:
                failures += 1
                _circle(c, x, y, 6.4, RUST, RUST)
                _line(c, x - 2, y - 2, x + 2, y + 2, PAPER, 1)
                _line(c, x - 2, y + 2, x + 2, y - 2, PAPER, 1)
    _circle(c, 26, 51, 4.5, TEAL)
    _text(c, "Rule satisfied*", 37, 57, 133, 9)
    _circle(c, 183, 51, 6, RUST, RUST)
    _label(c, "x", 183, 48, 8, PAPER)
    _text(c, "Rule violated", 196, 57, 129, 9)
    _text(c, f"{failures} recorded violations", 346, 57, 173, 9)
    _line(c, 20, 36, 520, 36)
    _text(
        c,
        "*Includes untriggered conditions. These are programmed checks on synthetic records.",
        20,
        28,
        500,
        9,
        MUTED,
    )


def _watershed(c: Canvas) -> None:
    _header(
        c,
        "E",
        "Who decides about the water?",
        "Three institutional arrangements for the same hypothetical scarcity",
    )
    headings = (
        (181, "E1 / ASSOCIATIONS", TEAL),
        (302, "E2 / TERRITORY", VIOLET),
        (423, "E3 / WATERSHED", RUST),
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


def generate_figures(report: Workbench, output: Path, rasterizer: str) -> dict[str, str]:
    """Write new deterministic vector masters and PNG derivatives."""
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
        "watershed-options",
    ):
        stream = io.BytesIO()
        height = 445 if name == "case-traces" else 345
        c = Canvas(stream, pagesize=(540, height), invariant=1)
        c.setFillColor(HexColor(PAPER))
        c.rect(0, 0, 540, height, fill=1, stroke=0)
        if name == "abstract-1":
            _composition(c)
        elif name == "abstract-2":
            _warrants(c)
        elif name == "abstract-3":
            _authority(c)
        elif name == "abstract-4":
            _scale(c)
        elif name == "typed-relations":
            _relations(c)
        elif name == "source-census":
            _census(c, report)
        elif name == "watershed-options":
            _watershed(c)
        else:
            _matrix(c, report)
        c.showPage()
        c.save()
        pdf = output / (name + ".pdf")
        _ = pdf.write_bytes(stream.getvalue())
        _ = subprocess.run(  # noqa: S603 -- Explicit caller-selected argv; no shell.
            [rasterizer, "-singlefile", "-scale-to", "2200", "-png", str(pdf), str(output / name)],
            check=True,
            capture_output=True,
        )
        results[name] = name + ".png"
    return results
