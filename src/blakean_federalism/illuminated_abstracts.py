# Copyright (c) 2026 Daniel Ari Friedman
"""Validate illuminated sources and dispatch the selected abstract profile."""

from collections.abc import Callable, Mapping
from functools import partial
from pathlib import Path
from typing import Final

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import FOCUS
from .analytical_abstracts import analytical_drawings
from .illuminated_readings import draw_composition, draw_scholarship
from .illuminated_records import draw_decision, draw_evidence
from .illuminated_sources import IlluminatedSources
from .illuminated_style import register_serif_fonts
from .models import ResearchError
from .publication_profiles import ANALYTICAL_PRODUCERS
from .workbench_models import Workbench

_MAX_BASELINES: Final = 5
_REQUIRED_ART: Final = frozenset({"J1", "J52", "J55", "J91"})
_QUOTE_LENGTHS: Final[Mapping[str, int]] = {
    "Q03": 2,
    "Q05": 4,
    "Q13": 1,
    "Q14": 4,
    "Q16": 1,
    "Q18": 2,
    "Q23": 1,
    "Q31": 1,
}


def illuminated_drawings(
    report: Workbench, artwork: Mapping[str, Path]
) -> dict[str, Callable[[Canvas], None]]:
    """Require real artwork, recorded verse and analytical inputs before drawing any page."""
    missing = _REQUIRED_ART - artwork.keys()
    if missing:
        raise ResearchError("figure_artwork", ", ".join(sorted(missing)))
    for key in sorted(_REQUIRED_ART):
        if not artwork[key].is_file():
            raise ResearchError("figure_artwork", key)
    quotes = {q.quote_id: q for q in report.quotations}
    for key, count in _QUOTE_LENGTHS.items():
        if key not in quotes or len(quotes[key].segments) < count:
            raise ResearchError("figure_quotation", key)
    stats, experiment = report.corpus_statistics, report.institutional_experiments
    if stats is None or experiment is None:
        raise ResearchError(
            "publication_statistics", "Statistics and intervention results required"
        )
    if not set(FOCUS) <= {q.query_id for q in stats.queries}:
        raise ResearchError("figure_queries", "Eight declared comparison queries required")
    failed = [row for row in experiment.decisions if row.baseline_failed_rules]
    if len(failed) > _MAX_BASELINES:
        raise ResearchError("figure_case_layout", "At most five failed baselines fit this figure")
    if report.producer_version in ANALYTICAL_PRODUCERS:
        return analytical_drawings(report, artwork)
    register_serif_fonts()
    source = IlluminatedSources(report, dict(artwork), quotes, stats, experiment)
    return {
        "abstract-1": partial(draw_composition, source=source),
        "abstract-2": partial(draw_scholarship, source=source),
        "abstract-3": partial(draw_decision, source=source),
        "abstract-4": partial(draw_evidence, source=source),
    }
