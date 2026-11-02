# Copyright (c) 2026 Daniel Ari Friedman
"""Carry the complete stipulated timing run into manuscript preparation."""

from pathlib import Path

from .models import ResearchError
from .review_timing import timing_figure_data, timing_summary
from .review_timing_captions import timing_captions
from .review_timing_run import publish_timing
from .storage import copy_new, safe_path

TIMING_LABELS = frozenset({"fig:review-timing-readiness", "fig:review-timing-protection"})
TIMING_FIGURES = ("review-timing-readiness", "review-timing-protection")


def _markdown_caption(text: str) -> str:
    """Keep plain domain text literal inside a Markdown image label."""
    return text.translate(str.maketrans({"\\": "\\\\", "[": "\\[", "]": "\\]"}))


def require_timing_pair(labels: tuple[str, ...]) -> bool:
    """A timing section needs both readiness and protection, retaining each duty stratum."""
    selected = TIMING_LABELS.intersection(labels)
    if selected and selected != TIMING_LABELS:
        raise ResearchError("timing_figure_pair", "Both timing figures must be requested")
    return bool(selected)


def prepare_timing_figures(root: Path, stage: Path) -> dict[str, str]:
    """Produce a fresh complete atlas, then copy its bound vector and raster derivatives."""
    atlas = publish_timing(root, stage / "review-timing", figures=True)
    for name in TIMING_FIGURES:
        for suffix in (".pdf", ".png"):
            source = safe_path(stage / "review-timing/figures", name + suffix)
            target = stage / "output/figures" / (name + suffix)
            copy_new(source, target)
    captions = timing_captions(timing_summary(atlas), timing_figure_data(atlas))
    return {
        "TIMING_READINESS_CAPTION": _markdown_caption(captions.readiness),
        "TIMING_PROTECTION_CAPTION": _markdown_caption(captions.protection),
    }
