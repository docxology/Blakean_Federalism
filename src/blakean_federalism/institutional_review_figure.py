# Copyright (c) 2026 Daniel Ari Friedman
"""Directly labeled review-condition matrix and event-hour continuity diagram."""

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, WHITE, label, line, registry, text
from .institutional_review import ClaimantReview, ProcedureReview, ReviewReport

_WIDTH = 540
_MATRIX_HEIGHT = 590
_TIMELINE_HEIGHT = 490
_ROW_HEIGHT = 27
_TIMELINE_ROW_HEIGHT = 43
_MATRIX_LIMIT = 14
_TIMELINE_LIMIT = 7
_COLUMNS = (
    "Standing",
    "Remain",
    "Filing\nhours",
    "Ready\nin time",
    "No wait\ngap",
    "Separate\noffice",
    "Revise\nact",
)


def _mark(canvas: Canvas, x: float, y: float, *, holds: bool) -> None:
    canvas.setLineWidth(1.2)
    canvas.setStrokeColor(HexColor(BLACK if holds else RED))
    if holds:
        canvas.circle(x, y, 3, stroke=1, fill=0)
    else:
        canvas.line(x - 3, y - 3, x + 3, y + 3)
        canvas.line(x - 3, y + 3, x + 3, y - 3)


def _matrix(canvas: Canvas, report: ReviewReport) -> None:
    text(canvas, "A review forum can exist while access fails", 16, 574, 510, 18)
    text(
        canvas,
        "14 stipulated procedures · standing, support and timing checked person by person",
        16,
        542,
        510,
        9,
    )
    line(canvas, 16, 519, 524, 519, RED, 1.5)
    text(canvas, "PROCEDURE / CHANGED PREMISE", 16, 508, 240, 8, MUTED)
    for i, title in enumerate(_COLUMNS):
        for j, part in enumerate(title.split("\n")):
            label(canvas, part, 285 + i * 36, 502 - j * 10, 7.6)
    for i, result in enumerate(report.results):
        y = 465 - i * _ROW_HEIGHT
        line(canvas, 16, y - 12, 524, y - 12, GREY, 0.4)
        suffix = " *" if result.procedure.unassessed_issues else ""
        text(canvas, f"{result.procedure.procedure_id}{suffix}", 16, y + 6, 38, 9, RED)
        text(canvas, result.procedure.label, 58, y + 6, 201, 8.7)
        for j, holds in enumerate(result.conditions):
            _mark(canvas, 285 + j * 36, y, holds=holds)
    _mark(canvas, 20, 80, holds=True)
    text(canvas, "condition holds", 29, 87, 120, 9)
    _mark(canvas, 157, 80, holds=False)
    text(canvas, "at least one individual / procedure condition fails", 166, 87, 358, 9)
    text(
        canvas,
        """The first five columns require every listed individual.
Office separation and revision power apply to the procedure.
No conditions are pooled or scored.""",
        16,
        65,
        510,
        8.5,
    )
    text(
        canvas,
        "* Declared unassessed issues accompany the procedure outside these seven conditions.",
        16,
        33,
        510,
        8.5,
        RED,
    )


def _selection(report: ReviewReport) -> tuple[tuple[ProcedureReview, ClaimantReview], ...]:
    rows: list[tuple[ProcedureReview, ClaimantReview]] = []
    for selection in report.study.timeline_selections:
        result = next(
            x for x in report.results if x.procedure.procedure_id == selection.procedure_id
        )
        person = next(x for x in result.claimants if x.claimant_id == selection.claimant_id)
        rows.append((result, person))
    return tuple(rows)


def _timeline(canvas: Canvas, report: ReviewReport) -> None:
    rows = _selection(report)
    maximum = max(
        max(result.procedure.response_hour, person.consequence_hour)
        for result, audit in rows
        for person in result.procedure.claimants
        if person.claimant_id == audit.claimant_id
    )
    maximum = max(maximum, 1)
    left, span = 211, 298

    def at(hour: int) -> float:
        return left + span * hour / maximum

    text(canvas, "When review arrives matters", 16, 475, 510, 19)
    text(canvas, "Selected individuals · exact event hours from notice (0 h)", 16, 444, 510, 9)
    line(canvas, 16, 422, 524, 422, RED, 1.5)
    for tick in range(6):
        value = maximum * tick / 5
        x = left + span * tick / 5
        line(canvas, x, 103, x, 397, GREY, 0.4)
        label(canvas, f"{value:g} h", x, 404, 8, MUTED)
    for i, (result, audit) in enumerate(rows):
        person = next(x for x in result.procedure.claimants if x.claimant_id == audit.claimant_id)
        y = 374 - i * _TIMELINE_ROW_HEIGHT
        text(
            canvas,
            f"{result.procedure.procedure_id}  {result.procedure.label}",
            16,
            y + 13,
            188,
            8.5,
        )
        opens = at(result.procedure.filing_opens_hour)
        closes = at(result.procedure.filing_closes_hour)
        line(canvas, opens, y + 15, closes, y + 15, MUTED, 1)
        line(canvas, opens, y + 12, opens, y + 18, MUTED, 1)
        line(canvas, closes, y + 12, closes, y + 18, MUTED, 1)
        line(canvas, left, y, left + span, y, GREY, 1)
        if audit.active_protection is not None:
            start, end = audit.active_protection
            line(canvas, at(start), y + 6, at(end), y + 6, BLACK, 4)
        for start, end in audit.uncovered_intervals:
            line(canvas, at(start), y, at(end), y, RED, 5)
        harm = at(person.consequence_hour)
        response = at(result.procedure.response_hour)
        line(canvas, harm, y - 5, harm, y + 11, RED, 1.3)
        canvas.setStrokeColor(HexColor(BLACK))
        canvas.setFillColor(HexColor(WHITE))
        canvas.circle(response, y, 3, stroke=1, fill=1)
        text(
            canvas,
            f"{audit.uncovered_wait_hours} h uncovered",
            211,
            y - 8,
            280,
            8,
            RED if audit.uncovered_wait_hours else MUTED,
        )
    line(canvas, 20, 77, 20, 89, RED, 1.3)
    text(canvas, "consequence", 28, 88, 76, 7.6)
    canvas.setStrokeColor(HexColor(BLACK))
    canvas.circle(111, 83, 3, stroke=1, fill=0)
    text(canvas, "response", 120, 88, 64, 7.6)
    line(canvas, 185, 83, 198, 83, MUTED, 1)
    line(canvas, 185, 80, 185, 86, MUTED, 1)
    line(canvas, 198, 80, 198, 86, MUTED, 1)
    text(canvas, "filing window", 207, 88, 82, 7.6)
    line(canvas, 291, 83, 304, 83, BLACK, 4)
    text(canvas, "protection", 313, 88, 68, 7.6)
    line(canvas, 386, 83, 399, 83, RED, 5)
    text(canvas, "uncovered wait", 408, 88, 116, 7.6)
    text(
        canvas,
        """Protection covers [start, end). An end at the response hour covers the wait.
A response at the consequence instant acts first.""",
        16,
        65,
        510,
        8.5,
    )
    text(
        canvas,
        """Automatic protection starts independently of filing.
Filing-triggered protection starts only once the individual can file.""",
        16,
        34,
        510,
        8.5,
    )


def _rasterizer() -> str:
    executable = shutil.which("pdftoppm")
    if executable is None:
        raise ValueError("pdftoppm_missing")
    return executable


def validate_review_figure_report(report: ReviewReport) -> None:
    if (
        len(report.results) != _MATRIX_LIMIT
        or len(report.study.timeline_selections) != _TIMELINE_LIMIT
    ):
        raise ValueError("review_figure_requires_fixed_14_by_7_study")
    _ = _rasterizer()


def render_review_figures(report: ReviewReport, output: Path) -> tuple[Path, ...]:
    validate_review_figure_report(report)
    rasterizer = _rasterizer()
    fonts = Path(__file__).parent / "resources/fonts"
    registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(fonts / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    results: list[Path] = []
    drawings = (
        ("institutional-review", _MATRIX_HEIGHT, _matrix),
        ("review-continuity", _TIMELINE_HEIGHT, _timeline),
    )
    for name, height, draw in drawings:
        path = output / (name + ".pdf")
        canvas = Canvas(str(path), pagesize=(_WIDTH, height), invariant=1)
        canvas.setFillColor(HexColor(WHITE))
        canvas.rect(0, 0, _WIDTH, height, stroke=0, fill=1)
        draw(canvas, report)
        canvas.showPage()
        canvas.save()
        _ = subprocess.run(  # noqa: S603 -- Resolved executable and explicit file argv; no shell.
            [rasterizer, "-singlefile", "-scale-to", "2400", "-png", str(path), str(output / name)],
            check=True,
            capture_output=True,
        )
        results.extend((path, output / (name + ".png")))
    return tuple(results)
