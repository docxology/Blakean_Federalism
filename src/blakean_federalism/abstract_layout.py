# Copyright (c) 2026 Daniel Ari Friedman
"""Shared measured typography and verified inputs for analytical abstract pages."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

from .abstract_analysis import corpus_diagnostics, repair_diagnostics
from .abstract_analysis_models import QueryDiagnostic, RepairDiagnostics
from .analysis_figures import FOCUS
from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, MUTED, RED, line
from .illuminated_style import prose, register_serif_fonts
from .institutional_experiment_models import InstitutionalExperiment
from .manuscript import Quotation
from .models import ResearchError
from .workbench_models import Workbench

_MAX_FAILING_BASELINES = 5


@dataclass(frozen=True)
class AbstractSources:
    report: Workbench
    statistics: CorpusStatistics
    experiment: InstitutionalExperiment
    artwork: Mapping[str, Path]
    quotations: Mapping[str, Quotation]
    corpus: tuple[QueryDiagnostic, ...]
    repairs: RepairDiagnostics

    def verse(self, quote_id: str, start: int = 0, stop: int | None = None) -> str:
        return " ".join(segment.text for segment in self.quotations[quote_id].segments[start:stop])


def analytical_sources(report: Workbench, artwork: Mapping[str, Path]) -> AbstractSources:
    quotes = {quote.quote_id: quote for quote in report.quotations}
    for key, count in {
        "Q03": 2,
        "Q13": 1,
        "Q14": 4,
        "Q37": 1,
        "Q38": 3,
        "Q39": 3,
        "Q40": 1,
    }.items():
        if key not in quotes or len(quotes[key].segments) < count:
            raise ResearchError("figure_quotation", key)
    if "J1" not in artwork or not artwork["J1"].is_file():
        raise ResearchError("figure_artwork", "J1")
    if report.corpus_statistics is None or report.institutional_experiments is None:
        raise ResearchError("publication_statistics", "Corpus and intervention inputs required")
    repairs = repair_diagnostics(report.institutional_experiments)
    if sum(bool(row.baseline_failed_rules) for row in repairs.cases) > _MAX_FAILING_BASELINES:
        raise ResearchError("figure_case_layout", "At most five failing baselines fit")
    register_serif_fonts()
    return AbstractSources(
        report,
        report.corpus_statistics,
        report.institutional_experiments,
        dict(artwork),
        quotes,
        corpus_diagnostics(report.corpus_statistics, FOCUS),
        repairs,
    )


def heading(canvas: Canvas, title: str, subtitle: str) -> None:
    prose(canvas, title, (20, 505, 500, 27), size=16, font="BF-Serif-Bold")
    prose(canvas, subtitle, (20, 476, 500, 25), size=9.5, color=MUTED)
    line(canvas, 20, 446, 520, 446, RED, 0.8)


def footer(canvas: Canvas, value: str) -> None:
    line(canvas, 20, 36, 520, 36, BLACK, 0.45)
    prose(canvas, value, (20, 29, 500, 25), size=8.6, color=MUTED)


def cell(  # noqa: PLR0913, PLR0917 -- Explicit geometry and independent text settings.
    canvas: Canvas,
    value: str,
    x: float,
    top: float,
    width: float,
    height: float = 28,
    *,
    size: float = 9.3,
    color: str = BLACK,
    font: str = "BF-Vera",
) -> None:
    prose(canvas, value, (x, top, width, height), size=size, color=color, font=font)
