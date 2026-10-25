# Copyright (c) 2026 Daniel Ari Friedman
"""Vector essays: relational diagrams and source-bound analytical figures."""

from collections.abc import Callable
from typing import Protocol, cast
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


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


def registry(module: object) -> _FontRegistry:
    return cast("_FontRegistry", module)


BLACK = "#000000"
RED = "#b00020"
WHITE = "#ffffff"
GREY = "#cccccc"
MUTED = "#444444"


def text(
    c: Canvas,
    value: str,
    x: float,
    y: float,
    width: float,
    size: float = 11,
    color: str = BLACK,
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


def line(
    c: Canvas, x: float, y: float, end_x: float, end_y: float, color: str = GREY, width: float = 1
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x, y, end_x, end_y)


def curve(
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


def circle(
    c: Canvas, x: float, y: float, radius: float, color: str, fill: str = WHITE, width: float = 1.3
) -> None:
    c.setStrokeColor(HexColor(color))
    c.setFillColor(HexColor(fill))
    c.setLineWidth(width)
    c.circle(x, y, radius, stroke=1, fill=1)


def label(c: Canvas, value: str, x: float, y: float, size: float = 10, color: str = BLACK) -> None:
    c.setFillColor(HexColor(color))
    c.setFont("BF-Vera", size)
    c.drawCentredString(x, y, value)


def header(c: Canvas, index: str, title: str, subtitle: str) -> None:
    text(c, index, 20, 328, 38, 10, RED)
    text(c, title, 63, 331, 458, 19)
    text(c, subtitle, 63, 304, 458, 9, MUTED)
    line(c, 20, 286, 520, 286)


def footer(c: Canvas, value: str) -> None:
    line(c, 20, 40, 520, 40)
    text(c, value, 20, 31, 500, 9, MUTED)


def petal(c: Canvas, x: float, y: float, color: str, turn: float = 0) -> None:
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


def ribbon(c: Canvas, x: float, y: float, color: str, flip: float = 1) -> None:
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
