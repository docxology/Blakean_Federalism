# Copyright (c) 2026 Daniel Ari Friedman
"""Draw endpoint topology and source-cell two-person timeline anchors."""

from dataclasses import dataclass
from typing import Final

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, label, line, text
from .review_timing import MEMBER, RESIDENT, gap_topology, timing_figure_data
from .review_timing_models import GapTopology, TimingAtlas, TimingCell, TimingMode

_COLORS: Final = {
    GapTopology.EMPTY: "#ffffff",
    GapTopology.INITIAL: "#4477aa",
    GapTopology.TERMINAL: "#ccbb44",
    GapTopology.TWO_COMPONENTS: "#ee6677",
    GapTopology.WHOLE_WAIT: "#332288",
}


@dataclass(frozen=True, slots=True)
class EndpointPanel:
    x: float
    y: float
    mode: TimingMode
    stratum: str


def _triangle(c: Canvas, cells: tuple[TimingCell, ...], panel: EndpointPanel) -> None:
    width = 4.7
    c.setFillColor(HexColor("#dddddd"))
    c.rect(panel.x, panel.y, 24 * width, 24 * width, stroke=0, fill=1)
    for cell in cells:
        config = cell.configuration
        if config.stratum_id != panel.stratum or config.mode != panel.mode:
            continue
        band = config.band
        if band is None:
            continue
        c.setFillColor(HexColor(_COLORS[gap_topology(cell, RESIDENT)]))
        c.rect(
            panel.x + band.starts_hour * width,
            panel.y + (band.ends_hour - 1) * width,
            width,
            width,
            stroke=0,
            fill=1,
        )
    c.setStrokeColor(HexColor(MUTED))
    c.setLineWidth(0.5)
    c.rect(panel.x, panel.y, 24 * width, 24 * width, stroke=1, fill=0)
    line(c, panel.x, panel.y, panel.x + 24 * width, panel.y + 24 * width, MUTED, 0.6)
    line(c, panel.x, panel.y + 19 * width, panel.x + 24 * width, panel.y + 19 * width, RED, 0.6)
    for start in (0, 6, 12, 18, 23):
        label(c, str(start), panel.x + (start + 0.5) * width, panel.y - 11, 7)
    for end in (1, 6, 12, 18, 24):
        label(c, str(end), panel.x - 10, panel.y + (end - 0.5) * width - 2, 7)
    label(c, "declared start (h)", panel.x + 65, panel.y - 24, 8)
    text(
        c,
        f"{panel.stratum}: {panel.mode.value.replace('_', ' ')}",
        panel.x - 25,
        panel.y + 137,
        225,
        9,
    )
    label(c, "end", panel.x - 21, panel.y + 116, 7)


def _timeline(c: Canvas, cell: TimingCell, y: float) -> None:
    config = cell.configuration
    text(
        c,
        config.configuration_id.removeprefix("T.").replace(".r20.a06.", " / "),
        15,
        y + 5,
        510,
        7.7,
    )
    left, scale = 175, 13.7
    for row, identifier in enumerate((MEMBER, RESIDENT)):
        base = y - 12 - row * 12
        person = next(p for p in cell.review.procedure.claimants if p.claimant_id == identifier)
        audit = next(p for p in cell.review.claimants if p.claimant_id == identifier)
        text(c, identifier, 95, base + 4, 75, 7.5)
        line(c, left, base, left + 24 * scale, base, GREY, 0.5)
        if config.band is not None:
            c.setStrokeColor(HexColor(MUTED))
            c.setLineWidth(0.5)
            c.rect(
                left + config.band.starts_hour * scale,
                base - 3,
                (config.band.ends_hour - config.band.starts_hour) * scale,
                6,
                stroke=1,
                fill=0,
            )
        if audit.active_protection is not None:
            start, end = audit.active_protection
            line(c, left + start * scale, base, left + end * scale, base, "#4477aa", 3)
        for start, end in audit.uncovered_intervals:
            line(c, left + start * scale, base, left + end * scale, base, RED, 4)
        line(
            c,
            left + person.consequence_hour * scale,
            base - 4,
            left + person.consequence_hour * scale,
            base + 4,
            RED,
            0.8,
        )
        line(
            c,
            left + config.response_hour * scale,
            base - 4,
            left + config.response_hour * scale,
            base + 4,
            BLACK,
            0.8,
        )


def draw_protection(c: Canvas, atlas: TimingAtlas) -> None:
    data = timing_figure_data(atlas)
    text(c, "Where protection leaves exposure", 15, 605, 510, 16)
    text(
        c,
        "Resident-b: response 20 h, readiness 6 h. Grey: excluded bands; white: empty gap.",
        15,
        580,
        510,
        8.5,
    )
    for row, stratum in enumerate(atlas.specification.strata):
        for column, mode in enumerate((TimingMode.AUTOMATIC, TimingMode.ON_FILING)):
            _triangle(
                c,
                data.geometry,
                EndpointPanel(55 + column * 260, 420 - row * 176, mode, stratum.stratum_id),
            )
    for index, topology in enumerate(GapTopology):
        x = 15 + index * 105
        c.setFillColor(HexColor(_COLORS[topology]))
        c.setStrokeColor(HexColor(MUTED))
        c.rect(x, 199, 9, 9, stroke=1, fill=1)
        text(c, topology.value.replace("_", " "), x + 13, 210, 90, 7.5)
    for index, cell in enumerate(data.timeline_cells):
        _timeline(c, cell, 179 - index * 37)
    for hour in (0, 3, 6, 12, 18, 20, 24):
        label(c, str(hour), 175 + hour * 13.7, 26, 7.5)
    text(
        c,
        "Notice clock (h). Red: gap; blue: active; outline: declared. Ticks: consequence/response.",
        15,
        17,
        510,
        7.5,
    )
