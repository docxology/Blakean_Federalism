# Copyright (c) 2026 Daniel Ari Friedman
"""Produce the two exact timing views with vector masters and recorded raster children."""

import json
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Final

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .figure_style import registry
from .models import ResearchError
from .review_timing import timing_figure_data, timing_summary
from .review_timing_captions import timing_captions
from .review_timing_models import TimingAtlas
from .review_timing_protection_figure import draw_protection
from .review_timing_readiness_figure import draw_readiness

_READINESS_CELLS: Final = 1122
_ENDPOINT_CELLS: Final = 1200
_TIMELINE_CELLS: Final = 4


def validate_timing_figures(atlas: TimingAtlas) -> None:
    if shutil.which("pdftoppm") is None:
        raise ResearchError("timing_rasterizer_missing", "pdftoppm is required for PNG derivatives")
    data = timing_figure_data(atlas)
    if (len(data.readiness), len(data.geometry), len(data.timeline_cells)) != (
        _READINESS_CELLS,
        _ENDPOINT_CELLS,
        _TIMELINE_CELLS,
    ):
        raise ResearchError("timing_figure_scope", "This layout requires the complete fixed views")


def _rasterize(pdf: Path, executable: str) -> Path:
    """Retain actual child identity, raw streams and terminal status, including failures."""
    stem = pdf.with_suffix("")
    command = [executable, "-singlefile", "-scale-to", "3200", "-png", str(pdf), str(stem)]
    with (
        stem.with_suffix(".stdout.log").open("xb") as stdout,
        stem.with_suffix(".stderr.log").open("xb") as stderr,
    ):
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr)  # noqa: S603 -- Resolved rasterizer; bounded argv.
        _ = stem.with_suffix(".child.json").write_text(
            json.dumps({"pid": child.pid, "argv": command}) + "\n"
        )
        status = child.wait()
    _ = stem.with_suffix(".exit.json").write_text(
        json.dumps({"returncode": status, "reaped": True}) + "\n"
    )
    if status != 0:
        raise subprocess.CalledProcessError(status, command)
    return stem.with_suffix(".png")


def render_timing_figures(atlas: TimingAtlas, output: Path) -> tuple[Path, ...]:
    validate_timing_figures(atlas)
    rasterizer = shutil.which("pdftoppm")
    if rasterizer is None:
        raise ResearchError("timing_rasterizer_missing", "Rasterizer became unavailable")
    fonts = Path(__file__).parent / "resources/fonts"
    registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(fonts / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    results: list[Path] = []
    for name, size, draw in (
        ("review-timing-readiness", (540, 580), draw_readiness),
        ("review-timing-protection", (540, 620), draw_protection),
    ):
        pdf = output / (name + ".pdf")
        canvas = Canvas(str(pdf), pagesize=size, invariant=1)
        canvas.setTitle(name)
        draw(canvas, atlas)
        canvas.showPage()
        canvas.save()
        results.extend((pdf, _rasterize(pdf, rasterizer)))
    data = timing_figure_data(atlas)
    captions = timing_captions(timing_summary(atlas), data)
    _ = (output / "figure-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "figure_data_sha256": sha256(
                    (data.model_dump_json(indent=2, round_trip=True) + "\n").encode()
                ).hexdigest(),
                "figures": [
                    {
                        "label": "fig:review-timing-readiness",
                        "pdf": "review-timing-readiness.pdf",
                        "png": "review-timing-readiness.png",
                        "width_points": 540,
                        "height_points": 580,
                        "caption": captions.readiness,
                        "alt": "Resident panels, member strips and late-readiness crosses.",
                    },
                    {
                        "label": "fig:review-timing-protection",
                        "pdf": "review-timing-protection.pdf",
                        "png": "review-timing-protection.png",
                        "width_points": 540,
                        "height_points": 620,
                        "caption": captions.protection,
                        "alt": "Four endpoint triangles and four paired timing contrasts.",
                    },
                ],
            },
            indent=2,
        )
        + "\n"
    )
    return tuple(results)
