# Copyright (c) 2026 Daniel Ari Friedman
"""Bind the new requirement analysis and its captions into the native publication stage."""

from dataclasses import dataclass
from pathlib import Path

from .review_comparison import ReviewComparison
from .review_comparison_figure import comparison_captions
from .review_comparison_run import publish_comparison
from .review_publication import prepare_review_figures
from .storage import copy_new, safe_path

NAMES = ("review-requirements", "review-comparability")


@dataclass(frozen=True, slots=True)
class PreparedDomainFigures:
    figures: dict[str, str]
    captions: dict[str, str]


def prepare_domain_figures(
    root: Path, stage: Path, labels: tuple[str, ...]
) -> PreparedDomainFigures:
    """Prepare only the domain analyses selected by the manuscript's figure labels."""
    figures = prepare_review_figures(root, stage) if "fig:review-matrix" in labels else {}
    captions: dict[str, str] = {}
    if "fig:review-requirements" in labels:
        report = prepare_comparison_figures(root, stage)
        figures.update({name: name + ".png" for name in NAMES})
        captions.update(comparison_captions(report))
    return PreparedDomainFigures(figures, captions)


def prepare_comparison_figures(root: Path, stage: Path) -> ReviewComparison:
    """Keep the complete domain run beside the copied publication figure masters."""
    audit = stage / "review-comparison"
    report = publish_comparison(
        safe_path(root, "research/institutional-review-cases.json"),
        safe_path(root, "research/cases.json"),
        audit,
        figures=True,
    )
    for name in NAMES:
        for suffix in (".pdf", ".png"):
            copy_new(
                safe_path(audit, "figures/" + name + suffix),
                stage / "output/figures" / (name + suffix),
            )
    return report
