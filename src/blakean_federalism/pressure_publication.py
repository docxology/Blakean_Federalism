# Copyright (c) 2026 Daniel Ari Friedman
"""Keep the fixed pressure experiment beside its manuscript figures and caption."""

from pathlib import Path

from .review_pressure_run import pressure_caption, publish_pressure
from .storage import copy_new, safe_path


def prepare_pressure_figure(root: Path, stage: Path) -> str:
    """Retain the complete source-bound experiment and copy independent figure bytes."""
    audit = stage / "review-pressure"
    report = publish_pressure(root, audit, figures=True)
    for suffix in (".pdf", ".png"):
        copy_new(
            safe_path(audit, "figures/review-pressure" + suffix),
            stage / "output/figures" / ("review-pressure" + suffix),
        )
    return pressure_caption(report)
