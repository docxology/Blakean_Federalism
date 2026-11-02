# Copyright (c) 2026 Daniel Ari Friedman
"""Draw the exact readiness slice with a separate member exposure strip."""

from dataclasses import dataclass

from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, MUTED, RED, label, line, text
from .review_timing import MEMBER, RESIDENT, timing_figure_data
from .review_timing_models import TimingAtlas, TimingCell, TimingMode


@dataclass(frozen=True, slots=True)
class ReadinessPanel:
    x: float
    y: float
    mode: TimingMode
    stratum: str


def _shade(hours: int) -> Color:
    fraction = hours / 24
    return Color(1 - 0.35 * fraction, 1 - 0.88 * fraction, 1 - 0.82 * fraction)


def _panel(c: Canvas, cells: tuple[TimingCell, ...], panel: ReadinessPanel) -> None:
    selected = tuple(
        cell
        for cell in cells
        if cell.configuration.stratum_id == panel.stratum and cell.configuration.mode == panel.mode
    )
    indexed = {
        (cell.configuration.response_hour, cell.configuration.resident_ready_hour): cell
        for cell in selected
    }
    width = 8.7
    label(c, panel.mode.value.replace("_", " "), panel.x + 48, panel.y + 165, 9)
    for response in range(8, 25):
        y = panel.y + (response - 8) * width
        label(c, str(response), panel.x - 10, y + 1, 7.2)
        for ready in range(11):
            cell = indexed[response, ready]
            person = next(p for p in cell.review.claimants if p.claimant_id == RESIDENT)
            x = panel.x + ready * width
            c.setFillColor(_shade(person.uncovered_wait_hours))
            c.rect(x, y, width, width, stroke=0, fill=1)
            if not person.filing_ready:
                c.setStrokeColor(HexColor(BLACK))
                c.setLineWidth(0.45)
                c.line(x + 2, y + 2, x + width - 2, y + width - 2)
                c.line(x + 2, y + width - 2, x + width - 2, y + 2)
        member = next(p for p in indexed[response, 0].review.claimants if p.claimant_id == MEMBER)
        c.setFillColor(_shade(member.uncovered_wait_hours))
        c.rect(panel.x + 105, y, width, width, stroke=0, fill=1)
    for ready in range(11):
        label(c, str(ready), panel.x + (ready + 0.5) * width, panel.y - 11, 7)
    c.setStrokeColor(HexColor(MUTED))
    c.setLineWidth(0.6)
    c.rect(panel.x, panel.y, 11 * width, 17 * width, stroke=1, fill=0)
    c.rect(panel.x + 105, panel.y, width, 17 * width, stroke=1, fill=0)
    line(c, panel.x + 9 * width, panel.y, panel.x + 9 * width, panel.y + 17 * width, RED, 0.8)
    c.saveState()
    c.setDash(2, 2)
    line(
        c, panel.x, panel.y + 12.5 * width, panel.x + 11 * width, panel.y + 12.5 * width, MUTED, 0.6
    )
    c.restoreState()
    label(c, "member", panel.x + 109, panel.y - 26, 7)
    label(c, "ready (h)", panel.x + 48, panel.y - 26, 8)


def draw_readiness(c: Canvas, atlas: TimingAtlas) -> None:
    """Draw six panels at intended manuscript width, retaining every zero and late cell."""
    cells = timing_figure_data(atlas).readiness
    text(c, "When protection becomes usable", 15, 565, 510, 16)
    text(
        c,
        "Resident exposure by response and completed readiness; member-a remains separate",
        15,
        540,
        510,
        9,
    )
    for row, stratum in enumerate(atlas.specification.strata):
        y = 300 - row * 235
        text(
            c,
            f"{stratum.stratum_id}: resident consequence {stratum.resident_consequence_hour} h",
            15,
            y + 195,
            510,
            9,
            RED,
        )
        for column, mode in enumerate(TimingMode):
            panel = ReadinessPanel(37 + column * 171, y + 7, mode, stratum.stratum_id)
            _panel(c, cells, panel)
    text(
        c,
        "Response 8-24 h; cross: readiness after closing at 8 h. Dashed guide: response 20 h.",
        15,
        36,
        510,
        8,
    )
    text(
        c,
        "Expiry is 20 h. Protected bands begin at the resident consequence for both named people.",
        15,
        22,
        510,
        8,
    )
    for hours in range(25):
        c.setFillColor(_shade(hours))
        c.rect(180 + hours * 5.5, 2, 5.5, 8, stroke=0, fill=1)
    label(c, "0 h", 164, 2, 7)
    label(c, "24 h uncovered", 363, 2, 7)
