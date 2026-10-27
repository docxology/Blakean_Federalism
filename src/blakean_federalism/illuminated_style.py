# Copyright (c) 2026 Daniel Ari Friedman
"""Measured serif typography and uncropped plate placement for illuminated abstracts."""

from math import atan2, cos, sin
from pathlib import Path
from typing import Protocol, cast
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from .figure_style import BLACK, MUTED, RED, line, registry
from .models import ResearchError

Rect = tuple[float, float, float, float]


class _ImageCanvas(Protocol):
    def drawImage(  # noqa: N802, PLR0913 -- ReportLab API geometry and placement.
        self,
        image: str,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        preserveAspectRatio: bool,  # noqa: N803 -- Third-party keyword API.
        anchor: str,
    ) -> tuple[float, float]: ...


def register_serif_fonts() -> None:
    """Embed the bundled DejaVu faces so italic shape survives reader substitution."""
    directory = Path(__file__).parent / "resources/fonts"
    for face, filename in (
        ("BF-Serif", "DejaVuSerif.ttf"),
        ("BF-Serif-Bold", "DejaVuSerif-Bold.ttf"),
        ("BF-Serif-Italic", "DejaVuSerif-Italic.ttf"),
    ):
        registry(pdfmetrics).registerFont(TTFont(face, str(directory / filename)))


def prose(  # noqa: PLR0913 -- Text geometry and explicit typography are independent controls.
    canvas: Canvas,
    value: str,
    rect: Rect,
    *,
    size: float = 10,
    font: str = "BF-Vera",
    color: str = BLACK,
) -> None:
    """Draw within a top-origin text rectangle; reject overflow instead of shrinking type."""
    x, top, width, available = rect
    paragraph = Paragraph(
        escape(value),
        ParagraphStyle(
            "illuminated",
            fontName=font,
            fontSize=size,
            leading=size * 1.16,
            textColor=HexColor(color),
        ),
    )
    _, height = paragraph.wrap(width, available)
    if height > available:
        raise ResearchError("figure_text_overflow", value)
    paragraph.drawOn(canvas, x, top - height)


def plate(canvas: Canvas, path: Path, rect: Rect) -> None:
    """Fit the whole original image without crop, recoloring or orientation changes."""
    x, top, width, height = rect
    _ = cast("_ImageCanvas", canvas).drawImage(
        str(path), x, top - height, width, height, preserveAspectRatio=True, anchor="c"
    )


def heading(canvas: Canvas, number: str, title: str, subtitle: str) -> None:
    prose(canvas, number, (20, 504, 30, 20), size=11, color=RED)
    prose(canvas, title, (55, 506, 465, 32), size=21, font="BF-Serif-Bold")
    prose(canvas, subtitle, (55, 475, 465, 25), size=9.5, color=MUTED)
    line(canvas, 20, 445, 520, 445, RED, 1.2)


def footer(canvas: Canvas, value: str) -> None:
    line(canvas, 20, 39, 520, 39, BLACK, 0.5)
    prose(canvas, value, (20, 32, 500, 25), size=9, color=MUTED)


def arrow(
    canvas: Canvas,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    dashed: bool = False,
) -> None:
    """Connect two analytical annotations with a red directional stroke."""
    x, y = start
    ex, ey = end
    canvas.saveState()
    if dashed:
        canvas.setDash(3, 3)
    line(canvas, x, y, ex, ey, RED, 1)
    canvas.setDash()
    angle = atan2(ey - y, ex - x)
    for delta in (-0.45, 0.45):
        line(canvas, ex, ey, ex - 5 * cos(angle + delta), ey - 5 * sin(angle + delta), RED, 1)
    canvas.restoreState()
