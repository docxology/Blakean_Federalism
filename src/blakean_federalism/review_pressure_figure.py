# Copyright (c) 2026 Daniel Ari Friedman
"""Place measured access beside separately declared practical pressure boundaries."""

import shutil
import subprocess
from pathlib import Path
from typing import Final, assert_never

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, WHITE, label, line, registry, text
from .models import ResearchError
from .review_pressure import PressureReport
from .review_pressure_models import BoundaryStatus, PressureIssue

_WIDTH: Final = 720
_HEIGHT: Final = 500
_CASE_COUNT: Final = 8
_HEADINGS: Final = (
    "Admit",
    "Remain",
    "Filing\nhours",
    "Ready",
    "No wait\ngap",
    "Separate\noffice",
    "Revise",
    "Material\nsupport",
    "Reprisal\nsafety",
    "Reviewer\ncontrol",
    "Collective\nreservation",
)


def _boundary_mark(canvas: Canvas, position: tuple[float, float], status: BoundaryStatus) -> None:
    """Encode one declared premise; exhaustive return paths leave no implicit variant."""
    x, y = position
    match status:
        case BoundaryStatus.STIPULATED_PROTECTION:
            canvas.setStrokeColor(HexColor(BLACK))
            canvas.circle(x, y, 3, stroke=1, fill=0)
            return
        case BoundaryStatus.STIPULATED_OBSTRUCTION:
            canvas.setStrokeColor(HexColor(RED))
            canvas.line(x - 3, y - 3, x + 3, y + 3)
            canvas.line(x - 3, y + 3, x + 3, y - 3)
            return
        case BoundaryStatus.UNASSESSED:
            label(canvas, "?", x, y - 3, 11, MUTED)
            return
        case _:
            assert_never(status)


def _draw(canvas: Canvas, report: PressureReport) -> None:
    text(canvas, "A completed access profile leaves practical questions open", 18, 483, 684, 18)
    text(
        canvas,
        (
            f"{len(report.results)} constructed pressures on "
            f"{report.study.reference_procedure_id}; the underlying decision stays fixed"
        ),
        18,
        454,
        684,
        10,
    )
    line(canvas, 18, 432, 702, 432, RED, 1.4)
    label(canvas, "COMPUTED REVIEW CONDITIONS", 350, 419, 8.5, MUTED)
    label(canvas, "DECLARED PRACTICAL PREMISES", 620, 419, 8.5, RED)
    for index, heading in enumerate(_HEADINGS):
        x = 242 + index * 42
        for row, part in enumerate(heading.split("\n")):
            label(canvas, part, x, 397 - row * 10, 7.5)
    for index, item in enumerate(report.results):
        y = 348 - index * 30
        text(canvas, str(item.case.procedure.procedure_id), 18, y + 6, 36, 10, RED)
        text(canvas, item.case.procedure.label, 53, y + 6, 164, 8)
        line(canvas, 18, y - 13, 702, y - 13, GREY, 0.4)
        for column, holds in enumerate(item.review.conditions):
            x = 242 + column * 42
            canvas.setStrokeColor(HexColor(BLACK if holds else RED))
            canvas.setLineWidth(1.2)
            if holds:
                canvas.circle(x, y, 3, stroke=1, fill=0)
            else:
                canvas.line(x - 3, y - 3, x + 3, y + 3)
                canvas.line(x - 3, y + 3, x + 3, y - 3)
        statuses = {entry.issue: entry.status for entry in item.case.boundaries}
        for column, issue in enumerate(PressureIssue, start=7):
            x = 242 + column * 42
            _boundary_mark(canvas, (x, y), statuses[issue])
    line(canvas, 513, 106, 513, 412, GREY, 0.8)
    text(
        canvas, "Left: open circle = condition holds; red cross = condition fails.", 18, 94, 684, 9
    )
    text(
        canvas,
        "Right: circle = stipulated protection; cross = stipulated obstruction; ? = unassessed.",
        18,
        76,
        684,
        9,
    )
    text(
        canvas,
        (
            "The first five conditions require every listed claimant. "
            "Practical premises have separate subjects:"
        ),
        18,
        56,
        684,
        8.5,
    )
    text(
        canvas,
        (
            f"Subjects: {report.study.affected_person_id} (support/reprisal); "
            f"office (control); {report.study.collective_party_id} (reservation)."
        ),
        18,
        41,
        684,
        8.5,
    )
    text(
        canvas,
        "No combined score or finding of institutional legitimacy follows from either panel.",
        18,
        22,
        684,
        8.5,
        RED,
    )


def render_pressure_figure(report: PressureReport, output: Path) -> tuple[Path, Path]:
    """Render a source-derived vector master and sharp raster without replacing old output."""
    rasterizer = shutil.which("pdftoppm")
    if rasterizer is None:
        raise ResearchError("pressure_rasterizer_missing", "pdftoppm is required")
    if len(report.results) != _CASE_COUNT:
        raise ResearchError("pressure_figure_scope", "This layout requires the fixed eight cases")
    fonts = Path(__file__).parent / "resources/fonts"
    registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(fonts / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    pdf = output / "review-pressure.pdf"
    canvas = Canvas(str(pdf), pagesize=(_WIDTH, _HEIGHT), invariant=1)
    canvas.setFillColor(HexColor(WHITE))
    canvas.rect(0, 0, _WIDTH, _HEIGHT, stroke=0, fill=1)
    _draw(canvas, report)
    canvas.showPage()
    canvas.save()
    _ = subprocess.run(  # noqa: S603 -- Resolved executable and explicit file argv.
        [
            rasterizer,
            "-singlefile",
            "-scale-to",
            "3000",
            "-png",
            str(pdf),
            str(output / "review-pressure"),
        ],
        check=True,
        capture_output=True,
    )
    return pdf, output / "review-pressure.png"
