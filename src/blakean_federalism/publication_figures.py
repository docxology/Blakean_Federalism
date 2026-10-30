# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound body figures and deterministic vector/raster output."""

import io
import subprocess
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import FOCUS, cooccurrence, rates, repairs, sensitivity
from .federated_comparison_figure import draw_federated_comparison
from .figure_style import (
    WHITE as PAPER,
)
from .figure_style import (
    registry as _registry,
)
from .illuminated_abstracts import illuminated_drawings
from .proximity_figure import draw_proximity_study
from .proximity_study import ProximityStudy
from .publication_abstracts import composition, decision, scholarship
from .publication_body import (
    draw_agreement_routes,
    draw_census,
    draw_relations,
    draw_rule_matrix,
    draw_watershed,
)
from .publication_evidence import evidence
from .search_figure import draw_search_study
from .search_study import SearchStudy
from .workbench_models import Workbench


def generate_figures(
    report: Workbench,
    output: Path,
    rasterizer: str,
    search_study: SearchStudy | None = None,
    proximity_study: ProximityStudy | None = None,
    *,
    artwork: dict[str, Path] | None = None,
) -> dict[str, str]:
    """Write new deterministic vector masters and PNG derivatives."""
    directory = Path(__file__).parent / "resources/fonts"
    _registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(directory / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    results: dict[str, str] = {}
    drawings: dict[str, Callable[[Canvas], None]] = {
        "abstract-1": composition,
        "abstract-2": scholarship,
        "abstract-3": decision,
        "abstract-4": partial(evidence, report=report),
        "typed-relations": draw_relations,
        "source-census": partial(draw_census, report=report),
        "case-traces": partial(draw_rule_matrix, report=report),
        "watershed-options": draw_watershed,
        "agreement-routes": draw_agreement_routes,
    }
    if artwork is not None:
        drawings.update(illuminated_drawings(report, artwork))
        if report.producer_version in ("0.12.0", "0.13.0", "0.14.0", "0.15.0", "0.16.0", "0.17.0"):
            drawings["federated-inference-authority"] = draw_federated_comparison
    stats = report.corpus_statistics
    if stats is not None and set(FOCUS) <= {q.query_id for q in stats.queries}:
        drawings.update(
            {
                "copy-balanced-rates": partial(rates, stats=stats),
                "source-sensitivity": partial(sensitivity, stats=stats),
                "term-associations": partial(cooccurrence, stats=stats),
            }
        )
        if report.institutional_experiments is not None:
            drawings["counterfactual-repairs"] = partial(repairs, report=report)
    if search_study is not None:
        drawings["literal-search-strata"] = partial(draw_search_study, study=search_study)
    if proximity_study is not None:
        drawings["literal-proximity-windows"] = partial(draw_proximity_study, study=proximity_study)
    for name, drawing in drawings.items():
        stream = io.BytesIO()
        height = 520 if name.startswith("abstract-") else 445
        c = Canvas(stream, pagesize=(540, height), invariant=1)
        c.setFillColor(HexColor(PAPER))
        c.rect(0, 0, 540, height, fill=1, stroke=0)
        drawing(c)
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
